import pickle

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
    tree_item_dict = {
        tree_item_tuple[0]: {
            'subdirectories': tree_item_tuple[1],
            'files': tree_item_tuple[2],
            'specifications': tree_item_tuple[3]
        }
    }
    return tree_item_dict


def get_dict_of_other_files_by_remove_keys_from_set(the_dict: dict,
                                                    the_set: set,
                                                    created: bool = True):
    direction_of_created = 1 if created is True else -1
    other_files_dict = {'files': {},
                        'specifications': {'file_size': 0, 'file_resize': 0}}
    if the_dict and the_set:
        for key in the_set:
            if key in the_dict:
                value = the_dict.pop(key)
                the_file_size = value if created else 0
                the_file_resize = value * direction_of_created
                other_files_dict['files'].update(
                    {key: {'size': the_file_size, 'resize': the_file_resize}})

                other_files_dict['specifications']['file_size'] += the_file_size
                other_files_dict['specifications']['file_resize'] += \
                    the_file_resize

        if not created:
            other_files_dict['specifications']['file_size'] = 0

    return other_files_dict


def merge_other_directory(directory: dict, created: bool = True):
    direction_of_change = 1 if created is True else -1

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

                i_directory_dict['subdirectories'].update(i_subdirectory_dict)

            subdirectory_size = len(i_subdirectories) * empty_directory_size
            i_directory_dict['specifications']['subdirectory_size'] = \
                subdirectory_size
            i_directory_dict['specifications']['resize'] += \
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

                i_directory_dict['specifications']['file_size'] += \
                    f_i_file[1]
                i_directory_dict['specifications']['file_resize'] += \
                    f_i_file[1] * direction_of_change

                i_directory_dict['files'].update(f_i_file_dict)
        merging_result.update(i_directory_dict)
    return merging_result


def merge_modified_directory(modified_start_directories,
                             modified_end_directories):
    merging_result = {}
    for k_directory_name, v_end_directory_content in modified_end_directories:
        v_start_directory_content = modified_start_directories[k_directory_name]

        merged_subdirectories = merge_subdirectories_from_modified_directory(
            v_start_directory_content['subdirectories'],
            v_end_directory_content['subdirectories'])

        merged_files = merge_files_from_modified_directory(
            v_start_directory_content['files'],
            v_end_directory_content['files'])

        i_specifications = {
            'subdirectories_size':
                merged_subdirectories['specifications']['subdirectories_size'],
            'subdirectories_resize':
                merged_subdirectories['specifications']['subdirectories_resize'],
            'file_size': merged_files['specifications']['file_size'],
            'file_resize': merged_files['specifications']['file_resize']}

        merging_result.update({k_directory_name: {
            'files': merged_files['files'],
            'subdirectories': merged_subdirectories['subdirectories'],
            'specifications': i_specifications
        }})
    return merging_result


def merge_files_from_modified_directory(start_files: set, end_files: set):
    files_from_modified_directory = \
        {'files': {}, 'specifications': {'file_size': 0, 'file_resize': 0}}

    difference_start_dict = dict(start_files.difference(end_files))
    difference_end_dict = dict(end_files.difference(start_files))
    # Identical_files
    identical_files_set = start_files.intersection(end_files)
    identical_files_dict = {}
    for k_file_names, v_file_size in identical_files_set:
        identical_files_dict.update({k_file_names: {'size': v_file_size,
                                                    'resize': 0}})

    files_from_modified_directory['files'].update(identical_files_dict)
    files_from_modified_directory['specifications']['file_size'] = \
        sum([x[1] for x in identical_files_set])
    # Resized file names
    resized_file_names_set = \
        set(difference_start_dict).intersection(set(difference_end_dict))
    # Deleted files
    deleted_files_dict = get_dict_of_other_files_by_remove_keys_from_set(
        difference_start_dict, resized_file_names_set, created=False)
    # Removed items of deleted files from difference_start_dict
    resized_start_files_dict = difference_start_dict
    files_from_modified_directory['files'].update(deleted_files_dict['files'])

    files_from_modified_directory['specifications']['file_resize'] += \
        (deleted_files_dict['specifications']['file_resize'])
    # Created files
    created_files_dict = get_dict_of_other_files_by_remove_keys_from_set(
        difference_end_dict, resized_file_names_set, created=True)
    # Removed items of created files from created_start_dict
    resized_end_files_dict = difference_end_dict
    files_from_modified_directory['files'].update(created_files_dict['files'])

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


def merge_subdirectories_from_modified_directory(start_subdirectories: set,
                                                 end_subdirectories: set):
    subdirectories_from_modified_directory = \
        {'subdirectories': {}, 'specifications': {'subdirectories_size': 0,
                                                  'subdirectories_resize': 0}}

    difference_start_set = start_subdirectories.difference(end_subdirectories)
    difference_end_set = end_subdirectories.difference(start_subdirectories)
    # Identical_subdirectories
    identical_subdirectories_set = start_subdirectories.intersection(
        end_subdirectories)
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
