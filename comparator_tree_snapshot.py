from utils import ReaderPKL


class TreeSnapshotComparator:
    def __init__(self, start_file, end_file):
        self.start_file = start_file
        self.end_file = end_file

    def get_difference_minus_and_plus(self):
        start_data_set = set(ReaderPKL(self.start_file).read())
        end_data_set = set(ReaderPKL(self.end_file).read())
        difference_minus = start_data_set.difference(end_data_set)
        difference_plus = end_data_set.difference(start_data_set)
        comparison_results = {'difference_minus': difference_minus,
                              'difference_plus': difference_plus}
        return comparison_results

    def write_comparison_to_pkl(self):
        pass


class App:
    def __init__(self, start_file, end_file):
        self.start_file = start_file
        self.end_file = end_file

    def run(self):
        result = TreeSnapshotComparator(
            start_file=self.start_file,
            end_file=self.end_file).get_difference_minus_and_plus()

        # test
        for i_difference_minus in result['difference_minus']:
            print(i_difference_minus)
            print()
        print('===================================')
        for i_difference_plus in result['difference_plus']:
            print(i_difference_plus)


if __name__ == '__main__':
    App(start_file='tree_snapshot_20210419-141901.pkl',
        end_file='tree_snapshot_20210419-142903.pkl').run()
