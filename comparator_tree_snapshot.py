from dataclasses import dataclass

from utils import (ReaderPKL,
                   converting_tree_item_tuple_to_dict,
                   merge_other_directory, merge_modified_directory)


@dataclass
class TreeSnapshotComparator:
    start_snapshot: str
    end_snapshot: str

    def get_differing_directories(self) -> dict:
        start_data = set(ReaderPKL(self.start_snapshot).read())
        end_data = set(ReaderPKL(self.end_snapshot).read())
        # Getting tuple of differing start directories and converting into tuple
        differing_start_dir_tuple = tuple(start_data.difference(end_data))
        differing_start_directories = {}
        for i_start_dir_tuple in differing_start_dir_tuple:
            i_differing_start_directories = \
                converting_tree_item_tuple_to_dict(i_start_dir_tuple)
            differing_start_directories.update(i_differing_start_directories)
        # Getting tuple of differing end directories and converting into tuple
        differing_end_dir_tuple = tuple(end_data.difference(start_data))
        differing_end_directories = {}
        for i_end_dir_tuple in differing_end_dir_tuple:
            i_differing_end_directories = \
                converting_tree_item_tuple_to_dict(i_end_dir_tuple)
            differing_end_directories.update(i_differing_end_directories)
        # Getting deleted and created directory names
        difference_start_directory_names = set(differing_start_directories)
        difference_end_directory_names = set(differing_end_directories)
        deleted_directory_names = \
            difference_start_directory_names.difference(
                difference_end_directory_names)
        created_directory_names = \
            difference_end_directory_names.difference(
                difference_start_directory_names)
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

    def write_comparison_to_pkl(self):
        pass


class App:
    def __init__(self, start_file, end_file):
        self.start_file = start_file
        self.end_file = end_file

    def run(self):
        result = TreeSnapshotComparator(
            start_snapshot=self.start_file,
            end_snapshot=self.end_file).get_differing_directories()

        # test
        print('difference_minus-----------------------------------------------')
        for k, i in result['difference_minus'].items():
            print(k, i)
            print()
        print('difference_plus++++++++++++++++++++++++++++++++++++++++++++++++')
        for k, i in result['difference_plus'].items():
            print(k, i)
            print()
        print('difference_change_start_dict ssssssssssssssssssssssssssssssssss')
        for k, i in result['difference_change_start_dict'].items():
            print(k, i)
            print()
        print('difference_change_end_dict eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        for k, i in result['difference_change_start_dict'].items():
            print(k, i)
            print()


if __name__ == '__main__':
    App(start_file='tree_snapshot_20210419-141901.pkl',
        end_file='tree_snapshot_20210419-142903.pkl').run()
