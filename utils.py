import os
import pickle

directory_size = 4096


def get_dict_of_other_files_by_remove_keys_from_set(the_dict: dict,
                                                    the_set: set,
                                                    created: bool = True):
    direction_of_created = 1 if created is True else -1

    other_files_dict = {'files': {}, 'specifications': {'size': 0, 'resize': 0}}
    if the_dict and the_set:
        for key in the_set:
            if key in the_dict:
                value = the_dict.pop(key)
                other_files_dict['files'].update({key: value})
                other_files_dict['specifications']['size'] += value

        other_files_dict['specifications']['resize'] = \
            other_files_dict['specifications']['size'] * direction_of_created

    return other_files_dict


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
            # with open('file_not_found_error.txt', 'a') as f_n_f:
            #     print(file_not_found_error, file=f_n_f)
            # print(file_not_found_error)
        except PermissionError as permission_error:
            file_size = 0
            # with open('permission_error.txt', 'a') as f_p:
            #     print(permission_error, file=f_p)
            # print(permission_error)

        final_file_tuple_i = (start_file_list_i, file_size)
        final_file_tuple.append(final_file_tuple_i)
        sum_file_tuple[1] += file_size
    final_directory_tuple = tuple(final_directory_tuple)
    final_file_tuple = tuple(final_file_tuple)
    sum_file_tuple = tuple(sum_file_tuple)
    return final_directory_tuple, final_file_tuple, sum_file_tuple


def converting_tree_item_tuple_to_dict(tree_item_tuple):
    tree_item_dict = {
        tree_item_tuple[0]: {
            'subdirectories': tree_item_tuple[1],
            'files': tree_item_tuple[2],
            'specifications': tree_item_tuple[3]
        }
    }
    return tree_item_dict


def merge_differences_plus_or_minus(directory_difference, plus=True):
    direction_of_change = 1 if plus is True else -1

    result_difference = {}
    for key_directory_difference, i_directory_difference \
            in directory_difference.items():

        i_files = i_directory_difference['files']
        i_subdirectories = i_directory_difference['subdirectories']
        i_specifications = \
            {
                i_directory_difference['specifications']['size'][0]:
                    i_directory_difference['specifications']['size'][
                        1],
                'resize': 0
            }

        i_directory_difference_dict = \
            {
                key_directory_difference:
                    {
                        'subdirectories': {},
                        'files': {},
                        'specifications': i_specifications
                    }
            }

        if i_subdirectories:
            for d_i_subdirectory in i_subdirectories:
                d_i_subdirectory_dict = \
                    {
                        d_i_subdirectory:
                            {
                                'size': directory_size,
                                'resize': directory_size * direction_of_change
                            }
                    }

                i_directory_difference_dict['specifications'] \
                    ['resize'] += directory_size * direction_of_change

                i_directory_difference_dict['specifications']. \
                    update(d_i_subdirectory_dict)

        if i_files:
            for f_i_file in i_files:
                f_i_file_dict = \
                    {
                        f_i_file[0]:
                            {
                                'size': f_i_file[1],
                                'resize': f_i_file[1] * direction_of_change
                            }
                    }

                i_directory_difference_dict['specifications'] \
                    ['resize'] += f_i_file[1] * direction_of_change

                i_directory_difference_dict['files']. \
                    update(f_i_file_dict)

        result_difference.update(i_directory_difference_dict)
    return result_difference


def merge_files_from_changed_directory(start_files: set, end_files: set):
    files_from_changed_directory = \
        {'files': {}, 'specifications': {'size': 0, 'resize': 0}}

    difference_start_dict = dict(start_files.difference(end_files))
    difference_end_dict = dict(start_files.difference(end_files))
    #     Неизмененные файлы
    identical_files_set = start_files.intersection(end_files)
    identical_files_dict = dict(identical_files_set)
    files_from_changed_directory['files'].update(identical_files_dict)
    # Resized file names
    resized_file_names_set = \
        set(difference_start_dict).intersection(difference_end_dict)
     # Deleted files
    deleted_files_dict = get_dict_of_other_files_by_remove_keys_from_set(
        difference_start_dict, resized_file_names_set, created=False)

    resized_start_files_dict = difference_start_dict
    files_from_changed_directory['files'].update(deleted_files_dict['files'])

    files_from_changed_directory['specifications']['size'] += \
        (deleted_files_dict['specifications']['size'])

    files_from_changed_directory['specifications']['resize'] += \
        (deleted_files_dict['specifications']['resize'])
    # Created files
    created_files_dict = get_dict_of_other_files_by_remove_keys_from_set(
        difference_end_dict, resized_file_names_set, created=True)

    resized_end_files_dict = difference_end_dict
    files_from_changed_directory['files'].update(created_files_dict['files'])

    files_from_changed_directory['specifications']['size'] += \
        (created_files_dict['specifications']['size'])

    files_from_changed_directory['specifications']['resize'] += \
        (created_files_dict['specifications']['resize'])
    # Resized file
    resized_files_dict = \
        {'files': {}, 'specifications': {'size': 0, 'resize': 0}}

    for key in resized_end_files_dict:
        size = resized_end_files_dict[key]
        resize = size - resized_start_files_dict[key]
        resized_files_dict.update({key: {'size': size, 'resize': resize}})
        resized_files_dict['specifications']['size'] += size
        resized_files_dict['specifications']['resize'] += resize
    files_from_changed_directory['files'].update(resized_files_dict['files'])

    files_from_changed_directory['specifications']['size'] += \
        (resized_files_dict['specifications']['size'])

    files_from_changed_directory['specifications']['resize'] += \
        (resized_files_dict['specifications']['resize'])

    return files_from_changed_directory


class WriterPKL:
    def __init__(self, data: str = '/', file_name='no_name'):
        self.data = data
        self.file_name = file_name + '.pkl'

    def write(self):
        with open(self.file_name, "wb") as file_handler:
            file_handler.write(pickle.dumps(self.data))
        return True


class ReaderPKL:
    def __init__(self, file_pkl=None):
        self.file_pkl = file_pkl

    def read(self):
        with open(self.file_pkl, "rb") as file_handler:
            data_tuple = pickle.load(file_handler)
        return data_tuple
