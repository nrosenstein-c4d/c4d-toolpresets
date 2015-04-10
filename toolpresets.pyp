# coding: utf-8
#
# Copyright (C) 2015, Niklas Rosenstein
# All rights reserved.

exec (r"""
# _localimport context-manager
# Copyright (C) 2015  Niklas Rosenstein
# Licensed under the MIT license
# see https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556

import os, sys, glob
_localimport_objects = []  # must not loose reference to cache in importer
class _localimport(object):
    project_path = os.path.dirname(os.path.abspath(__file__))
    stdlib_dir = os.path.dirname(os.path.dirname(os.__file__))
    def __init__(self, libpath, autoeggs=False, isolate=False, path=os.path):
        if not os.path.isabs(libpath):
            libpath = os.path.join(self.project_path, libpath)
        self.libpath = libpath
        self.autoeggs = autoeggs
        self.isolate = isolate
        self.path = [self.libpath] + self.eggs()
        self.modules = {}
        self.meta_path = []
        _localimport_objects.append(self)
    def __enter__(self):
        # Save the previous state of the import mechanism to restore it later.
        self._cache = {
            'path': sys.path[:],
            'meta_path': sys.meta_path[:],
            'disabled_modules': {},
            'prev_modules': frozenset(sys.modules.keys()),
        }
        # Update the path and meta_path.
        sys.path[:] = self.path + sys.path
        sys.meta_path[:] = self.meta_path + sys.meta_path
        # In isolate mode, disable all modules that are not stdlib
        # modules. Also disable all None modules so we can restore them.
        for key, mod in sys.modules.items():
            if mod is None or (self.isolate and not self.is_stdlib(mod)):
                self._cache['disabled_modules'][key] = sys.modules.pop(key)
        # Restore modules imported with _localimport.
        for key, mod in self.modules.iteritems():
            if key in sys.modules:
                self._cache['disabled_modules'][key] = sys.modules.pop(key)
            sys.modules[key] = mod
        return self
    def __exit__(self, *args):
        # Move newly added meta_path objects to self.meta_path.
        for meta in sys.meta_path:
            if meta not in self._cache['meta_path']:
                if meta not in self.meta_path:
                    self.meta_path.append(meta)
        # Move newly added modules to self.modules.
        for key, mod in sys.modules.items():
            remove = mod is None or key in self._cache['disabled_modules']
            remove = remove or key not in self._cache['prev_modules']
            remove = remove or key in self.modules
            if remove:
                self.modules[key] = sys.modules.pop(key)
        # Restore disabled modules.
        sys.modules.update(self._cache['disabled_modules'])
        # Make sure we did everything right with the meta path.
        meta_path_sum = len(self._cache['meta_path']) + len(self.meta_path)
        assert len(sys.meta_path) == meta_path_sum, \
            "_localimport: Error restoring meta_path state. Please report"
        # Make sure we did everything right with the modules dict.
        diff_modules = set(sys.modules.keys()).difference(
            self._cache['prev_modules'])
        assert not diff_modules, \
            "_localimport: Error restoring module state. Please report\n" \
            "Failed to flush modules: {0}".format(diff_modules)
        # Restore the path and meta_path
        sys.path[:] = self._cache['path']
        sys.meta_path[:] = self._cache['meta_path']
        # Delete cache attributes.
        del self._cache
    def eggs(self):
        if not self.autoeggs: return []
        return glob.glob(os.path.join(self.libpath, '*.egg'))
    def is_subpath(self, filename, dirname):
        try: f = os.path.relpath(filename, dirname)
        except ValueError: return False
        else: return f == os.curdir or not f.startswith(os.pardir)
    def is_stdlib(self, mod):
        filename = getattr(mod, '__file__', None)
        if not filename: return True
        return self.is_subpath(filename, self.stdlib_dir)
""")

import os
import re
import c4d
import shutil
import platform
import subprocess
import glob

from c4d import BaseContainer
from c4d.gui import GetIcon, GeDialog, TreeViewFunctions, MessageDialog
from c4d.bitmaps import BaseBitmap
from c4d.storage import HyperFile
from c4d.documents import GetActiveDocument


