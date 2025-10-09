from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

app = QApplication([])

# Главное окно
window = QWidget()
main_layout = QVBoxLayout()

# Панель с кнопками (горизонтальная)
button_panel = QHBoxLayout()
button_panel.addWidget(QPushButton("Файл"))
button_panel.addWidget(QPushButton("Правка"))
button_panel.addWidget(QPushButton("Вид"))
button_panel.addStretch()  # Растягивающееся пространство
button_panel.addWidget(QPushButton("Справка"))

# Основная область (грид)
content = QGridLayout()
content.addWidget(QLabel("Текст:"), 0, 0)
content.addWidget(QLineEdit(), 0, 1)
content.addWidget(QPushButton("Отправить"), 1, 0, 1, 2)  # Объединение колонок

# Добавляем всё в основной слой
main_layout.addLayout(button_panel)
main_layout.addLayout(content)

window.setLayout(main_layout)
window.show()
app.exec()