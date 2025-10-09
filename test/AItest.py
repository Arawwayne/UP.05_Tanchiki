import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QKeyEvent


class Tank:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.direction = 0  # 0: up, 1: right, 2: down, 3: left
        self.speed = 3
        self.color = color
        self.is_player = is_player
        self.bullets = []
        self.cooldown = 0
        self.health = 3

    def move(self, dx, dy, obstacles):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check collision with obstacles
        tank_rect = QRectF(new_x, new_y, self.width, self.height)
        for obstacle in obstacles:
            if tank_rect.intersects(obstacle.rect()):
                return False
        
        # Check boundary collision
        if (new_x < 0 or new_x > 800 - self.width or 
            new_y < 0 or new_y > 600 - self.height):
            return False
            
        self.x = new_x
        self.y = new_y
        return True

    def update(self, obstacles):
        if self.cooldown > 0:
            self.cooldown -= 1
            
        # AI for enemy tanks
        if not self.is_player:
            if random.random() < 0.02:  # Random direction change
                self.direction = random.randint(0, 3)
            
            if random.random() < 0.01:  # Random shooting
                self.shoot()
                
            # Move based on direction
            if self.direction == 0:  # Up
                self.move(0, -self.speed, obstacles)
            elif self.direction == 1:  # Right
                self.move(self.speed, 0, obstacles)
            elif self.direction == 2:  # Down
                self.move(0, self.speed, obstacles)
            elif self.direction == 3:  # Left
                self.move(-self.speed, 0, obstacles)

    def shoot(self):
        if self.cooldown <= 0:
            bullet_x = self.x + self.width / 2 - 2.5
            bullet_y = self.y + self.height / 2 - 2.5
            
            if self.direction == 0:  # Up
                bullet_y = self.y - 5
            elif self.direction == 1:  # Right
                bullet_x = self.x + self.width
            elif self.direction == 2:  # Down
                bullet_y = self.y + self.height
            elif self.direction == 3:  # Left
                bullet_x = self.x - 5
                
            self.bullets.append(Bullet(bullet_x, bullet_y, self.direction, self.is_player))
            self.cooldown = 20

    def draw(self, painter):
        # Draw tank body
        painter.setBrush(QBrush(self.color))
        painter.drawRect(int(self.x), int(self.y), self.width, self.height)
        
        # Draw tank barrel
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        barrel_length = 15
        if self.direction == 0:  # Up
            painter.drawRect(int(self.x + self.width/2 - 2.5), int(self.y - barrel_length), 5, barrel_length)
        elif self.direction == 1:  # Right
            painter.drawRect(int(self.x + self.width), int(self.y + self.height/2 - 2.5), barrel_length, 5)
        elif self.direction == 2:  # Down
            painter.drawRect(int(self.x + self.width/2 - 2.5), int(self.y + self.height), 5, barrel_length)
        elif self.direction == 3:  # Left
            painter.drawRect(int(self.x - barrel_length), int(self.y + self.height/2 - 2.5), barrel_length, 5)
        
        # Draw health
        if self.is_player:
            painter.setBrush(QBrush(Qt.GlobalColor.red))
            for i in range(self.health):
                painter.drawRect(int(self.x) + i * 10, int(self.y) - 15, 8, 8)


class Bullet:
    def __init__(self, x, y, direction, is_player_bullet):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 5
        self.direction = direction
        self.speed = 7
        self.is_player_bullet = is_player_bullet

    def update(self):
        if self.direction == 0:  # Up
            self.y -= self.speed
        elif self.direction == 1:  # Right
            self.x += self.speed
        elif self.direction == 2:  # Down
            self.y += self.speed
        elif self.direction == 3:  # Left
            self.x -= self.speed
            
        # Check if bullet is out of bounds
        if (self.x < 0 or self.x > 800 or 
            self.y < 0 or self.y > 600):
            return False
        return True

    def draw(self, painter):
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawRect(int(self.x), int(self.y), self.width, self.height)

    def rect(self):
        return QRectF(self.x, self.y, self.width, self.height)


