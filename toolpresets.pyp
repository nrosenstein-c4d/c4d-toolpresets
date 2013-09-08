# coding: utf-8
#
# Copyright (C) 2013, Niklas Rosenstein
# All rights reserved.

import os
import re
import abc
import c4d
import c4dtools
import shutil
import platform
import subprocess
import glob

from c4d import BaseContainer
from c4d.gui import GetIcon, GeDialog, TreeViewFunctions, MessageDialog
from c4d.bitmaps import BaseBitmap
from c4d.storage import HyperFile
from c4d.documents import GetActiveDocument
from c4dtools.helpers import Attributor
from c4dtools.resource import menuparser

res, importer = c4dtools.prepare(cache=False)
res.new_symbols('TREEVIEW', 'COLUMN_MAIN', 'BMPB_SAVE', 'BMPB_RELOAD',
                'STR_TOOL', 'BMPB_TOOL', 'GRP_MAIN', 'GRP_TOOL')
options = Attributor({
    'defaultw': 600,
    'defaulth': 300,
    'iconsize': 18,
    'hpadding': 3,
    'vpadding': 1,
    'icon_folder_open': GetIcon(c4d.RESOURCEIMAGE_TIMELINE_FOLDER2),
    'icon_folder_closed': GetIcon(c4d.RESOURCEIMAGE_TIMELINE_FOLDER1),
    'icon_save': GetIcon(12098), # Save Command
    'icon_reload': GetIcon(c4d.RESOURCEIMAGE_ITERATORGROUP),
    'icon_noicon': GetIcon(c4d.RESOURCEIMAGE_GENERICCOMMAND),
    'iconoff': (0, 0),
    'active_tool_color': c4d.COLOR_BGFOCUS, # Currently not used.
    'active_tool_selected': c4d.Vector(0, 1, 0),
    'active_tool_deselected': c4d.Vector(0, 0.8, 0),
    'presets_suffix': '.tpr',
    'presets_glob': '*.tpr',
})

with importer.protected():
    import treenode


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

def open_path(path):
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        dpath = os.path.dirname(path)

    system = platform.system()
    if system == 'Windows':
        args = ['explorer', '/select,', path]
    elif system == 'Darwin':
        args = ['open', dpath]
    else:
        args = ['xdg-open', dpath]

    if args:
        subprocess.Popen(args)