with _localimport('lib', isolate=True, autoeggs=True):
    import res
    from c4dtools.structures.treenode import TreeNode


class options:
    defaultw = 200
    defaulth = 300
    iconsize = 18
    hpadding = 3
    vpadding = 1
    icon_folder_open = GetIcon(c4d.RESOURCEIMAGE_TIMELINE_FOLDER2)
    icon_folder_closed = GetIcon(c4d.RESOURCEIMAGE_TIMELINE_FOLDER1)
    icon_save = GetIcon(12098)  # Save Command
    icon_reload = GetIcon(c4d.RESOURCEIMAGE_ITERATORGROUP)
    icon_noicon = GetIcon(c4d.RESOURCEIMAGE_GENERICCOMMAND)
    iconoff = (0, 0)
    active_tool_color = c4d.COLOR_BGFOCUS  # Currently not used.
    active_tool_selected = c4d.Vector(0, 1, 0)
    active_tool_deselected = c4d.Vector(0, 0.8, 0)
    presets_suffix = '.tpr'
    presets_glob = '*.tpr'


PLUGIN_ID = 1000005

# Sent to reload all data.
MSG_TOOLPRESETS_RELOAD = 1030473

# Sent to refresh the tree-view of the tool presets dialog.
MSG_TOOLPRESETS_REFRESH = 1030474

# Sent to notify the dialog that the next recognized tool change
# was triggered by itself.
MSG_TOOLPRESETS_SELFCOMMAND = 1030475


def scale_bmp(bmp, dw, dh=None, src=None):
    if not bmp:
        return None
    if isinstance(bmp, dict):
        sx = bmp['x']
        sy = bmp['y']
        sw = bmp['w']
        sh = bmp['h']
        bmp = bmp['bmp']
    elif src:
        sx, sy, sw, sh = src
    else:
        sx = sy = 0
        sw = bmp.GetBw()
        sh = bmp.GetBh()

    if dh is None:
        dh = dw

    dst = BaseBitmap()
    dst.Init(dw, dh, 32)
    sx2 = sx + sw - 1
    sy2 = sy + sh - 1
    dw -= 1
    dh -= 1
    bmp.ScaleBicubic(dst, sx, sy, sx2, sy2, 0, 0, dw, dh)
    return dst


def del_suffix(path):
    dirname, base = os.path.split(path)
    index = base.rfind('.')
    if index > 0:
        base = base[:index]
    return os.path.join(dirname, base)


class Data(object):

    ID_PRESET_PATH = 1000
    ID_SHOW_ALL = 1001

    DEFAULT_PATH = c4d.storage.GeGetC4DPath(c4d.C4D_PATH_LIBRARY_USER)
    DEFAULT_PATH = os.path.join(DEFAULT_PATH, 'toolpresets')

    def __init__(self):
        super(Data, self).__init__()
        self.bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
        if self.bc is None:
            self.bc = c4d.BaseContainer()

    def save(self):
        c4d.plugins.SetWorldPluginData(PLUGIN_ID, self.bc)

    def get_preset_path(self):
        return self.bc.GetString(self.ID_PRESET_PATH, self.DEFAULT_PATH)

    def set_preset_path(self, path):
        self.bc.SetString(self.ID_PRESET_PATH, path)

    def get_show_all(self):
        return self.bc.GetBool(self.ID_SHOW_ALL)

    def set_show_all(self, show):
        self.bc.SetBool(self.ID_SHOW_ALL, show)

    preset_path = property(get_preset_path, set_preset_path)
    show_all = property(get_show_all, set_show_all)


pdata = Data()




