
import numpy as np
import pandas as pd
import sys
import scipy.io as sio
import mat73
from scipy.io.matlab.mio5_params import MatlabOpaque
from sklearn.preprocessing import PowerTransformer, FunctionTransformer, StandardScaler


# CURRENTLY NOT USED
def save_run_outputs_subsample_nogrid(out_path, iter_, outputs, y):
    """
    Save run outputs for subsample CPM
    :param out_path: output path
    :type out_path: string
    :param iter_: iteration number
    :type iter_: int
    :param outputs: outputs of kfold_cpm_subsample
    :type outputs: dict
    :param y: actual target behavioral data
    :type y: numpy array (n,)
    :return: None
    :rtype: None
    """
    for fold, (network_p, network_n) in enumerate(zip(outputs['edges_p'], outputs['edges_n'])):
        np.savetxt('{}/positive_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_p,
                   fmt='%d')
        np.savetxt('{}/negative_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_n,
                   fmt='%d')

    df_y_predict = pd.DataFrame(columns=['y_pred_both', 'y_actual'])
    df_y_predict['y_pred_both'] = outputs['y_pred_both'].flatten()
    df_y_predict['y_actual'] = y
    df_y_predict.to_csv('{}/y_prediction_iter{}.csv'.format(out_path, iter_))

    df_fit = pd.DataFrame(columns=['both_m', 'both_b'],
                          index=['fold {}'.format(x + 1) for x in range(len(outputs['fit_b']))])
    df_fit['both_m'] = [fit.coef_[0][0] for fit in outputs['fit_b']]
    df_fit['both_b'] = [fit.intercept_[0] for fit in outputs['fit_b']]
    df_fit.to_csv('{}/fit_parameters_iter{}.csv'.format(out_path, iter_))
    return None


# CURRENTLY NOT USED
def save_run_outputs_subsample(out_path, iter_, outputs, y):
    """
    Save run outputs for subsample CPM
    :param out_path: output path
    :type out_path: string
    :param iter_: iteration number
    :type iter_: int
    :param outputs: outputs of kfold_cpm_subsample
    :type outputs: dict
    :param y: actual target behavioral data
    :type y: numpy array (n,)
    :return: None
    :rtype: None
    """
    for fold, (network_p, network_n) in enumerate(zip(outputs['edges_p'], outputs['edges_n'])):
        np.savetxt('{}/positive_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_p,
                   fmt='%d')
        np.savetxt('{}/negative_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_n,
                   fmt='%d')

    df_y_predict = pd.DataFrame(columns=['y_pred_both', 'y_actual'])
    df_y_predict['y_pred_both'] = outputs['y_pred_both'].flatten()
    df_y_predict['y_actual'] = y
    df_y_predict.to_csv('{}/y_prediction_iter{}.csv'.format(out_path, iter_))

    df_fit = pd.DataFrame(columns=['both_m', 'both_b'],
                          index=['fold {}'.format(x + 1) for x in range(len(outputs['fit_b']))])
    df_fit['both_m'] = [fit.coef_[0][0] for fit in outputs['fit_b']]
    df_fit['both_b'] = [fit.intercept_[0] for fit in outputs['fit_b']]
    df_fit.to_csv('{}/fit_parameters_iter{}.csv'.format(out_path, iter_))

    for fold, dict_best_params in enumerate(outputs['best_params']):
        df_params = pd.DataFrame(columns=list(dict_best_params.keys()), index=['fold {}'.format(fold + 1)])
        for param in list(dict_best_params.keys()):
            df_params[param] = dict_best_params[param]
        df_params.to_csv('{}/best_params_iter{}_fold_{}.csv'.format(out_path, iter_, fold + 1))
    return None


