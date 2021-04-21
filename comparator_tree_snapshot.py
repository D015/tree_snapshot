from utils import (ReaderPKL,
                   converting_tree_item_tuple_to_dict,
                   merge_differences_plus_or_minus)


class TreeSnapshotComparator:
    def __init__(self, start_snapshot, end_snapshot):
        self.start_snapshot = start_snapshot
        self.end_snapshot = end_snapshot

    def get_directory_difference(self):
        start_data_set = set(ReaderPKL(self.start_snapshot).read())
        end_data_set = set(ReaderPKL(self.end_snapshot).read())

        difference_start_set = start_data_set.difference(end_data_set)
        difference_start_tuple = tuple(difference_start_set)
        difference_start_dict = {}
        for i_difference_start_tuple in difference_start_tuple:
            i_difference_start_dict = \
                converting_tree_item_tuple_to_dict(i_difference_start_tuple)
            difference_start_dict.update(i_difference_start_dict)

        difference_end_set = end_data_set.difference(start_data_set)
        difference_end_tuple = tuple(difference_end_set)
        difference_end_dict = {}
        for i_difference_end_tuple in difference_end_tuple:
            i_difference_end_dict = \
                converting_tree_item_tuple_to_dict(i_difference_end_tuple)
            difference_end_dict.update(i_difference_end_dict)

        difference_start_directories = set(difference_start_dict.keys())
        difference_end_directories = set(difference_end_dict.keys())
        difference_minus_directories = \
            difference_start_directories.difference(difference_end_directories)
        difference_plus_directories = \
            difference_end_directories.difference(difference_start_directories)

        difference_minus_dict = {}
        for i_difference_minus_directories in difference_minus_directories:
            i_difference_minus_dict \
                = difference_start_dict.pop(i_difference_minus_directories)
            difference_minus_dict.update(
                {i_difference_minus_directories: i_difference_minus_dict})
        difference_change_start_dict = difference_start_dict

        difference_plus_dict = {}
        for i_difference_plus_directories in difference_plus_directories:
            i_difference_plus_dict \
                = difference_end_dict.pop(i_difference_plus_directories)
            difference_plus_dict.update(
                {i_difference_plus_directories: i_difference_plus_dict})
        difference_change_end_dict = difference_end_dict

        differences = {
            'difference_minus': difference_minus_dict,
            'difference_plus': difference_plus_dict,
            'difference_change_start_dict': difference_change_start_dict,
            'difference_change_end_dict': difference_change_end_dict
        }
        return differences

    def merge_differences(self):
        directory_difference = self.get_directory_difference()

        comparison_result = {}

        directory_difference_minus_dict = merge_differences_plus_or_minus(
            directory_difference['difference_minus'], plus=False)
        comparison_result.update(directory_difference_minus_dict)

        directory_difference_plus_dict = merge_differences_plus_or_minus(
            directory_difference['difference_plus'], plus=True)
        comparison_result.update(directory_difference_plus_dict)

        '-----------------------------------------------------------------'

        difference_change_start = \
            directory_difference['difference_change_start_dict']
        difference_change_end = \
            directory_difference['difference_change_end_dict']

        for key_difference_change_end, i_difference_change_end \
                in difference_change_end.items():

            i_files = i_difference_change_end['files']
            i_subdirectories = i_difference_change_end['subdirectories']

            i_specifications = \
                {
                    i_difference_change_end['specifications']['size'][0]:
                        i_difference_change_end['specifications']['size'][1],
                    'resize': 0
                }

            i_directory_difference_change_dict = \
                {
                    key_difference_change_end:
                        {
                            'subdirectories': {},
                            'files': {},
                            'specifications': i_specifications
                        }
                }




    def write_comparison_to_pkl(self):
        pass


class App:
    def __init__(self, start_file, end_file):
        self.start_file = start_file
        self.end_file = end_file

    def run(self):
        result = TreeSnapshotComparator(
            start_snapshot=self.start_file,
            end_snapshot=self.end_file).get_directory_difference()

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
