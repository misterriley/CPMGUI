from PyQt5.QtWidgets import QApplication
import sys

from common.main_gui import MainGUI


def main():
    app = QApplication([])
    ex = MainGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
