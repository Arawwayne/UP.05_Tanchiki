import sys, json, time, random, os
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QPushButton, QFrame, QLabel, QVBoxLayout, 
                             QWidget, QStackedWidget, QMainWindow, QHBoxLayout, QGridLayout,
                             QSpacerItem, QSizePolicy)

def read_from_json(filename = "data/fields.json") -> dict or list: # type: ignore
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


objects = {
    "void": -1,
    "air": [0, 'data/air,png'],
    "wall": [1, "data/wall.png"],
    'base': [9, 'data/baza.png'],
    "tankPlayer": [11, "data/tankMain.png"],
    "tankEnemy1": [12, 'data/Enemy1.png'],
    "bullet": [111, "data/bullet.png"],
    "tankEnemy": [12, "data/wall.png"]
}

directions = {
    'north': [0, (-1, 0)],
    'east': [90, (0, 1)],
    'south': [180, (1, 0)],
    'west': [270, (0, -1)],
}

moveKeys = {
    Qt.Key.Key_Up: 'north',
    Qt.Key.Key_Right: 'east',
    Qt.Key.Key_Down: 'south', 
    Qt.Key.Key_Left: 'west'
}

actionKeys = {
    Qt.Key.Key_Space
}
            

rows = 18
collumns = 25

field = read_from_json()

chosenField = field['field1']


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
        self.menu = Menu(parent=self)
        self.setCentralWidget(self.game)

    def keyPressEvent(self, e):
        self.game.tank._keyPressEvent(e)
        return super().keyPressEvent(e)
        

class Menu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.varWindowMain = parent
        self.mainLayout = QVBoxLayout


class GameInterface(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.fieldObjects = []

        mainLayout = QHBoxLayout()
        self.gameField = QGridLayout()
        interface = QVBoxLayout()

        for curRow in range(rows):
            for curCol in range(collumns):
                match chosenField[curRow][curCol]:
                    # case 0: 
                    #     self.space = QLabel()
                    #     self.space.setPixmap(QPixmap(objects["air"][1]))
                    #     self.space.setScaledContents(True)
                    #     # space = QSpacerItem(60, 60, QSizePolicy.Policy.Fixed)
                    #     self.gameField.addWidget(self.space, curRow, curCol)
                    
                    case 1: 
                        self.wall = Wall(parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)
                    
                    case 9:
                        base = QLabel()
                        base.setPixmap(QPixmap(objects["base"][1]))
                        base.setScaledContents(True)
                        self.gameField.addWidget(base, curRow, curCol)

                    case 11: 
                        self.tank = Tank(pos=(curRow, curCol), parent=self) 
                        self.gameField.addWidget(self.tank, curRow, curCol)

        pauseButton = ClickableImages('data/pause.png', 'pauseButton', parent = parent)
        pauseButton.setScaledContents(True)
        interface.addWidget(pauseButton, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.gameField.setSpacing(0) 
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)

        

class Wall(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.setPixmap(QPixmap(objects["wall"][1]))
        self.setScaledContents(True)
    
    def destroyed(self):
        self.deleteLater()
        self = None
        

class Tank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.direction = "north"
        self.shot_busy = False
        self.health = 3
        
        self.setPixmap(QPixmap(objects["tankPlayer"][1]))
        self.setScaledContents(True)
        self.row, self.col = pos

    def move(self, direction):
        r, c = directions[direction][1]
        new_row, new_col = self.row + r, self.col + c

        if chosenField[new_row][new_col] == 0 and direction == self.direction:
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[self.row][self.col] = 0
            chosenField[new_row][new_col] = 11
            self.row, self.col = new_row, new_col        

        self.setPixmap(rotate_pixmap(QPixmap(objects["tankPlayer"][1]), directions[direction][0]))
        self.direction = direction

# ОЧИСТКА ТЕРМИНАЛА И ВЫВОД МАТРИЦЫ
        # os.system('cls' if os.name == 'nt' else 'clear')
        # for i in chosenField:
        #     for j in i:
        #         print(j, end='  ')
        #     print()

    def shoot(self, direction):
        bullet = Bullet(self, self.direction, pos=(self.row, self.col), parent=self.gameInterface)
        bullet._move()

    def destroyed(self):
        return
    
    def _keyPressEvent(self, e):
        key = e.key()
        if key in moveKeys:
            self.move(moveKeys[key])
        elif key in actionKeys:
            self.shoot(self.direction)

class Bullet(QLabel):
    def __init__(self, owner, direction, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.owner = owner
        self.direction = direction
        self.row, self.col = pos
        self.r, self.c = directions[self.direction][1]
        self.row, self.col = self.row + self.r, self.col + self.c

        self.shot_timer = QTimer(self)
        self.shot_timer.timeout.connect(self._move)
        self.shot_timer.start(100)

        self.setPixmap(rotate_pixmap(QPixmap(objects['bullet'][1]), directions[self.direction][0]))
        self.setScaledContents(True)

    def _move(self):
        new_row, new_col = self.row, self.col
        if chosenField[new_row][new_col] == 0:
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[new_row][new_col] = 111
            chosenField[self.row][self.col] = 0
            self.row, self.col = self.row + self.r, self.col + self.c
            return
        elif (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.fieldObjects:
            widget.destroyed()
            chosenField[new_row][new_col] = 0
        self.deleteLater()
        


class ClickableImages(QLabel):
    def __init__(self, image, senderName, parent = None):    
        super().__init__(parent)

        self.main = parent
        self.image = image
        self.senderName = senderName
        
        self.setPixmap(QPixmap(image))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем изображение

    def mousePressEvent(self, event):  # Обработка клика
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.senderName)  # Вызываем свою функцию

    def on_click(self, senderName):
        if senderName == 'pauseButton':
            self.main.close()


def rotate_pixmap(pixmap, angle):
    rotated = QPixmap(pixmap)
    rotated.fill(Qt.GlobalColor.transparent)  # Прозрачный фон
    
    painter = QPainter(rotated)
    painter.translate(rotated.width() / 2, rotated.height() / 2)
    painter.rotate(angle)
    painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return rotated

def find_widget(layout, row, column):
    """Найти виджет по позиции (строка, колонка)"""
    item = layout.itemAtPosition(row, column)
    if item and item.widget():
        return item.widget()

def get_widgets(layout):
        """Получить все виджеты из QGridLayout"""
        widgets = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                widgets.append(item.widget())
        
        print(f"Найдено виджетов: {len(widgets)}")
        for widget in widgets:
            if type(widget).__name__ == 'Tank':
                print(f"Виджет: {widget}, Тип: {type(widget).__name__}")



def handle_qt_messages(msg_type, context, message):  #QPainter ругается из-за QPixmap в setup_mainMenu, поэтому таким незамысловатым образом мы пропускаем эту ошибку. 
    if msg_type == QtMsgType.QtWarningMsg:
        return  # Игнорируем предупреждения
    print(message)  # Выводим остальные сообщения
qInstallMessageHandler(handle_qt_messages)

# Старт самой программы (святыня) (НЕ ТРОГАТЬ!!!)        

if __name__ == '__main__':  # нужно чтобы программа запускалась именно из этого файла, а не из других. Типо инкапсуляция.
    app = QApplication(sys.argv)
    start = WindowMain()
    start.showFullScreen()
    app.exec()
