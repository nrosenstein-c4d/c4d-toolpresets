# coding: utf-8
# Copyright (C) 2015  Niklas Rosenstein
# All rights reserved.

from __future__ import print_function
__version__ = '2.0'

# localimport-v1.7.3-blob-mcw99
import base64 as b, types as t, zlib as z; m=t.ModuleType('localimport');
m.__file__ = __file__; blob=b'\
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'
exec(z.decompress(b.b64decode(blob)), vars(m)); _localimport=m;localimport=getattr(m,"localimport")
del blob, b, t, z, m;


import c4d
import os
import re
import uuid
import shutil
import sys
import webbrowser

with localimport('res/modules' + sys.version[:3]) as importer:
  from c4dtools.gui import IconView
  from c4dtools.structures.treenode import TreeNode


PLUGIN_ID = 1030475
TYPE_PRESET = 'preset'
TYPE_FOLDER = 'folder'
TYPE_TOOL = 'tool'
TYPE_ROOT = 'root'


def get_logger():
  import logging
  formatter = logging.Formatter('[%(name)s - %(levelname)s]: %(message)s')
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.Logger('toolpresets{0}'.format(__version__))
  logger.addHandler(handler)
  return logger

logger = get_logger()


def del_suffix(path):
  """
  Removes the suffix if the specified *path* and returns it.
  """

  dirname, base = os.path.split(path)
  index = base.rfind('.')
  if index > 0:
    base = base[:index]
  return os.path.join(dirname, base)


def sane_filename(string):
  """
  Creates a sane filename containing only alphanumerical and digit
  characters plus periods, hypens, underscors and whitespaces. Invalid
  characters are replaced by hyphens and consecutives are merged.
  """

  keep_chars = '.-_ '
  filename = ''.join(
    c if (c.isalpha() or c.isdigit() or c in keep_chars) else '-'
    for c in string)
  return re.sub('\-+', '-', filename).rstrip()


class Node(TreeNode):
  """
  Base class for nodes in the Tool Preset tree display.
  """

  def __init__(self, name, type_, path=None, data=None):
    super(Node, self).__init__()
    if type_ == TYPE_FOLDER and path is None:
      raise RuntimeError('path must be specified for Folder nodes')
    if type_ not in (TYPE_ROOT, TYPE_TOOL, TYPE_FOLDER, TYPE_PRESET):
      raise ValueError('unexpected value for type_', type_)
    self.name = name
    self.type_ = type_
    self.path = path
    self.selected = False
    self.open = type_ == TYPE_TOOL
    self.data = data

  def apply(self, func):
    """
    Applies *func* to *self* and all child nodes recursively. *func*
    may raise :class:`StopIteration` to indicate that any further
    processing should be stopped.
    """

    try:
      func(self)
    except StopIteration:
      return False

    for child in self.iter_children():
      if not child.apply(func):
        return False

    return True

  def apply_attr(self, **kwargs):
    """
    Applies :func:`setattr` for all keys in *\*\*kwargs* recursively
    over the tree starting with *self*.
    """

    for key, value in kwargs.iteritems():
      setattr(self, key, value)
    for child in self.iter_children():
      child.apply_attr(**kwargs)

  def get_selected_nodes(self, max_nodes=None):
    """
    Returns a list of all selected nodes in the hierarchy of *self*.
    """

    selected = []

    @self.apply
    def func(node):
      if node.selected:
        selected.append(node)
        if max_nodes is not None and len(selected) >= max_nodes:
          raise StopIteration

    return selected

  def delete(self, remove=True):
    """
    Deletes the file or folder the node is referencing on the file
    system and removes the node from the hierarchy.
    """

    if self.type_ in (TYPE_TOOL, TYPE_FOLDER):
      if os.path.exists(self.path):
        shutil.rmtree(self.path)
    elif self.type_ == TYPE_PRESET:
      if os.path.exists(self.path):
        os.remove(self.path)
    else:
      raise RuntimeError('{0} node can not be deleted'.format(self.type_))

    if remove:
      self.remove()


