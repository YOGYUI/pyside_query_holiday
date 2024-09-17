if __name__ == '__main__':
    import sys
    from MainWindow import MainWindow
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QApplication.setStyle('fusion')
    mainWnd = MainWindow()
    mainWnd.show()
    app.exec()
