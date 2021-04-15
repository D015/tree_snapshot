#!/usr/bin/python3
import os
import pickle
from datetime import datetime

start_root = '/'
test_start_root = '/run'

test_snapshot_file = 'test'
snapshot_file = f'tree_snapshot_{datetime.now().strftime("%Y%m%d-%H%M%S")}'
empty_directory_size = 1024


def converting_file_list_to_tuple_file_size(file_directory_root,
                                            final_directory_tuple,
                                            start_file_list):
    final_file_tuple = []
    sum_file_tuple = ['size_all_files', 0]
    for start_file_list_i in start_file_list:
        file_root = os.path.join(file_directory_root, start_file_list_i)
        try:
            file_size = os.path.getsize(file_root)
        except FileNotFoundError as file_not_found_error:
            file_size = 0
            with open('file_not_found_error.txt', 'a') as f_n_f:
                print(file_not_found_error, file=f_n_f)
        except PermissionError as permission_error:
            file_size = 0
            with open('permission_error.txt', 'a') as f_p:
                print(permission_error, file=f_p)
        final_file_tuple_i = (start_file_list_i, file_size)
        final_file_tuple.append(final_file_tuple_i)
        sum_file_tuple[1] += file_size
    final_directory_tuple = tuple(final_directory_tuple)
    final_file_tuple = tuple(final_file_tuple)
    sum_file_tuple = tuple(sum_file_tuple)
    return final_directory_tuple, final_file_tuple, sum_file_tuple


class TreeWriterPKL:
    def __init__(self, file_name='no_name', tree_start_path='/'):
        self.tree_start_path = tree_start_path
        self.file_name = file_name + '.pkl'

    tree_list = []

    def save_tree_snapshot_to_pkl(self):
        with open(self.file_name, "wb") as file_handler:
            for i in os.walk(self.tree_start_path):
                directory_tuple, file_tuple, sum_tuple = \
                    converting_file_list_to_tuple_file_size(i[0], i[1], i[2])
                size_i = (i[0], directory_tuple, file_tuple, sum_tuple)
                self.tree_list.append(size_i)
            tree_tuple = tuple(self.tree_list)
            file_handler.write(pickle.dumps(tree_tuple))
        return True


class App:
    def __init__(self, file_name, tree_start_path):
        self.file_name = file_name
        self.tree_start_path = tree_start_path

    def run(self):
        result = TreeWriterPKL(
            file_name=self.file_name,
            tree_start_path=self.tree_start_path).save_tree_snapshot_to_pkl()
        print(result)


if __name__ == '__main__':
    App(file_name=snapshot_file,
        tree_start_path=start_root).run()
