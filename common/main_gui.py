import multiprocessing
import os.path
import traceback

from PyQt5.QtWidgets import QMainWindow, QTableWidget, QWidget, QVBoxLayout, QTabWidget, QFormLayout, \
    QGridLayout, QPushButton, QLineEdit, QCheckBox, QComboBox, QLabel, QFileDialog, QMessageBox, \
    QTextBrowser

from run_cpm import CPMRunner
from cpm_data import CPMData
import documentation

last_file_path = None
auto_run = False


def get_text_from_object(obj):
    if obj.text() == '':
        return None
    else:
        return obj.text().strip()


def get_int_from_object(obj, object_descriptor):
    if obj.text() == '':
        return None
    else:
        try:
            return int(obj.text())
        except ValueError:
            raise ValueError('Invalid value for {}: {}'.format(object_descriptor, obj.text()))


class MainGUI(QMainWindow):

    def __init__(self, log):
        super().__init__()
        if not os.path.exists("logs"):
            os.makedirs("logs")

        self.setWindowTitle("CPM GUI")
        self.setGeometry(100, 100, 485, 300)

        self.cw = CentralWidget(self)
        self.setCentralWidget(self.cw)
        self.show()
        self.run_actually = False
        self.log = log
        self.set_default_values()

    def set_default_values(self):
        pass

    def show_run_check_dialog(self, cpm_data):
        global auto_run
        if auto_run:
            self.run_actually = True
            return
        dialog = QMessageBox(self)
        dialog.setText("Run CPM with these settings?\n" + cpm_data.get_summary())
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog.buttonClicked.connect(self.dialog_clicked)
        dialog.exec_()

    def dialog_clicked(self, button):
        self.run_actually = button.text() == "OK"

    def run(self):
        self.cw.run_tab.run_button.setText("Running...")
        self.cw.run_tab.run_button.setEnabled(False)
        self.cw.run_tab.run_button.repaint()

        try:
            cpm_data = CPMData(t=self.cw.get_t(), log_name=self.log.name, k=self.cw.get_k(),
                               p_thresh=self.cw.get_p_thresh(),
                               repeat=self.cw.get_num_repeats(), num_iter=self.cw.get_num_permuted_repeats(),
                               x_mat_path=self.cw.get_x_mat_path(), x_mat_name=self.cw.get_x_mat_name(),
                               x_name_in_mat=self.cw.get_x_name_in_mat(),
                               y_mat_path=self.cw.get_y_mat_path(), y_mat_name=self.cw.get_y_mat_name(),
                               y_name_in_mat=self.cw.get_y_name_in_mat(),
                               subj_key_mat_path=self.cw.get_subject_key_path(),
                               subj_key_mat_name=self.cw.get_subject_key_name(),
                               subj_key_name_in_mat=self.cw.get_subject_key_name_in_mat(),
                               zscore=self.cw.get_zscore(),
                               mode=self.cw.get_mode(), base_dir=self.cw.get_base_dir(), jobs=self.cw.get_jobs())
            self.show_run_check_dialog(cpm_data)
            if not self.run_actually:
                return
            cpm_runner = CPMRunner(cpm_data)
            cpm_runner.run(self.log)
            self.show_message_dialog("CPM run complete. Check most recent log for details. "
                                     "Files saved to {}".format(os.path.abspath(cpm_data.get_out_path())))
        except AssertionError as e:
            self.show_message_dialog("Unable to run CPM: " + e.args[0], QMessageBox.Critical)
        except Exception as e:
            self.show_message_dialog("Unable to run CPM due to unexpected Exception. "
                                     "Please check most recent log file. Shutting down.", QMessageBox.Critical)
            self.log.error(traceback.format_exc())
            print(traceback.format_exc())
            raise e
        finally:
            self.cw.run_tab.run_button.setText("Run")
            self.cw.run_tab.run_button.setEnabled(True)

    def show_message_dialog(self, message, icon=QMessageBox.Information):
        dialog = QMessageBox(self)
        dialog.setText(message)
        dialog.setIcon(icon)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()


class InputTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.x_row = FileSelectRow(self, 0, "Connectivity Matrices File:",
                                   "Connectivity Matrices Variable Name:", "")
        self.y_row = FileSelectRow(self, 2,
                                   "Behavioral Data File:",
                                   "Behavioral Variable Name:", "")
        self.subj_key_row = FileSelectRow(self, 4, "Subject Key File:",
                                          "Subject Key Variable Name:", "")

        self.add_row(self.x_row)
        self.add_row(self.y_row)
        self.add_row(self.subj_key_row)

    def add_row(self, file_select_row):
        self.layout.addWidget(QLabel(file_select_row.file_descriptor), file_select_row.row_index, 0)
        self.layout.addWidget(file_select_row.browse_button, file_select_row.row_index, 2)
        self.layout.addWidget(file_select_row.file_label, file_select_row.row_index, 1)
        self.layout.addWidget(QLabel(file_select_row.variable_descriptor), file_select_row.row_index + 1, 0)
        self.layout.addWidget(file_select_row.variable_name_line_edit, file_select_row.row_index + 1, 1, 1, 2)

    def get_x_mat_path(self):
        return self.x_row.get_file_path()

    def get_x_mat_name(self):
        return self.x_row.get_mat_name()

    def get_x_name_in_mat(self):
        return self.x_row.get_var_name()

    def get_y_mat_path(self):
        return self.y_row.get_file_path()

    def get_y_mat_name(self):
        return self.y_row.get_mat_name()

    def get_y_name_in_mat(self):
        return self.y_row.get_var_name()

    def get_subject_key_path(self):
        return self.subj_key_row.get_file_path()

    def get_subject_key_name(self):
        return self.subj_key_row.get_mat_name()

    def get_subject_key_name_in_mat(self):
        return self.subj_key_row.get_var_name()


class FileSelectRow(QWidget):
    def __init__(self, parent, row_index, file_descriptor, variable_descriptor, default_variable_value):
        super().__init__(parent)
        self.row_index = row_index
        self.file_descriptor = file_descriptor
        self.variable_descriptor = variable_descriptor
        self.browse_button = QPushButton("Browse")
        self.file_label = QLabel("None")
        self.variable_name_line_edit = QLineEdit(default_variable_value)
        self.browse_button.clicked.connect(self.browse_button_clicked)

    def get_file_path(self):
        text = get_text_from_object(self.file_label)
        if text is None or text == "None":
            return None

        if os.path.isdir(text):
            return text
        else:
            return os.path.dirname(text)

    def browse_button_clicked(self):
        global last_file_path
        if last_file_path is None:
            last_file_path = "."
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            last_file_path, "CPM Data Files (*.xlsx *.csv *.txt *.mat)")
        self.file_label.setText(fname[0])
        last_file_path = os.path.dirname(fname[0])

    def get_mat_name(self):
        text = get_text_from_object(self.file_label)
        if text is None or text == "None":
            return None
        return os.path.basename(text)

    def get_var_name(self):
        return get_text_from_object(self.variable_name_line_edit)


def get_float_from_object(obj, object_descriptor):
    if obj.text() == '':
        return None
    else:
        try:
            return float(obj.text())
        except ValueError:
            raise ValueError('Invalid value for {}: {}'.format(object_descriptor, obj.text()))


class ParametersTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QFormLayout(self)
        self.setLayout(self.layout)

        self.t_line_edit = QLineEdit("1")
        self.k_folds_line_edit = QLineEdit("10")
        self.p_thresh_line_edit = QLineEdit("0.05")
        self.num_repeats_line_edit = QLineEdit("100")
        self.num_permuted_repeats_line_edit = QLineEdit("100")
        self.zscore_checkbox = QCheckBox()
        self.mode_combo_box = QComboBox()
        self.mode_combo_box.addItems(["linear", "ridge", "logistic"])
        self.jobs_line_edit = QLineEdit(str(max(1, int(multiprocessing.cpu_count() / 3))))

        self.layout.addRow("Time index:", self.t_line_edit)
        self.layout.addRow("K folds", self.k_folds_line_edit)
        self.layout.addRow("P threshold", self.p_thresh_line_edit)
        self.layout.addRow("Repeats", self.num_repeats_line_edit)
        self.layout.addRow("Permuted repeats", self.num_permuted_repeats_line_edit)
        self.layout.addRow("Z-score", self.zscore_checkbox)
        self.layout.addRow("Mode", self.mode_combo_box)
        self.layout.addRow("Jobs", self.jobs_line_edit)

    def get_t(self):
        return get_int_from_object(self.t_line_edit, "Time index")

    def get_k(self):
        return get_int_from_object(self.k_folds_line_edit, "K folds")

    def get_p_thresh(self):
        return get_float_from_object(self.p_thresh_line_edit, "P threshold")

    def get_num_repeats(self):
        return get_int_from_object(self.num_repeats_line_edit, "Repeats")

    def get_num_permuted_repeats(self):
        return get_int_from_object(self.num_permuted_repeats_line_edit, "Permuted repeats")

    def get_zscore(self):
        return self.zscore_checkbox.isChecked()

    def get_mode(self):
        return self.mode_combo_box.currentText()

    def get_jobs(self):
        return get_int_from_object(self.jobs_line_edit, "Jobs")


class OutputsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.base_dir_label = QLabel("./output")
        self.layout.addWidget(QLabel("Output Directory"), 0, 0)
        self.layout.addWidget(self.base_dir_label, 0, 1)
        self.base_dir_button = QPushButton("Browse")
        self.base_dir_button.clicked.connect(self.base_dir_button_clicked)
        self.layout.addWidget(self.base_dir_button, 0, 2)

    def base_dir_button_clicked(self):
        fname = QFileDialog.getExistingDirectory(self, 'Select output directory',
                                                 ".")
        self.base_dir_label.setText(fname)

    def get_base_dir(self):
        return get_text_from_object(self.base_dir_label)


class RunTab(QWidget):
    def __init__(self, parent, main_gui):
        super().__init__(parent)
        self.main_gui = main_gui
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.run_button = QPushButton("Run")
        self.layout.addWidget(self.run_button, 0, 0)
        self.run_button.clicked.connect(self.run)

    def run(self):
        self.main_gui.run()


class DocumentationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.text_browser = QTextBrowser()
        self.layout.addWidget(self.text_browser)
        self.text_browser.setHtml(documentation.documentation)


class CentralWidget(QTableWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.input_tab = InputTab(self)
        self.params_tab = ParametersTab(self)
        self.outputs_tab = OutputsTab(self)
        self.run_tab = RunTab(self, parent)
        self.documentation_tab = DocumentationTab()

        self.tabs.addTab(self.input_tab, "Inputs")
        self.tabs.addTab(self.params_tab, "Parameters")
        self.tabs.addTab(self.outputs_tab, "Outputs")
        self.tabs.addTab(self.run_tab, "Run")
        self.tabs.addTab(self.documentation_tab, "Documentation")
        self.layout.addWidget(self.tabs)

    def get_t(self):
        return self.params_tab.get_t()

    def get_k(self):
        return self.params_tab.get_k()

    def get_p_thresh(self):
        return self.params_tab.get_p_thresh()

    def get_num_repeats(self):
        return self.params_tab.get_num_repeats()

    def get_num_permuted_repeats(self):
        return self.params_tab.get_num_permuted_repeats()

    def get_x_mat_path(self):
        return self.input_tab.get_x_mat_path()

    def get_x_mat_name(self):
        return self.input_tab.get_x_mat_name()

    def get_x_name_in_mat(self):
        return self.input_tab.get_x_name_in_mat()

    def get_y_mat_path(self):
        return self.input_tab.get_y_mat_path()

    def get_y_mat_name(self):
        return self.input_tab.get_y_mat_name()

    def get_y_name_in_mat(self):
        return self.input_tab.get_y_name_in_mat()

    def get_subject_key_path(self):
        return self.input_tab.get_subject_key_path()

    def get_subject_key_name(self):
        return self.input_tab.get_subject_key_name()

    def get_subject_key_name_in_mat(self):
        return self.input_tab.get_subject_key_name_in_mat()

    def get_zscore(self):
        return self.params_tab.get_zscore()

    def get_mode(self):
        return self.params_tab.get_mode()

    def get_base_dir(self):
        return self.outputs_tab.get_base_dir()

    def get_jobs(self):
        return self.params_tab.get_jobs()
