from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QGridLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        grid = QGridLayout(central_widget)
        
        # Центральный label
        screen = QGuiApplication.primaryScreen()
        sSize = screen.size()
        center_label = QLabel(sSize)
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("font-size: 20px; border: 1px solid red;")
        
        # Правый верхний label
        top_right_label = QLabel("Правый верх")
        top_right_label.setStyleSheet("border: 1px solid blue;")
        
        # Добавляем виджеты в grid
        grid.addWidget(top_right_label, 0, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        grid.addWidget(center_label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Настройка растяжения
        grid.setRowStretch(0, 1)  # Верхняя часть
        grid.setRowStretch(1, 2)  # Центральная часть (больше места)
        grid.setColumnStretch(0, 1)

app = QApplication([])
window = MainWindow()
window.showMaximized()
app.exec()