class PresetNode(Node):
  """
  This class represents a Tool Preset which is basically just a
  :class:`c4d.BaseContainer` that contains the settings of the tool
  plugin and a UUID.
  """

  def __init__(self, tool_id, name, uuid, data, filename):
    super(PresetNode, self).__init__(name, TYPE_PRESET, filename, data)
    self.tool_id = tool_id
    self.uuid = uuid

  @classmethod
  def load(class_, filename):
    """
    Loads the preset data from a file with the specified *filename*.

    :raise OSError: If the file could not be loaded or if it contains
      invalid data.
    """

    hfile = c4d.storage.HyperFile()
    status = hfile.Open(0, filename, c4d.FILEOPEN_READ, c4d.FILEDIALOG_NONE)
    if not status:
      raise OSError('failed to open HyperFile at {0}'.format(filename))

    tool_id = hfile.ReadLong()
    data = hfile.ReadContainer()
    uuid_string = hfile.ReadString()
    name = hfile.ReadString()
    if None in (tool_id, data, uuid, name):
      raise OSError('invalid data in HyperFile at {0}'.format(filename))

    try:
      uuid_value = uuid.UUID(uuid_string)
    except ValueError:
      raise OSError('invalid UUID in HyperFile at {0}'.format(filename))

    return PresetNode(tool_id, name, uuid_value, data, filename)

  def save(self, filename=None):
    """
    Saves the preset as a HyperFile to its source file or the
    specified *filename*.

    :raise OSError: If the file could not be opened for write or if
      writing to it failed.
    """

    if filename is None:
      filename = self.path

    hfile = c4d.storage.HyperFile()
    status = hfile.Open(0, filename, c4d.FILEOPEN_WRITE, c4d.FILEDIALOG_NONE)
    if not status:
      raise OSError('failed to open HyperFile at {0}'.format(filename))

    status = status and hfile.WriteLong(self.tool_id)
    status = status and hfile.WriteContainer(self.data)
    status = status and hfile.WriteString(str(self.uuid))
    status = status and hfile.WriteString(self.name)
    if not status:
      raise OSError('failed to write to HyperFile at {0}'.format(filename))

  # c4dtools.structures.treenode.TreeNode

  def append(self, *args, **kwargs):
    raise RuntimeError('can not append to PresetNode')


# Gui Implementation

class g:
  """
  Global data that will be accessed from anywhere.
  """

  # There's a bug in TreeViewFunctions.SetName() that when a
  # MessageDialog() is opened the function will be called again.
  # So we process this list in TP_Dialog.CoreMessage() to open
  # queued dialogs.
  message_dialogs = []


def apply_preset(preset):
  """
  Applies the :class:`PresetNode` *preset* to the active document.
  """

  doc = c4d.documents.GetActiveDocument()
  doc.SetAction(preset.tool_id)
  data = doc.GetActiveToolData()
  if data is None:
    c4d.gui.MessageDialog('Unknown Tool ID: {0}'.format(preset.tool_id))
    return False
  data.MergeContainer(preset.data)
  c4d.EventAdd()
  return True


def save_preset_main(preset):
  """
  Saves the :class:`PresetNode` with appropriate GUI calls.
  """

  # Make sure the folder in which we plan to save the preset
  # in exists.
  folder = os.path.dirname(preset.path)
  if not os.path.isdir(folder):
    try:
      os.makedirs(folder)
    except (IOError, OSError) as exc:
      logger.warn(str(exc))
      c4d.gui.MessageDialog(str(exc))
      return False

  # Generate the filename for the preset and check if it
  # already exists.
  if os.path.isfile(preset.path):
    question = 'Do you want to overwrite the existing preset?'
    confirmation = c4d.gui.MessageDialog(question, c4d.GEMB_YESNO)
    if confirmation != c4d.GEMB_R_YES:
      return False

  # Save the preset.
  try:
    preset.save()
  except (IOError, OSError) as exc:
    logger.warn(exc)
    c4d.gui.MessageDialog(str(exc))
    return False

  return True


