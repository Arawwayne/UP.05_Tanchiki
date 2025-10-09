import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QBrush, QColor, QKeyEvent, QPainter


class Tank(QGraphicsItem):
    def __init__(self, color, is_player=False):
        super().__init__()
        self.color = color
        self.is_player = is_player
        self.direction = 0  # 0: up, 1: right, 2: down, 3: left
        self.speed = 2
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        
        # Tank dimensions
        self.width = 30
        self.height = 30
        
        # Bullet cooldown
        self.can_shoot = True
        self.shoot_cooldown = 500  # ms
        self.shoot_timer = QTimer()
        self.shoot_timer.timeout.connect(self.reset_shoot)
        
    def boundingRect(self):
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(self.color))
        
        # Draw tank body
        painter.drawRect(-self.width/2, -self.height/2, self.width, self.height)
        
        # Draw tank barrel based on direction
        barrel_length = 20
        if self.direction == 0:  # up
            painter.drawRect(-3, -self.height/2 - barrel_length, 6, barrel_length)
        elif self.direction == 1:  # right
            painter.drawRect(self.width/2, -3, barrel_length, 6)
        elif self.direction == 2:  # down
            painter.drawRect(-3, self.height/2, 6, barrel_length)
        elif self.direction == 3:  # left
            painter.drawRect(-self.width/2 - barrel_length, -3, barrel_length, 6)
    
    def move(self, dx, dy):
        self.setPos(self.x() + dx, self.y() + dy)
    
    def shoot(self):
        if not self.can_shoot:
            return None
        
        self.can_shoot = False
        self.shoot_timer.start(self.shoot_cooldown)
        
        # Calculate bullet starting position based on tank direction
        if self.direction == 0:  # up
            return Bullet(self.x(), self.y() - self.height/2 - 10, self.direction, self.is_player)
        elif self.direction == 1:  # right
            return Bullet(self.x() + self.width/2 + 10, self.y(), self.direction, self.is_player)
        elif self.direction == 2:  # down
            return Bullet(self.x(), self.y() + self.height/2 + 10, self.direction, self.is_player)
        elif self.direction == 3:  # left
            return Bullet(self.x() - self.width/2 - 10, self.y(), self.direction, self.is_player)
    
    def reset_shoot(self):
        self.can_shoot = True
        self.shoot_timer.stop()


class Bullet(QGraphicsItem):
    def __init__(self, x, y, direction, is_player_bullet):
        super().__init__()
        self.direction = direction
        self.speed = 5
        self.is_player_bullet = is_player_bullet
        self.setPos(x, y)
        self.radius = 5
        
        # Bullet will be removed after this timer expires (if it doesn't hit anything)
        self.lifetime = 2000  # ms
        self.lifetime_timer = QTimer()
        self.lifetime_timer.timeout.connect(self.remove)
        self.lifetime_timer.start(self.lifetime)
    
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius*2, self.radius*2)
    
    def paint(self, painter, option, widget):
        color = QColor(255, 255, 0) if self.is_player_bullet else QColor(255, 0, 0)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(-self.radius, -self.radius, self.radius*2, self.radius*2)
    
    def move(self):
        if self.direction == 0:  # up
            self.setPos(self.x(), self.y() - self.speed)
        elif self.direction == 1:  # right
            self.setPos(self.x() + self.speed, self.y())
        elif self.direction == 2:  # down
            self.setPos(self.x(), self.y() + self.speed)
        elif self.direction == 3:  # left
            self.setPos(self.x() - self.speed, self.y())
    
    def remove(self):
        if self.scene():
            self.scene().removeItem(self)
        self.lifetime_timer.stop()


class Brick(QGraphicsItem):
    def __init__(self, x, y):
        super().__init__()
        self.setPos(x, y)
        self.width = 20
        self.height = 20
    
    def boundingRect(self):
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(139, 69, 19)))  # brown
        painter.drawRect(-self.width/2, -self.height/2, self.width, self.height)


class Steel(QGraphicsItem):
    def __init__(self, x, y):
        super().__init__()
        self.setPos(x, y)
        self.width = 20
        self.height = 20
    
    def boundingRect(self):
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(169, 169, 169)))  # gray
        painter.drawRect(-self.width/2, -self.height/2, self.width, self.height)


