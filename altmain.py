import sys, json, time, random, os
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QPushButton, QFrame, QLabel, QVBoxLayout, 
                             QWidget, QStackedWidget, QMainWindow, QHBoxLayout, QGridLayout,
                             QSpacerItem, QSizePolicy)

# Функция для чтения json файла, в котором находится макет (матрица) игрового поля
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

# Объекты с ссылками на их изображения
objects = {
    "void": -1,
    "air": [0, 'data/air,png'],
    "wall": [1, "data/wall.png"],
    "unWall": [8, 'data/unWall.png'],
    'base': [9, 'data/baza.png'],
    "tankPlayer": [10, "data/tankMain.png"],
    "tankEnemy": [11, 'data/Enemy1.png'],
    "bullet": [111, "data/bullet.png"],
}

pictures = {
    'play': 'data/playButton.png',
    'exit': 'data/exitButton.png',
    'replay': 'data/replayButton.png',
    'title': 'data/title.png',
    'pause': 'data/pause.png',
    'pause_title': 'data/pause_title.png',
    'home': 'data/home.png',
}

# Направления движения с их углами поворота и координатами передвижения по полю
directions = {
    'north': [0, (-1, 0)],
    'east': [90, (0, 1)],
    'south': [180, (1, 0)],
    'west': [270, (0, -1)],
}

# Клавиши пережвижения с их направлениями
moveKeys = {
    Qt.Key.Key_Up: 'north',
    Qt.Key.Key_Right: 'east',
    Qt.Key.Key_Down: 'south', 
    Qt.Key.Key_Left: 'west'
}

# Клавиши атаки
actionKeys = {
    Qt.Key.Key_Space
}
            
# Матрица поля 18 на 25
rows = 18
collumns = 25

field = read_from_json()

field_key = 'field1'

chosenField = field[field_key]


# Класс главного окна или рамки, в которую мы будем вставлять виджет с формой меню или игрового интерфейса
class WindowMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Создаём заголовок окна, его геометрию и иконку.
        screen_width, screen_height = app.primaryScreen().size().width(), app.primaryScreen().size().height()

        self.setWindowTitle("TANKS")
        paletTe = app.palette()
        paletTe.setColor(QPalette.ColorRole.Window, QColor("#353232"))
        self.setPalette(paletTe)
        self.setWindowIcon(QIcon('data/logo.ico'))
        #self.setFixedSize(screen_width, screen_height)

        self.pagesStack = QStackedWidget()
        self.pagesStack.setFixedSize(screen_width, screen_height)

        # Определяем формы и вносим их в стэк
        self.menu = Menu(parent=self)
        self.pause = PauseScreen(parent=self)
        self.win = WinScreen(parent=self)
        self.game = GameInterface(parent=self)

        self.pagesStack.addWidget(self.menu)
        self.pagesStack.addWidget(self.pause)
        self.pagesStack.addWidget(self.win)
        self.pagesStack.addWidget(self.game)

        # Вставляем стэк в рамку. Тк меню был введён в стэк первым, то оно и будет показываться
        self.setCentralWidget(self.pagesStack)
        self.pagesStack.setCurrentIndex(2)

    def reset_game(self):
        reset_game_state()
        new_game = GameInterface(parent=self)
        self.pagesStack.removeWidget(self.game)
        self.game.deleteLater()
        self.game = new_game
        self.pagesStack.addWidget(self.game)
        self.pagesStack.setCurrentIndex(self.pagesStack.count() - 1)

    # Обработка нажатия клавиш, которая передаётся в класс Tank
    def keyPressEvent(self, e):
        self.game.tank._keyPressEvent(e)
        return super().keyPressEvent(e)

    
