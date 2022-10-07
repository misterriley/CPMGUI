import multiprocessing

from datetime import datetime

class CPMData:
    """
    Store data relevant to running a CPM analysis
    """
    def __init__(self, t=1, k=10, p_thresh=0.05, repeat=100, num_iter=100, x_mat_path=None, x_mat_name=None,
                 x_name_in_mat='x', y_mat_path=None, y_mat_name=None, y_name_in_mat=None, subj_key_mat_path=None,
                 subj_key_mat_name=None, subj_key_name_in_mat=None, zscore=False, mode='linear', y_norm=None,
                 base_dir='./output', jobs=max(1, multiprocessing.cpu_count()-2)):
        """
        :param t: timepoint to run CPM on
        :param k: folds in cross-validation
        :param p_thresh: threshold for feature selection
        :param repeat: num repeats of CPM
        :param num_iter: num repeats for CPM permutation test
        :param x_mat_path: path to the file containing connectivity matrices
        :param x_mat_name: name of the file containing connectivity matrices
        :param x_name_in_mat: label of the data column containing connectivity matrices
        :param y_mat_path: path to the file containing behavioral data
        :param y_mat_name: name of the file containing behavioral data
        :param y_name_in_mat: label of the data column containing behavioral data (should be None if there is no column
        name)
        :param subj_key_mat_path: path to the file containing subject keys
        :param subj_key_mat_name: name of the file containing subject keys
        :param subj_key_name_in_mat: label of the data column containing subject keys (should be None if no subject IDs
        are available)
        :param zscore: should the data be z-scored?
        :param mode: 'linear' for linear regression, 'ridge' for ridge regression
        :param y_norm: method of norming y data (possibly deprecated)
        :param base_dir: where to save output
        :param jobs: number of parallel workers to use (defaults to 2 less than the number of available cores)
        """
        self.t = t
        self.k = k
        self.p_thresh = p_thresh
        self.repeat = repeat
        self.num_iter = num_iter

        self.x_mat_path = x_mat_path
        self.x_mat_name = x_mat_name
        self.x_name_in_mat = x_name_in_mat

        self.y_mat_path = y_mat_path
        self.y_mat_name = y_mat_name
        self.y_name_in_mat = y_name_in_mat

        self.subj_key_mat_path = subj_key_mat_path
        self.subj_key_mat_name = subj_key_mat_name
        self.subj_key_name_in_mat = subj_key_name_in_mat

        self.zscore = zscore
        self.mode = mode
        self.y_norm = y_norm
        self.base_dir = base_dir
        self.jobs = jobs
        self.today_date = datetime.today().strftime('%Y-%m-%d')

    def get_out_path(self):
        return '{}/{}_{}fold_p_thresh_{}_repeat{}_iter{}_timepoint_{}_z{}_mode_{}_mat_{}'.format(
            self.base_dir, self.today_date, self.k, self.p_thresh, self.repeat, self.num_iter, self.t, int(self.zscore),
            self.mode, self.x_mat_name[:-4])
