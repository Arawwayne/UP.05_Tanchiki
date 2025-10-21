import sys, json, time, random, os
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QPushButton, QFrame, QLabel, QVBoxLayout, 
                             QWidget, QStackedWidget, QMainWindow, QHBoxLayout, QGridLayout,
                             QSpacerItem, QSizePolicy)


"""
3 макета карты, 
4 усиления (вместе с картинками): неуязвимость на несколько секунд; пробивающие стены снаряды; двойной урон у снарядов; дополнительная жизнь.
появление врагов с переодичностью в шесть секунд, 
статистика боя, 
пауза
"""


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
objects_pics = {
    "bullet": "data/bullet.png",
    "wall1": "data/wall.png",
    "wall2": "data/wall2.png",
    'water': 'data/water.png',
    'bush': 'data/bush.png',
    "unWall": 'data/unWall.png',
    'base': 'data/baza.png',
    "tankPlayer": "data/tankMain.png",
    "tankEnemy1": 'data/Enemy1.png',
    "tankEnemy2": 'data/Enemy2.png',
    "tankEnemy3": 'data/Enemy3.png',
    "tankEnemy4": 'data/Enemy4.png',
}

solid_objects = {
    "wall1": 1,
    'wall2': 2,
    "unWall": 8,
    'base': 9, 
    "tankPlayer": 10, 
    "bullet": 111,
}

nonsolid_objects = {
    'air': 0,
    'water': 3,
    'bush': 4,
}


enemies_objects = {
    "tankEnemy1": 11,
    "tankEnemy2": 12,
    "tankEnemy3": 13,
    "tankEnemy4": 14,
}

