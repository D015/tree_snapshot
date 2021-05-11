import operator
import os
import pickle
from typing import Union, Optional, List, Tuple, Dict

empty_directory_size = 4096

directory_sample_dict = \
    {
        '/':
            {'subdirectory': {}, 'files': {}, 'specifications':
                {
                    'directory_size': 0,
                    'directory_resize': 0,
                    'subdirectory_size': 0,
                    'subdirectory_resize': 0,
                    'file_size': 0,
                    'file_resize': 0
                }

             }
    }


def converting_tree_item_tuple_to_dict(tree_item_tuple):
    directory, subdirectories, files = tree_item_tuple
    tree_item_dict = {
        directory: {
            'subdirectories': subdirectories,
            'files': files
        }
    }
    return tree_item_dict


def get_dict_of_resized_files_by_remove_keys_from_set(the_dict: dict,
                                                      the_set: set,
                                                      created: bool = True):
    direction_of_created = 1 if created is True else -1
    resized_files_dict = {'files': {},
                          'specifications': {'file_size': 0, 'file_resize': 0}}
    if the_dict and the_set:
        for key in the_set:
            if key in the_dict:
                value = the_dict.pop(key)
                the_file_size = value if created else 0
                the_file_resize = value * direction_of_created
                resized_files_dict['files'].update(
                    {key: {'size': the_file_size, 'resize': the_file_resize}})

                resized_files_dict['specifications']['file_size'] += \
                    the_file_size
                resized_files_dict['specifications']['file_resize'] += \
                    the_file_resize

        if not created:
            resized_files_dict['specifications']['file_size'] = 0

    return resized_files_dict


def merge_other_directory(directory: dict, created: bool = True):
    direction_of_change = 1 if created else -1

    merging_result = {}
    for k_directory_name, v_directory_contents \
            in directory.items():

        i_subdirectories = v_directory_contents['subdirectories']
        i_files = v_directory_contents['files']

        i_directory_dict = \
            {
                k_directory_name:
                    {
                        'subdirectories': {},
                        'files': {},
                        'specifications':
                            {
                                'directory_size': 0,
                                'directory_resize': 0,
                                'subdirectory_size': 0,
                                'subdirectory_resize': 0,
                                'file_size': 0,
                                'file_resize': 0
                            }
                    }
            }

        if i_subdirectories:
            for i_subdirectory_name in i_subdirectories:
                i_subdirectory_dict = \
                    {
                        i_subdirectory_name:
                            {
                                'size': empty_directory_size,
                                'resize':
                                    empty_directory_size * direction_of_change
                            }
                    }

                i_directory_dict[k_directory_name]['subdirectories']. \
                    update(i_subdirectory_dict)

            subdirectory_size = len(i_subdirectories) * empty_directory_size
            i_directory_dict[
                k_directory_name]['specifications']['subdirectory_size'] = \
                subdirectory_size
            i_directory_dict[
                k_directory_name]['specifications']['subdirectory_resize'] += \
                subdirectory_size * direction_of_change

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

                i_directory_dict[
                    k_directory_name]['specifications']['file_size'] += \
                    f_i_file[1]
                i_directory_dict[
                    k_directory_name]['specifications']['file_resize'] += \
                    f_i_file[1] * direction_of_change

                i_directory_dict[k_directory_name]['files']. \
                    update(f_i_file_dict)

        i_directory_dict[
            k_directory_name]['specifications']['directory_size'] = \
            i_directory_dict[
                k_directory_name]['specifications']['subdirectory_size'] \
            + i_directory_dict[
                k_directory_name]['specifications']['file_size']

        i_directory_dict[
            k_directory_name]['specifications']['directory_resize'] = \
            i_directory_dict[
                k_directory_name]['specifications']['subdirectory_resize'] \
            + i_directory_dict[
                k_directory_name]['specifications']['file_resize']

        merging_result.update(i_directory_dict)
    return merging_result


def merge_modified_directory(modified_start_directories,
                             modified_end_directories):
    merging_result = {}
    for k_directory_name, v_end_directory_content \
            in modified_end_directories.items():
        v_start_directory_content = modified_start_directories[k_directory_name]

        merged_subdirectories = merge_subdirectories_from_modified_directory(
            v_start_directory_content['subdirectories'],
            v_end_directory_content['subdirectories'])

        merged_files = merge_files_from_modified_directory(
            v_start_directory_content['files'],
            v_end_directory_content['files'])

        directory_size = \
            merged_subdirectories['specifications']['subdirectories_size'] + \
            merged_files['specifications']['file_size']

        directory_resize = \
            merged_subdirectories['specifications']['subdirectories_resize'] + \
            merged_files['specifications']['file_resize']

        i_specifications = {
            'directory_size': directory_size,
            'directory_resize': directory_resize,
            'subdirectories_size':
                merged_subdirectories['specifications']['subdirectories_size'],
            'subdirectories_resize':
                merged_subdirectories['specifications'][
                    'subdirectories_resize'],
            'file_size': merged_files['specifications']['file_size'],
            'file_resize': merged_files['specifications']['file_resize']}

        merging_result.update({k_directory_name: {
            'files': merged_files['files'],
            'subdirectories': merged_subdirectories['subdirectories'],
            'specifications': i_specifications
        }})
    return merging_result