class BaseTreeNode(treenode.TreeNode):

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

    @path.setter
    def path(self, path):
        self._path = path

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

    def get_bg_col(self, column, area, bgcol):
        return bgcol

    def get_text_col(self, column, area, col):
        return col

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
        area.DrawSetPen(self.get_bg_col(column, area, bgcol))
        area.DrawRectangle(x1, y1, x2, y2)

        # Set the text color.
        tcol = c4d.COLOR_TEXTFOCUS if self.selected else c4d.COLOR_TEXT
        tcol = self.get_text_col(column, area, tcol)
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
        res = []
        def cb(x):
            if max_ >= 0 and len(res) >= max_:
                return False
            if x.selected:  
                res.append(x)
            return True
        self.traverse(cb)
        return res

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
        name = c4dtools.utils.change_suffix(name, '')
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
        children = self.pop_children()
        folders = []
        others = []

        for child in children:
            if isinstance(child, ToolPresetFolder):
                folders.append(child)
            else:
                others.append(child)

        folders.sort(key=key)
        others.sort(key=key)

        self.insert_children(others + folders)

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

    def get_bg_col(self, column, area, bgcol):
        col = None
        """
        doc = GetActiveDocument()
        if doc.GetAction() == self.pluginid:
            col = options.active_tool_color
        """
        if not col:
            col = bgcol
        return col

    def get_text_col(self, column, area, col):
        doc = GetActiveDocument()
        if doc.GetAction() == self.pluginid:
            if self.selected:
                col = options.active_tool_selected or col
            else:
                col = options.active_tool_deselected or col

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
            MessageDialog(res['IDS_ERROR_NAMEEMPTY'])
            return

        if not curr.rename(name):
            # Add the message to the messages list.
            messages.append(res['IDC_ERROR_RENAMEFAILED', curr.name, name])

        c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)

    def GetLineHeight(self, root, ud, curr, col, area):
        h = area.DrawGetFontHeight()
        if options.iconsize > h:
            h = options.iconsize
        return h + options.vpadding * 2

    def GetColumnWidth(self, root, ud, curr, col, area):
        return curr.get_column_width(col, area)

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
            message = res['IDC_ASK_REMOVENODE']
        else:
            message = res['IDC_ASK_REMOVENODE_MULTIPLE', count]

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
                msg = res['IDC_ERROR_PRESETSNOTREMOVED', fmt]
                MessageDialog(msg)

    def CreateContextMenu(self, root, ud, curr, column, bc):
        add = ''

        if not curr:
            add = '&d&'
        bc.InsData(res.CONTEXT_NEWFOLDER, res['CONTEXT_NEWFOLDER'] + add)

        if not curr:
            add = '&d&'
        bc.InsData(res.CONTEXT_OPEN, res['CONTEXT_OPEN'] + add)

    def ContextMenuCall(self, root, ud, curr, column, command):
        if command == res.CONTEXT_NEWFOLDER:
            name = c4d.gui.RenameDialog(res['IDC_FOLDER'])
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
                MessageDialog(res['IDC_ERROR_FOLDEREXISTS'], name)
                return

            try:
                os.makedirs(path)
            except OSError as exc:
                MessageDialog(res['IDC_ERROR_FOLDERCREATIONFAILED', name])
                return True

            new = ToolPresetFolder(name, path)
            new.insert_under_last(parent)
            parent.open = True
            c4d.SpecialEventAdd(MSG_TOOLPRESETS_REFRESH)
            return True
        elif command == res.CONTEXT_OPEN:
            if not curr:
                return True

            open_path(curr.path)
        elif command == c4d.ID_TREEVIEW_CONTEXT_RESET:
            result = MessageDialog(res['IDC_ASK_REMOVEALL'], c4d.GEMB_YESNO)
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
        self.root = RootNode()
        self.model = ToolsPresetsHierarchy()

    def Reload(self):
        self.last_tool = -1
        for child in self.root.list_children():
            child.remove()

        path = pdata.preset_path
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

            node.insert_under(self.root)

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
                    preset.insert_under(node)
            elif os.path.isdir(filename):
                fnode = ToolPresetFolder(basename, filename)
                self.FillNode(fnode, filename)
                fnode.insert_under(node)

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
            MessageDialog(res['IDC_TOOLNOTSUPPORTED'])
            return True

        pluginid = doc.GetAction()
        toolname = c4d.GetCommandName(pluginid)
        name = toolname + ' ' + res['IDS_PRESET']
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
                MessageDialog(res['IDC_ERROR_FOLDERCREATIONFAILED', folder])
                return False

            toolnode = ToolNode(pluginid, toolname, dirname)
            toolnode.insert_under_last(self.root)

        if not parent:
            parent = toolnode

        dirname = parent.path
        filename = os.path.join(dirname, name) + options.presets_suffix
        status = self.SaveFile(filename, data)

        message = None
        if status == 'fail':
            message = res['IDS_ERROR_FILENOTOPENED', filename]
        elif status == 'denied':
            message = res['IDS_ERROR_ACCESSDENIED', filename]

        if message:
            MessageDialog(message)
            return False

        self.root.select_all(False)
        node = ToolPreset(data, name, filename)
        node.insert_under_last(parent)
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
            name = res['IDC_UNKOWNTOOL']

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
        filename = self.FILENAME_MENURES
        if not os.path.exists(filename):
            MessageDialog(res['IDS_MISSING_FILE', filename])
            return False
        menuparser.parse_and_prepare(filename, self, res)

        self.SetTitle(res['IDS_TOOLPRESETS'])
        fullfit = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT

        # Menu-line Group
        if self.GroupBeginInMenuLine():
            if self.GroupBegin(res.GRP_TOOL, 0):
                self.AddStaticText(res.STR_TOOL, 0)
                self.bmpb_tool = self.AddBitmapButton(res.BMPB_TOOL, None)
                self.AddStaticText(0, 0, name=':')
                self.GroupEnd()

            self.bmpb_save = self.AddBitmapButton(
                    res.BMPB_SAVE, options.icon_save)
            self.bmpb_reload = self.AddBitmapButton(
                    res.BMPB_RELOAD, options.icon_reload)
            self.GroupEnd()

        # Tree-View Group
        if self.GroupBegin(res.GRP_MAIN, fullfit, cols=1):
            cd = BaseContainer()
            cd.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True)
            self.tree = self.AddCustomGui(
                    res.TREEVIEW, c4d.CUSTOMGUI_TREEVIEW, "", fullfit,
                    0, 0, cd)
            self.GroupEnd()

        return True

    def InitValues(self):
        self.UpdateMenuLine()
        if not self.tree:
            return False

        layout = BaseContainer()
        layout.SetLong(res.COLUMN_MAIN, c4d.LV_USERTREE)
        self.tree.SetLayout(1, layout)
        self.tree.SetRoot(self.root, self.model, None)
        self.Reload()
        self.Refresh()
        return True

    def Command(self, id, msg):
        if id == res.MENU_FILE_SETTINGS:
            # TODO: Open settings dialog
            pass
        elif id == res.BMPB_SAVE:
            self.SaveState()
        elif id == res.BMPB_RELOAD:
            self.Reload()
        elif id == res.BMPB_TOOL:
            doc = GetActiveDocument()
            doc.SetAction(doc.GetAction())
            c4d.EventAdd()
        return True

    def CoreMessage(self, id, msg):
        # Process messages that are to be displayed.
        for message in messages:
            MessageDialog(message)
        messages[:] = []

        if id == c4d.EVMSG_CHANGE:
            self.Refresh()
            self.UpdateMenuLine()
        elif id == MSG_TOOLPRESETS_RELOAD:
            self.Reload()
        elif id == MSG_TOOLPRESETS_REFRESH:
            self.tree.Refresh()
        elif id == MSG_TOOLPRESETS_SELFCOMMAND:
            self.selftriggered = True
        return True

