from PyQt6.QtWidgets import (QLabel)
from PyQt6.QtGui import (QPixmap)



class Tank(QLabel):
    def __init__(self, pos, parent=None):
        super().__init__(parent)
        self.gameInterface = parent
        self.direction = "north"
        self.shot_busy = False
        self.setPixmap(QPixmap("./data/tankMain.png"))
        self.setScaledContents(True)
        self.row, self.col = pos

    def move(self):
        self.move(1000, 1000)
    
    def __del__(self):
        print()



    # def destroy(self):
        # if 'tankPlayer' in ingame_objects:
        #     self.gameInterface.gameField.removeWidget(ingame_objects["tankPlayer"])
        #     ingame_objects["tankPlayer"].deleteLater()
        #     ingame_objects.pop('tankPlayer')
        #     print('tank destroyed')