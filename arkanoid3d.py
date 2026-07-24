# arkanoid3d.py — Арканоид 3D на Python

import os
import time
import random
import sys

try:
    import keyboard
except ImportError:
    print("Установите keyboard: pip install keyboard")
    sys.exit(1)

# Параметры поля
WIDTH = 10   # X
HEIGHT = 8   # Y
DEPTH = 5    # Z
PADDLE_WIDTH = 5
BALL_CHAR = '●'
BLOCK_CHAR = '█'
PADDLE_CHAR = '═'

class Arkanoid3D:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.depth = DEPTH
        self.blocks = [[[1 for _ in range(self.depth)] for _ in range(self.height)] for _ in range(self.width)]
        # Убираем блоки в нижней части (для платформы)
        for x in range(self.width):
            for z in range(self.depth):
                self.blocks[x][self.height-1][z] = 0
        # Платформа (x, z)
        self.paddle_x = self.width // 2
        self.paddle_z = self.depth // 2
        # Мяч (x, y, z, dx, dy, dz)
        self.ball_x = self.paddle_x
        self.ball_y = self.height - 2
        self.ball_z = self.paddle_z
        self.ball_dx = 1
        self.ball_dy = -1
        self.ball_dz = 0
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.paused = False
        self.ball_launched = False
        self.high_score = self.load_high_score()

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open('highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🧱 ARKANOID 3D  |  Счёт: {self.score}  |  Уровень: {self.level}  |  Жизни: {self.lives}  |  Рекорд: {self.high_score}")
        if self.paused:
            print("⏸ ПАУЗА")
        # Отображение слоёв (z)
        for z in range(self.depth-1, -1, -1):
            print(f"\nСлой {z} (z={z}):")
            # Верхняя граница
            print('+' + '-' * self.width * 2 + '+')
            for y in range(self.height):
                line = '|'
                for x in range(self.width):
                    if self.blocks[x][y][z] > 0:
                        line += BLOCK_CHAR * 2
                    elif x == self.ball_x and y == self.ball_y and z == self.ball_z:
                        line += BALL_CHAR * 2
                    else:
                        line += '  '
                line += '|'
                print(line)
            # Нижняя граница
            print('+' + '-' * self.width * 2 + '+')
        # Отображение платформы (вид сверху)
        print("\nПлатформа (вид сверху):")
        line = '  '
        for x in range(self.width):
            if self.paddle_x - self.paddle_width//2 <= x <= self.paddle_x + self.paddle_width//2 and z == self.paddle_z:
                line += PADDLE_CHAR
            else:
                line += ' '
        print(line)

        print("Управление: WASD - движение платформы, Пробел - запуск/пауза, Q - выход")

    def update(self):
        if self.game_over or self.paused or not self.ball_launched:
            return
        # Движение мяча
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        self.ball_z += self.ball_dz
        # Отражение от стен (по X и Z)
        if self.ball_x <= 0 or self.ball_x >= self.width-1:
            self.ball_dx *= -1
            self.ball_x += self.ball_dx * 2
        if self.ball_z <= 0 or self.ball_z >= self.depth-1:
            self.ball_dz *= -1
            self.ball_z += self.ball_dz * 2
        # Отражение от потолка (y=0)
        if self.ball_y <= 0:
            self.ball_dy *= -1
            self.ball_y += self.ball_dy * 2
        # Проверка столкновения с платформой
        if self.ball_y >= self.height-1:
            # Проверяем, попадает ли мяч на платформу
            if (self.paddle_x - self.paddle_width//2 <= self.ball_x <= self.paddle_x + self.paddle_width//2 and
                self.ball_z == self.paddle_z):
                self.ball_dy *= -1
                self.ball_y = self.height - 2
                # Меняем направление по X в зависимости от места попадания
                dx = self.ball_x - self.paddle_x
                self.ball_dx = dx
                if self.ball_dx == 0:
                    self.ball_dx = 1 if self.ball_dx > 0 else -1
                # Изменяем направление по Z случайно
                self.ball_dz = random.choice([-1, 0, 1])
            else:
                # Потеря мяча
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                else:
                    self.reset_ball()
        # Столкновение с блоками
        if 0 <= self.ball_x < self.width and 0 <= self.ball_y < self.height and 0 <= self.ball_z < self.depth:
            if self.blocks[self.ball_x][self.ball_y][self.ball_z] > 0:
                self.blocks[self.ball_x][self.ball_y][self.ball_z] -= 1
                if self.blocks[self.ball_x][self.ball_y][self.ball_z] == 0:
                    self.score += 10 * self.level
                # Отражение мяча (определяем, с какой стороны столкнулись)
                # Проверяем соседние клетки
                if self.ball_x > 0 and self.blocks[self.ball_x-1][self.ball_y][self.ball_z] > 0:
                    self.ball_dx *= -1
                elif self.ball_x < self.width-1 and self.blocks[self.ball_x+1][self.ball_y][self.ball_z] > 0:
                    self.ball_dx *= -1
                elif self.ball_y > 0 and self.blocks[self.ball_x][self.ball_y-1][self.ball_z] > 0:
                    self.ball_dy *= -1
                elif self.ball_y < self.height-1 and self.blocks[self.ball_x][self.ball_y+1][self.ball_z] > 0:
                    self.ball_dy *= -1
                elif self.ball_z > 0 and self.blocks[self.ball_x][self.ball_y][self.ball_z-1] > 0:
                    self.ball_dz *= -1
                elif self.ball_z < self.depth-1 and self.blocks[self.ball_x][self.ball_y][self.ball_z+1] > 0:
                    self.ball_dz *= -1
                else:
                    # Если не понятно, просто меняем направление по Y
                    self.ball_dy *= -1
                # Сдвигаем мяч, чтобы избежать застревания
                self.ball_x += self.ball_dx
                self.ball_y += self.ball_dy
                self.ball_z += self.ball_dz
        # Проверка на отсутствие блоков (победа уровня)
        blocks_left = sum(sum(sum(1 for cell in row if cell > 0) for row in layer) for layer in self.blocks)
        if blocks_left == 0:
            self.level += 1
            self.generate_blocks()
            self.reset_ball()

    def generate_blocks(self):
        # Генерация блоков для нового уровня
        for x in range(self.width):
            for y in range(self.height-1):
                for z in range(self.depth):
                    # Случайное размещение блоков с разной прочностью
                    if (x+y+z) % 2 == 0:  # узор
                        self.blocks[x][y][z] = random.randint(1, 2)
                    else:
                        self.blocks[x][y][z] = 0

    def reset_ball(self):
        self.ball_x = self.paddle_x
        self.ball_y = self.height - 2
        self.ball_z = self.paddle_z
        self.ball_dx = 1
        self.ball_dy = -1
        self.ball_dz = 0
        self.ball_launched = False

    def launch_ball(self):
        if not self.ball_launched:
            self.ball_launched = True

    def move_paddle(self, dx, dz):
        new_x = self.paddle_x + dx
        new_z = self.paddle_z + dz
        if 0 <= new_x < self.width and 0 <= new_z < self.depth:
            self.paddle_x = new_x
            self.paddle_z = new_z
            if not self.ball_launched:
                self.ball_x = self.paddle_x
                self.ball_z = self.paddle_z

    def handle_input(self):
        if keyboard.is_pressed('w') and not keyboard.is_pressed('a') and not keyboard.is_pressed('d'):
            self.move_paddle(0, -1)
        if keyboard.is_pressed('s'):
            self.move_paddle(0, 1)
        if keyboard.is_pressed('a'):
            self.move_paddle(-1, 0)
        if keyboard.is_pressed('d'):
            self.move_paddle(1, 0)
        if keyboard.is_pressed('space'):
            if not self.ball_launched:
                self.launch_ball()
            else:
                self.paused = not self.paused
        if keyboard.is_pressed('q'):
            self.game_over = True

    def run(self):
        while not self.game_over:
            self.draw()
            self.handle_input()
            self.update()
            time.sleep(0.05)
        self.save_high_score()
        print("ИГРА ОКОНЧЕНА! Ваш счёт:", self.score)

if __name__ == "__main__":
    game = Arkanoid3D()
    game.run()