def reload_presets(node):
  """
  Reloads the preset node using its specified filename.
  """

  path = node.path

  # Remove all existing child nodes.
  [c.remove() for c in node.iter_children()]
  if not os.path.exists(path):
    return

  if node.type_ == TYPE_ROOT and os.path.isdir(path):
    tools = {}
    for filename in os.listdir(path):
      # Tools must be folders.
      filepath = os.path.join(path, filename)
      if not os.path.isdir(filepath):
        continue
      # A folder for a tool starts with its plugin ID.
      match = re.match('\d+', filename)
      if not match:
        continue
      # Get the name of the tool plugin with the specified ID.
      tool_id = int(match.group(0))
      tool_name = c4d.GetCommandName(tool_id)
      if not tool_name:
        logger.warn("Unknown Plugin ID {0} at {1}", tool_id, filepath)
        continue
      # Retrieve the node that will contain the presets for this Tool.
      try:
        tool_node = tools[tool_id]
      except KeyError:
        tool_node = Node(tool_name, TYPE_TOOL, path=filepath, data=tool_id)
        tools[tool_id] = tool_node
        node.append(tool_node)
      # Parse in the presets for this tool.
      reload_presets(tool_node)
  elif node.type_ in (TYPE_TOOL, TYPE_FOLDER) and os.path.isdir(path):
    nodes = {'folders': [], 'presets': []}
    for filename in os.listdir(path):
      filepath = os.path.join(path, filename)
      if os.path.isdir(filepath):
        # Continue to search for presets in the sub directory.
        folder = Node(filename, TYPE_FOLDER, filepath)
        reload_presets(folder)
        nodes['folders'].append(folder)
      elif os.path.isfile(filepath) and filename.endswith('.tpr'):
        # Attempt to load the preset.
        try:
          preset = PresetNode.load(filepath)
        except (IOError, OSError) as exc:
          logger.warn(str(exc))
          continue
        nodes['presets'].append(preset)

    key = lambda n: n.name
    for child in sorted(nodes['folders'], key=key):
      node.append(child)
    for child in sorted(nodes['presets'], key=key):
      node.append(child)
  else:
    logger.warn("reload_presets() - invalid node type {0}".format(node.type_))


def load_icon(*parts):
  path = os.path.join(os.path.dirname(__file__), *parts)
  bmp = c4d.bitmaps.BaseBitmap()
  if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
    return None
  return bmp


def draw_icon(frame, icon, x, y, w, h, flags=c4d.BMP_ALLOWALPHA):
  """
  Draws the *icon* onto the GeUserArea *frame*.
  """

  if isinstance(icon, c4d.bitmaps.BaseBitmap):
    icon = {'bmp': icon, 'x': 0, 'y': 0, 'w': icon.GetBw(), 'h': icon.GetBh()}
  elif not isinstance(icon, dict):
    raise TypeError('icon must be dict or BaseBitmap')

  frame.DrawBitmap(
    icon['bmp'], x, y, w, h, icon['x'], icon['y'], icon['w'], icon['h'], flags)