# CURRENTLY NOT USED
def y_transform(y, log, y_norm='id'):
    """
    normalize all behavioral data
    :param y: list of all behavioral data, (n_subj,)
    :type y: numpy array
    :param y_norm: normalization method
    :type y_norm: 'id', 'yj', or 'norm'
    :return:
        yn: normalized list of all behavioral data, (n_subj,)
        transformer: trained transformer
    :rtype: (list of floats, sklearn object)
    """
    y = y.reshape(-1, 1)
    if y_norm == 'yj':
        transformer = PowerTransformer(method='yeo-johnson', standardize=True)
        transformer.fit(y)
        yn = transformer.transform(y)
    elif y_norm == 'id':
        transformer = FunctionTransformer()  # identity function
        transformer.fit(y)
        yn = transformer.transform(y)
    elif y_norm == 'norm':
        transformer = StandardScaler()  # identity function
        transformer.fit(y)
        yn = transformer.transform(y)
    else:
        log.warning("WARNING: undefined y_norm {}. Use identity function instead.".format(y_norm))
        transformer = FunctionTransformer()  # identity function
        transformer.fit(y)
        yn = transformer.transform(y)

    yn = yn.reshape(-1, )
    return yn, transformer


# CURRENTLY NOT USED
def save_matlab_mat(path, matname, x, y, lst_subj):
    """
    save mdict to matlab .mat file.
    :param path: path to output file.
    :type path: string.
    :param matname: name of the output .mat file.
    :type matname: string.
    :param x: stacked feature matrix of size (v, v, n) where v is the number of nodes, and n is the number of subjects.
    :type x: Numpy Array.
    :param y: true behavioral data of size (n,).
    :type y: Numpy Array.
    :param lst_subj: list of subject keys.
    :type lst_subj: list of strings.
    :return: None
    :rtype: None
    """
    mdict = {"x": x, "y": y, "subjectkey": lst_subj}
    sio.savemat("{}/{}".format(path, matname), mdict)
    return None


def file_to_dict(directory, mat_txt_or_csv_file, log):
    """
    convert a .mat, .txt, or .csv file to a dictionary.
    :param mat_txt_or_csv_file: path to .mat, .txt, or .csv file.
    :type mat_txt_or_csv_file: string.
    :return: dictionary of the file.
    :rtype: dictionary.
    """
    if mat_txt_or_csv_file is None:
        return None

    file = "{}/{}".format(directory, mat_txt_or_csv_file)

    if file.endswith('.mat'):
        try:
            return sio.loadmat(file)
        except NotImplementedError:
            return mat73.loadmat(file)
    elif file.endswith('.txt'):
        return np.loadtxt(file)
    elif file.endswith('.csv'):
        return pd.read_csv(file)
    elif file.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        log.warning("WARNING: file_to_dict only accepts .mat, .txt, or .csv files. {} is not supported.".format(
            file.split('.')[-1]))
        return None


