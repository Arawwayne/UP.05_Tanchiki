import sys, json, time, random
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform
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

rows = 18
collumns = 25

field = read_from_json()

chosenField = field['field1']

Keys = [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Space]

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

class GameInterface(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        ingame_objects = {
    
        }

        mainLayout = QHBoxLayout()
        self.gameField = QGridLayout()
        interface = QVBoxLayout()

        for curRow in range(rows):
            for curCol in range(collumns):
                match chosenField[curRow][curCol]:
                    case 0: 
                        self.space = QLabel()
                        self.space.setPixmap(QPixmap(objects["air"][1]))
                        self.space.setScaledContents(True)
                        # space = QSpacerItem(60, 60, QSizePolicy.Policy.Fixed)
                        self.gameField.addWidget(self.space, curRow, curCol)
                        
                    case 1: 
                        wall = QLabel()
                        wall.setPixmap(QPixmap(objects["wall"][1]))
                        wall.setScaledContents(True)
                        self.gameField.addWidget(wall, curRow, curCol)
                    
                    case 9:
                        base = QLabel()
                        base.setPixmap(QPixmap(objects["base"][1]))
                        base.setScaledContents(True)
                        self.gameField.addWidget(base, curRow, curCol)

                    case 11: 
                        self.tank = Tank(pos=(curRow, curCol), parent=self) 
                        self.gameField.addWidget(self.tank, curRow, curCol)
                        ingame_objects['tankPlayer'] = self.tank
                        print(ingame_objects)

        pauseButton = ClickableImages('data/pause.png', 'pauseButton', parent = parent)
        pauseButton.setScaledContents(True)
        interface.addWidget(pauseButton, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.gameField.setSpacing(0)
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)

class Tank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.direction = "north"
        self.shot_busy = False
        self.setPixmap(QPixmap(objects["tankPlayer"][1]))
        self.setScaledContents(True)
        self.row, self.col = pos

    def move(self):
        
        self.move(1000, 1000)



    def destroy(self):
        if 'tankPlayer' in self.gameInterface.ingame_objects:
            self.gameInterface.gameField.removeWidget(self.gameInterface.ingame_objects["tankPlayer"])
            self.gameInterface.ingame_objects["tankPlayer"].deleteLater()
            self.gameInterface.ingame_objects.pop('tankPlayer')
            print('tank destroyed')

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