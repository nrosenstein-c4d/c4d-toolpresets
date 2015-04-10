# Copyright (C) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
r"""
:mod:`c4dtools.utils`
=====================

This module provides useful utility functions and classes that are
generally useful through out many topics of Cinema 4D plugin
development.
"""

import c4d
import warnings


def find_root(node):
    r"""
    Returns the top-most parent node of *node*s hierarchy, or the
    *node* itself if it is the top-most node.
    """

    parent = node.GetUp()
    while parent:
        node = parent
        parent = node.GetUp()

    return node


def remove_document(doc, new_active_doc=None):
    r"""
    Removes the document *doc* from the list of documents in Cinema 4D
    and activates the next or a new document. This is similar to the
    :func:`c4d.documents.KillDocument` function, but on the contrary,
    *doc* will not be deallocated and still be valid.

    If *new_active_doc* is specified, it will be set as the new active
    document instead of the determined successor.
    """

    if type(doc) is not c4d.documents.BaseDocument:
        raise TypeError("doc must be a BaseDocument object")
    if new_active_doc is not None and \
            type(new_active_doc) is not c4d.documents.BaseDocument:
        raise TypeError("new_active_doc must be a BaseDocument object")

    successor = new_active_doc or doc.GetPred() or doc.GetNext()
    doc.Remove()

    # Note: The document will be removed before eventually inserting
    # a new document because if *doc* is the active document and is
    # empty, InsertBaseDocument will actually kill it before inserting
    # the new document.

    if not successor:
        successor = c4d.documents.BaseDocument()
        c4d.documents.InsertBaseDocument(successor)

    c4d.documents.SetActiveDocument(successor)


def iter_timeline(doc, start, end):
    r"""
    Returns a generator that yields one frame number after the other
    while updating the Cinema 4D document *doc* timeline and editor
    view. All expressions and animations are being evaluated every
    frame.

    for frame in iter_timeline(doc, 0, 100):
        pass  # process current frame here

    Both *start* and *end* can be either :class:`c4d.BaseTime` or
    frame numbers. *end* is inclusive.
    """

    fps = doc.GetFps()
    time = doc.GetTime()

    if isinstance(start, c4d.BaseTime):
        start = start.GetFrame(fps)
    if isinstance(end, c4d.BaseTime):
        end = end.GetFrame(fps)

    for frame in xrange(start, end + 1):
        doc.SetTime(c4d.BaseTime(frame, fps))
        c4d.DrawViews(
            c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW | c4d.DRAWFLAGS_NO_THREAD |
            c4d.DRAWFLAGS_NO_REDUCTION | c4d.DRAWFLAGS_STATICBREAK)
        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
        yield frame

    doc.SetTime(time)
    c4d.DrawViews(
        c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW | c4d.DRAWFLAGS_NO_THREAD |
        c4d.DRAWFLAGS_NO_REDUCTION | c4d.DRAWFLAGS_STATICBREAK)
    c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)


class UndoHandler(object):
    r"""
    The *UndoHandler* is a useful class to temporarily apply changes to
    components of Cinema 4D objects, tags, materials, nodes, documents
    etc. and revert them at a specific point.

    Internally, the *UndoHandler* simply stores a list of callables
    that are called upon :meth:`revert`. All methods that store the
    original state of a node simply append a callable to it. Custom
    callables can be added with :meth:`custom`.
    """

    __slots__ = ('_flist',)

    def __init__(self):
        super(UndoHandler, self).__init__()
        self._flist = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.revert()

    def revert(self):
        r"""
        Reverts back to the original states that have been kept track
        of with this *UndoHandler* and flushes these states.
        """

        flist, self._flist = self._flist, []
        [f() for f in reversed(flist)]

    def custom(self, target):
        r"""
        Adds a custom callable object that is invoked when
        :meth:`revert` is called. It must accept no arguments.
        """

        if not callable(target):
            raise TypeError("<target> must be callable", type(target))
        self._flist.append(target)

    def matrix(self, op):
        r"""
        Restores *op*s current matrix upon :meth:`revert`.
        """

        ml = op.GetMl()
        def revert_matrix():
            op.SetMl(ml)
        self._flist.append(revert_matrix)

    def location(self, node):
        r"""
        Tracks the hierarchical location of *node* and restores it upon
        :meth:`revert`. This method only supports materials, tags and
        objects. This will also remove nodes that were not inserted any
        where before.
        """

        pred_node = node.GetPred()
        next_node = node.GetNext()
        parent = node.GetUp()
        tag_host = node.GetObject() if isinstance(node, c4d.BaseTag) else None
        doc = node.GetDocument()

        if not any([pred_node, next_node, parent, tag_host]) and doc:
            supported_classes = (c4d.BaseMaterial, c4d.BaseObject)
            if not isinstance(node, supported_classes):
                raise TypeError(
                    "only materials and objects are supported when "
                    "located at their root", type(node))

        def revert_hierarchy():
            node.Remove()
            if pred_node and pred_node.GetUp() == parent:
                node.InsertAfter(pred_node)
            elif next_node and next_node.GetUp() == parent:
                node.InsertBefore(next_node)
            elif parent:
                node.InsertUnder(parent)
            elif tag_host:
                tag_host.InsertTag(node)
            elif doc:
                if isinstance(node, c4d.BaseMaterial):
                    doc.InsertMaterial(node)
                elif isinstance(node, c4d.BaseObject):
                    doc.InsertObject(node)
                else:
                    raise RuntimeError("unexpected type of <node>", type(node))

        self._flist.append(revert_hierarchy)

    def container(self, node):
        r"""
        Grabs a copy of the *node*s :class:`c4d.BaseContainer` and
        restores it upon :meth:`revert`.
        """

        data = node.GetData()
        def revert_container():
            node.SetData(data)
        self._flist.append(revert_container)

    def full(self, node):
        r"""
        Gets a complete copy of *node* and restores its complete state
        upon :meth:`revert`. This is like using :data:`c4d.UNDOTYPE_CHANGE`
        with :meth:`c4d.documents.BaseDocument.AddUndo` except that it
        does not include the hierarchical location. For that, you can
        use :meth:`track_hierarchy`.
        """

        flags = c4d.COPYFLAGS_NO_HIERARCHY | c4d.COPYFLAGS_NO_BRANCHES
        clone = node.GetClone(flags)
        def revert_node():
            clone.CopyTo(node, c4d.COPYFLAGS_0)
        self._flist.append(revert_node)


