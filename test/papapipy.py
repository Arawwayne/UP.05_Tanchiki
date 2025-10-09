import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QBrush, QColor, QPainter, QKeyEvent


class GameObject(QGraphicsItem):
    def __init__(self, x, y, width, height, color, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.color = color
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.fillRect(self.boundingRect(), QBrush(self.color))


class Tank(GameObject):
    def __init__(self, x, y, color, parent=None):
        super().__init__(x, y, 40, 40, color, parent)
        self.direction = Qt.Key.Key_Up
        self.speed = 5
        self.bullets = []
        self.cooldown = 0

    def move(self, keys_pressed):
        dx, dy = 0, 0
        
        if keys_pressed[Qt.Key.Key_Left]:
            dx = -self.speed
            self.direction = Qt.Key.Key_Left
        elif keys_pressed[Qt.Key.Key_Right]:
            dx = self.speed
            self.direction = Qt.Key.Key_Right
        elif keys_pressed[Qt.Key.Key_Up]:
            dy = -self.speed
            self.direction = Qt.Key.Key_Up
        elif keys_pressed[Qt.Key.Key_Down]:
            dy = self.speed
            self.direction = Qt.Key.Key_Down
        
        new_x = self.x() + dx
        new_y = self.y() + dy
        
        # Границы игрового поля
        if 0 <= new_x <= 800 - self.width and 0 <= new_y <= 600 - self.height:
            self.setPos(new_x, new_y)

    def fire(self):
        if self.cooldown <= 0:
            bullet_x = self.x() + self.width // 2 - 5
            bullet_y = self.y() + self.height // 2 - 5
            
            if self.direction == Qt.Key.Key_Left:
                bullet_x -= 20
            elif self.direction == Qt.Key.Key_Right:
                bullet_x += 20
            elif self.direction == Qt.Key.Key_Up:
                bullet_y -= 20
            elif self.direction == Qt.Key.Key_Down:
                bullet_y += 20
                
            bullet = Bullet(bullet_x, bullet_y, self.direction)
            self.bullets.append(bullet)
            self.scene().addItem(bullet)
            self.cooldown = 20

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1


class EnemyTank(Tank):
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, QColor("red"), parent)
        self.move_timer = 0
        self.move_direction = random.choice([
            Qt.Key.Key_Left, Qt.Key.Key_Right, 
            Qt.Key.Key_Up, Qt.Key.Key_Down
        ])
        self.fire_chance = 0.02

    def auto_move(self):
        self.move_timer += 1
        if self.move_timer >= 30:
            self.move_timer = 0
            self.move_direction = random.choice([
                Qt.Key.Key_Left, Qt.Key.Key_Right, 
                Qt.Key.Key_Up, Qt.Key.Key_Down
            ])
        
        keys = {self.move_direction: True}
        self.move(keys)
        
        if random.random() < self.fire_chance:
            self.fire()


class Bullet(GameObject):
    def __init__(self, x, y, direction, parent=None):
        super().__init__(x, y, 10, 10, QColor("yellow"), parent)
        self.direction = direction
        self.speed = 10
        self.damage = 1

    def move(self):
        if self.direction == Qt.Key.Key_Left:
            self.setPos(self.x() - self.speed, self.y())
        elif self.direction == Qt.Key.Key_Right:
            self.setPos(self.x() + self.speed, self.y())
        elif self.direction == Qt.Key.Key_Up:
            self.setPos(self.x(), self.y() - self.speed)
        elif self.direction == Qt.Key.Key_Down:
            self.setPos(self.x(), self.y() + self.speed)
        
        # Удаление пули при выходе за границы
        if (self.x() < 0 or self.x() > 800 or 
            self.y() < 0 or self.y() > 600):
            self.scene().removeItem(self)
            return True
        return False


class Wall(GameObject):
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, 40, 40, QColor("brown"), parent)


class Steel(GameObject):
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, 40, 40, QColor("gray"), parent)


class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__(0, 0, 800, 600)
        self.keys_pressed = {}
        self.player = None
        self.enemies = []
        self.walls = []
        self.steels = []
        self.setBackgroundBrush(QBrush(QColor("black")))
        
        self.setup_game()

    def setup_game(self):
        # Создание игрока
        self.player = Tank(400, 500, QColor("green"))
        self.addItem(self.player)
        self.player.setFocus()
        
        # Создание врагов
        for i in range(3):
            enemy = EnemyTank(100 + i * 200, 100)
            self.addItem(enemy)
            self.enemies.append(enemy)
        
        # Создание стен
        for i in range(5):
            for j in range(3):
                wall = Wall(200 + i * 40, 300 + j * 40)
                self.addItem(wall)
                self.walls.append(wall)
        
        # Создание стальных блоков
        for i in range(5):
            steel = Steel(300 + i * 40, 200)
            self.addItem(steel)
            self.steels.append(steel)

    def keyPressEvent(self, event: QKeyEvent):
        self.keys_pressed[event.key()] = True
        if event.key() == Qt.Key.Key_Space:
            self.player.fire()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys_pressed[event.key()] = False

    def update(self):
        # Обновление игрока
        self.player.move(self.keys_pressed)
        self.player.update()
        
        # Обновление врагов
        for enemy in self.enemies:
            enemy.auto_move()
        
        # Обновление пуль игрока
        for bullet in self.player.bullets[:]:
            if bullet.move():
                self.player.bullets.remove(bullet)
                continue
            self.check_bullet_collision(bullet)
        
        # Обновление пуль врагов
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.move():
                    enemy.bullets.remove(bullet)
                    continue
                self.check_bullet_collision(bullet, True)

    def check_bullet_collision(self, bullet, is_enemy_bullet=False):
        # Проверка столкновений с врагами
        for enemy in self.enemies:
            if bullet.collidesWithItem(enemy):
                self.removeItem(bullet)
                if is_enemy_bullet:
                    enemy.bullets.remove(bullet)
                else:
                    self.player.bullets.remove(bullet)
                self.removeItem(enemy)
                self.enemies.remove(enemy)
                return
        
        # Проверка столкновения с игроком
        if not is_enemy_bullet and bullet.collidesWithItem(self.player):
            self.removeItem(bullet)
            # Здесь должна быть обработка смерти игрока
            return
        
        # Проверка столкновения со стенами
        for wall in self.walls[:]:
            if bullet.collidesWithItem(wall):
                self.removeItem(bullet)
                if is_enemy_bullet:
                    for enemy in self.enemies:
                        if bullet in enemy.bullets:
                            enemy.bullets.remove(bullet)
                else:
                    self.player.bullets.remove(bullet)
                self.removeItem(wall)
                self.walls.remove(wall)
                return
        
        # Проверка столкновения со сталью
        for steel in self.steels:
            if bullet.collidesWithItem(steel):
                self.removeItem(bullet)
                if is_enemy_bullet:
                    for enemy in self.enemies:
                        if bullet in enemy.bullets:
                            enemy.bullets.remove(bullet)
                else:
                    self.player.bullets.remove(bullet)
                return


class BattleCity(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battle City")
        self.setFixedSize(800, 600)
        
        self.scene = GameScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(50)  # 20 FPS
        
        self.show()

    def game_loop(self):
        self.scene.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = BattleCity()
    sys.exit(app.exec())