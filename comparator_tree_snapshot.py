import copy
import operator
import os
from dataclasses import dataclass
from pprint import pprint
from typing import Union, Dict, List, Tuple

from utils import (ReaderPKL,
                   converting_tree_item_tuple_to_dict,
                   merge_other_directory, merge_modified_directory,
                   empty_directory_size, sort_dictionary_by_keys_into_list)


def create_directories_with_parent(
        directory: Tuple,
        copy_of_all_directories: Dict) -> None:
    directory_name, directory_content = directory
    directory_size = directory_content['specifications']['directory_size']
    directory_resize = directory_content['specifications']['directory_resize']
    data = (directory_name, directory_size, directory_resize,
            copy_of_all_directories)
    while directory_name != '/':
        data = add_one_parent_directory(*data)
        directory_name, s, r, c = data
    n, s, r, copy_of_all_directories = data
    return copy_of_all_directories


def add_one_parent_directory(directory_name: str,
                             directory_size: int,
                             directory_resize: int,
                             parent_directories: dict) -> Union[tuple, bool]:
    parent_directory_name = os.path.dirname(directory_name)
    is_root = parent_directory_name == directory_name
    if is_root:
        return False
    parent_directory_size = directory_size + empty_directory_size

    parent_directory_resize = directory_resize

    specifications = {
        'specifications': {'directory_size': parent_directory_size,
                           'directory_resize': parent_directory_resize}}
    parent_directory = {parent_directory_name: specifications}
    if not (parent_directory_name in parent_directories):
        parent_directories.update(parent_directory)
    else:
        parent_directories[
            parent_directory_name]['specifications']['directory_size'] \
            += specifications['specifications']['directory_size']

        parent_directories[
            parent_directory_name]['specifications']['directory_resize'] \
            += specifications['specifications']['directory_resize']

    result = (parent_directory_name, directory_size, directory_resize,
              parent_directories)
    return result


@dataclass
class TreeSnapshotComparator:
    start_snapshot: str
    end_snapshot: str

    def get_differing_directories(self) -> dict:
        start_data = set(ReaderPKL(self.start_snapshot).read())
        end_data = set(ReaderPKL(self.end_snapshot).read())
        # Getting tuple of differing start directories and converting into tuple
        differing_start_dir_tuple = tuple(start_data - end_data)
        differing_start_directories = {}
        for i_start_dir_tuple in differing_start_dir_tuple:
            i_differing_start_directories = \
                converting_tree_item_tuple_to_dict(i_start_dir_tuple)
            differing_start_directories.update(i_differing_start_directories)
        # Getting tuple of differing end directories and converting into tuple
        differing_end_dir_tuple = tuple(end_data - start_data)
        differing_end_directories = {}
        for i_end_dir_tuple in differing_end_dir_tuple:
            i_differing_end_directories = \
                converting_tree_item_tuple_to_dict(i_end_dir_tuple)
            differing_end_directories.update(i_differing_end_directories)
        # Getting deleted and created directory names
        difference_start_directory_names = set(differing_start_directories)
        difference_end_directory_names = set(differing_end_directories)
        deleted_directory_names = \
            difference_start_directory_names - difference_end_directory_names
        created_directory_names = \
            difference_end_directory_names - difference_start_directory_names
        # Making dict of deleted directories and modified start directories
        deleted_directories = {}
        for i_deleted_directory_name in deleted_directory_names:
            v_deleted_directory \
                = differing_start_directories.pop(i_deleted_directory_name)
            deleted_directories.update(
                {i_deleted_directory_name: v_deleted_directory})
        modified_start_directories = differing_start_directories
        # Making dict of created directories and modified end directories
        created_directories = {}
        for i_created_directory_name in created_directory_names:
            v_created_directory \
                = differing_end_directories.pop(i_created_directory_name)
            created_directories.update(
                {i_created_directory_name: v_created_directory})
        modified_end_directories = differing_end_directories

        different_directories = {
            'deleted_directories': deleted_directories,
            'created_directories': created_directories,
            'modified_start_directories': modified_start_directories,
            'modified_end_directories': modified_end_directories}
        return different_directories

    def merge_differences(self):
        differing_directories = self.get_differing_directories()

        merging_result = {}

        merged_deleted_directories = merge_other_directory(
            differing_directories['deleted_directories'], created=False)
        merging_result.update(merged_deleted_directories)

        merged_created_directories = merge_other_directory(
            differing_directories['created_directories'], created=True)
        merging_result.update(merged_created_directories)

        merged_modified_directories = merge_modified_directory(
            differing_directories['modified_start_directories'],
            differing_directories['modified_end_directories'])
        merging_result.update(merged_modified_directories)

        return merging_result


@dataclass
class DirectoryHierarchyCreator:
    merged_directories: Dict

    def add_parent_directory_in_hierarchy(self) -> List[Tuple]:
        copy_of_all_directories = copy.deepcopy(self.merged_directories)
        for i_directory in self.merged_directories.items():

            copy_of_all_directories = \
                create_directories_with_parent(i_directory,
                                               copy_of_all_directories)
        # todo Use copy or " = " &
        directories_with_parent = copy_of_all_directories.copy()

        directories_with_parents_in_hierarchy: List[Tuple] = \
            sort_dictionary_by_keys_into_list(directories_with_parent)

        return directories_with_parents_in_hierarchy


class App:
    def __init__(self, start_file, end_file):
        self.start_file = start_file
        self.end_file = end_file

    def run(self):
        merged_directories = TreeSnapshotComparator(
            start_snapshot=self.start_file,
            end_snapshot=self.end_file).merge_differences()
        resize = 0
        for n, directory_content in merged_directories.items():
            resize += directory_content['specifications']['directory_resize']
        print(resize)
        result = DirectoryHierarchyCreator(
            merged_directories=merged_directories). \
            add_parent_directory_in_hierarchy()

        r = 0

        for k_directory, i_content in result:
            # if '/var/lib/' in k_directory:
            #     r += i_content['specifications']['directory_resize']

            # if i_content['specifications']['directory_resize'] > 1000000:
            # if '/var/lib' in k_directory:

            if k_directory.count('/') == 1 or k_directory.count('/') == 2 or k_directory.count('/') == 3:
                print(round((i_content['specifications'][
                                 'directory_resize'] / 1024 / 1024), 2))
                print(k_directory)
                pprint(i_content['specifications'])
                print()
        # print(r)


if __name__ == '__main__':
    App(start_file='tree_snapshot_20210427-150027.pkl',
        end_file='tree_snapshot_20210509-011538.pkl').run()