class TP_TreeModel(c4d.gui.TreeViewFunctions):
  """
  This is a model for :class:`PresetNode`s to display them in a Cinema
  4D Tree View gui.
  """

  MENU_REMOVE = 1000
  MENU_REVEAL = 1001
  MENU_NEWFOLDER = 1002

  COLUMN_NAME = 1
  COLUMN_ICON = 2

  ICONSIZE = 16

  show_all = True

  def InitLayout(self, tree):
    """
    Called after the model was attached to *tree*.
    """

    layout = c4d.BaseContainer()
    layout.SetLong(self.COLUMN_ICON, c4d.LV_USER)
    layout.SetLong(self.COLUMN_NAME, c4d.LV_TREE)
    tree.SetLayout(2, layout)

  def GetFirstParent(self, root, ud):
    if self.show_all:
      return root
    else:
      # Search for the tool node that matches the current Tool ID.
      tool_id = c4d.documents.GetActiveDocument().GetAction()
      for node in root.iter_children():
        if node.data == tool_id:
          return node
      return None

  # c4d.gui.TreeViewFunctions

  def GetFirst(self, root, ud):
    node = self.GetFirstParent(root, ud)
    if node:
      return node.down
    return node

  def GetNext(self, root, ud, node):
    return node.next

  def GetPred(self, root, ud, node):
    return node.pred

  def GetDown(self, root, ud, node):
    return node.down

  def GetUp(self, root, ud, node):
    return node.parent

  def GetName(self, root, ud, node):
    return node.name

  def SetName(self, root, ud, node, name):
    # Bug: When you open up a MessageDialog in this function,
    # it will be called one more time. So instead, we need to
    # open the dialog at another time.
    def message_dialog(*a, **kw):
      g.message_dialogs.append((a, kw))
      c4d.EventAdd()

    name = name.strip()
    if node.type_ == TYPE_FOLDER:
      if sane_filename(name) != name:
        message_dialog('"{0}" is an invalid filename'.format(name))
        return

      folder = os.path.dirname(node.path)
      dest = os.path.join(folder, sane_filename(name))
    elif node.type_ == TYPE_PRESET:
      folder = os.path.dirname(node.path)
      dest = os.path.join(folder, sane_filename(name) + '.tpr')
    else:
      return

    if os.path.exists(dest):
      message_dialog('"{0}" already exists'.format(name))
      return

    try:
      if node.type_ == TYPE_FOLDER:
        os.rename(node.path, dest)
        node.name = name
        node.path = dest
      elif node.type_ == TYPE_PRESET:
        node.delete(remove=False)
        node.path = dest
        node.name = name
        node.save()
    except (IOError, OSError) as exc:
      logger.warn(exc)
      message_dialog(str(exc))

    c4d.EventAdd()

  def IsOpened(self, root, ud, node):
    if node.type_ in (TYPE_TOOL, TYPE_FOLDER):
      return node.open
    return False

  def Open(self, root, ud, node, opened):
    if node.type_ in (TYPE_TOOL, TYPE_FOLDER):
      node.open = opened

  def IsSelected(self, root, ud, node):
    return node.selected

  def Select(self, root, ud, node, mode):
    if mode == c4d.SELECTION_NEW:
      root.apply_attr(selected=False)
      if node:
        node.selected = True
    elif mode == c4d.SELECTION_ADD:
      node.selected = True
    elif mode == c4d.SELECTION_SUB:
      node.selected = False

  def SelectionChanged(self, root, ud):
    selected = root.get_selected_nodes(max_nodes=2)
    if len(selected) == 1 and selected[0].type_ == TYPE_PRESET:
      apply_preset(selected[0])

  def DeletePressed(self, root, ud):
    selected = root.get_selected_nodes()
    if not selected:
      return

    if len(selected) == 1 and selected[0].type_ in (TYPE_TOOL, TYPE_FOLDER):
      question = 'Do you want to remove this folder an all its presets?'
    elif len(selected) == 1 and selected[0].type_ == TYPE_PRESET:
      question = 'Do you want to remove this preset?'
    else:
      question = 'Do you want to remove the selected elements?'
    confirmation = c4d.gui.MessageDialog(question, c4d.GEMB_YESNO)
    if confirmation != c4d.GEMB_R_YES:
      return

    for node in selected:
      node.delete()

  def CreateContextMenu(self, root, ud, node, column, menu):
    menu.FlushAll()
    menu.SetString(self.MENU_REMOVE, 'Remove')
    menu.SetString(self.MENU_REVEAL, 'Reveal in Explorer/Finder')
    menu.SetString(self.MENU_NEWFOLDER, 'New Folder')

    selected = root.get_selected_nodes(max_nodes=2)
    single = node and len(selected) == 1

    remove_enabled = node is not None
    reveal_enabled = single and node.type_ != TYPE_TOOL
    newfolder_enabled = single and node.type_ != TYPE_PRESET

    if not selected and not self.show_all and not node:
      node = self.GetFirstParent(root, ud)
      newfolder_enabled = node is not None

    disable = lambda id_: menu.SetString(id_, menu.GetString(id_) + '&d&')
    enable_if = lambda id_, cond: disable(id_) if not cond else None
    enable_if(self.MENU_REMOVE, remove_enabled)
    enable_if(self.MENU_REVEAL, reveal_enabled)
    enable_if(self.MENU_NEWFOLDER, newfolder_enabled)

  def ContextMenuCall(self, root, ud, node, column, command):
    if command == self.MENU_REMOVE:
      self.DeletePressed(root, ud)
      return True
    elif command == self.MENU_REVEAL:
      if node is not None:
        c4d.storage.ShowInFinder(node.path)
      return True
    elif command == self.MENU_NEWFOLDER:
      if node is None and not self.show_all:
          node = self.GetFirstParent(root, ud)
      if node is not None:
        name = c4d.gui.InputDialog('New Folder')
        if not name:
          return True
        if sane_filename(name) != name:
          c4d.gui.MessageDialog('"{0}" is an invalid filename'.format(name))
          return True
        path = os.path.join(node.path, name)
        if os.path.exists(path):
          c4d.gui.MessageDialog('"{0}" already exists'.format(name))
          return True
        try:
          os.makedirs(path)
        except (IOError, OSError) as exc:
          logger.warn(exc)
          c4d.gui.MessageDialog(str(exc))
          return True
        reload_presets(root)
      return True
    return False

  def DrawCell(self, root, ud, node, column, dinfo, bgcol):
    icon = None
    if node.type_ == TYPE_TOOL:
      if node.data:
        icon = c4d.gui.GetIcon(node.data)
    elif node.type_ == TYPE_FOLDER:
      icon = c4d.gui.GetIcon(c4d.RESOURCEIMAGE_TIMELINE_FOLDER2)

    x1, y1 = dinfo['xpos'], dinfo['ypos']
    sx, sy = dinfo['width'], dinfo['height']
    frame = dinfo['frame']

    frame.DrawSetPen(bgcol)
    frame.DrawRectangle(x1, y1, x1 + sx, y1 + sy)
    if icon:
      draw_icon(frame, icon, x1, y1, self.ICONSIZE, self.ICONSIZE)

  def GetColumnWidth(self, root, ud, node, column, frame):
    if column == self.COLUMN_ICON:
      return self.ICONSIZE

  def GetLineHeight(self, root, ud, node, column, frame):
    if column == self.COLUMN_ICON:
      return self.ICONSIZE


