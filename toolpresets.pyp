# coding: utf-8
#
# Copyright (C) 2015, Niklas Rosenstein
# All rights reserved.

exec ("""import os, sys, glob      # _localimport context-manager             #
class _localimport(object):        # by Niklas Rosenstein, Copyright (C) 2015 #
    _modulecache = []              # Licensed under MIT                       #
    _eggs = staticmethod(lambda x: glob.glob(os.path.join(x, '*.egg')))
    def __init__(s, libpath, autoeggs=False, isolate=False, path=os.path):
        if not path.isabs(libpath):
            libpath = path.join(path.dirname(path.abspath(__file__)), libpath)
        s.libpath = libpath; s.autoeggs = autoeggs; s.isolate = isolate
    def __enter__(s):
        s._path, s._mpath = list(sys.path), list(sys.meta_path)
        s._mods = frozenset(sys.modules.keys())
        sys.path.append(s.libpath)
        sys.path.extend(s._eggs(s.libpath) if s.autoeggs else [])
    def __exit__(s, *args):
        sys.path[:] = s._path; sys.meta_path[:] = s._mpath
        for key in sys.modules.keys():
            if key not in s._mods and s._islocal(sys.modules[key]):
                s._modulecache.append(sys.modules.pop(key))
    def _islocal(s, mod):
        if s.isolate: return True
        filename = getattr(mod, '__file__', None)
        if filename:
            try: s = os.path.relpath(filename, s.libpath)
            except ValueError: return False
            else: return s == os.curdir or not s.startswith(os.pardir)
        else: return False""")


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


with _localimport('lib', autoeggs=True):
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

# Opening a MessageDialog in TreeViewFunctions.SetName()
# will re-trigger the method. This list keeps track of messages
# that are to be displayed.
messages = []


def init_options():
    r"""
    Called to initialize values in the options attributor.
    """
    pass


def get_bmp(icon):
    if not icon:
        return None
    if isinstance(icon, BaseBitmap):
        return icon
    else:
        return icon['bmp']


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

    def __init__(self, name, path):
        super(BaseTreeNode, self).__init__()
        self.name = name
        self.path = path

    @property
    def path(self):
        if self.parent and self.parent.path:
            return os.path.join(self.parent.path, os.path.basename(self._path))
        else:
            return self._path

    @property
    def child(self):
        return self.down

    @path.setter
    def path(self, path):
        self._path = path

    def traverse(self, callback):
        if not callback(self):
            return False
        for child in self.iter_children():
            if not child.traverse(callback):
                return False
        return True

    def list_children(self):
        return list(self.iter_children())

    def sort(self, *a, **kw):
        children = self.list_children()
        children.sort(*a, **kw)
        for child in children:
            child.remove()
            self.append(child)

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
            return self.name

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
        name_full = os.path.join(dirname, name)
        if not os.path.exists(self.path):
            self.path = name_full
            self.save()
        else:
            try:
                os.rename(self.path, name_full)
                self.path = name_full
            except OSError:
                return False
        self.name = name
        return True

    def delete(self):
        if os.path.exists(self.path):
            try:
                if os.path.isdir(self.path):
                    shutil.rmtree(self.path)
                else:
                    os.remove(self.path)
            except OSError:
                return False
        self.remove()
        return True

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
        super(RootNode, self).__init__('root', None)

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

    def __init__(self, data, name, path):
        super(ToolPreset, self).__init__(name, path)
        index = name.rfind('.')
        if index > 0: name = name[:index]
        self.name = name
        self.data = c4d.BaseContainer(data)

    def action(self):
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

    def sort(self, recursive=True, key=lambda x: x.name):
        children = self.list_children()
        folders = []
        others = []

        for child in children:
            child.remove()
            if isinstance(child, ToolPresetFolder):
                folders.append(child)
            else:
                others.append(child)

        folders.sort(key=key)
        others.sort(key=key)

        [self.append(c) for c in folders]
        [self.append(c) for c in others]

        for child in children:
            child.sort(recursive, key)


