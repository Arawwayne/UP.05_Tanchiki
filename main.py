import sys, json, random, os
from PyQt6.QtCore import Qt, QtMsgType, QPoint, qInstallMessageHandler, QTimer, QElapsedTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette, QGuiApplication, QTransform, QKeyEvent, QFont
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
    'invincible': 'data/invincible.png',
    'pierce': 'data/pierce.png',
    'dd': 'data/dd.png',
    'hp': 'data/hp.png',
}

solid_objects = {
    "wall1": 1,
    'wall2': 2,
    "unWall": 8,
    'base': 9, 
    "tankPlayer": 10, 
    "tankEnemy1": 11,
    "tankEnemy2": 12,
    "tankEnemy3": 13,
    "tankEnemy4": 14,
}

nonsolid_objects = {
    'air': 0,
    'water': 3,
    'bush': 4,
    'invincible': 21,
    'pierce': 22,
    'dd': 23,
    'hp': 24,
}

enemies_objects = {
    "tankEnemy1": 11,
    "tankEnemy2": 12,
    "tankEnemy3": 13,
    "tankEnemy4": 14,
    'invincible': 21,
    'pierce': 22,
    'dd': 23,
    'hp': 24,
}

pickups_objects = {
    'invincible': 21,
    'pierce': 22,
    'dd': 23,
    'hp': 24,
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

stats = {
    21: 0,
    22: 0,
    23: 0,
    24: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
}


# Матрица поля 18 на 25
rows = 18
collumns = 25

field = read_from_json()

field_keys = ['field1', 'field2', 'field3']
field_enemies_keys = ["field1_enemies", "field2_enemies", "field3_enemies"]
lvl = 0

chosenField = field[field_keys[lvl]]
chosenEnemies = field[field_enemies_keys[lvl]]

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
        self.end_game = EndGame(parent=self)
        self.game = GameInterface(parent=self)

        self.pagesStack.addWidget(self.menu)
        self.pagesStack.addWidget(self.pause)
        self.pagesStack.addWidget(self.end)
        self.pagesStack.addWidget(self.end_game)
        self.pagesStack.addWidget(self.game)

        # Вставляем стэк в рамку. Тк меню был введён в стэк первым, то оно и будет показываться
        self.setCentralWidget(self.pagesStack)
        self.pagesStack.setCurrentIndex(0)

        self.paused = False

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
        key = e.key()
        if key == Qt.Key.Key_Escape :
            match self.pagesStack.currentIndex():
                case x if x == self.pagesStack.count() - 1:
                    self.game._keyPressEvent(e)
                    return super().keyPressEvent(e)
                case x if x in [1, 2, 3]:
                    self.pagesStack.setCurrentIndex(0)
                case x if x == 0:
                    self.close()
        if not self.paused:
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
        temp = QLabel('Уничтожено танков')
        font = QFont()
        font.setPointSize(30)
        temp.setFont(font)
        frame_kills_layout.addWidget(temp, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_kills_layout.addLayout(self.pics('tankEnemy1'))
        frame_kills_layout.addLayout(self.pics('tankEnemy2'))
        frame_kills_layout.addLayout(self.pics('tankEnemy3'))
        frame_kills_layout.addLayout(self.pics('tankEnemy4'))

        frame_pickups_layout = QVBoxLayout()
        temp = QLabel('Подобрано усилений')
        font = QFont()
        font.setPointSize(30)
        temp.setFont(font)
        frame_pickups_layout.addWidget(temp, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_pickups_layout.addLayout(self.pics('invincible'))
        frame_pickups_layout.addLayout(self.pics('pierce'))
        frame_pickups_layout.addLayout(self.pics('dd'))
        frame_pickups_layout.addLayout(self.pics('hp'))

        frame_kills.setLayout(frame_kills_layout)
        frame_pickups.setLayout(frame_pickups_layout)

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

            nextButton = ClickableImages(self.next_pixmap, "next", parent = self.main)
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

    def pics(self, id):
        temp = QHBoxLayout()
        temp1 = QLabel()
        temp1.setPixmap(QPixmap(objects_pics[id]))
        scaling(temp1, 60, 60)
        temp1.setScaledContents(True)
        temp.addWidget(temp1)

        temp2 = QLabel(f'{stats[enemies_objects[id]]}')
        font = QFont()
        font.setPointSize(30)
        temp2.setFont(font)
        temp.addWidget(temp2)
        temp.setSpacing(50)
        return temp

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

class EndGame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main = parent

        self.title_pixmap = QPixmap(pictures['win'])
        self.exit_pixmap = QPixmap(pictures['home'])

        mainLayout = QVBoxLayout()
        row1 = QGridLayout()
        row2 = QHBoxLayout()

        title = QLabel()
        title.setPixmap(self.title_pixmap)
        scaling(title, 1000, 200)
        title.setScaledContents(True)
        
        exitButton = ClickableImages(self.exit_pixmap, 'home', parent = self.main)
        scaling(exitButton, 200, 200)
        exitButton.setScaledContents(True)

        row1.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        row1.addWidget(exitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        text = QLabel(
        'Вы победили! Уровни кончились, поэтому можете выходить из игры. \n' \
        'Либо же начать заного.'
        )
        font = QFont()
        font.setPointSize(40)
        text.setFont(font)

        row2.addWidget(text, alignment=Qt.AlignmentFlag.AlignCenter)
        
        mainLayout.addLayout(row1)
        mainLayout.addLayout(row2)
        self.setLayout(mainLayout)

class GameInterface(QWidget):  # Класс игрового интерфейса. Здесь будет очерчено игровое поле с помощью матрицы и UI по состоянию и возможностям игрока
    def __init__(self, parent = None):
        super().__init__(parent)

        self.fieldObjects = []
        self.fieldNonObjects = []
        self.temp = []
        self.enemies = []

        self.main = parent
        self.pause_pixmap = QPixmap(pictures['pause'])

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.start_spawn)
        self.execution = len(chosenEnemies)
        self.enemy_all = self.execution
        self.curExecution = 0
        self.spawn_timer.start(5000)
        
        mainLayout = QHBoxLayout()
        self.gameField = QGridLayout()
        self.gameField.setSpacing(0) 
        interface = QVBoxLayout()
        

        # Сканируем матрицу и в соответствии с ней, отображаем объекты на поле
        for curRow in range(rows):
            for curCol in range(collumns):
                match chosenField[curRow][curCol]:
                    case x if x == solid_objects['wall1']: 
                        self.wall = Wall1(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)

                    case x if x == solid_objects['wall2']: 
                        self.wall = Wall2(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.wall, curRow, curCol)
                        self.fieldObjects.append(self.wall)
                    
                    case x if x == solid_objects['unWall']: 
                        self.unWall = Wall3(pos=(curRow, curCol), parent=self)
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

                    case x if x in list(enemies_objects.values()):
                        match x:
                            case y if y == enemies_objects['tankEnemy1']:
                                self.enemy = EnemyTank1(pos=(curRow, curCol), parent=self)
                            case y if y == enemies_objects['tankEnemy2']:
                                self.enemy = EnemyTank2(pos=(curRow, curCol), parent=self)
                            case y if y == enemies_objects['tankEnemy3']:
                                self.enemy = EnemyTank3(pos=(curRow, curCol), parent=self)
                            case y if y == enemies_objects['tankEnemy4']:
                                self.enemy = EnemyTank4(pos=(curRow, curCol), parent=self)
                        self.gameField.addWidget(self.enemy, curRow, curCol)
                        self.enemies.append(self.enemy)
                        
        # Кнопка паузы
        self.pauseButton = ClickableImages(self.pause_pixmap, 'pause', parent = self.main)
        scaling(self.pauseButton, 400, 180)
        self.pauseButton.setScaledContents(True)

        # Фрейм с хп
        self.health_frame = QFrame()
        self.health_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.health_frame.setLineWidth(2)
        self.health_frame.setMidLineWidth(3)
        scaling(self.health_frame, 400, 200)
        self.pauseButton.setScaledContents(True)

        self.health_frame_layout = QHBoxLayout()

        self.health = QLabel(f'{self.tank.health} ♥') 
        font = QFont()
        font.setPointSize(120)
        self.health.setFont(font)

        self.health_frame_layout.addWidget(self.health, alignment=Qt.AlignmentFlag.AlignCenter)
        self.health_frame.setLayout(self.health_frame_layout)

        # Фрейм с врагами
        self.enemy_frame = QFrame()
        self.enemy_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.enemy_frame.setLineWidth(2)
        self.enemy_frame.setMidLineWidth(3)
        scaling(self.enemy_frame, 400, 300)
        self.pauseButton.setScaledContents(True)

        self.enemy_frame_layout = QHBoxLayout()

        self.enemy_count = QLabel(f'{self.enemy_all}')
        font = QFont()
        font.setPointSize(120)
        self.enemy_count.setFont(font)

        enemy_pic = QPixmap(objects_pics['tankEnemy1'])
        enemy_pic_1 = QLabel()
        enemy_pic_1.setPixmap(enemy_pic)
        scaling(enemy_pic_1, 100, 100)
        enemy_pic_1.setScaledContents(True)

        self.enemy_frame_layout.addWidget(self.enemy_count, alignment=Qt.AlignmentFlag.AlignCenter)
        self.enemy_frame_layout.addWidget(enemy_pic_1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.enemy_frame.setLayout(self.enemy_frame_layout)

        # Фрейм с усилениями
        self.pickups_frame = QFrame()
        self.pickups_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.pickups_frame.setLineWidth(2)
        self.pickups_frame.setMidLineWidth(3)
        scaling(self.pickups_frame, 400, 300)
        self.pauseButton.setScaledContents(True)

        self.pickups_frame_layout = QHBoxLayout()
        self.pickups_frame.setLayout(self.pickups_frame_layout)

        interface.addWidget(self.pauseButton, alignment=Qt.AlignmentFlag.AlignTop)
        interface.addWidget(self.health_frame, alignment=Qt.AlignmentFlag.AlignTop)
        interface.addWidget(self.enemy_frame, alignment=Qt.AlignmentFlag.AlignTop)
        interface.addWidget(self.pickups_frame, alignment=Qt.AlignmentFlag.AlignTop)

        
        mainLayout.addLayout(self.gameField)
        mainLayout.addLayout(interface)
        self.setLayout(mainLayout)


    def health_update(self):
        if not self.tank.invincible:
            self.health.setText(f'{self.tank.health} ♥')
        else:
            self.health.setText(f'∞ ♥')

    def enemy_update(self):
        self.enemy_count.setText(f'{self.enemy_all}')

    def pickups_update(self):
        return

    def start_spawn(self):
        row, col = random.randint(1, 2), random.randint(1, 23)
        if chosenField[row][col] == 0:
            self.enemy = get_tank_id(chosenEnemies[self.curExecution])(pos=(row, col), parent=self)
            chosenField[row][col] = self.enemy.id
            self.gameField.addWidget(self.enemy, row, col)
            self.enemies.append(self.enemy)
            self.curExecution += 1
            if self.curExecution == self.execution:
                self.spawn_timer.stop()
        else:
            self.start_spawn()


    def pause(self, paused):
        if paused:
            self.spawn_timer.stop()
        else:
            self.spawn_timer.start()
        self.main.paused = paused
        for enemy in self.enemies:
            enemy.pause(paused)
        for t in self.temp:
            t.pause(paused)

    def _keyPressEvent(self, e):
        key = e.key()
        self.pauseButton.on_click('pause')
        

class PickUp(QLabel):
    def __init__(self, pos=None, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.row, self.col = pos

        QTimer().singleShot(10000, self.destroyed)

    def pics(self, pic):
        self.temp = QLabel()
        self.temp.setPixmap(pic)
        scaling(self.temp, 100, 100)
        self.temp.setScaledContents(True)
        self.gameInterface.pickups_frame_layout.addWidget(self.temp)

        

    def destroyed(self):
        self.deleteLater()
        self = None

class Invincible(PickUp):
    def __init__(self, pos=None, parent=None):
        super().__init__(pos, parent)

        self.inv_pixmap = QPixmap(objects_pics['invincible'])
        self.setPixmap(self.inv_pixmap)
        scaling(self, 45, 45)
        self.setScaledContents(True)

    def start(self):
        self.gameInterface.tank.invincible = True
        self.gameInterface.health_update()
        QTimer.singleShot(10000, lambda: self.over())
        stats[pickups_objects['invincible']] += 1
        self.pics(self.inv_pixmap)
        self.destroyed()
    def over(self):
        self.gameInterface.tank.invincible = False
        self.gameInterface.health_update()
        try:
            self.gameInterface.pickups_frame_layout.removeWidget(self.temp)
        except:
            return
    
class Pierce(PickUp):
    def __init__(self, pos=None, parent=None):
        super().__init__(pos, parent)

        self.inv_pixmap = QPixmap(objects_pics['pierce'])
        self.setPixmap(self.inv_pixmap)
        scaling(self, 45, 45)
        self.setScaledContents(True)

    def start(self):
        self.gameInterface.tank.pierce = True
        QTimer.singleShot(10000, lambda: self.over())
        stats[pickups_objects['pierce']] += 1
        self.pics(self.inv_pixmap)
        self.destroyed()
    def over(self):
        self.gameInterface.tank.pierce = False
        try:
            self.gameInterface.pickups_frame_layout.removeWidget(self.temp)
        except:
            return
 
class DoubleDamage(PickUp):
    def __init__(self, pos=None, parent=None):
        super().__init__(pos, parent)

        self.inv_pixmap = QPixmap(objects_pics['dd'])
        self.setPixmap(self.inv_pixmap)
        scaling(self, 45, 45)
        self.setScaledContents(True)

    def start(self):
        self.gameInterface.tank.dmg += 1
        stats[pickups_objects['dd']] += 1
        QTimer.singleShot(10000, lambda: self.over())
        self.pics(self.inv_pixmap)
        self.destroyed()
    def over(self):
        self.gameInterface.tank.dmg -= 1
        try:
            self.gameInterface.pickups_frame_layout.removeWidget(self.temp)
        except:
            return
        
class HealthPoint(PickUp):
    def __init__(self, pos=None, parent=None):
        super().__init__(pos, parent)

        self.inv_pixmap = QPixmap(objects_pics['hp'])
        self.setPixmap(self.inv_pixmap)
        scaling(self, 45, 45)
        self.setScaledContents(True)

    def start(self):
        self.gameInterface.tank.health += 1
        self.gameInterface.health_update()
        stats[pickups_objects['hp']] += 1
        self.destroyed()
        

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

    def spawn_pickups(self):
        pickups = ['invincible','pierce','dd','hp']
        weights = [25, 10, 30, 40]

        match random.choices(pickups, weights=weights, k=1)[0]:
            case x if x == 'invincible':
                self.pickup = Invincible(pos=(self.row, self.col), parent=self.gameInterface)
            case x if x == 'pierce':
                self.pickup = Pierce(pos=(self.row, self.col), parent=self.gameInterface)
            case x if x == 'dd':
                self.pickup = DoubleDamage(pos=(self.row, self.col), parent=self.gameInterface)
            case x if x == 'hp':
                self.pickup = HealthPoint(pos=(self.row, self.col), parent=self.gameInterface)
        self.gameInterface.gameField.addWidget(self.pickup, self.row, self.col, alignment=Qt.AlignmentFlag.AlignCenter)
        chosenField[self.row][self.col] = pickups_objects[x]

    def health_down(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            chosenField[self.row][self.col] = 0
            self.destroyed()       

    def destroyed(self):
        self.deleteLater()
        self.gameInterface.fieldObjects.remove(self)
        if random.random() < 0.05:
            self.spawn_pickups()
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
      
class Wall2(Wall):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)
        self.health = 2
        self.row, self.col = pos

        self.wall_pixmap = QPixmap(objects_pics['wall2'])
        self.setPixmap(self.wall_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)

class Wall3(Wall):
    def __init__(self, pos, parent=None):
        super().__init__(pos, parent)
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
        self.pierce = False
        self.dmg = 1
        self.invincible = False
        
        
        self.setPixmap(self.tank_pixmap)
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.cell_new = 0

    def move(self, direction):
        self.setVisible(True)
        r, c = directions[direction][1]
        new_row, new_col = self.row + r, self.col + c
            
        if (chosenField[new_row][new_col] not in list(solid_objects.values()) and chosenField[new_row][new_col] != nonsolid_objects['water']) and direction == self.direction:
            if chosenField[new_row][new_col] in list(pickups_objects.values()):
                pickup = find_widget(self.gameInterface.gameField, new_row, new_col)
                if hasattr(pickup, 'inv_pixmap') == True:
                    pickup.start()
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
            bullet = Bullet(self, self.direction, pos=(self.row, self.col), dmg = self.dmg, pierce=self.pierce, parent=self.gameInterface)
            self.shot_busy = True

    def health_down(self):
        if not self.invincible:
            self.health -= 1
            self.gameInterface.health_update()
            if self.health <= 0:
                self.destroyed()

    def destroyed(self):
        self.gameInterface.main.end_state(False)

    def pause(self, paused):
        if paused:
            self._keyPressEvent.__setattr__()
        else:
            self.setEnabled(True)

    def _keyPressEvent(self, e):
        key = e.key()
        if key in moveKeys:
            self.move(moveKeys[key])
        elif key in actionKeys:
            self.shoot()


class Bullet(QLabel):
    def __init__(self, owner, direction, pos, dmg, pierce=False, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.owner = owner
        self.gameInterface.temp.append(self)
        self.direction = direction
        self.row, self.col = pos
        self.r, self.c = directions[self.direction][1]
        self.row, self.col = self.row + self.r, self.col + self.c
        self.speed = 50
        self.bullet_pixmap = QPixmap(objects_pics['bullet'])
        self.pierce = pierce
        self.dmg = dmg

        self.speed_timer = QTimer(self)
        self.speed_timer.setObjectName('bullet')
        self.speed_timer.timeout.connect(self._move)                                                                                                                                                                                                                                                                                                                                                            

        self.speed_timer.start(self.speed)  # CКОРОСТЬ ПУЛИ В МС

        self.setPixmap(rotate_pixmap(self.bullet_pixmap, directions[self.direction][0]))
        scaling(self, 30, 30)
        self.setScaledContents(True)

    def _move(self):
        self.owner.shot_busy = True
        new_row, new_col = self.row, self.col
        if chosenField[new_row][new_col] in list(nonsolid_objects.values()):
            self.gameInterface.gameField.addWidget(self, new_row, new_col, alignment=Qt.AlignmentFlag.AlignCenter)
            self.row, self.col = self.row + self.r, self.col + self.c
            return
        else:
            self.collision(new_row, new_col)

    def collision(self, new_row, new_col):
        if chosenField[new_row][new_col] == 9: 
            self.gameInterface.main.end_state(False)
        if (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.fieldObjects:
            widget.health_down(self.dmg)
        elif self.owner == self.gameInterface.tank:
            if (widget := find_widget(self.gameInterface.gameField, new_row, new_col)) in self.gameInterface.enemies:
                widget.health_down(self.dmg)
        elif widget == self.gameInterface.tank:
            widget.health_down()
        if self.pierce and chosenField[new_row][new_col] != 8:
            pass
        else:
            self.owner.shot_busy = False
            self.deleteLater()
            self.gameInterface.temp.remove(self)

    
    def pause(self, paused):
        if paused:
            self.speed_timer.stop()
        else:
            self.speed_timer.start(self.speed)


class EnemyTank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)

        self.gameInterface = parent
        self.row, self.col = pos
        self.cell_new = 0
        self.dgm = 1

    def setup_timers(self):
        self.move_timer = QTimer()
        self.shot_timer = QTimer()

    def start_timers(self, speed, freq):
        self.move_timer.timeout.connect(self.move)
        self.shot_timer.timeout.connect(self.shoot)
        self.move_timer.start(speed)
        self.shot_timer.start(freq)

    def move(self):
        self.setVisible(True)
        weights = [10, 10, 10, 10]
        weights[self.dir_list.index(self.direction)] = 90
        self.direction = random.choices(self.dir_list, weights=weights, k=1)[0]

        r, c = directions[self.direction][1]
        new_row, new_col = self.row + r, self.col + c

        if (chosenField[new_row][new_col] not in list(solid_objects.values()) and chosenField[new_row][new_col] != nonsolid_objects['water'] and chosenField[new_row][new_col] not in list(pickups_objects.values())):
            self.gameInterface.gameField.addWidget(self, new_row, new_col)
            chosenField[self.row][self.col] = self.cell_new
            self.cell_new = chosenField[new_row][new_col]
            chosenField[new_row][new_col] = self.id
            self.row, self.col = new_row, new_col
        
        if self.cell_new == 4:
            self.setVisible(False)

        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        
    def shoot(self):
        if not self.shot_busy:
            bullet = Bullet(self, self.direction, pos=(self.row, self.col), dmg = self.dgm, parent=self.gameInterface)

    def health_down(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.destroyed()       

    def pause(self, paused):
        if paused:
            self.move_timer.stop()
            self.shot_timer.stop()
        else:
            self.move_timer.start()
            self.shot_timer.start()

    def destroyed(self):
        stats[self.id] += 1
        self.deleteLater()
        chosenField[self.row][self.col] = 0
        self.gameInterface.enemies.remove(self)
        self.gameInterface.enemy_all -= 1
        self.gameInterface.enemy_update()
        if self.gameInterface.enemy_all == 0:
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
        self.id = enemies_objects['tankEnemy1']
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos
    
        self.setup_timers()
        self.start_timers(self.speed, self.shot_freq)

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
        self.id = enemies_objects['tankEnemy2']
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.setup_timers()
        self.start_timers(self.speed, self.shot_freq)

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
        self.id = enemies_objects['tankEnemy3']
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.setup_timers()
        self.start_timers(self.speed, self.shot_freq)

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
        self.id = enemies_objects['tankEnemy4']
        
        self.setPixmap(rotate_pixmap(self.tank_pixmap, directions[self.direction][0]))
        scaling(self, 60, 60)
        self.setScaledContents(True)
        self.row, self.col = pos

        self.setup_timers()
        self.start_timers(self.speed, self.shot_freq)


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
        global lvl
        if senderName == 'pause':
            self.main.pagesStack.setCurrentIndex(1)
            self.main.game.pause(paused=True)
        elif senderName == 'resume':
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.game.pause(paused=False)
        elif senderName == 'home':
            self.main.pagesStack.setCurrentIndex(0)
        elif senderName == 'replay':
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.reset_game()
            self.main.game.pause(paused=False)
        elif senderName == 'play':
            lvl = 0
            self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
            self.main.reset_game()
            self.main.game.pause(paused=False)
        elif senderName == 'next':
            lvl += 1
            if lvl == 3:
                 self.main.pagesStack.setCurrentIndex(3)
            else:
                self.main.pagesStack.setCurrentIndex(self.main.pagesStack.count()-1)
                self.main.reset_game()
        elif senderName == 'exit':
            self.main.close()


def get_tank_id(id):
    match id:
        case x if x == enemies_objects['tankEnemy1']:
            return EnemyTank1
        case x if x == enemies_objects['tankEnemy2']:
            return EnemyTank2
        case x if x == enemies_objects['tankEnemy3']:
            return EnemyTank3
        case x if x == enemies_objects['tankEnemy4']:
            return EnemyTank4


def reset_game_state():  # Переприсваиваем field макет, чтобы перезапустить игру
    global field, chosenField, stats, chosenEnemies
    stats = {
        21: 0,
        22: 0,
        23: 0,
        24: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
    }
    field = read_from_json()
    if field is None:
        return
    chosenField = field.get(field_keys[lvl], chosenField)
    chosenEnemies = field[field_enemies_keys[lvl]]


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