class TemporaryDocument(object):
    r"""
    The *TemporaryDocument* provides, as the name implies, a temporary
    :class:`BaseDocument<c4d.documents.BaseDocument>` that can be used
    to perform operations in an isolated environment such as calling
    modeling commands or :func:`CallCommands<c4d.CallCommand>`.

    When the *TemporaryDocument* is created, it is not immediately
    activated. To do so, one must call the :meth:`Attach` method or use
    it as a context-manager. When the document is no longer needed, the
    context-manager will close the document and remove it from the
    Cinema 4D document list or :meth:`detach` must be called manually.
    The *TemporaryDocument* can be re-used after it has been closed.

    Use the :meth:`get` method to obtain the wrapped *BaseDocument*
    or catch the return value of the context-manager.

    .. note::

        If :meth:`detach` was not called after :meth:`Attach` and the
        *TemporaryDocument* is being deleted via the garbage collector,
        a :class:`RuntimeWarning` will be issued but the document will
        not be detached.

    .. important::

        The *TemporaryDocument* will not expect that the internal
        *BaseDocument* might actually be removed by any other mechanism
        but the :meth:`detach` method.
    """

    __slots__ = ('_bdoc', '_odoc')

    def __init__(self):
        super(TemporaryDocument, self).__init__()
        self._bdoc = c4d.documents.BaseDocument()
        self._odoc = None

    def __del__(self):
        if self._odoc is not None:
            warnings.warn(
                "TemporaryDocument not detached before being "
                "garbage collected", RuntimeWarning)

    def __enter__(self):
        r"""
        Attaches the real temporary document and returns it.
        """

        self.attach()
        return self.get()

    def __exit__(self, *args):
        self.detach()

    def attach(self):
        r"""
        Attaches the temporary document to the Cinema 4D document list.
        It will also be promoted to be the active document. A call to
        :meth:`detach` must be paired with :meth:`attach`.

        The document that is active before this method is called will
        be saved and promoted back to being the active document with
        calling :meth:`detach`.

        Returns *self* for method-chaining.
        """

        if self._odoc is not None:
            raise RuntimeErrorn("attach() has already been called")

        self._odoc = c4d.documents.GetActiveDocument()
        c4d.documents.InsertBaseDocument(self._bdoc)
        c4d.documents.SetActiveDocument(self._bdoc)
        return self

    def detach(self, do_recall=True):
        r"""
        Detaches the temporary document from the Cinema 4D document
        list and promotes the previous active document back to its
        original status unless *do_recall* is False.

        Returns *self* for method-chaining.
        """

        if self._odoc is None:
            raise RuntimeError("attach() has not been called before")

        remove_document(self._bdoc, self._odoc() if do_recall else None)
        self._odoc = None
        return self

    def get(self):
        r"""
        Returns the internal *BaseDocument* object.
        """

        return self._bdoc

    def is_attached(self):
        r"""
        Returns :const:`True` if this *TemporaryDocument* is attached,
        that is, inside the Cinema 4D document list, and :const:`False`
        if it's not.
        """

        attached = self._odoc is not None
        return attached
