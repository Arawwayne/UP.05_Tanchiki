# Import necessary libraries
import sys, json, time, random
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform
from PyQt6.QtWidgets import (QApplication, QPushButton, QFrame, QLabel, QVBoxLayout, 
                             QWidget, QStackedWidget, QMainWindow, QHBoxLayout, QGridLayout,
                             QSpacerItem, QSizePolicy)

"""
План архитектуры работы окон такой, что я создаю одно главное окно (MainWindow) в которое я буду с помощью setCentralWidget() 
вставлять шаблоны экранных форм в виде виджетов, всё содержимое которых будет генерироваться из методов setup_. 

Все формы будут находится в stackedWidgets, которые переключаются при нажатии определённых кнопок, которые дают сигнал классу ClickableImages,
который в свою очередь будет исполнять метод, который должна исполнять нажатая кнопка.
"""

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

chosenField = field['field5']

Key_Arrows = [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Space]



class WindowMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Создаём заголовок окна, его геометрию и иконку.
        self.setWindowTitle("TANKS")
        paletTe = app.palette()
        paletTe.setColor(QPalette.ColorRole.Window, QColor("#E5E4E2"))
        self.setPalette(paletTe)
        self.setWindowIcon(QIcon('data/logo.ico'))

        # В нем будут храниться формы в виде виджетов 
        self.pagesStack = QStackedWidget()

        self.setup_pages()
        self.setCentralWidget(self.pagesStack)  # Нужен QMainWondow
        
        
    def setup_pages(self):
        self.mainMenu = MainMenu(parent = self)
        self.settingsMenu = SettingsMenu(parent = self)
        self.gameInterface = GameInterface(parent = self)
        
        
        self.pagesStack.addWidget(self.mainMenu)
        self.pagesStack.addWidget(self.settingsMenu)
        self.pagesStack.addWidget(self.gameInterface)   
        
        self.pagesStack.setCurrentIndex(2)
    
        
    def keyPressEvent(self, ev):
        if self.pagesStack.currentIndex() == 2:
            if ev.key() in Key_Arrows:
                self.gameInterface.tank.on_keyPress(ev.key())
        
        return super().keyPressEvent(ev)
        


class MainMenu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        mainLayout = QVBoxLayout()
        row1 = QHBoxLayout()
        ro1 = QGridLayout()
        row2 = QHBoxLayout()
        
        
        title = QLabel()
        title.setPixmap(QPixmap("data/title.png"))
        scaling(title, 1000, 200)
        #title.setFixedSize(1000, 280)
        #title.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        title.setScaledContents(True)
        
        exitButton = ClickableImages("data/exitButton.png", "exitButton", parent = parent)
        scaling(exitButton, 200, 200)
        #exitButton.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop) 
        #exitButton.setFixedSize(200, 200)
        exitButton.setScaledContents(True)
        
        startButton = ClickableImages("data/playButton.png", "startButton", parent = parent)
        scaling(startButton, 500, 500)
        startButton.setScaledContents(True)
        
        settingsButton = ClickableImages("data/settingsButton.png", "settingsButton", parent = parent)
        scaling(settingsButton, 500, 500)
        settingsButton.setScaledContents(True)
        #settingsButton.clicked.connect(lambda: self.pagesStack.setCurrentIndex(1))
        
        #row1.addWidget(title)
        #row1.addWidget(exitButton)
        ro1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ro1.addWidget(exitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        row2.addWidget(startButton)
        row2.addWidget(settingsButton)
        
        
        #mainLayout.addLayout(row1)
        mainLayout.addLayout(ro1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)
        

    
class SettingsMenu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)    
        
        self.main = parent
        mainLayout = QVBoxLayout()
        
        title = QLabel('SETTINGS')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        startButton = QPushButton('BACK TO MENU')
        
        startButton.clicked.connect(lambda: self.main.pagesStack.setCurrentIndex(0))
        
        mainLayout.addWidget(title)
        mainLayout.addWidget(startButton)
        self.setLayout(mainLayout)