class ToolPresetsCommand(c4dtools.plugins.Command):

    @property
    def dialog(self):
        if not getattr(self, '_dialog', None):
            self._dialog = ToolPresetsDialog()
        return self._dialog

    # c4dtools.plugins.Command

    PLUGIN_ID = 1000005
    PLUGIN_NAME = res['IDS_TOOLPRESETS']
    PLUGIN_HELP = res['IDS_TOOLPRESETS_HELP']
    PLUGIN_ICON = res.file('icon.tif')

    # c4d.plugins.CommandData

    def Execute(self, doc):
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID,
                                defaultw=options.defaultw,
                                defaulth=options.defaulth)

    def RestoreLayout(self, secret):
        return self.dialog.Restore(self.PLUGIN_ID, secret)


class Data(object):

    ID_DATA = ToolPresetsCommand.PLUGIN_ID
    ID_PRESET_PATHS = 1000

    DEFAULT_PATH = c4d.storage.GeGetC4DPath(c4d.C4D_PATH_LIBRARY_USER)
    DEFAULT_PATH = os.path.join(DEFAULT_PATH, 'toolpresets')

    @property
    def data(self):
        return c4d.plugins.GetWorldPluginData(self.ID_DATA) \
               or BaseContainer()

    @data.setter
    def data(self, bc):
        c4d.plugins.SetWorldPluginData(self.ID_DATA, data, True)

    @property
    def preset_path(self):
        bc = self.data
        return bc.GetString(self.ID_PRESET_PATHS, self.DEFAULT_PATH)

    @preset_path.setter
    def preset_path(self, paths):
        bc = BaseContainer()
        bc.SetString(self.ID_PRESET_PATHS, paths)
        self.data = bc

pdata = Data()


def main():
    init_options()
    ToolPresetsCommand().register()

if __name__ == '__main__':
    main()