# Картинки с ссылками на их изображения
pictures = {
    'play': 'data/playButton.png',
    'exit': 'data/exitButton.png',
    'replay': 'data/replayButton.png',
    'title': 'data/title.png',
    'pause': 'data/pause.png',
    'pause_title': 'data/pause_title.png',
    'home': 'data/home.png',
    'win': 'data/win.png',
    'lose': 'data/lose.png',
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


class WindowMain(QMainWindow):  # Класс главного окна или рамки, в которую мы будем вставлять виджет с формой меню или игрового интерфейса
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
        self.end = EndScreen(parent=self)
        self.game = GameInterface(parent=self)

        self.pagesStack.addWidget(self.menu)
        self.pagesStack.addWidget(self.pause)
        self.pagesStack.addWidget(self.end)
        self.pagesStack.addWidget(self.game)

        # Вставляем стэк в рамку. Тк меню был введён в стэк первым, то оно и будет показываться
        self.setCentralWidget(self.pagesStack)
        self.pagesStack.setCurrentIndex(0)

    def reset_game(self):
        reset_game_state()
        new_game = GameInterface(parent=self)
        self.pagesStack.removeWidget(self.game)
        self.game.deleteLater()
        self.game = new_game
        self.pagesStack.addWidget(self.game)
        self.pagesStack.setCurrentIndex(self.pagesStack.count() - 1)

    def end_state(self, win:bool):
        new_end = EndScreen(win, parent=self)
        self.pagesStack.removeWidget(self.end)
        self.end.deleteLater()
        self.end = new_end
        self.pagesStack.insertWidget(2, self.end)
        self.pagesStack.setCurrentIndex(2)
        

    def keyPressEvent(self, e):  # Обработка нажатия клавиш, которая передаётся в класс Tank
        self.game.tank._keyPressEvent(e)
        return super().keyPressEvent(e)


class Menu(QWidget):  # Меню
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.main = parent
        self.title_pixmap = QPixmap(pictures['title'])
        self.exit_pixmap = QPixmap(pictures['exit'])
        self.start_pixmap = QPixmap(pictures['play'])
        self.setup_ui()

    def setup_ui(self):
        mainLayout = QVBoxLayout()
        ro1 = QGridLayout()
        row2 = QHBoxLayout()
        
        title = QLabel()
        title.setPixmap(self.title_pixmap)
        scaling(title, 1000, 200)
        title.setScaledContents(True)
        
        exitButton = ClickableImages(self.exit_pixmap, 'exit', parent = self.main)
        scaling(exitButton, 200, 200)
        exitButton.setScaledContents(True)
        
        startButton = ClickableImages(self.start_pixmap, "play", parent = self.main)
        scaling(startButton, 500, 500)
        startButton.setScaledContents(True)

        ro1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ro1.addWidget(exitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        row2.addWidget(startButton)
        
        mainLayout.addLayout(ro1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)


class EndScreen(QWidget):  # Экран конца игры. Если победа, то показывает победу, если поражение – соответсвенно
    def __init__(self, win=None, parent = None):
        super().__init__(parent)
        
        self.main = parent
        self.home_pixmap = QPixmap(pictures['home'])
        self.replay_pixmap = QPixmap(pictures['replay'])
        self.lose_pixmap = QPixmap(pictures['lose'])
        self.win_pixmap = QPixmap(pictures['win'])
        self.next_pixmap = QPixmap(pictures['play'])

        self.setup_ui(win)

    def setup_ui(self, win):
        self.mainLayout = QVBoxLayout()
        stats_buttons_row = QHBoxLayout()
        
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
        homeButton = ClickableImages(self.home_pixmap, 'home', parent = self.main)
        scaling(homeButton, 200, 200)
        homeButton.setScaledContents(True)

        replayButton = ClickableImages(self.replay_pixmap, "replay", parent = self.main)
        scaling(replayButton, 200, 200)
        replayButton.setScaledContents(True)

        buttons_layout = QVBoxLayout()
        buttons1_layout = QHBoxLayout()

        buttons_layout.addLayout(buttons1_layout)
        buttons1_layout.addWidget(replayButton)
        buttons1_layout.addWidget(homeButton)


        if not win:
            # Заголовок с поражением/победой
            title = QLabel()
            title.setPixmap(self.lose_pixmap)       
            scaling(title, 1000, 200)       
            title.setScaledContents(True)
        else:
            title = QLabel()
            title.setPixmap(self.win_pixmap)       
            scaling(title, 1000, 200)       
            title.setScaledContents(True)

            nextButton = ClickableImages(self.next_pixmap, "resume", parent = self.main)
            scaling(nextButton, 500, 500)
            nextButton.setScaledContents(True)

            buttons_layout.addWidget(nextButton)

        # Вставляем всё что надо
        self.mainLayout.addWidget(title)
        self.mainLayout.addLayout(stats_buttons_row)


        stats_buttons_row.addWidget(frame_kills)
        stats_buttons_row.addWidget(frame_pickups)
        stats_buttons_row.addLayout(buttons_layout)

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


class PauseScreen(QWidget):  # Пауза
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main = parent
        mainLayout = QVBoxLayout()
        ro1 = QGridLayout()
        row2 = QHBoxLayout()
        
        self.title_pixmap = QPixmap(pictures['pause_title'])
        self.resume_pixmap = QPixmap(pictures['play'])
        self.home_pixmap = QPixmap(pictures['home'])
        self.replay_pixmap = QPixmap(pictures['replay'])
        
        title = QLabel()
        title.setPixmap(QPixmap(pictures['pause_title']))
        scaling(title, 1000, 200)
        title.setScaledContents(True)
        
        resumeButton = ClickableImages(pictures['play'], 'resume', parent = self.main)
        scaling(resumeButton, 500, 500)
        resumeButton.setScaledContents(True)

        homeButton = ClickableImages(pictures['home'], 'home', parent = self.main)
        scaling(homeButton, 200, 200)
        homeButton.setScaledContents(True)

        replayButton = ClickableImages(pictures['replay'], "replay", parent = self.main)
        scaling(replayButton, 500, 500)
        replayButton.setScaledContents(True)

        ro1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        ro1.addWidget(homeButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        row2.addWidget(resumeButton)
        row2.addWidget(replayButton)
        
        
        #mainLayout.addLayout(row1)
        mainLayout.addLayout(ro1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)


class GameInterface(QWidget):  # Класс игрового интерфейса. Здесь будет очерчено игровое поле с помощью матрицы и UI по состоянию и возможностям игрока
    def __init__(self, parent = None):
        super().__init__(parent)

        self.fieldObjects = []
        self.fieldNonObjects = []
        self.enemies = []
        self.timers = []

        self.pause_pixmap = QPixmap(pictures['pause'])

        self.main = parent
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
                    #     self.space.setPixmap(objects_pics["air"][1])
                    #     scaling(self.space, 60, 60)
                    #     self.space.setScaledContents(True)
                    #     # space = QSpacerItem(60, 60, QSizePolicy.Policy.Fixed)
                    #     self.gameField.addWidget(self.space, curRow, curCol)
                    
                    case x if x == solid_objects['wall1']: 
                        self.wall = Wall1(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)

                    case x if x == solid_objects['wall2']: 
                        self.wall = Wall2(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)
                    
                    case x if x == solid_objects['unWall']: 
                        self.unWall = Wall3(parent=self)
                        self.gameField.addWidget(self.unWall, curRow, curCol)
                    
                    case x if x == nonsolid_objects['bush']:
                        self.bush = Bush(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.bush, curRow, curCol)
                        self.fieldNonObjects.append(self.bush)

                    case x if x == nonsolid_objects['water']:
                        self.water = Water(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.water, curRow, curCol)
                        self.fieldNonObjects.append(self.water)


                    case x if x == solid_objects['base']:
                        base = QLabel()
                        base.setPixmap(QPixmap(objects_pics['base']))
                        base.setScaledContents(True)
                        self.gameField.addWidget(base, curRow, curCol)

                    case x if x == solid_objects['tankPlayer']: 
                        self.tank = Tank(pos=(curRow, curCol), parent=self) 
                        self.gameField.addWidget(self.tank, curRow, curCol)

                    case x if x == enemies_objects['tankEnemy1']:
                        self.enemy = EnemyTank1(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy, curRow, curCol)
                        self.enemies.append(self.enemy)
                    
                    case x if x == enemies_objects['tankEnemy2']:
                        self.enemy2 = EnemyTank2(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy2, curRow, curCol)
                        self.enemies.append(self.enemy2)
                
                    case x if x == enemies_objects['tankEnemy3']:
                        self.enemy3 = EnemyTank3(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy3, curRow, curCol)
                        self.enemies.append(self.enemy3)

                    case x if x == enemies_objects['tankEnemy4']:
                        self.enemy4 = EnemyTank4(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy4, curRow, curCol)
                        self.enemies.append(self.enemy4)


        pauseButton = ClickableImages(self.pause_pixmap, 'pause', parent = self.main)
        scaling(pauseButton, 200, 600)
        pauseButton.setScaledContents(True)
        interface.addWidget(pauseButton, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)


class Bush(QLabel):
    def __init__(self, pos=None, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.row, self.col = pos

        self.bush_pixmap = QPixmap(objects_pics['bush'])
        self.setPixmap(self.bush_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)


class Water(QLabel):
    def __init__(self, pos=None, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.row, self.col = pos

        self.water_pixmap = QPixmap(objects_pics['water'])
        self.setPixmap(self.water_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)


class Wall(QLabel):
    def __init__(self, pos=None, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.row, self.col = pos

    def health_down(self):
        self.health -= 1
        chosenField[self.row][self.col] = 0
        if self.health == 0:
            self.destroyed()       

    def destroyed(self):
        self.deleteLater()
        self.gameInterface.fieldObjects.remove(self)
        self = None

class Wall1(Wall):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)
        self.health = 1
        self.row, self.col = pos

        self.wall_pixmap = QPixmap(objects_pics['wall1'])
        self.setPixmap(self.wall_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)
      
class Wall2(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)
        self.health = 2
        self.row, self.col = pos

        self.wall_pixmap = QPixmap(objects_pics['wall2'])
        self.setPixmap(self.wall_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)

class Wall3(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wall_pixmap = QPixmap(objects_pics['unWall'])
        self.setPixmap(self.wall_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)


class Tank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.direction = "north"
        self.shot_busy = False
        self.health = 3
        self.tank_pixmap = QPixmap(objects_pics['tankPlayer'])
        
        self.setPixmap(self.tank_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(lambda: self.move(self.direction))
        self.gameInterface.timers.append(self.move_timer)

        self.cell_new = 0

    def move(self, direction):
        self.setVisible(True)
        r, c = directions[direction][1]
        new_row, new_col = self.row + r, self.col + c


        if (chosenField[new_row][new_col] in list(nonsolid_objects.values()) and chosenField[new_row][new_col] != nonsolid_objects['water']) and direction == self.direction:
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[self.row][self.col] = self.cell_new
            self.cell_new = chosenField[new_row][new_col]
            chosenField[new_row][new_col] = solid_objects['tankPlayer']
            self.row, self.col = new_row, new_col        

        if self.cell_new == 4:
            self.setVisible(False)

        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[direction][0]))
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
        self.gameInterface.main.end_state(False)

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
        self.speed = 50
        self.bullet_pixmap = QPixmap(objects_pics['bullet'])

        self.speed_timer = QTimer(self)
        self.speed_timer.timeout.connect(self._move)                                                                                                                                                                                                                                                                                                                                                                

        self.speed_timer.start(self.speed)  # CКОРОСТЬ ПУЛИ В МС

        self.setPixmap(rotate_pixmap(self.bullet_pixmap, directions[self.direction][0]))
        scaling(self, 30, 30)
        self.setScaledContents(True)
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _move(self):
        self.owner.shot_busy = True
        new_row, new_col = self.row, self.col
        if chosenField[new_row][new_col] in list(nonsolid_objects.values()):
            self.gameInterface.gameField.addWidget(self, new_row, new_col, alignment=Qt.AlignmentFlag.AlignCenter)
            # chosenField[new_row][new_col] = 111
            # chosenField[self.row][self.col] = 0
            self.row, self.col = self.row + self.r, self.col + self.c
            return
        else:
            self.collision(new_row, new_col)

    def collision(self, new_row, new_col):
        if (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.fieldObjects:
            widget.health_down()
        elif self.owner == self.gameInterface.tank:
            if (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.enemies:
                widget.health_down()
        elif widget == self.gameInterface.tank:
            widget.health_down()
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

        self.gameInterface = parent
        self.row, self.col = pos
        self.cell_new = 0

    def move(self):
        self.setVisible(True)
        weights = [10, 10, 10, 10]
        weights[self.dir_list.index(self.direction)] = 90
        self.direction = random.choices(self.dir_list, weights=weights, k=1)[0]

        r, c = directions[self.direction][1]
        new_row, new_col = self.row + r, self.col + c

        if (chosenField[new_row][new_col] in list(nonsolid_objects.values()) and chosenField[new_row][new_col] != nonsolid_objects['water']):
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[self.row][self.col] = self.cell_new
            self.cell_new = chosenField[new_row][new_col]
            chosenField[new_row][new_col] = 11
            self.row, self.col = new_row, new_col
        
        if self.cell_new == 4:
            self.setVisible(False)
        # elif chosenField[new_row][new_col] in list(solid_objects.values()):
        #     self.setPixmap(rotate_pixmap(QPixmap(objects_pics["tankEnemy"]), directions[self.dir_list[self.dir_list.index(self.direction) - 1]][0]))

        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        
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
        chosenField[self.row][self.col] = 0
        self.gameInterface.enemies.remove(self)
        if len(self.gameInterface.enemies) == 0:
            self.gameInterface.main.end_state(True)
        self = None

class EnemyTank1(EnemyTank):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)

        self.dir_list = ['north', 'east', 'south', 'west']

        self.gameInterface = parent
        self.direction = random.choices(self.dir_list)[0]
        self.shot_busy = False
        self.health = 1
        self.speed = 1200
        self.shot_freq = 1500
        self.tank_pixmap = QPixmap(objects_pics["tankEnemy1"])
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
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

class EnemyTank2(EnemyTank):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)

        self.dir_list = ['north', 'east', 'south', 'west']

        self.gameInterface = parent
        self.direction = random.choices(self.dir_list)[0]
        self.shot_busy = False
        self.health = 2
        self.speed = 1000
        self.shot_freq = 1200
        self.tank_pixmap = QPixmap(objects_pics["tankEnemy2"])
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
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

class EnemyTank3(EnemyTank):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)

        self.dir_list = ['north', 'east', 'south', 'west']

        self.gameInterface = parent
        self.direction = random.choices(self.dir_list)[0]
        self.shot_busy = False
        self.health = 1
        self.speed = 500
        self.shot_freq = 1500
        self.tank_pixmap = QPixmap(objects_pics["tankEnemy3"])
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
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

class EnemyTank4(EnemyTank):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)

        self.dir_list = ['north', 'east', 'south', 'west']

        self.gameInterface = parent
        self.direction = random.choices(self.dir_list)[0]
        self.shot_busy = False
        self.health = 3
        self.speed = 2000
        self.shot_freq = 2200
        self.tank_pixmap = QPixmap(objects_pics["tankEnemy4"])
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
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
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.reset_game()
        elif senderName == 'play':
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.reset_game()
        elif senderName == 'exit':
            self.main.close()


def reset_game_state():  # Переприсваиваем field макет, чтобы перезапустить игру
    global field, chosenField
    field = read_from_json()
    if field is None:
        return
    chosenField = field.get(field_key, chosenField)


def rotate_pixmap(pixmap, angle):  # Повернуть изображение под angle-углом
    rotated = QPixmap(pixmap)
    rotated.fill(Qt.GlobalColor.transparent)  # Прозрачный фон
    painter = QPainter(rotated)
    painter.translate(rotated.width() / 2, rotated.height() / 2)
    painter.rotate(angle)
    painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return rotated


def find_widget(layout, row, column):  # Найти виджет в layout по координатам
    """Найти виджет по позиции (строка, колонка)"""
    item = layout.itemAtPosition(row, column)
    if item and item.widget():
        return item.widget()


def get_widgets(layout):  # Получить виджет из layout
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


def show():  # ОЧИСТКА ТЕРМИНАЛА И ВЫВОД МАТРИЦЫ
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