class ToolNode(ToolPresetFolder):

    type_id = 2
    isfolder = True

    def __init__(self, pluginid, name, path):
        super(ToolNode, self).__init__(name, path)
        self.pluginid = int(pluginid)

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
        return curr.name

    def SetName(self, root, ud, curr, name):
        if not name:
            MessageDialog(res.string('IDS_ERROR_NAMEEMPTY'))
            return

        if not curr.rename(name):
            # Add the message to the messages list.
            messages.append(res.string('IDC_ERROR_RENAMEFAILED', curr.name, name))

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
            message = res.string('IDC_ASK_REMOVENODE_MULTIPLE', count)

        result = MessageDialog(message, c4d.GEMB_YESNO)
        if result == c4d.GEMB_R_YES:
            errors = []
            def callback(x):
                if x.selected:
                    if not x.delete():
                        errors.append(x)
                    return False
                return True
            root.traverse(callback)

            if errors:
                fmt = ', '.join(e.name for e in errors)
                msg = res.string('IDC_ERROR_PRESETSNOTREMOVED', fmt)
                MessageDialog(msg)

    def CreateContextMenu(self, root, ud, curr, column, bc):
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
            name = name.replace('\\', '').replace('/', '')
            if not name: return True

            if isinstance(curr, (ToolNode, ToolPresetFolder)):
                parent = curr
            elif curr:
                parent = curr.parent
            else:
                return True

            path = os.path.join(parent.path, name)
            if os.path.isdir(path):
                MessageDialog(res.string('IDC_ERROR_FOLDEREXISTS'), name)
                return

            try:
                os.makedirs(path)
            except OSError as exc:
                MessageDialog(res.string('IDC_ERROR_FOLDERCREATIONFAILED', name))
                return True

            new = ToolPresetFolder(name, path)
            parent.append(new)
            parent.open = True
            c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)
            return True
        elif command == res.CONTEXT_OPEN:
            if not curr:
                return True

            c4d.storage.ShowInFinder(curr.path)
        elif command == c4d.ID_TREEVIEW_CONTEXT_RESET:
            result = MessageDialog(res.string('IDC_ASK_REMOVEALL'), c4d.GEMB_YESNO)
            if result != c4d.GEMB_R_YES:
                return True

            first = self.GetFirst(root, ud)
            for child in first.list_children():
                child.delete()
            c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)
            return True

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
        for child in self.root.list_children():
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
                name = split[1] if len(split) > 1 else ''

                try:
                    pluginid = int(pluginid)
                except ValueError:
                    continue

                node = ToolNode(pluginid, name, folder_full)
                self.FillNode(node, folder_full, items)
                self.root.append(node, 0)

        self.tree.SetRoot(self.root, self.model, None)
        self.Refresh()

    def FillNode(self, node, folder, items=None):
        if items is None:
            items = os.listdir(folder)

        for filename in items:
            basename = filename
            filename = os.path.join(folder, filename)

            is_preset = filename.endswith(options.presets_suffix)
            if is_preset and os.path.isfile(filename):
                data = self.LoadFile(filename)
                if data:
                    preset = ToolPreset(data, basename, filename)
                    node.append(preset, 0)
            elif os.path.isdir(filename):
                fnode = ToolPresetFolder(basename, filename)
                self.FillNode(fnode, filename)
                node.append(fnode, 0)

    def LoadFile(self, filename):
        if not os.path.isfile(filename):
            return

        hf = HyperFile()
        success = hf.Open(0, filename, c4d.FILEOPEN_READ, c4d.FILEDIALOG_NONE)
        if not success:
            return

        bc = hf.ReadContainer()
        hf.Close()
        return bc

    def SaveFile(self, filename, data):
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                return 'denied'

        hf = HyperFile()
        success = hf.Open(0, filename, c4d.FILEOPEN_WRITE, c4d.FILEDIALOG_NONE)
        if not success:
            return 'fail'

        hf.WriteContainer(data)
        hf.Close()
        return 'ok'

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
        toolnode = None
        for toolnode in self.root.iter_children():
            if toolnode.pluginid == pluginid:
                break
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

            toolnode = ToolNode(pluginid, toolname, dirname)
            self.root.append(toolnode)

        if not parent:
            parent = toolnode

        dirname = parent.path
        filename = os.path.join(dirname, name) + options.presets_suffix
        status = self.SaveFile(filename, data)

        message = None
        if status == 'fail':
            message = res.string('IDS_ERROR_FILENOTOPENED', filename)
        elif status == 'denied':
            message = res.string('IDS_ERROR_ACCESSDENIED', filename)

        if message:
            MessageDialog(message)
            return False

        self.root.select_all(False)
        node = ToolPreset(data, name, filename)
        parent.append(node)
        node.selected = True
        parent.open = True
        self.Refresh()
        return True

    def AddBitmapButton(self, id, icon, cd=None):
        if cd is None:
            cd = BaseContainer()
            cd.SetBool(c4d.BITMAPBUTTON_BUTTON, True)

        bmpb = self.AddCustomGui(
                id, c4d.CUSTOMGUI_BITMAPBUTTON, "", 0,
                0, 0, cd)
        icon =  scale_bmp(icon, options.iconsize)
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
        elif id == res.BMPB_RELOAD:
            self.Reload()
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
        # Process messages that are to be displayed.
        while messages:
            MessageDialog(messages.pop())

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
    init_options()
    ToolPresetsCommand().register()


if __name__ == '__main__':
    main()
