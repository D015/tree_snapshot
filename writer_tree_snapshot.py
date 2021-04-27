#!/usr/bin/python3
import os
from datetime import datetime

from utils import WriterPKL

start_root = '/'
snapshot_file = f'tree_snapshot_{datetime.now().strftime("%Y%m%d-%H%M%S")}'

test_snapshot_file = 'end_test_5'
test_start_root = '/home/dmitry/Coding/General/scripts'

empty_directory_size = 4096


def converting_lists_to_tuples_with_file_size(directory_root: str,
                                              subdirectories: list,
                                              files: list) -> dict:

    final_subdirectories = tuple(subdirectories)

    final_files = []
    for file_name in files:
        file_root = os.path.join(directory_root, file_name)
        try:
            file_size = os.path.getsize(file_root)
        except FileNotFoundError as file_not_found_error:
            file_size = 0
            # with open('file_not_found_error.txt', 'a') as f_n_f:
            #     print(file_not_found_error, file=f_n_f)
            # print(file_not_found_error)
        except PermissionError as permission_error:
            file_size = 0
            # with open('permission_error.txt', 'a') as f_p:
            #     print(permission_error, file=f_p)
            # print(permission_error)

        final_file_i = (file_name, file_size)
        final_files.append(final_file_i)
    final_files = tuple(final_files)

    result = {'subdirectories': final_subdirectories, 'files': final_files}

    return result


class TreeSnapshotCreator:
    def __init__(self, file_name='no_name', tree_start_path='/'):
        self.tree_start_path = tree_start_path
        self.file_name = file_name

    def save_tree_snapshot_to_tuple(self) -> tuple:
        tree_list = []
        for directory in os.walk(self.tree_start_path):
            directory_0 = directory[0]
            # todo clarify the condition with / at the end
            if not (directory_0.startswith('/proc') or directory_0.startswith('/dev')):
                converted_directory = \
                    converting_lists_to_tuples_with_file_size(directory_0,
                                                              directory[1],
                                                              directory[2])
                subdirectory_tuple = converted_directory['subdirectories']
                file_tuple = converted_directory['files']
                directory_tuple = \
                    (directory_0, subdirectory_tuple, file_tuple)

                tree_list.append(directory_tuple)
        tree_tuple = tuple(tree_list)
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
