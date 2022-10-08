import logging
import os
from PyQt5.QtWidgets import QApplication
import sys
import multiprocessing as mp
from main_gui import MainGUI
import time


def main():
    mp.freeze_support()
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename=f"logs\\CPMGUI_{int(time.time())}.log", level=logging.NOTSET)
    logging.root.setLevel(logging.NOTSET)
    log = logging.getLogger("cpmlog")
    log.info("Starting CPM GUI")

    app = QApplication([])
    ex = MainGUI(log)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