class TP_Dialog(c4d.gui.GeDialog):
  """
  The dialog that implements the Tool Preset GUI.
  """

  ID_SHOWALL = 1003
  ID_TREEVIEW = 1004
  ID_SAVEPRESET = 1005
  ID_VISITDEVELOPER = 1006

  bmp_globe = load_icon('res', 'images', 'globe.png')

  def __init__(self, root):
    super(TP_Dialog, self).__init__()
    self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
    self.widgets = {}
    self.root = root

  def add_icon(self, id_, flags, *args, **kwargs):
    """
    Adds an :class:`IconView` to the dialog.
    """

    view = IconView(*args, **kwargs)
    self.AddUserArea(id_, flags)
    self.AttachUserArea(view, id_)

    if id_ == 0:
      self.widgets.setdefault(0, []).append(view)
    else:
      self.widgets[id_] = view

  def CreateLayout(self):
    self.SetTitle('Tool Presets')
    self.GroupSpace(0, 2)
    self.GroupBorderSpace(2, 2, 2, 2)

    # Faked menu-line (the real doesn't look so nice).
    if self.GroupBegin(0, c4d.BFH_SCALEFIT):
      self.GroupSpace(4, 0)
      self.AddGadget(c4d.DIALOG_PIN, 0)

      self.AddCheckbox(self.ID_SHOWALL, c4d.BFH_SCALEFIT, 0, 0, name='Show All')
      ID_COMMAND_SAVE = 12098
      self.add_icon(self.ID_VISITDEVELOPER, 0, self.bmp_globe, height=18)
      self.add_icon(self.ID_SAVEPRESET, 0, ID_COMMAND_SAVE, height=18)
      self.GroupEnd()

    self.AddSeparatorH(0)

    # Add the tree view.
    fit = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT
    self.tree = self.AddCustomGui(
      self.ID_TREEVIEW, c4d.CUSTOMGUI_TREEVIEW, "", fit, 0, 0)

    return True

  def InitValues(self):
    reload_presets(self.root)
    self.tree_model = TP_TreeModel()
    self.tree_model.show_all = True
    self.SetBool(self.ID_SHOWALL, True)
    self.tree.SetRoot(self.root, self.tree_model, None)
    self.tree_model.InitLayout(self.tree)
    self.tree.Refresh()
    return True

  def Command(self, id_, msg):
    if id_ == self.ID_SHOWALL:
      self.tree_model.show_all = self.GetBool(self.ID_SHOWALL)
      self.tree.Refresh()
      return True
    elif id_ == self.ID_VISITDEVELOPER:
      webbrowser.open('http://niklasrosenstein.com/')
      return True
    elif id_ == self.ID_SAVEPRESET:
      # Get the current tool data, ID and name.
      doc = c4d.documents.GetActiveDocument()
      tool_id = doc.GetAction()
      tool_name = c4d.GetCommandName(tool_id)
      tool_data = doc.GetActiveToolData()
      if tool_data is None or not tool_name:
        message = 'could not retrieved current tool data'
        logger.error(message)
        c4d.gui.MessageDialog(message)
        return True

      title = 'Create new {0} Preset'.format(tool_name)

      # Should we save the preset under the tool's folder or
      # under the selected folder?
      selected = self.root.get_selected_nodes(max_nodes=2)
      if len(selected) == 1 and selected[0].type_ == TYPE_FOLDER:
        title += ' in {0}'.format(selected[0].name)
        folder = selected[0].path
      else:
        folder = '{0} {1}'.format(tool_id, tool_name)
      folder = os.path.join(self.root.path, folder)

      # Ask the user for the preset name.
      name = c4d.gui.InputDialog(title)
      if not name:
        return True

      filename = os.path.join(folder, sane_filename(name)) + '.tpr'
      preset = PresetNode(tool_id, name, uuid.uuid4(), tool_data, filename)
      save_preset_main(preset)

      # Reload our preset hierarchy and refresh the tree.
      reload_presets(self.root)
      self.tree.Refresh()
      return True
    return False

  def CoreMessage(self, id_, data):
    if id_ == c4d.EVMSG_CHANGE:
      # Process queued message dialogs.
      while g.message_dialogs:
        args, kwargs = g.message_dialogs.pop(0)
        c4d.gui.MessageDialog(*args, **kwargs)
      self.tree.Refresh()
    return super(TP_Dialog, self).CoreMessage(id_, data)


