import pickle
import requests
import pandas as pd
from typing import Union
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QPushButton, QLineEdit, QSpinBox, QMessageBox,
                               QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                               QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy)
from Functions import query_holidays_dataframe


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._df_result: Union[pd.DataFrame, None] = None
        self._editKey = QLineEdit()
        self._spinYear = QSpinBox()
        self._buttonQuery = QPushButton('QUERY')
        self._tableResult = QTableWidget()
        self._buttonClipboard = QPushButton('CLIPBOARD')
        self._buttonCSV = QPushButton('CSV')
        self.initControl()
        self.initLayout()
        self.updateQueryResult()

    def initLayout(self):
        central = QWidget()
        self.setCentralWidget(central)

        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)

        grbox = QGroupBox()
        grbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        vbox_gr = QVBoxLayout(grbox)
        vbox_gr.setContentsMargins(4, 6, 4, 4)
        vbox_gr.setSpacing(4)
        vbox.addWidget(grbox)

        subwgt = QWidget()
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        lbl = QLabel('API Key')
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        hbox.addWidget(lbl)
        hbox.addWidget(self._editKey)
        vbox_gr.addWidget(subwgt)

        subwgt = QWidget()
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        lbl = QLabel('Year')
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        hbox.addWidget(lbl)
        hbox.addWidget(self._spinYear)
        self._spinYear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        hbox.addWidget(QWidget())
        vbox_gr.addWidget(subwgt)

        vbox_gr.addWidget(self._buttonQuery)

        vbox.addWidget(self._tableResult)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        lbl = QLabel('EXPORT')
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        hbox.addWidget(lbl)
        hbox.addWidget(self._buttonClipboard)
        hbox.addWidget(self._buttonCSV)
        vbox.addWidget(subwgt)

    def initControl(self):
        self._spinYear.setRange(1900, 9999)
        self._spinYear.setValue(datetime.now().year)
        self._editKey.setPlaceholderText('API Key from data.go.kr')
        self._editKey.setClearButtonEnabled(True)
        self._editKey.setEchoMode(QLineEdit.Password)
        self._buttonQuery.clicked.connect(self.onClickButtonQuery)
        hlabels = ['이름', '날짜']
        self._tableResult.setColumnCount(len(hlabels))
        self._tableResult.setHorizontalHeaderLabels(hlabels)
        self._tableResult.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tableResult.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._tableResult.setAlternatingRowColors(True)
        self._buttonClipboard.clicked.connect(self.onClickButtonClipboard)
        self._buttonCSV.clicked.connect(self.onClickButtonCSV)
        self.loadAPIKeyFromLocal()

    def onClickButtonQuery(self):
        year = self._spinYear.value()
        api_key = self._editKey.text()
        self._df_result = None
        try:
            self._df_result = query_holidays_dataframe(year, api_key)
            self.storeAPIKeyToLocal()
        except ValueError as e:
            QMessageBox.warning(self, 'Exception', str(e))
        except requests.exceptions.ConnectionError as e:
            QMessageBox.warning(self, 'Exception', str(e))
        self.updateQueryResult()

    def storeAPIKeyToLocal(self):
        api_key = self._editKey.text()
        with open('./api_key.pkl', 'wb') as fp:
            pickle.dump(api_key, fp)

    def loadAPIKeyFromLocal(self):
        try:
            with open('./api_key.pkl', 'rb') as fp:
                api_key = pickle.load(fp)
            self._editKey.setText(api_key)
            self._editKey.setCursorPosition(0)
        except FileNotFoundError:
            pass

    def updateQueryResult(self):
        self._tableResult.clearContents()
        self._buttonClipboard.setEnabled(False)
        self._buttonCSV.setEnabled(False)
        if self._df_result is None:
            return

        self._tableResult.setRowCount(len(self._df_result))
        values = self._df_result.values
        for r in range(len(self._df_result)):
            for c in range(len(self._df_result.columns)):
                item = QTableWidgetItem()
                if isinstance(values[r][c], pd.Timestamp):
                    item.setText(values[r][c].strftime('%Y-%m-%d'))
                else:
                    item.setText(values[r][c])
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                self._tableResult.setItem(r, c, item)

        self._buttonClipboard.setEnabled(True)
        self._buttonCSV.setEnabled(True)

    def onClickButtonClipboard(self):
        if self._df_result is None:
            return
        self._df_result.to_clipboard(excel=True, sep='\t')

    def onClickButtonCSV(self):
        if self._df_result is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "result.csv", "CSV Files (*.csv)")
        if path:
            self._df_result.to_csv(path, sep=',')