def merge_files_from_modified_directory(start_files: tuple, end_files: tuple):
    files_from_modified_directory = \
        {'files': {}, 'specifications': {'file_size': 0, 'file_resize': 0}}

    difference_start_dict = dict(set(start_files) - set(end_files))
    difference_end_dict = dict(set(end_files) - set(start_files))
    # Identical_files
    identical_files_set = set(start_files) & (set(end_files))
    identical_files_dict = {}
    for k_file_names, v_file_size in identical_files_set:
        identical_files_dict.update({k_file_names: {'size': v_file_size,
                                                    'resize': 0}})

    files_from_modified_directory['files'].update(identical_files_dict)
    files_from_modified_directory['specifications']['file_size'] = \
        sum([x[1] for x in identical_files_set])
    # Deleted file names
    deleted_file_names_set = \
        set(difference_start_dict) - set(difference_end_dict)
    # Deleted files
    deleted_files_dict = get_dict_of_resized_files_by_remove_keys_from_set(
        difference_start_dict, deleted_file_names_set, created=False)
    # Removed items of deleted files from difference_start_dict
    resized_start_files_dict = difference_start_dict
    if deleted_files_dict['files']:
        files_from_modified_directory['files'].update(
            deleted_files_dict['files'])

        files_from_modified_directory['specifications']['file_resize'] += \
            (deleted_files_dict['specifications']['file_resize'])
    # Created file names
    created_file_names_set = \
        set(difference_end_dict) - set(difference_start_dict)
    # Created files
    created_files_dict = get_dict_of_resized_files_by_remove_keys_from_set(
        difference_end_dict, created_file_names_set, created=True)
    # Removed items of created files from created_start_dict
    resized_end_files_dict = difference_end_dict
    if created_files_dict['files']:
        files_from_modified_directory['files'].update(
            created_files_dict['files'])

        files_from_modified_directory['specifications']['file_size'] += \
            (created_files_dict['specifications']['file_size'])

        files_from_modified_directory['specifications']['file_resize'] += \
            (created_files_dict['specifications']['file_resize'])
    # Resized file
    for key in resized_end_files_dict:
        size = resized_end_files_dict[key]
        resize = size - resized_start_files_dict[key]
        files_from_modified_directory['files'].update(
            {key: {'size': size, 'resize': resize}})
        files_from_modified_directory['specifications']['file_size'] += size
        files_from_modified_directory['specifications']['file_resize'] += resize

    return files_from_modified_directory


def merge_subdirectories_from_modified_directory(start_subdirectories: tuple,
                                                 end_subdirectories: tuple):
    subdirectories_from_modified_directory = \
        {'subdirectories': {}, 'specifications': {'subdirectories_size': 0,
                                                  'subdirectories_resize': 0}}

    difference_start_set = set(start_subdirectories) - (set(end_subdirectories))

    difference_end_set = set(end_subdirectories) - (set(start_subdirectories))
    # Identical_subdirectories
    identical_subdirectories_set = \
        set(start_subdirectories) & (set(end_subdirectories))

    for i_subdirectory_names in identical_subdirectories_set:
        subdirectories_from_modified_directory['subdirectories'].update(
            {i_subdirectory_names: {'size': empty_directory_size,
                                    'resize': 0}})

    subdirectories_from_modified_directory[
        'specifications']['subdirectories_size'] += \
        len(identical_subdirectories_set) * empty_directory_size

    # Deleted subdirectories
    for i_subdirectory_names in difference_start_set:
        subdirectories_from_modified_directory['subdirectories'].update(
            {i_subdirectory_names: {'size': 0,
                                    'resize': -empty_directory_size}})
    subdirectories_from_modified_directory[
        'specifications']['subdirectories_resize'] -= \
        len(difference_start_set) * empty_directory_size

    # Created subdirectories
    for i_subdirectory_names in difference_end_set:
        subdirectories_from_modified_directory['subdirectories'].update(
            {i_subdirectory_names: {'size': empty_directory_size,
                                    'resize': empty_directory_size}})
    subdirectories_size = len(difference_end_set) * empty_directory_size
    subdirectories_from_modified_directory[
        'specifications']['subdirectories_size'] += subdirectories_size

    subdirectories_from_modified_directory[
        'specifications']['subdirectories_resize'] += subdirectories_size

    return subdirectories_from_modified_directory


# todo (mentor) typing and validating the argument with the return False (isn't it superfluous?)
# todo (mentor) типизация и проверка аргумента с возвратом False (это не лишнее?)
# todo copy to global utilities
def sort_dictionary_by_keys_into_list(
        dictionary: Dict) -> Union[List[Tuple], bool]:
    if type(dictionary) is dict:
        if dictionary:
            sorted_dictionary = sorted(dictionary.items(),
                                       key=operator.itemgetter(0))
            return sorted_dictionary
        else:
            return [tuple()]
    return False


class WriterPKL:
    def __init__(self, data: tuple = '/', file_name='no_name'):
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