class Obstacle:
    def __init__(self, x, y, width, height, destructible=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.destructible = destructible

    def draw(self, painter):
        if self.destructible:
            painter.setBrush(QBrush(QColor(139, 69, 19)))  # Brown
        else:
            painter.setBrush(QBrush(QColor(100, 100, 100)))  # Gray
        painter.drawRect(int(self.x), int(self.y), self.width, self.height)

    def rect(self):
        return QRectF(self.x, self.y, self.width, self.height)


class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 800, 600)
        
        # Create player tank
        self.player = Tank(400, 500, QColor(0, 0, 255)), True
        
        # Create enemy tanks
        self.enemies = [
            Tank(100, 100, QColor(255, 0, 0)),
            Tank(700, 100, QColor(255, 0, 0)),
            Tank(100, 300, QColor(255, 0, 0))
        ]
        
        # Create obstacles
        self.obstacles = []
        self.create_obstacles()
        
        # Game state
        self.game_over = False
        self.score = 0
        
        # Set up game timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)  # ~30 FPS

    def create_obstacles(self):
        # Indestructible walls (borders)
        self.obstacles.append(Obstacle(0, 0, 800, 20))  # Top
        self.obstacles.append(Obstacle(0, 580, 800, 20))  # Bottom
        self.obstacles.append(Obstacle(0, 0, 20, 600))  # Left
        self.obstacles.append(Obstacle(780, 0, 20, 600))  # Right
        
        # Some destructible walls
        for i in range(5):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            self.obstacles.append(Obstacle(x, y, 40, 40, True))
        
        # Some indestructible walls
        for i in range(10):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            self.obstacles.append(Obstacle(x, y, 30, 30))

    def update_game(self):
        if self.game_over:
            return
            
        # Update player tank
        self.player.update(self.obstacles)
        
        # Update enemy tanks
        for enemy in self.enemies:
            enemy.update(self.obstacles)
        
        # Update player bullets
        for bullet in self.player.bullets[:]:
            if not bullet.update():
                self.player.bullets.remove(bullet)
                continue
                
            # Check collision with enemies
            bullet_rect = bullet.rect()
            for enemy in self.enemies[:]:
                enemy_rect = QRectF(enemy.x, enemy.y, enemy.width, enemy.height)
                if bullet_rect.intersects(enemy_rect):
                    enemy.health -= 1
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                    break
                    
            # Check collision with obstacles
            for obstacle in self.obstacles[:]:
                if bullet_rect.intersects(obstacle.rect()):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if obstacle.destructible:
                        self.obstacles.remove(obstacle)
                    break
        
        # Update enemy bullets
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if not bullet.update():
                    enemy.bullets.remove(bullet)
                    continue
                    
                # Check collision with player
                bullet_rect = bullet.rect()
                player_rect = QRectF(self.player.x, self.player.y, self.player.width, self.player.height)
                if bullet_rect.intersects(player_rect):
                    self.player.health -= 1
                    enemy.bullets.remove(bullet)
                    if self.player.health <= 0:
                        self.game_over = True
                    break
                    
                # Check collision with obstacles
                for obstacle in self.obstacles[:]:
                    if bullet_rect.intersects(obstacle.rect()):
                        if bullet in enemy.bullets:
                            enemy.bullets.remove(bullet)
                        if obstacle.destructible:
                            self.obstacles.remove(obstacle)
                        break
        
        # Check win condition
        if len(self.enemies) == 0:
            self.game_over = True
        
        self.update()

    # def drawForeground(self, painter, rect):
    #     # Draw player tank
    #     self.player.draw(painter)
        
        # Draw enemy tanks
        for enemy in self.enemies:
            enemy.draw(painter)
        
        # Draw bullets
        for bullet in self.player.bullets:
            bullet.draw(painter)
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                bullet.draw(painter)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(painter)
        
        # Draw score
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(10, 20, f"Score: {self.score}")
        
        # Draw health
        painter.drawText(10, 40, f"Health: {self.player.health}")
        
        # Draw game over message
        if self.game_over:
            painter.setPen(Qt.GlobalColor.red)
            font = painter.font()
            font.setPointSize(40)
            painter.setFont(font)
            
            if len(self.enemies) == 0:
                painter.drawText(250, 300, "YOU WIN!")
            else:
                painter.drawText(250, 300, "GAME OVER")
            
            font.setPointSize(20)
            painter.setFont(font)
            painter.drawText(300, 350, f"Final Score: {self.score}")

    def keyPressEvent(self, event):
        if self.game_over:
            return
            
        if event.key() == Qt.Key.Key_Up:
            self.player.direction = 0
            self.player.move(0, -self.player.speed, self.obstacles)
        elif event.key() == Qt.Key.Key_Right:
            self.player.direction = 1
            self.player.move(self.player.speed, 0, self.obstacles)
        elif event.key() == Qt.Key.Key_Down:
            self.player.direction = 2
            self.player.move(0, self.player.speed, self.obstacles)
        elif event.key() == Qt.Key.Key_Left:
            self.player.direction = 3
            self.player.move(-self.player.speed, 0, self.obstacles)
        elif event.key() == Qt.Key.Key_Space:
            self.player.shoot()


class BattleCityGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battle City Clone")
        self.setFixedSize(800, 600)
        
        self.scene = GameScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = BattleCityGame()
    game.show()
    sys.exit(app.exec())