class BaseTreeNode(TreeNode):

    type_id = 1
    isfolder = False
    open = False
    selected = False
    prev_selected = False
    loaded = True

    def __init__(self, path):
        super(BaseTreeNode, self).__init__()
        self.path = path
        self.name = del_suffix(os.path.basename(path))

    child = TreeNode.down

    def traverse(self, callback):
        if not callback(self):
            return False
        for child in self.iter_children():
            if not child.traverse(callback):
                return False
        return True

    def sort(self, recursive=True, *a, **kw):
        folders = []
        others = []
        for child in self.iter_children():
            if isinstance(child, ToolPresetFolder):
                folders.append(child)
            else:
                others.append(child)
        folders.sort(*a, **kw)
        others.sort(*a, **kw)
        for child in folders + others:
            child.remove()
            self.append(child)
            if recursive:
                child.sort(True, *a, **kw)

    def get_icon(self, column):
        icon = None
        if column == res.COLUMN_MAIN:
            if self.isfolder:
                if self.open:
                    icon = options.icon_folder_open
                else:
                    icon = options.icon_folder_closed
        return icon

    def text_for_column(self, column):
        if column == res.COLUMN_MAIN:
            text = self.name
        if not self.loaded:
            text = '[!] {0}'.format(text)
        return text

    def get_bg_col(self, row):
        return None

    def get_text_col(self, column):
        return None

    def get_column_width(self, column, area):
        w = 0
        if column == res.COLUMN_MAIN:
            w = area.DrawGetTextWidth(self.name)
            if self.isfolder:
                w += options.iconsize + options.hpadding
        return w

    def draw_cell(self, column, df, bgcol):
        x1 = df['xpos']
        y1 = df['ypos']
        w = df['width']
        h = df['height']
        x2 = x1 + w
        y2 = y1 + h

        # Draw the background onto the area.
        area = df['frame']
        area.DrawSetPen(bgcol)
        area.DrawRectangle(x1, y1, x2, y2)

        # Set the text color.
        tcol = c4d.COLOR_TEXTFOCUS if self.selected else c4d.COLOR_TEXT
        tcol = self.get_text_col(column) or tcol
        area.DrawSetTextCol(tcol, c4d.COLOR_TRANS)

        # Retrieve the draw information for the cell.
        icon = self.get_icon(column)
        text = self.text_for_column(column)

        x, y = x1, y1
        y += options.vpadding

        if icon:
            sx = 0
            sy = 0
            if isinstance(icon, dict):
                sx = icon['x']
                sy = icon['y']
                sw = icon['w']
                sh = icon['h']
                icon = icon['bmp']
            else:
                sw = icon.GetBh()
                sh = icon.GetBw()


            size = options.iconsize
            area.DrawBitmap(icon, x - options.iconoff[0], y - options.iconoff[1],
                            size, size, sx, sy, sw, sh, c4d.BMP_ALLOWALPHA)
            x += size + options.hpadding

        if text:
            y_mid = y1 + (h / 2)
            area.DrawText(text, x, y_mid, c4d.DRAWTEXT_VALIGN_CENTER)
            x += area.DrawGetTextWidth(text) + options.hpadding

    def allow_remove(self):
        return False

    def rename(self, name):
        dirname = os.path.dirname(self.path)
        path = os.path.join(dirname, name)
        if isinstance(self, ToolPreset):
            path = path + options.presets_suffix

        if os.path.exists(self.path):
            os.renames(self.path, path)
        else:
            self.path = path
            self.save()

        self.name = name

    def delete(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)
        self.remove()

    def action(self):
        pass

    def get_selected(self, state, max_=-1):
        result = []
        def cb(x):
            if max_ >= 0 and len(result) >= max_:
                return False
            if x.selected:
                result.append(x)
            return True
        self.traverse(cb)
        return result


class RootNode(BaseTreeNode):

    type_id = 4

    def __init__(self):
        super(RootNode, self).__init__('root')

    @property
    def path(self):
        return None

    @path.setter
    def path(self, value):
        pass

    @property
    def selected(self):
        return False

    @selected.setter
    def selected(self, v):
        pass

    def select_all(self, state):
        self.traverse(lambda x: setattr(x, 'selected', state) or True)

    def open_all(self, state):
        self.traverse(lambda x: setattr(x, 'open', state) or True)

    def cache_selection(self):
        def cb(x):
            x.prev_selected = x.selected
            return True
        self.traverse(cb)


