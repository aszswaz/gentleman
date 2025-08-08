from PySide6 import QtWidgets


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 工具栏


def start():
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    exit(app.exec())