class GameInterface(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        
        mainLayout = QHBoxLayout()
        self.gameField = QGridLayout()
        interface = QVBoxLayout()
        
        for curRow in range(rows):
            for curCol in range(collumns):
                match chosenField[curRow][curCol]:
                    case 0: 
                        self.space = QLabel()
                        self.space.setPixmap(QPixmap(objects["air"][1]))
                        scaling(self.space, 60, 60)
                        self.space.setScaledContents(True)
                        # space = QSpacerItem(60, 60, QSizePolicy.Policy.Fixed)
                        self.gameField.addWidget(self.space, curRow, curCol)
                        
                    case 1: 
                        wall = QLabel()
                        wall.setPixmap(QPixmap(objects["wall"][1]))
                        scaling(wall, 60, 60)
                        wall.setScaledContents(True)
                        self.gameField.addWidget(wall, curRow, curCol)
                    
                    case 9:
                        base = QLabel()
                        base.setPixmap(QPixmap(objects["base"][1]))
                        scaling(base, 60, 60)
                        base.setScaledContents(True)
                        self.gameField.addWidget(base, curRow, curCol)
                    
                    case 11: 
                        self.tank = Tank(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.tank, curRow, curCol)
                    
                    case 12:
                        self.enemy = EnemyTank(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy, curRow, curCol)
        
        pauseButton = ClickableImages('data/pause.png', 'pauseButton', parent = parent)
        scaling(pauseButton, 350, 150)
        pauseButton.setScaledContents(True)
        interface.addWidget(pauseButton, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.gameField.setSpacing(0)
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)
        


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
        if senderName == 'settingsButton':
            self.main.pagesStack.setCurrentIndex(1)
        if senderName == 'startButton':
            self.main.pagesStack.setCurrentIndex(2)
        if senderName == 'exitButton':
            self.main.close()
        if senderName == 'pauseButton':
            self.main.pagesStack.setCurrentIndex(0)
            
            
    
class Tank(QLabel):
    def __init__(self, pos, parent = None):
        super().__init__(parent)
        self.gameInterface = parent
        
        self.direction = "north"
        
        self.shot_busy = False
        
        self.setPixmap(QPixmap(objects["tankPlayer"][1]))
        scaling(self, 60, 60)
        self.setScaledContents(True)

        self.row, self.col = pos

        # if not args: 
        #     pass
        # else:
        #     self.row, self.col = args
        
    def on_keyPress(self, key):

        if key == Qt.Key.Key_Up:
            time.sleep(0.07)
            newRow = self.row - 1
            newCol = self.col

            rotated = rotate_pixmap(QPixmap(objects["tankPlayer"][1]), 0)
            self.setPixmap(rotated)

            if self.direction != 'north':
                self.direction = 'north'

            else:
                if chosenField[newRow][newCol] == 0:
                    self._move_to(newRow, newCol)
                
        if key == Qt.Key.Key_Down:
            time.sleep(0.07)
            newRow = self.row + 1
            newCol = self.col

            rotated = rotate_pixmap(QPixmap(objects["tankPlayer"][1]), 180)
            self.setPixmap(rotated)
            
            if newRow > 17:
                return
            
            if self.direction != 'south':
                self.direction = 'south'
            else:
                if chosenField[newRow][newCol] == 0:
                    self._move_to(newRow, newCol)
                
        if key == Qt.Key.Key_Left:
            time.sleep(0.07)
            newRow = self.row
            newCol = self.col - 1 
                
            rotated = rotate_pixmap(QPixmap(objects["tankPlayer"][1]), 270)
            self.setPixmap(rotated) 
            
            if self.direction != 'west':
                self.direction = 'west'
            else:           
                if chosenField[newRow][newCol] == 0:
                    self._move_to(newRow, newCol)
        
        if key == Qt.Key.Key_Right:
            time.sleep(0.07)
            
            newRow = self.row
            newCol = self.col + 1           
            
            rotated = rotate_pixmap(QPixmap(objects["tankPlayer"][1]), 90)
            self.setPixmap(rotated)
            
            if newCol > 24:
                return
            
            if self.direction != 'east':
                self.direction = 'east'  
    
            else:
                if chosenField[newRow][newCol] == 0: 
                    self._move_to(newRow, newCol) 

        if self.shot_busy == False:
            if key == Qt.Key.Key_Space:
                Bullet3((self.row, self.col), self.direction, parent=self.gameInterface)


    def _move_to(self, new_row, new_col):
        """Перемещает танк на новую позицию"""
        chosenField[self.row][self.col] = 0
        chosenField[new_row][new_col] = 11
        
        self.gameInterface.gameField.removeWidget(self)
        self.row, self.col = new_row, new_col
        self.gameInterface.gameField.addWidget(self, self.row, self.col)    
    
    def destroy(self):
        """Уничтожение танка"""
        chosenField[self.row][self.col] = 0
        self.gameInterface.gameField.removeWidget(self)
        self.deleteLater()    
        
        
class EnemyTank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.direction = random.choice(["north", "south", "west", "east"])
        self.shotEnemy_busy = False
        self.move_timer = QTimer()
        self.shot_timer = QTimer()
        
        # Настройка внешнего вида
        self.setPixmap(self._get_rotated_pixmap())
        self.setScaledContents(True)
        self.setFixedSize(60, 60)
        
        # Позиция на поле
        self.row, self.col = pos
        chosenField[self.row][self.col] = 12  # 12 - код вражеского танка
        
        # Таймеры для ИИ
        self.move_timer.timeout.connect(self._ai_move)
        self.shot_timer.timeout.connect(self._ai_shot)
        self.move_timer.start(500)  # Движение каждые 500 мс
        self.shot_timer.start(2000)  # Выстрел каждые 2 секунды
    
    def _get_rotated_pixmap(self, angle=None):
        """Возвращает повернутое изображение танка"""
        if angle is None:
            angle = {
                "north": 0,
                "south": 180,
                "west": 270,
                "east": 90
            }[self.direction]
        
        return rotate_pixmap(QPixmap(objects["tankEnemy1"][1]), angle)
    
    def _ai_move(self):
        """ИИ для движения вражеского танка"""
        # Случайно выбираем направление (20% chance to change)
        if random.random() < 0.2:
            self.direction = random.choice(["north", "south", "west", "east"])
            self.setPixmap(self._get_rotated_pixmap())
        
        # Определяем новую позицию
        if self.direction == "north":
            new_row, new_col = self.row - 1, self.col
        elif self.direction == "south":
            new_row, new_col = self.row + 1, self.col
        elif self.direction == "west":
            new_row, new_col = self.row, self.col - 1
        else:  # east
            new_row, new_col = self.row, self.col + 1
        
        # Проверка границ и препятствий
        if (0 <= new_row < len(chosenField)) and (0 <= new_col < len(chosenField[0])):
            if chosenField[new_row][new_col] == 0:
                self._move_to(new_row, new_col)
            else:
                # Если путь заблокирован - меняем направление
                self.direction = random.choice(["north", "south", "west", "east"])
                self.setPixmap(self._get_rotated_pixmap())
        # else:
        #     # Если достиг границы - разворачиваемся
        #     self.direction = "south" if self.direction == "north" else \
        #                     "north" if self.direction == "south" else \
        #                     "east" if self.direction == "west" else "west"
                            
    def _move_to(self, new_row, new_col):
        """Перемещает танк на новую позицию"""
        chosenField[self.row][self.col] = 0
        chosenField[new_row][new_col] = 12
        
        self.gameInterface.gameField.removeWidget(self)
        self.row, self.col = new_row, new_col
        self.gameInterface.gameField.addWidget(self, self.row, self.col)
    
    def _ai_shot(self):
        """ИИ для выстрела вражеского танка"""
        if not self.shotEnemy_busy:
            self.shotEnemy_busy = True
            Bullet3((self.row, self.col), self.direction, parent=self.gameInterface)
            QTimer.singleShot(1000, lambda: setattr(self, 'shot_busy', False))
    
    def destroy(self):
        """Уничтожение танка"""
        self.move_timer.stop()
        self.shot_timer.stop()
        chosenField[self.row][self.col] = 0
        self.gameInterface.gameField.removeWidget(self)
        self.deleteLater()
        
                

class Bullet3(QLabel):
    def __init__(self, tankPos, direction, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        
        self.gameInterface.tank.shot_busy = True
        
        self.direction = direction
        self.row, self.col = tankPos
        self.speed = 30  # Уменьшили для большей скорости
        
        self.bullet_pixmap = QPixmap(objects["bullet"][1])
        
        # Оптимизированная инициализация
        self.setPixmap(self.bullet_pixmap)
        scaling(self, 30, 30)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Предварительные вычисления для движения
        self.move_vectors = {
            'north': (-1, 0),
            'south': (1, 0),
            'west': (0, -1),
            'east': (0, 1)
        }
        
        # Быстрое добавление в layout
        self.update_position()
        if self.direction == 'north':
            self.gameInterface.gameField.addWidget(self, self.row-1, self.col, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            rotated = rotate_pixmap(QPixmap(objects["bullet"][1]), 0)
            self.setPixmap(rotated)
            
        elif self.direction == 'south':
            self.gameInterface.gameField.addWidget(self, self.row+1, self.col, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            rotated = rotate_pixmap(QPixmap(objects["bullet"][1]), 180)
            self.setPixmap(rotated)
            
        elif self.direction == 'west':
            self.gameInterface.gameField.addWidget(self, self.row, self.col-1, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
            rotated = rotate_pixmap(QPixmap(objects["bullet"][1]), 270)
            self.setPixmap(rotated)
            
        elif self.direction == 'east':
            self.gameInterface.gameField.addWidget(self, self.row, self.col+1, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            rotated = rotate_pixmap(QPixmap(objects["bullet"][1]), 90)
            self.setPixmap(rotated)
        
        # Оптимизированный таймер
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)  # Более точный таймер
        self.timer.timeout.connect(self.move_bullet)
        self.start_time = QElapsedTimer()
        self.start_time.start()
        self.timer.start(self.speed)

    def update_position(self):
        """Оптимизированное обновление позиции"""
        if hasattr(self, 'prev_row'):
            chosenField[self.prev_row][self.prev_col] = 0
        chosenField[self.row][self.col] = 111
        self.prev_row, self.prev_col = self.row, self.col

    def move_bullet(self):
        """Оптимизированное движение пули"""
        dr, dc = self.move_vectors[self.direction]
        new_row, new_col = self.row + dr, self.col + dc
        
        #Быстрая проверка границ
        if (0 <= new_row < len(chosenField)) and (0 <= new_col < len(chosenField[0])):
            if chosenField[new_row][new_col] == 0:
                # Быстрое перемещение
                self.gameInterface.gameField.removeWidget(self)
                self.row, self.col = new_row, new_col
                
                if self.direction == 'north': 
                    self.gameInterface.gameField.addWidget(self, self.row, self.col, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                    
                elif self.direction == 'south':
                    self.gameInterface.gameField.addWidget(self, self.row, self.col, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
                    
                elif self.direction == 'west':
                    self.gameInterface.gameField.addWidget(self, self.row, self.col, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    
                elif self.direction == 'east':
                    self.gameInterface.gameField.addWidget(self, self.row, self.col, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
                    
                self.update_position()
                return
            
            elif chosenField[new_row][new_col] > 0:
                chosenField[new_row][new_col] = 0
                item1 = self.gameInterface.gameField.itemAtPosition(new_row, new_col)
                widget1 = item1.widget()
                self.gameInterface.gameField.removeWidget(widget1)
                self.gameInterface.gameField.addWidget(self.gameInterface.space, new_row, new_col)

            
        # Обработка столкновения (оптимизированная)
        self.cleanup()
    
    def cleanup(self):
        """Оптимизированная очистка"""
        self.timer.stop()
        self.gameInterface.gameField.removeWidget(self)
        if hasattr(self, 'prev_row'):
            chosenField[self.prev_row][self.prev_col] = 0
        chosenField[self.row][self.col] = 0
        self.deleteLater()
        self.gameInterface.tank.shot_busy = False
        self.gameInterface.enemy.shotEnemy_busy = False

        
            
def scaling(image, w, h):
    image = image
    screen = QGuiApplication.primaryScreen()
    screenSize = screen.size()
    screenWidth = screenSize.width()
    
    if 1920 == screenWidth:
        image.setFixedSize(w, h)  
    if 1280 == screenWidth:
        image.setFixedSize(round(w * (1280/1920)), round(h * (1280/1920)))

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