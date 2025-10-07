import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow)
from PyQt6.QtCore import (QtMsgType, qInstallMessageHandler)
from PyQt6.QtGui import (QIcon, QPainter, QPalette, QColor)

from game import GameInterface


def handle_qt_messages(msg_type, context, message):  #QPainter ругается из-за QPixmap в setup_mainMenu, поэтому таким незамысловатым образом мы пропускаем эту ошибку. 
    if msg_type == QtMsgType.QtWarningMsg:
        return  # Игнорируем предупреждения
    print(message)  # Выводим остальные сообщения
qInstallMessageHandler(handle_qt_messages)

class WindowMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Создаём заголовок окна, его геометрию и иконку.
        self.setWindowTitle("TANKS")
        paletTe = app.palette()
        paletTe.setColor(QPalette.ColorRole.Window, QColor("#353232"))
        self.setPalette(paletTe)
        self.setWindowIcon(QIcon('data/logo.ico'))

        self.game = GameInterface(parent=self)

        self.setCentralWidget(self.game)




if __name__ == '__main__':  # нужно чтобы программа запускалась именно из этого файла, а не из других. Типо инкапсуляция.
    app = QApplication(sys.argv)
    start = WindowMain()
    start.showFullScreen()
    app.exec()