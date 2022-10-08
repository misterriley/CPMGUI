import os
from functools import partial
from multiprocessing import Pool

import numpy as np

import cpm
import utils
from cpm_data import CPMData


class CPMRunner:
    def __init__(self, cpm_data_):
        self.data = cpm_data_

    def run(self, log):
        # read run settings and output run settings

        assert self.data.t is not None, 't is not specified'
        assert self.data.k is not None, 'k is not specified'
        assert self.data.p_thresh is not None, 'p_thresh is not specified'
        assert self.data.repeat is not None, 'repeat is not specified'
        assert self.data.num_iter is not None, 'num_iter is not specified'

        assert self.data.x_mat_path is not None, 'Connectivity Matrices File is not specified'
        assert self.data.x_mat_name is not None, 'Connectivity Matrices File is not specified'
        assert self.data.y_mat_name is not None or self.data.y_name_in_mat is not None, 'Behavioral Data File is not specified'

        assert self.data.zscore is not None, 'zscore is not specified'
        assert self.data.mode is not None, 'mode is not specified'
        assert self.data.base_dir is not None, 'base_dir is not specified'
        assert self.data.jobs is not None, 'jobs is not specified'

        if not os.path.exists(self.data.get_out_path()):
            os.makedirs(self.data.get_out_path())

        with open('{}/run_settings.txt'.format(self.data.get_out_path()), 'w') as f:
            f.write('Run Date: {}\n'.format(self.data.today_date))
            f.write('Time Point: {}\n'.format(self.data.t))
            f.write('Number of folds k: {}\n'.format(self.data.k))
            f.write('P threshold: {}\n'.format(self.data.p_thresh))
            f.write('Number of repeats: {}\n'.format(self.data.repeat))
            f.write('Number of iterations: {}\n'.format(self.data.num_iter))
            f.write('Path to mat: {}\n'.format(self.data.x_mat_path))
            f.write('mat name: {}\n'.format(self.data.x_mat_name))
            f.write('z-score training edges: {}\n'.format(int(self.data.zscore)))
            f.write('mode: {}\n'.format(self.data.mode))
            f.write('y norm method: {}\n'.format(self.data.y_norm))
            f.write('Output path: {}\n'.format(self.data.get_out_path()))

        x, y, lst_subjectkey = utils.read_matlab_mat(self.data, log)
        assert x.shape[2] == y.shape[0], 'x ({}) and y ({}) have different number of subjects'.format(x.shape[2], y.shape[0])
        with open('{}/lst_subjkey_analyzed.txt'.format(self.data.get_out_path()), 'w') as f:
            for subj in lst_subjectkey:
                f.write('{}\n'.format(subj))

        lst_of_i = []
        lst_of_yrun = []
        for i in range(0, self.data.repeat + self.data.num_iter):
            lst_of_i.append(i + 1)
            if i < self.data.repeat:  # true behavioral data
                lst_of_yrun.append(y)
            else:
                y_run = np.random.permutation(y)
                lst_of_yrun.append(y_run)

        num_proc = self.data.jobs

        log.info("Using {} jobs".format(num_proc))
        pool = Pool(processes=num_proc)
        cpm_par = partial(cpm.run_cpm_thread, x=x, k=self.data.k, p_thresh=self.data.p_thresh,
                          out_path=self.data.get_out_path(), zscore=self.data.zscore, mode=self.data.mode,
                          logger_name=self.data.log_name)
        pool.starmap(cpm_par, zip(lst_of_yrun, lst_of_i))
        pool.close()
        pool.join()

        # the following code also works but sometimes have missing stdout
        # with Pool(processes=num_proc) as pool:
        #    cpm_par = partial(run_cpm_thread, x=x, k=k, out_path=out_path, p_thresh=p_thresh, zscore=zscore, mode=mode)
        #    pool.starmap(cpm_par, zip(lst_of_yrun, lst_of_i))


if __name__ == "__main__":
    cpm_data = CPMData(t=1, k=10, p_thresh=0.05, repeat=5, num_iter=5,
                       x_mat_path='G:\\My Drive\\CPM_test_data', x_mat_name='stp_all_clean2.mat',
                       x_name_in_mat='stp_all',
                       y_mat_path='G:\\My Drive\\CPM_test_data', y_mat_name='txnegop.txt',
                       zscore=False, mode='linear')
    cpm_runner = CPMRunner(cpm_data)
    cpm_runner.run()
