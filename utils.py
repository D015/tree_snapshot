import os
import pickle


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

def converting_recursively_tuple_to_dict(data_tuple):
    if data_tuple == ():
        return {}
    elif type(data_tuple) == tuple:
        data_dict = {}
        for i_data_tuple in data_tuple:
            if type(i_data_tuple) == tuple:
                data_dict.update(
                    {i_data_tuple[0]:
                         converting_recursively_tuple_to_dict(i_data_tuple[1])})
            elif len(data_tuple) == 2:
                data_dict.update(
                    {data_tuple[0]:
                         converting_recursively_tuple_to_dict(data_tuple[1])})
        return data_dict
    elif type(data_tuple) != tuple:
        return data_tuple

def converting_tree_item_tuple_to_dict(tree_item_tuple):
    subdirectories = converting_recursively_tuple_to_dict(tree_item_tuple[1])
    files = converting_recursively_tuple_to_dict(tree_item_tuple[2])
    specifications = converting_recursively_tuple_to_dict(tree_item_tuple[3])
    tree_item_dict = {
        tree_item_tuple[0]: {
            'subdirectories': subdirectories,
            'files': files,
            'specifications': specifications
        }
                       }
    return tree_item_dict




class WriterPKL:
    def __init__(self, data='/', file_name='no_name'):
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