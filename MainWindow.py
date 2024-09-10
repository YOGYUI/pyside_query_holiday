from PySide6.QtWidgets import (QMainWindow, QPushButton, QLineEdit, QSpinBox, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QVBoxLayout, QHBoxLayout, QGroupBox)
from Functions import query_holidays_dataframe


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        pass

    def initControl(self):
        pass


if __name__ == '__main__':
    pass