class ToolPreset(BaseTreeNode):

    type_id = 3

    def __init__(self, path, data=None):
        super(ToolPreset, self).__init__(path)
        if data is not None:
            self.data = data
            self.loaded = True
        else:
            self.load()

    def load(self):
        self.data = None
        self.loaded = False
        if not os.path.isfile(self.path):
            return False

        hf = HyperFile()
        success = hf.Open(0, self.path, c4d.FILEOPEN_READ, c4d.FILEDIALOG_NONE)
        if not success:
            return False

        self.data = hf.ReadContainer()
        self.loaded = self.data is not None

        hf.Close()
        return True

    def save(self):
        if self.data is None:
            raise ValueError('no data to be saved')

        dirname = os.path.dirname(self.path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        hf = HyperFile()
        success = hf.Open(0, self.path, c4d.FILEOPEN_WRITE, c4d.FILEDIALOG_NONE)
        if not success:
            raise IOError('could not open HyperFile at "{0}"'.format(self.path))

        hf.WriteContainer(self.data)
        hf.Close()

    def action(self):
        if self.data is None:
            return None

        doc = GetActiveDocument()

        # Change to the tool.
        parent = self.parent
        while parent and not isinstance(parent, ToolNode):
            parent = parent.parent
        if not parent:
            # TODO: What if the action has no parent?
            print "<<< ToolPreset.action(): NO PARENT >>>"
            return

        doc.SetAction(parent.pluginid)
        toold = doc.GetActiveToolData()
        self.data.CopyTo(toold, c4d.COPYFLAGS_0)

        c4d.SpecialEventAdd(MSG_TOOLPRESETS_SELFCOMMAND)
        c4d.EventAdd()


class ToolPresetFolder(BaseTreeNode):

    type_id = 4
    isfolder = True


class ToolNode(ToolPresetFolder):

    type_id = 2
    isfolder = True

    def __init__(self, pluginid, path, toolname):
        super(ToolNode, self).__init__(path)
        self.pluginid = int(pluginid)
        self.name = toolname

    def get_icon(self, column):
        icon = None
        if column == res.COLUMN_MAIN:
            icon = c4d.gui.GetIcon(self.pluginid)
        if not icon:
            icon = super(ToolNode, self).get_icon(column)
        return icon

    def action(self):
        doc = GetActiveDocument()
        doc.SetAction(self.pluginid)
        c4d.EventAdd()

    def get_bg_col(self, row):
        col = None
        doc = GetActiveDocument()
        if doc.GetAction() == self.pluginid:
            col = options.active_tool_color
        return col




class ToolsPresetsHierarchy(TreeViewFunctions):

    show_all = True

    def Get(self, curr, mode='next'):
        if isinstance(curr, ToolNode):
            while curr and not curr.child:
                curr = getattr(curr, mode, None)

        return curr

    # c4d.gui.TreeViewFunctions

    def GetFirst(self, root, ud):
        if not root: return
        if self.show_all:
            return self.Get(root.child)
        else:
            doc = GetActiveDocument()
            tool = doc.GetAction()
            for child in root.iter_children():
                if child.pluginid == tool:
                    return child.child

    def GetNext(self, root, ud, curr):
        return self.Get(curr.next)

    def GetPred(self, root, ud, curr):
        return self.Get(curr.pred, 'pred')

    def GetDown(self, root, ud, curr):
        return curr.child

    def GetName(self, root, ud, curr):
        if isinstance(curr, ToolPreset) and not curr.loaded:
            return '[!] {0}'.format(curr.name)
        else:
            return curr.name

    def SetName(self, root, ud, curr, name):
        if not name:
            MessageDialog(res.string('IDS_ERROR_NAMEEMPTY'))
            return

        try:
            curr.rename(name)
        except (IOError, OSError) as exc:
            MessageDialog(res.string('IDC_ERROR_RENAMEFAILED', curr.name, name))

        c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)

    def GetLineHeight(self, root, ud, curr, col, area):
        h = area.DrawGetFontHeight()
        if options.iconsize > h:
            h = options.iconsize
        return h + options.vpadding * 2

    def GetColumnWidth(self, root, ud, curr, col, area):
        return curr.get_column_width(col, area)

    def GetBackgroundColor(self, root, ud, curr, row, color):
        color = curr.get_bg_col(row)
        return color or c4d.COLOR_BG

    def DrawCell(self, root, ud, curr, column, df, bgcol):
        curr.draw_cell(column, df, bgcol)

    def IsOpened(self, root, ud, curr):
        return curr.open

    def Open(self, root, ud, curr, mode):
        curr.open = mode

    def IsSelected(self, root, ud, curr):
        return curr.selected

    def Select(self, root, ud, curr, mode):
        #root.cache_selection()

        if mode == c4d.SELECTION_ADD:
            curr.selected = True
        elif mode == c4d.SELECTION_SUB:
            curr.selected = False
        elif mode == c4d.SELECTION_NEW:
            root.select_all(False)
            curr.selected = True

    def SelectionChanged(self, root, ud):
        nodes = root.get_selected(True, 2)

        if len(nodes) == 1 and not nodes[0].prev_selected:
            nodes[0].action()

    def DeletePressed(self, root, ud):
        count = [0]
        def counter(x):
            if x.selected:
                count[0] += 1
            return True
        root.traverse(counter)
        count = count[0]

        if not count:
            return
        elif count == 1:
            message = res.string('IDC_ASK_REMOVENODE')
        else:
            message = res.string('IDC_ASK_REMOVENODE_MULTIPLE', str(count))

        result = MessageDialog(message, c4d.GEMB_YESNO)
        if result == c4d.GEMB_R_YES:
            errors = []
            def callback(x):
                if x.selected:
                    try:
                        x.delete()
                    except (IOError, OSError) as exc:
                        errors.append(exc)
                return True
            root.traverse(callback)

            if errors:
                fmt = '\n'.join(map(str, errors))
                msg = res.string('IDC_ERROR_PRESETSNOTREMOVED', fmt)
                MessageDialog(msg)

    def CreateContextMenu(self, root, ud, curr, column, bc):
        bc.RemoveData(c4d.ID_TREEVIEW_CONTEXT_RESET)
        add = ''

        if not curr:
            add = '&d&'
        bc.InsData(res.CONTEXT_NEWFOLDER, res.string('CONTEXT_NEWFOLDER') + add)

        if not curr:
            add = '&d&'
        bc.InsData(res.CONTEXT_OPEN, res.string('CONTEXT_OPEN') + add)

    def ContextMenuCall(self, root, ud, curr, column, command):
        if command == res.CONTEXT_NEWFOLDER:
            name = c4d.gui.RenameDialog(res.string('IDC_FOLDER'))
            if not name:
                return True
            name = name.replace('\\', '').replace('/', '')

            if isinstance(curr, (ToolNode, ToolPresetFolder)):
                parent = curr
            elif curr:
                parent = curr.parent
            else:
                return True

            path = os.path.join(parent.path, name)
            if os.path.isdir(path):
                MessageDialog(res.string('IDC_ERROR_FOLDEREXISTS', name))
                return True

            try:
                os.makedirs(path)
            except OSError as exc:
                MessageDialog(res.string('IDC_ERROR_FOLDERCREATIONFAILED', name))
                return True

            new = ToolPresetFolder(path)
            parent.append(new)
            parent.open = True
            c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)
            return True
        elif command == res.CONTEXT_OPEN:
            if not curr:
                return True

            c4d.storage.ShowInFinder(curr.path)

        return False


