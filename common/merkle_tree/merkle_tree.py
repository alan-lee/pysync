__author__ = 'alan-lee'
import os
from tree_node import TreeNode


def build_merkle_tree(directory):
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception()

    tree = None
    files = os.listdir(directory)
    files.sort()
    children = list()

    for file_path in files:
        if os.path.isdir(file):
            node = build_merkle_tree(file_path)
            children.append(node)
        else:
            node = _create_file_node(file_path)
            children.append(node)

    node_list = children
    while True:
        if len(node_list) <= 3:
            tree = _create_dir_node(directory, node_list)
            break
        else:
            node_list = _build_parent_node_list()

    return tree


def _build_parent_node_list(directory, children=list()):
    node_list = list()
    index = 0

    children.sort(key=lambda child_node: child_node.get_path())
    while index < len(children):
        if index % 2 != 0:
            node = TreeNode(directory + '_' + (index + 1) % 2)
            node.add_child(children[index])
            node.add_child(children[index - 1])

            if index == len(children) - 2:
                index += 1
                node.add_child(children[index])

            node.calc_signature()
            node_list.append(node)
        index += 1
    return node_list


def _create_dir_node(dir_path, node_list):
    node = TreeNode(dir_path)
    for child_node in node_list:
        node.add_child(child_node)
    node.calc_signature()
    return node


def _create_file_node(file_path):
    node = TreeNode(file_path)
    node.calc_signature()
    return node