class BattleCity(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Battle City")
        self.setFixedSize(800, 600)
        
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 800, 600)
        
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.view)
        
        # Create player tank
        self.player = Tank(QColor(0, 255, 0), True)
        self.player.setPos(400, 500)
        self.player.setFocus()
        self.scene.addItem(self.player)
        
        # Create enemy tanks
        self.enemies = []
        for i in range(3):
            enemy = Tank(QColor(255, 0, 0))
            enemy.setPos(random.randint(50, 750), random.randint(50, 200))
            self.scene.addItem(enemy)
            self.enemies.append(enemy)
        
        # Create obstacles
        self.create_obstacles()
        
        # Game loop timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)  # ~60 FPS
        
        # Enemy movement timer
        self.enemy_move_timer = QTimer(self)
        self.enemy_move_timer.timeout.connect(self.move_enemies)
        self.enemy_move_timer.start(500)
        
        # Enemy shoot timer
        self.enemy_shoot_timer = QTimer(self)
        self.enemy_shoot_timer.timeout.connect(self.enemies_shoot)
        self.enemy_shoot_timer.start(1000)
        
        # Bullets list
        self.bullets = []
    
    def create_obstacles(self):
        # Create some bricks
        for i in range(10):
            brick = Brick(random.randint(50, 750), random.randint(100, 550))
            self.scene.addItem(brick)
        
        # Create some steel walls
        for i in range(5):
            steel = Steel(random.randint(50, 750), random.randint(100, 550))
            self.scene.addItem(steel)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Up:
            self.player.direction = 0
            self.player.move(0, -self.player.speed)
        elif event.key() == Qt.Key.Key_Right:
            self.player.direction = 1
            self.player.move(self.player.speed, 0)
        elif event.key() == Qt.Key.Key_Down:
            self.player.direction = 2
            self.player.move(0, self.player.speed)
        elif event.key() == Qt.Key.Key_Left:
            self.player.direction = 3
            self.player.move(-self.player.speed, 0)
        elif event.key() == Qt.Key.Key_Space:
            bullet = self.player.shoot()
            if bullet:
                self.scene.addItem(bullet)
                self.bullets.append(bullet)
        
        # Keep player within bounds
        self.keep_in_bounds(self.player)
    
    def keep_in_bounds(self, tank):
        x, y = tank.x(), tank.y()
        width, height = tank.width, tank.height
        
        if x < width/2:
            tank.setX(width/2)
        if x > self.scene.width() - width/2:
            tank.setX(self.scene.width() - width/2)
        if y < height/2:
            tank.setY(height/2)
        if y > self.scene.height() - height/2:
            tank.setY(self.scene.height() - height/2)
    
    def move_enemies(self):
        for enemy in self.enemies:
            # Randomly change direction
            if random.random() < 0.3:
                enemy.direction = random.randint(0, 3)
            
            # Move in current direction
            if enemy.direction == 0:  # up
                enemy.move(0, -enemy.speed)
            elif enemy.direction == 1:  # right
                enemy.move(enemy.speed, 0)
            elif enemy.direction == 2:  # down
                enemy.move(0, enemy.speed)
            elif enemy.direction == 3:  # left
                enemy.move(-enemy.speed, 0)
            
            # Keep enemy within bounds
            self.keep_in_bounds(enemy)
    
    def enemies_shoot(self):
        for enemy in self.enemies:
            if random.random() < 0.5:  # 50% chance to shoot
                bullet = enemy.shoot()
                if bullet:
                    self.scene.addItem(bullet)
                    self.bullets.append(bullet)
    
    def game_loop(self):
        # Move bullets and check collisions
        for bullet in self.bullets[:]:
            bullet.move()
            
            # Check if bullet is out of scene
            if (bullet.x() < 0 or bullet.x() > self.scene.width() or
                bullet.y() < 0 or bullet.y() > self.scene.height()):
                bullet.remove()
                self.bullets.remove(bullet)
                continue
            
            # Check bullet collisions
            colliding_items = bullet.collidingItems()
            for item in colliding_items:
                if isinstance(item, Tank):
                    if item.is_player and not bullet.is_player_bullet:
                        # Player hit by enemy bullet
                        print("Player hit!")
                        bullet.remove()
                        self.bullets.remove(bullet)
                        break
                    elif not item.is_player and bullet.is_player_bullet:
                        # Enemy hit by player bullet
                        print("Enemy hit!")
                        self.scene.removeItem(item)
                        self.enemies.remove(item)
                        bullet.remove()
                        self.bullets.remove(bullet)
                        break
                elif isinstance(item, (Brick, Steel)):
                    # Bullet hit a wall
                    if isinstance(item, Brick):
                        self.scene.removeItem(item)
                    bullet.remove()
                    self.bullets.remove(bullet)
                    break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = BattleCity()
    game.show()
    sys.exit(app.exec())