class ToolPresetsDialog(GeDialog):

    FILENAME_MENURES = res.file('menus/main.mnu')

    # Stored is the ID of the last tool.
    last_tool = -1

    # True when the tool change was triggered by the dialog
    # itself.
    selftriggered = False

    def __init__(self):
        super(ToolPresetsDialog, self).__init__()
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
        self.root = RootNode()
        self.model = ToolsPresetsHierarchy()

    def Reload(self):
        self.last_tool = -1
        for child in self.root.iter_children():
            child.remove()

        path = pdata.preset_path
        if os.path.isdir(path):
            for folder in os.listdir(path):
                folder_full = os.path.join(path, folder)
                if not os.path.isdir(folder_full): continue

                items = os.listdir(folder_full)
                # Remove empty folders.
                if not items:
                    try:
                        os.rmdir(folder_full)
                    except OSError:
                        pass
                    continue

                split = folder.split(' ', 1)
                if not split:
                    continue

                pluginid = split[0]
                toolname = split[1] if len(split) > 1 else ''

                try:
                    pluginid = int(pluginid)
                except ValueError:
                    continue

                node = ToolNode(pluginid, folder_full, toolname)
                self.FillNode(node, folder_full, items)
                self.root.append(node, 0)

        self.tree.SetRoot(self.root, self.model, None)
        self.Refresh()

    def FillNode(self, node, folder, items=None):
        if items is None:
            items = os.listdir(folder)

        for filename in items:
            is_preset = filename.endswith(options.presets_suffix)
            path = os.path.join(folder, filename)

            if is_preset and os.path.isfile(path):
                preset = ToolPreset(path)
                node.append(preset)
            elif os.path.isdir(path):
                fnode = ToolPresetFolder(path)
                self.FillNode(fnode, path)
                node.append(fnode)


    def SaveState(self):
        doc = GetActiveDocument()
        data = doc.GetActiveToolData()
        if data is None:
            MessageDialog(res.string('IDC_TOOLNOTSUPPORTED'))
            return True

        pluginid = doc.GetAction()
        toolname = c4d.GetCommandName(pluginid)
        name = toolname + ' ' + res.string('IDS_PRESET')
        name = c4d.gui.RenameDialog(name)
        if not name:
            return

        # Check if such a tool already exists.
        for toolnode in self.root.iter_children():
            if toolnode.pluginid == pluginid:
                break
        else:
            toolnode = None

        # Check if only one node is selected.
        selected = self.root.get_selected(True, 2)
        parent = None
        if len(selected) == 1 and isinstance(selected[0], ToolPresetFolder):
            parent = selected[0]

        if toolnode and parent:
            # Check if the new parent is a child of the active tool.
            current = parent
            while current and current != toolnode:
                current = current.parent

            if not current or current != toolnode:
                parent = None
        elif not toolnode:
            folder = '%d %s' % (pluginid, toolname)
            dirname = os.path.join(pdata.preset_path, folder)
            try:
                os.makedirs(dirname)
            except OSError:
                MessageDialog(res.string('IDC_ERROR_FOLDERCREATIONFAILED', folder))
                return False

            toolnode = ToolNode(pluginid, dirname, toolname)
            self.root.append(toolnode)

        if not parent:
            parent = toolnode

        dirname = parent.path
        path = os.path.join(dirname, name) + options.presets_suffix
        try:
            ToolPreset(path, data).save()
        except (IOError, OSError) as exc:
            MessageDialog(str(exc))
            return False

        self.root.select_all(False)
        node = ToolPreset(path, data)
        parent.append(node)
        node.selected = True
        parent.open = True
        self.Refresh()
        return True

    def AddBitmapButton(self, param, icon):
        bc = BaseContainer()
        bc.SetBool(c4d.BITMAPBUTTON_BUTTON, True)
        # bc.SetLong(c4d.BITMAPBUTTON_BACKCOLOR, c4d.COLOR_BG)  # doesnt work

        bmpb = self.AddCustomGui(
            id=param, pluginid=c4d.CUSTOMGUI_BITMAPBUTTON, name="",
            flags=0, minw=0, minh=0, customdata=bc)
        icon = scale_bmp(icon, options.iconsize)
        if icon:
            bmpb.SetImage(icon)
        return bmpb

    def UpdateMenuLine(self):
        doc = GetActiveDocument()
        toolid = doc.GetAction()

        icon = GetIcon(toolid) or options.icon_noicon
        icon = scale_bmp(icon, options.iconsize)
        if icon:
            self.bmpb_tool.SetImage(icon)

        name = c4d.GetCommandName(toolid).strip()
        if not name:
            name = res.string('IDC_UNKOWNTOOL')

        self.SetString(res.STR_TOOL, name)
        self.LayoutChanged(res.GRP_TOOL)

    def Refresh(self):
        tool = GetActiveDocument().GetAction()
        changed = tool != self.last_tool and not self.selftriggered
        self.last_tool = tool

        if changed:
            self.root.select_all(False)

        def callback(x):
            if isinstance(x, ToolNode) and x.pluginid == tool:
                if changed:
                    x.open = True
                    x.selected = True
                return False
            return True

        self.selftriggered = False

        self.root.sort(key=lambda x: x.name.lower())
        self.root.traverse(callback)
        self.tree.Refresh()

    # c4d.gui.GeDialog

    def CreateLayout(self):
        self.SetTitle(res.string('IDS_TOOLPRESETS'))
        fullfit = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT

        self.GroupSpace(0, 0)
        self.GroupBorderSpace(2, 2, 2, 2)

        # Top-line Group
        if self.GroupBegin(0, c4d.BFH_SCALEFIT):
            self.GroupSpace(4, 0)
            self.AddGadget(c4d.DIALOG_PIN, 0)

            if self.GroupBegin(res.GRP_TOOL, c4d.BFH_SCALEFIT):
                self.bmpb_tool = self.AddBitmapButton(res.BMPB_TOOL, None)
                self.AddStaticText(res.STR_TOOL, 0)
                self.GroupEnd()

            self.bmpb_save = self.AddBitmapButton(
                    res.BMPB_SAVE, options.icon_save)
            self.AddCheckbox(res.CHK_ALL, 0, 0, 0, name=res.string('CHK_ALL'))
            self.GroupEnd()

        self.AddSeparatorH(0)

        # Tree-View Group
        if self.GroupBegin(res.GRP_MAIN, fullfit, cols=1):
            self.tree = self.AddCustomGui(
                res.TREEVIEW, c4d.CUSTOMGUI_TREEVIEW, "", fullfit, 0, 0)
            self.GroupEnd()

        self.UpdateMenuLine()
        return True

    def InitValues(self):
        if not self.tree:
            return False

        layout = BaseContainer()
        layout.SetLong(res.COLUMN_MAIN, c4d.LV_USERTREE)
        self.model.show_all = pdata.show_all
        self.SetBool(res.CHK_ALL, pdata.show_all)
        self.tree.SetLayout(1, layout)
        self.tree.SetRoot(self.root, self.model, None)
        self.Reload()
        self.Refresh()
        return True

    def Command(self, id, msg):
        if id == res.BMPB_SAVE:
            self.SaveState()
        elif id == res.BMPB_TOOL:
            doc = GetActiveDocument()
            doc.SetAction(doc.GetAction())
            c4d.EventAdd()
        elif id == res.CHK_ALL:
            pdata.show_all = self.GetLong(res.CHK_ALL)
            self.model.show_all = self.GetLong(res.CHK_ALL)
            self.Reload()
        return True

    def CoreMessage(self, id, msg):
        if id == c4d.EVMSG_CHANGE:
            if not self.selftriggered:
                self.root.select_all(False)
            self.Refresh()
            self.UpdateMenuLine()
        elif id == MSG_TOOLPRESETS_RELOAD:
            self.Reload()
        elif id == MSG_TOOLPRESETS_REFRESH:
            self.tree.Refresh()
        elif id == MSG_TOOLPRESETS_SELFCOMMAND:
            self.selftriggered = True
        return True


class ToolPresetsCommand(c4d.plugins.CommandData):

    @property
    def dialog(self):
        if not getattr(self, '_dialog', None):
            self._dialog = ToolPresetsDialog()
        return self._dialog


    PLUGIN_ID = PLUGIN_ID
    PLUGIN_NAME = res.string('IDS_TOOLPRESETS')
    PLUGIN_HELP = res.string('IDS_TOOLPRESETS_HELP')
    PLUGIN_ICON = res.bitmap('res', 'icon.tif')

    def register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, 0, self.PLUGIN_ICON,
            self.PLUGIN_HELP, self)

    # c4d.plugins.CommandData

    def Execute(self, doc):
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID,
                                defaultw=options.defaultw,
                                defaulth=options.defaulth)

    def RestoreLayout(self, secret):
        return self.dialog.Restore(self.PLUGIN_ID, secret)




def PluginMessage(msg_type, data):
    if msg_type in [c4d.C4DPL_RELOADPYTHONPLUGINS, c4d.C4DPL_ENDPROGRAM]:
        pdata.save()
    return True


def main():
    ToolPresetsCommand().register()


if __name__ == '__main__':
    main()
