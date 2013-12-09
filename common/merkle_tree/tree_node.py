__author__ = 'alan-lee'
import os
import hashlib


class TreeNode:
    def __init__(self, path, virtual_node=False):
        self._children = list()
        self._path = path
        self._signature = ''
        self._virtual_node = virtual_node

    def get_signature(self):
        return self._signature

    def get_path(self):
        return self._path

    def is_virtual_node(self):
        return self._virtual_node

    def add_child(self, node):
        self._children.append(node)

    def calc_signature(self):
        if not os.path.exists(self._path):
            return

        sha1 = hashlib.sha1()
        if os.path.isdir(self._path):
            self._children.sort(key=lambda child_node: child_node.get_path())
            for child in self._children:
                sha1.update(child.get_signature())
        else:
            with open(self._path, 'rb') as fp:
                while True:
                    data = fp.read()
                    if not data:
                        break
                    else:
                        sha1.update(data)

        self._signature = sha1.hexdigest()
