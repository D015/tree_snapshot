#!/usr/bin/python3
import os
from datetime import datetime

from utils import converting_file_list_to_tuple_file_size, \
    WriterPKL

start_root = '/'
test_start_root = '/home/dmitry'

snapshot_file = f'tree_snapshot_{datetime.now().strftime("%Y%m%d-%H%M%S")}'
test_snapshot_file = 'test'
empty_directory_size = 4096


class TreeSnapshotCreator:
    def __init__(self, file_name='no_name', tree_start_path='/'):
        self.tree_start_path = tree_start_path
        self.file_name = file_name

    tree_list = []

    def save_tree_snapshot_to_tuple(self):
        for i in os.walk(self.tree_start_path):
            i_0 = i[0]
            if not(i_0.startswith('/proc') or i_0.startswith('/dev')):
                directory_tuple, file_tuple, sum_tuple = \
                    converting_file_list_to_tuple_file_size(i_0, i[1], i[2])
                size_i = (i_0, directory_tuple, file_tuple, sum_tuple)
                self.tree_list.append(size_i)
        tree_tuple = tuple(self.tree_list)
        return tree_tuple

    def write_to_pkl(self):
        return WriterPKL(data=self.save_tree_snapshot_to_tuple(),
                         file_name=self.file_name).write()


class App:
    def __init__(self, file_name, tree_start_path):
        self.file_name = file_name
        self.tree_start_path = tree_start_path

    def run(self):
        result = TreeSnapshotCreator(
            file_name=self.file_name,
            tree_start_path=self.tree_start_path).write_to_pkl()
        print(result)


if __name__ == '__main__':
    App(file_name=snapshot_file,
        tree_start_path=start_root).run()
