from PyQt6.QtCore import Qt, QtMsgType, qInstallMessageHandler    
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette
from PyQt6.QtWidgets import (QApplication, QWidget, 
                            QGridLayout, QPushButton, 
                            QLabel)

class GridWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Создаем QGridLayout
        grid = QGridLayout()
        
        title = QLabel()
        title.setPixmap(QPixmap('data/title.png'))
        title.setScaledContents(True)
        
        ex = QLabel()
        ex.setPixmap(QPixmap('data/exitButton.png'))
        ex.setScaledContents(True)
        ex.setFixedSize(220, 220)
        
        grid.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)       # Строка 1, Колонка 1
        grid.addWidget(ex, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)  # Строка 0, Колонка 1
        
        # Настройка растяжения
        #grid.setColumnStretch(1, 2)  # Колонка 1 растягивается в 2 раза сильнее
        
        self.setLayout(grid)
        self.setWindowTitle("Пример QGridLayout")

    def handle_qt_messages(msg_type, context, message):  #QPainter ругается из-за QPixmap в setup_mainMenu, поэтому таким незамысловатым образом мы пропускаем эту ошибку. 
        if msg_type == QtMsgType.QtWarningMsg:
            return  # Игнорируем предупреждения
        print(message)  # Выводим остальные сообщения
    qInstallMessageHandler(handle_qt_messages)
    
app = QApplication([])
window = GridWindow()
window.showMaximized()
app.exec()