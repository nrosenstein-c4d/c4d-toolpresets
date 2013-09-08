# coding: utf-8
#
# Copyright (c) 2012-2013, Niklas Rosenstein
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be interpreted
# as representing official policies,  either expressed or implied, of
# the FreeBSD Project.
r"""
``treenode`` - A double-linked hierarchical data-structure
==========================================================

.. license:: Simplified BSD License
.. author:: Niklas Rosenstein
"""

import abc
import warnings

__version__ = (0, 1, 0)
__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'

class TreeNodeMeta(abc.ABCMeta):
    r"""
    Meta-class for the :class:`TreeNode` class.
    """

    def __new__(self, name, bases, dict):
        if 'type_id' not in dict:
            raise ValueError('required class-level attribute '
                             '`type_id` not found.')
        type_id = dict['type_id']

        if 'type_order' in dict:
            warnings.warn('type_order attribute omitted')

        type_order = []
        for base in bases:
            type_order.extend(getattr(base, 'type_order', []))

        type_order.append(type_id)
        dict['type_order'] = type_order

        if len(set(type_order)) != len(type_order):
            raise ValueError('inconsistent type_id assignment. '
                             'inheritance results in double occurence of '
                             'the same type_id.')

        return super(TreeNodeMeta, self).__new__(self, name, bases, dict)

    def check_type(self, type_id):
        return type_id in self.type_order

class TreeNode(object):
    r"""
    This class implements a basic tree-node. This class has the type-id
    ``0`` (zero).
    """

    __metaclass__ = TreeNodeMeta
    
    type_id = 0

    name = 'TreeNode'
    parent = None
    next = None
    prev = None
    child = None

    def __init__(self):
        super(TreeNode, self).__init__()
        self.on_init()

    def on_init(self):
        r"""
        Called at the end of the :class:`TreeNode` constructor.
        """

    def on_detach(self):
        r"""
        Called when a node is removed from the hierarchy.
        """

    def remove(self):
        r"""
        Removes the node from the hierarchy (including its children).
        """

        self.on_detach()

        if self.parent and self.parent.child == self:
            self.parent.child = self.next

        next = self.next
        prev = self.prev

        if next:
            next.prev = prev
        if prev:
            prev.next = next

        self.parent = None
        self.next = None
        self.prev = None

    def insert_under(self, parent):
        r"""
        Insert *self* as first child node under *parent*.
        """

        if parent.child:
            self.next = parent.child
            parent.child.prev = self

        parent.child = self
        self.parent = parent

    def insert_under_last(self, parent):
        r"""
        Insert *self* as last child node under *parent*.
        """

        last = parent.child
        if not last:
            self.insert_under(parent)
        else:
            while last.next:
                last = last.next

            last.next = self
            self.prev = last
            self.parent = parent

    def insert_after(self, node):
        r"""
        Insert *self* after *node*.
        """

        if node.next:
            self.next = node.next
            node.next.prev = self
        node.next = self
        self.parent = node.parent

    def insert_before(self, node):
        r"""
        Insert *self* before *node*.
        """

        if node.prev:
            self.prev = node.prev
            node.prev.next = self
        node.prev = self
        self.parent = node.parent

    def iter_children(self):
        r"""
        Returns a generator iterating over the children of the object.
        """

        node = self.child
        while node:
            yield node
            node = node.next

    def list_children(self):
        r"""
        Returns a list of all children of *self*.
        """

        list_ = []
        node = self.child
        while node:
            list_.append(node)
            node = node.next

        return list_

    def set_children(self, children):
        r"""
        Sets a list of children to the node removing any previous
        children. Returns a list of the previous children.
        """

        old = self.pop_children()
        self.insert_children(children)
        return old

    def pop_children(self):
        r"""
        Removes all children from the node and returns them as a list.
        """

        old = self.list_children()
        for child in old:
            child.remove()
        return old

    def insert_children(self, children):
        r"""
        Inserts a list of children at the end of the node.
        """

        for child in children:
            child.insert_under_last(self)

    def sort(self, recursive=True, key=lambda x: x.name):
        r"""
        Sorts the children of the node.
        """

        children = self.pop_children()
        children.sort(key=key)
        self.insert_children(children)

        if recursive:
            for child in self.iter_children():
                child.sort(recursive, key)

    def traverse(self, callback):
        r"""
        Traverse the hierarchy recursively beginning with *self*. The
        passed *callback* must accept a single argument being the current
        node being processed.

        If the callback returns False, the recursion will stop.
        """

        if not callback(self):
            return

        for child in self.list_children():
            child.traverse(callback)

    def validate_tree(self, _parent=None, _temp_varname='_met_node'):
        r"""
        Tests if the tree is valid. Returns a tuple of
        ``(is_valid, reason, node)``.
        """

        if _parent and _parent != self.parent:
            return False, 'wrong-parent', self

        if hasattr(self, _temp_varname):
            delattr(self, _temp_varname)
            return False, 'met-twice', self

        setattr(self, _temp_varname, True)

        result = True, None, None
        for child in self.iter_children():
            result = child.validate_tree(self, _temp_varname)
            if not result[0]:
                break

        if hasattr(self, _temp_varname):
            delattr(self, _temp_varname)
        return result

    def check_type(self, type_id):
        return TreeNodeMeta.check_type(self.__class__, type_id)


