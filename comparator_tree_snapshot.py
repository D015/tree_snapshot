#!/usr/bin/python3
import json
import os
import pickle
from datetime import datetime
from typing import Tuple

start_root = '/'
test_start_root = '/home/dmitry/Coding/General/scripts'
test_snapshot_file = 'test'
snapshot_file = f'tree_snapshot_{datetime.now().strftime("%Y%m%d-%H%M%S")}'
empty_directory_size = 1024


def converting_file_list_to_dict_file_size(file_directory_root,
                                           start_file_list):
    final_file_dict = {}
    sum_file_dict = {'size_all_files': 0}
    for start_file_list_i in start_file_list:
        file_root = os.path.join(file_directory_root, start_file_list_i)
        try:
            file_size = os.path.getsize(file_root)
        except FileNotFoundError as file_not_found_error:
            file_size = 0
            print(file_not_found_error)
            print(f'FileNotFoundError {file_root}')
        except PermissionError as permission_error:
            file_size = 0
            print(permission_error)
            print(f'PermissionError {file_root}')
        final_file_dict_i = {start_file_list_i: file_size}
        final_file_dict.update(final_file_dict_i)
        sum_file_dict['size_all_files'] += file_size
    return final_file_dict, sum_file_dict



class TreeWriterJSON:
    def __init__(self, file_name='no_name', tree_start_path='/'):
        self.tree_start_path = tree_start_path
        self.file_name = file_name + '.json'

    def save_tree_snapshot_to_json(self):
        with open(self.file_name, "w") as file_handler:
            for i in os.walk(self.tree_start_path):
                file_dict, sum_dict = \
                    converting_file_list_to_dict_file_size(i[0], i[2])
                size_i = (i[0], i[1], file_dict, sum_dict)
                file_handler.write(json.dumps(size_i))
                file_handler.write('\n')
        return True

        # for root, directories, files in os.walk(self.tree_start_path):
        #     print(f'{root}, {directories}, {files}')


class App:
    def run(self):
        result = TreeWriterJSON(
            file_name=snapshot_file,
            tree_start_path=start_root).save_tree_snapshot_to_json()
        print(result)


if __name__ == '__main__':
    App().run()