def read_matlab_mat(cpm_data, log):
    """
    Read matlab .mat files and return x, y
    :param cpm_data: object containing CPM data
    :type cpm_data: CPMData object
    :param log: logger for writing to log file
    :type log: logging object
    :return:
        x: stacked feature matrix of size (v, v, n) where v is the number of nodes, and n is the number of subjects.
        y: true behavioral data of size (n,).
        lst_subjectkey: list of subject keys.
    :rtype: (NumPy Array, NumPy Array, list of strings)
    """
    mdict_x = file_to_dict(cpm_data.x_mat_path, cpm_data.x_mat_name, log)
    if cpm_data.x_name_in_mat is None:
        keylist = list(mdict_x.keys())
        try:
            keylist.remove('__header__')
            keylist.remove('__version__')
            keylist.remove('__globals__')
        except ValueError:
            # one or more of these isn't here
            pass

        if len(keylist) == 1:
            x = mdict_x[keylist[0]]
        else:
            raise ValueError("x_name_in_mat is not specified and there are multiple variables in this file. "
                             "Please specify the name of the variable in the .mat file.")
    else:
        x = mdict_x[cpm_data.x_name_in_mat]

    if len(x.shape) == 4:
        x = x[:, :, :, cpm_data.t - 1].squeeze()

    if cpm_data.y_mat_name is None:
        mdict_y = mdict_x
    else:
        mdict_y = file_to_dict(cpm_data.y_mat_path, cpm_data.y_mat_name, log)

    if cpm_data.y_name_in_mat is None:
        y = mdict_y
        if isinstance(y, dict):
            keylist = list(y.keys())
            try:
                keylist.remove('__header__')
                keylist.remove('__version__')
                keylist.remove('__globals__')
                keylist.remove('__function_workspace__')
            except ValueError:
                # one or more of these isn't here
                pass

            assert len(keylist) == 1, "y_name_in_mat is not specified and there are multiple variables in this file. "
            "Please specify the name of the variable in the .mat file."
            y = y[keylist[0]]
            assert not isinstance(y, MatlabOpaque), "python cannot read this type of file. Please save without class information or convert to .csv or .txt."
        elif isinstance(y, pd.DataFrame):
            y = y.values
            assert y.shape[1] == 1, "y_name_in_mat is not specified and there are multiple variables in this file. "
    else:
        assert cpm_data.y_name_in_mat in mdict_y.keys(), "y_name_in_mat is not in the .mat file."
        y = mdict_y[cpm_data.y_name_in_mat]

    assert y is not None, "no behavioral data found."
    if len(y.shape) > 1:
        y = y.squeeze()

    assert not any([isinstance(y_val, str) for y_val in y]), "y contains strings. Please convert to numbers."

    if cpm_data.subj_key_mat_name is None:
        mdict_subj = mdict_x
    else:
        mdict_subj = file_to_dict(cpm_data.subj_key_mat_path, cpm_data.subj_key_mat_name, log)

    if cpm_data.subj_key_name_in_mat is None:
        lst_subjectkey = [str(x) for x in range(1, y.shape[0] + 1)]
    else:
        lst_subjectkey = mdict_subj[cpm_data.subj_key_name_in_mat]
    return x, y, lst_subjectkey


def check_symmetric(a, rtol=1e-05, atol=1e-08):
    """
    Check symmetry of input matrix.
    :param a: input matrix.
    :type a: NumPy 2D Array.
    :param rtol: relative tolerance.
    :type rtol: float.
    :param atol: absolute tolerance.
    :type atol: float.
    :return: True or False
    :rtype: Boolean
    """
    return np.allclose(a, a.T, rtol=rtol, atol=atol, equal_nan=True)


# CURRENTLY NOT USED
def generate_file_list(path, lst_subj, num_roi, num_contrasts, t):
    """
    Generate list of files, where each file contains a single subject connectivity matrix.
    The files should have been generated by analysis_ABCD/make_coactivation_matrix.ipynb.
    :param path: path to where correlation matrices are saved.
    :type path: string.
    :param lst_subj: list of ABCD subjectkey.
    :type lst_subj: list of strings.
    :param num_roi: number of ROIs in the coactivation matrices
    :type num_roi: int
    :param num_contrasts: number of contrasts used to create coactivation matrices
    :type num_contrasts: int
    :param t: time point (bsl or y2).
    :type t: string.
    :return: list of files.
    :rtype: list of strings.
    """
    fn_list = []
    for subj in lst_subj:
        fn_list.append('{}/{}_{}ROI_{}contrasts_corr_matrix_{}.txt'.format(path, subj, num_roi, num_contrasts, t))
    return fn_list


# CURRENTLY NOT USED
def read_mats(fn_list):
    """
    Read list of single-subject connectivity matrix and return stacked matrices.
    :param fn_list: list of files, where each contains a single subject connectivity matrix.
    :type fn_list: list of strings.
    :return: stacked matrix of size (v, v, n), where v is the number of nodes, and n is the number of subjects.
    :rtype: Numpy Array.
    """
    fns = [pd.read_csv(fn, sep=' ', header=None) for fn in fn_list]
    if sum([df.isnull().values.any() for df in fns]) != 0:  # check for NaN
        sys.exit("ERROR: there are NaNs in the correlation matrices! Please check your data.")
    fns = [df.values for df in fns]
    fn_mats = np.stack(fns, axis=2)  # join the (v, v) arrays on a new axis (the third axis)
    return fn_mats


