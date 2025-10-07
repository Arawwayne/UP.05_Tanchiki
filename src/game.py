
from PyQt6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QGridLayout, QVBoxLayout)
from PyQt6.QtGui import (QPixmap)
from PyQt6.QtCore import (Qt)

from defs import ClickableImages, read_from_json
from tankPlayer import Tank

ingame_objects = {
    
}

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