class TP_Command(c4d.plugins.CommandData):
  """
  This plugin command handles the TP_Dialog.
  """

  def __init__(self, root):
    super(TP_Command, self).__init__()
    self.root = root

  @property
  def dialog(self):
    if not hasattr(self, '_dialog'):
      self._dialog = TP_Dialog(self.root)
    return self._dialog

  def register(self):
    icon = load_icon('res', 'images', 'icon.tif')
    return c4d.plugins.RegisterCommandPlugin(
      PLUGIN_ID, "Tool Presets", 0, icon, "", self)

  # c4d.plugin.CommandData

  def Execute(self, doc):
    return self.dialog.Open(
      c4d.DLG_TYPE_ASYNC, PLUGIN_ID, defaultw=200, defaulth=300)

  def RestoreLayout(self, secret):
    return self.dialog.Restore(PLUGIN_ID, secret)


def main():
  # Create a root node that is shared among all common
  # controllers.
  root_dir = c4d.storage.GeGetC4DPath(c4d.C4D_PATH_LIBRARY_USER)
  root_dir = os.path.join(root_dir, 'toolpresets')
  root = Node('<root>', TYPE_ROOT, root_dir)

  TP_Command(root).register()
  print("Tool Presets", __version__, "registered")


if __name__ == '__main__':
  main()