def return_estimator_coef(est, mode, log):
    """
    Return coefficients of an estimator.
    :param est: trained estimator
    :type est: a sklearn estimator, or np.nan
    :param mode: what function to use when determining edges. 'linear' or 'ridge'.
    :type mode: string
    :return: all related parameters to the estimator
    :rtype: floats
    """
    if mode == 'linear' or mode == 'logistic':
        if isinstance(est, float):  # if the estimator is np.nan
            return [np.nan, np.nan]
        else:
            return [est.coef_[0][0], est.intercept_[0]]
    elif mode == 'ridge':
        if isinstance(est, float):
            return [np.nan, np.nan, np.nan]
        else:
            return [est.best_estimator_.coef_[0][0], est.best_estimator_.intercept_[0], est.best_params_['alpha']]
    else:
        log.error("ERROR: mode {} not implemented!".format(mode))
        assert False, "ERROR: mode {} not implemented!".format(mode)


def save_run_outputs(out_path, iter_, outputs, y_run, mode='linear', log=None):
    """
    Save k-fold CPM outputs.
    :param out_path: output directory.
    :type out_path: string.
    :param iter_: iteration number.
    :type iter_: integer.
    :param outputs: outputs from kfold_cpm.
    :type outputs: dict.
    :param y_run: input behav data for kfold_cpm.
    :type y_run: NumPy Array.
    :param mode: what function to use when determining edges. 'linear' or 'ridge'.
    :type mode: string
    :return: None
    :rtype: None
    """
    for fold, (network_p, network_n) in enumerate(zip(outputs['edges_p'], outputs['edges_n'])):
        np.savetxt('{}/positive_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_p,
                   fmt='%d')
        np.savetxt('{}/negative_network_from_training_iter{}_fold_{}.txt'.format(out_path, iter_, fold + 1), network_n,
                   fmt='%d')

    df_y_predict = pd.DataFrame(columns=['y_pred_pos', 'y_pred_neg', 'y_pred_both', 'y_actual'])
    df_y_predict['y_pred_pos'] = outputs['y_pred_pos']
    df_y_predict['y_pred_neg'] = outputs['y_pred_neg']
    df_y_predict['y_pred_both'] = outputs['y_pred_both']
    df_y_predict['y_actual'] = y_run
    df_y_predict.to_csv('{}/y_prediction_iter{}.csv'.format(out_path, iter_))

    df_fit = pd.DataFrame(columns=['pos_m', 'pos_b', 'neg_m', 'neg_b', 'both_m', 'both_b'],
                          index=['fold {}'.format(x + 1) for x in range(len(outputs['fit_p']))])
    df_fit['pos_m'] = [return_estimator_coef(fit, mode, log)[0] for fit in outputs['fit_p']]
    df_fit['pos_b'] = [return_estimator_coef(fit, mode, log)[1] for fit in outputs['fit_p']]
    df_fit['neg_m'] = [return_estimator_coef(fit, mode, log)[0] for fit in outputs['fit_n']]
    df_fit['neg_b'] = [return_estimator_coef(fit, mode, log)[1] for fit in outputs['fit_n']]
    df_fit['both_m'] = [return_estimator_coef(fit, mode, log)[0] for fit in outputs['fit_b']]
    df_fit['both_b'] = [return_estimator_coef(fit, mode, log)[1] for fit in outputs['fit_b']]
    if mode == 'ridge':
        df_fit['pos_alpha'] = [return_estimator_coef(fit, mode, log)[2] for fit in outputs['fit_p']]
        df_fit['neg_alpha'] = [return_estimator_coef(fit, mode, log)[2] for fit in outputs['fit_n']]
        df_fit['both_alpha'] = [return_estimator_coef(fit, mode, log)[2] for fit in outputs['fit_b']]
    df_fit.to_csv('{}/fit_parameters_iter{}.csv'.format(out_path, iter_))

    return None