# Меню
class Menu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.main = parent
        self.setup_ui()

    def setup_ui(self):
        mainLayout = QVBoxLayout()
        ro1 = QGridLayout()
        row2 = QHBoxLayout()
        
        
        title = QLabel()
        title.setPixmap(QPixmap(pictures['title']))
        scaling(title, 1000, 200)
        title.setScaledContents(True)
        
        exitButton = ClickableImages(pictures['exit'], 'exit', parent = self.main)
        scaling(exitButton, 200, 200)
        exitButton.setScaledContents(True)
        
        startButton = ClickableImages(pictures['play'], "play", parent = self.main)
        scaling(startButton, 500, 500)
        startButton.setScaledContents(True)

        ro1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ro1.addWidget(exitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        row2.addWidget(startButton)
        
        mainLayout.addLayout(ro1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)
        

class Endcreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.main = parent
        self.setup_ui()

    def setup_ui(self, state):
        self.mainLayout = QVBoxLayout()
        stats_buttons_row = QHBoxLayout()
        
        # Заголовок с поражением/победой

        lose = QLabel()
        lose.setPixmap(QPixmap('data/lose.png'))       
        scaling(lose, 1000, 200)       
        lose.setScaledContents(True)
        
        # Фреймы со статистикой
        frame_kills = QFrame()
        frame_kills.setFixedSize(600, 600)
        frame_kills.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame_kills.setLineWidth(2)
        frame_kills.setMidLineWidth(3)

        frame_pickups = QFrame()
        frame_pickups.setFixedSize(600, 600)
        frame_pickups.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame_pickups.setLineWidth(2)
        frame_pickups.setMidLineWidth(3)

        frame_kills_layout = QVBoxLayout()
        frame_kills_layout.addWidget(QLabel('TANK KILLS – 10000'))
        frame_kills_layout.addWidget(QLabel('YOU WIN'))
        frame_kills_layout.addWidget(QLabel('YAHOOOO'))

        frame_layout = QVBoxLayout()
        frame_layout.addWidget(QLabel('TANK KILLS – xd'))
        frame_layout.addWidget(QLabel('YOU LOSE'))
        frame_layout.addWidget(QLabel('WAHOOOO'))

        frame_kills.setLayout(frame_kills_layout)
        frame_pickups.setLayout(frame_layout)

        # Кнопки
        homeButton = ClickableImages(pictures['home'], 'home', parent = self.main)
        scaling(homeButton, 200, 200)
        homeButton.setScaledContents(True)

        replayButton = ClickableImages(pictures['replay'], "replay", parent = self.main)
        scaling(replayButton, 200, 200)
        replayButton.setScaledContents(True)

        buttons1_layout = QHBoxLayout()

        buttons1_layout.addWidget(replayButton)
        buttons1_layout.addWidget(homeButton)

        # Вставляем всё что надо
        self.mainLayout.addWidget(lose)
        self.mainLayout.addLayout(stats_buttons_row)

        stats_buttons_row.addWidget(frame_kills)
        stats_buttons_row.addWidget(frame_pickups)
        stats_buttons_row.addLayout(buttons1_layout)


        self.mainLayout.addWidget(frame_kills)
        self.setLayout(self.mainLayout)

    def clear_layout(self):
    # Универсальная функция для очистки любого layout
        if self.mainLayout is not None:
            while self.mainLayout.count():
                child = self.mainLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.self.mainLayout():
                    self.clear_layout(child.self.mainLayout())  # Рекурсия для вложенных layouts


class WinScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.main = parent
        mainLayout = QVBoxLayout()
        stats_buttons_row = QHBoxLayout()
        
        # Заголовок с поражением/победой 
        win = QLabel()
        win.setPixmap(QPixmap('data/win.png'))       
        scaling(win, 1000, 200)       
        win.setScaledContents(True)
        
        # Фреймы со статистикой
        frame_kills = QFrame()
        frame_kills.setFixedSize(600, 600)
        frame_kills.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame_kills.setLineWidth(2)
        frame_kills.setMidLineWidth(3)

        frame_pickups = QFrame()
        frame_pickups.setFixedSize(600, 600)
        frame_pickups.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame_pickups.setLineWidth(2)
        frame_pickups.setMidLineWidth(3)

        frame_kills_layout = QVBoxLayout()
        frame_kills_layout.addWidget(QLabel('TANK KILLS – 10000'))
        frame_kills_layout.addWidget(QLabel('YOU WIN'))
        frame_kills_layout.addWidget(QLabel('YAHOOOO'))

        frame_layout = QVBoxLayout()
        frame_layout.addWidget(QLabel('TANK KILLS – xd'))
        frame_layout.addWidget(QLabel('YOU LOSE'))
        frame_layout.addWidget(QLabel('WAHOOOO'))

        frame_kills.setLayout(frame_kills_layout)
        frame_pickups.setLayout(frame_layout)

        # Кнопки
        homeButton = ClickableImages(pictures['home'], 'home', parent = parent)
        scaling(homeButton, 200, 200)
        homeButton.setScaledContents(True)
        
        startButton = ClickableImages(pictures['play'], "play", parent = parent)
        scaling(startButton, 200, 200)
        startButton.setScaledContents(True)

        replayButton = ClickableImages(pictures['replay'], "replay", parent = parent)
        scaling(replayButton, 200, 200)
        replayButton.setScaledContents(True)

        buttons_layout = QVBoxLayout()
        buttons1_layout = QHBoxLayout()

        buttons1_layout.addWidget(startButton)
        buttons1_layout.addWidget(replayButton)
        buttons_layout.addLayout(buttons1_layout)

        buttons_layout.addWidget(homeButton, alignment=Qt.AlignmentFlag.AlignCenter)
        

        # Вставляем всё что надо
        mainLayout.addWidget(win)
        mainLayout.addLayout(stats_buttons_row)

        stats_buttons_row.addWidget(frame_kills)
        stats_buttons_row.addWidget(frame_pickups)
        stats_buttons_row.addLayout(buttons_layout)


        mainLayout.addWidget(frame_kills)
        self.setLayout(mainLayout)

        # winlose2 = QLabel()
        # winlose2.setPixmap(QPixmap('data/win.png'))
        # scaling(winlose2, 1000, 200)
        # winlose2.setScaledContents(True)
        # mainLayout.addWidget(winlose2)


class PauseScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main = parent
        mainLayout = QVBoxLayout()
        row1 = QHBoxLayout()
        ro1 = QGridLayout()
        row2 = QHBoxLayout()
        
        
        title = QLabel()
        title.setPixmap(QPixmap(pictures['pause_title']))
        scaling(title, 1000, 200)
        title.setScaledContents(True)
        
        startButton = ClickableImages(pictures['play'], 'resume', parent = self.main)
        scaling(startButton, 500, 500)
        startButton.setScaledContents(True)

        homeButton = ClickableImages(pictures['home'], 'home', parent = self.main)
        scaling(homeButton, 200, 200)
        homeButton.setScaledContents(True)

        replayButton = ClickableImages(pictures['replay'], "replay", parent = self.main)
        scaling(replayButton, 500, 500)
        replayButton.setScaledContents(True)

        ro1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ro1.addWidget(homeButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        row2.addWidget(startButton)
        row2.addWidget(replayButton)
        
        
        #mainLayout.addLayout(row1)
        mainLayout.addLayout(ro1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)


# Класс игрового интерфейса. Здесь будет очерчено игровое поле с помощью матрицы и UI по состоянию и возможностям игрока
class GameInterface(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.fieldObjects = []
        self.enemies = []
        self.timers = []
    
        mainLayout = QHBoxLayout()
        self.gameField = QGridLayout()
        self.gameField.setSpacing(0) 
        interface = QVBoxLayout()

        # Сканируем матрицу и в соответствии с ней, отображаем объекты на поле
        for curRow in range(rows):
            for curCol in range(collumns):
                match chosenField[curRow][curCol]:
                    # case 0: 
                    #     self.space = QLabel()
                    #     self.space.setPixmap(QPixmap(objects["air"][1]))
                    #     scaling(self.space, 60, 60)
                    #     self.space.setScaledContents(True)
                    #     # space = QSpacerItem(60, 60, QSizePolicy.Policy.Fixed)
                    #     self.gameField.addWidget(self.space, curRow, curCol)
                    
                    case 1: 
                        self.wall = Wall(parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)
                    
                    case 8: 
                        self.unWall = Wall(parent=self, unbreakble=True)
                        self.gameField.addWidget(self.unWall, curRow, curCol)
                    
                    case 9:
                        base = QLabel()
                        base.setPixmap(QPixmap(objects["base"][1]))
                        base.setScaledContents(True)
                        self.gameField.addWidget(base, curRow, curCol)

                    case 10: 
                        self.tank = Tank(pos=(curRow, curCol), parent=self) 
                        self.gameField.addWidget(self.tank, curRow, curCol)

                    case 11:
                        self.enemy = EnemyTank(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy, curRow, curCol)
                        self.enemies.append(self.enemy)

        pauseButton = ClickableImages(pictures['pause'], 'pause', parent = parent)
        scaling(pauseButton, 200, 600)
        pauseButton.setScaledContents(True)
        interface.addWidget(pauseButton, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)


class Wall(QLabel):
    def __init__(self, unbreakble=False, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        if unbreakble:
            self.setPixmap(QPixmap(objects["unWall"][1]))
        else:
            self.setPixmap(QPixmap(objects["wall"][1]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
    
    def destroyed(self):
        self.deleteLater()
        self.gameInterface.fieldObjects.remove(self)
        self = None
        

class Tank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.direction = "north"
        self.shot_busy = False
        self.health = 3
        
        self.setPixmap(QPixmap(objects["tankPlayer"][1]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(lambda: self.move(self.direction))

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

    def shoot(self):
        if not self.shot_busy:
            bullet = Bullet(self, self.direction, pos=(self.row, self.col), parent=self.gameInterface)
            bullet._move()

    def health_down(self):
        self.health -= 1
        if self.health == 0:
            self.destroyed()     

    def destroyed(self):
        self.gameInterface.main.reset_game()
        self.gameInterface.main.setCurrentIndex(3)
    
    def _keyPressEvent(self, e):
        key = e.key()
        if key in moveKeys:
            self.move(moveKeys[key])
        elif key in actionKeys:
            self.shoot()


class Bullet(QLabel):
    def __init__(self, owner, direction, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.owner = owner
        self.direction = direction
        self.row, self.col = pos
        self.r, self.c = directions[self.direction][1]
        self.row, self.col = self.row + self.r, self.col + self.c
        self.speed = 40

        self.speed_timer = QTimer(self)
        self.speed_timer.timeout.connect(self._move)
        self.speed_timer.start(self.speed)  # CКОРОСТЬ ПУЛИ В МС

        self.setPixmap(rotate_pixmap(QPixmap(objects['bullet'][1]), directions[self.direction][0]))
        scaling(self, 30, 30)
        self.setScaledContents(True)
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _move(self):
        self.owner.shot_busy = True
        new_row, new_col = self.row, self.col
        if chosenField[new_row][new_col] == 0:
            self.gameInterface.gameField.addWidget(self, new_row, new_col, alignment=Qt.AlignmentFlag.AlignCenter)
            chosenField[new_row][new_col] = 111
            chosenField[self.row][self.col] = 0
            self.row, self.col = self.row + self.r, self.col + self.c
            return
        else:
            self.collision(new_row, new_col)

    def collision(self, new_row, new_col):
        if (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.fieldObjects:
            widget.destroyed()
            chosenField[new_row][new_col] = 0
        elif (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.enemies:
            widget.health_down()
            chosenField[new_row][new_col] = 0
        self.deleteLater()
        self.owner.shot_busy = False
    
    def pause(self, state: bool):
        if state:
            self.speed_timer.stop()
        else:
            self.speed_timer.start(self.speed)


class EnemyTank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)

        self.dir_list = ['north', 'east', 'south', 'west']

        self.gameInterface = parent
        self.direction = random.choices(self.dir_list)[0]
        self.shot_busy = False
        self.health = 1
        self.speed = 100
        self.shot_freq = 100
        
        self.setPixmap(rotate_pixmap(QPixmap(objects["tankEnemy"][1]), directions[self.direction][0]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.move_timer = QTimer()
        self.gameInterface.timers.append(self.move_timer)
        self.shot_timer = QTimer()

        self.move_timer.timeout.connect(self.move)
        self.shot_timer.timeout.connect(self.shoot)
        self.move_timer.start(self.speed)
        self.shot_timer.start(self.shot_freq)


    def move(self):
        weights = [10, 30, 50, 10]
        
        self.direction = random.choices(self.dir_list)[0]

        r, c = directions[self.direction][1]
        new_row, new_col = self.row + r, self.col + c

        if chosenField[new_row][new_col] == 0 and self.direction == self.direction:
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[self.row][self.col] = 0
            chosenField[new_row][new_col] = 11
            self.row, self.col = new_row, new_col

        self.setPixmap(rotate_pixmap(QPixmap(objects["tankEnemy"][1]), directions[self.direction][0]))

    def shoot(self):
        if not self.shot_busy:
            bullet = Bullet(self, self.direction, pos=(self.row, self.col), parent=self.gameInterface)
            bullet._move()

    def health_down(self):
        self.health -= 1
        if self.health == 0:
            self.destroyed()       

    def pause(self, state):
        if state:
            self.move_timer.stop()
            self.shot_timer.stop()
        else:
            self.move_timer.start(self.speed)
            self.shot_timer.start(self.shot_freq)

    def destroyed(self):
        self.deleteLater()
        self.gameInterface.enemies.remove(self)
        self = None
        

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
        if senderName == 'pause':
            self.main.pagesStack.setCurrentIndex(1)
            #self.main.game.
        elif senderName == 'resume':
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
        elif senderName == 'home':
            self.main.pagesStack.setCurrentIndex(0)
        elif senderName == 'replay':
            self.main.pause.clear_layout()
            # self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            # self.main.reset_game()
        elif senderName == 'play':
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.reset_game()
        elif senderName == 'exit':
            self.main.close()


def reset_game_state():
    global field, chosenField
    field = read_from_json()
    if field is None:
        return
    chosenField = field.get(field_key, chosenField)


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


# ОЧИСТКА ТЕРМИНАЛА И ВЫВОД МАТРИЦЫ
def show(self):
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in chosenField:
        for j in i:
            print(j, end='  ')
        print()


def scaling(image, w, h):
    image = image
    screen = QGuiApplication.primaryScreen()
    screenSize = screen.size()
    screenWidth = screenSize.width()
    
    if 1920 == screenWidth:
        image.setFixedSize(w, h)  
    if 1280 == screenWidth:
        image.setFixedSize(round(w * (1280/1920)), round(h * (1280/1920)))


def handle_qt_messages(msg_type, context, message):  #QPainter ругается из-за QPixmap в setup_mainMenu, поэтому таким незамысловатым образом мы пропускаем эту ошибку. 
    if msg_type == QtMsgType.QtWarningMsg:
        return  # Игнорируем предупреждения
    print(message)  # Выводим остальные сообщения
qInstallMessageHandler(handle_qt_messages)


# Старт самой программы (святыня) (НЕ ТРОГАТЬ!!!)        
if __name__ == '__main__':  # нужно чтобы программа запускалась именно из этого файла, а не из других. Типо инкапсуляция.
    app = QApplication(sys.argv)
    start = WindowMain()
    #start.show()
    start.showFullScreen()
    app.exec()