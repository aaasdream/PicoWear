import math
import random
from Pico_Wear import PicoWear
from machine import Timer

class EarthDefenseGame:
    def __init__(self, pico_wear):
        self.pico = pico_wear
        self.display = self.pico.display
        self.mpu = self.pico.mpu
        
        # 游戏参数
        self.screen_width = 128
        self.screen_height = 128
        self.earth_size = 32  # 地球图片大小
        self.shield_size = 10
        self.meteor_size = 4
        self.score = 0
        self.game_over = False
        
        # 加载地球图片
        self.earth_image = self.display.read_bmp_mono('earth.bmp')
        
        # 玩家盾牌位置
        self.shield_x = self.screen_width // 2
        self.shield_y = self.screen_height // 2
        
        # 陨石列表
        self.meteors = []
        
        # 定时器
        self.mpu_timer = Timer(-1)
        self.game_timer = Timer(-1)
        
        # 注册按钮回调
        self.pico.register_button_callback(self.restart_game)
        
    def init_game(self):
        self.score = 0
        self.game_over = False
        self.meteors = []
        self.shield_x = self.screen_width // 2
        self.shield_y = self.screen_height // 2
        
    def restart_game(self):
        if self.game_over:
            self.init_game()

    def update_shield_position(self):
        roll, pitch, _ = self.mpu.get_angles()
        # 将角度映射到屏幕坐标
        self.shield_x = int(self.screen_width / 2 + (roll / 15) * (self.screen_width / 2 - self.shield_size / 2))
        self.shield_y = int(self.screen_height / 2 + (pitch / 15) * (self.screen_height / 2 - self.shield_size / 2))
        
        # 确保盾牌不会超出屏幕边界
        self.shield_x = max(0, min(self.shield_x, self.screen_width - self.shield_size))
        self.shield_y = max(0, min(self.shield_y, self.screen_height - self.shield_size))

    def generate_meteor(self):
        # 随机生成陨石的起始位置（屏幕边缘）
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, self.screen_width)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, self.screen_width)
            y = self.screen_height
        elif side == 'left':
            x = 0
            y = random.randint(0, self.screen_height)
        else:  # right
            x = self.screen_width
            y = random.randint(0, self.screen_height)
        
        # 计算陨石移动方向（指向地球中心）
        dx = self.screen_width // 2 - x
        dy = self.screen_height // 2 - y
        length = math.sqrt(dx**2 + dy**2)
        speed = 1  # 可以调整陨石速度
        dx = dx / length * speed
        dy = dy / length * speed
        
        self.meteors.append({'x': x, 'y': y, 'dx': dx, 'dy': dy})

    def update_meteors(self):
        for meteor in self.meteors:
            meteor['x'] += meteor['dx']
            meteor['y'] += meteor['dy']
        
        # 移除超出屏幕的陨石
        self.meteors = [m for m in self.meteors if 0 <= m['x'] < self.screen_width and 0 <= m['y'] < self.screen_height]

    def check_collisions(self):
        earth_x = self.screen_width // 2 - self.earth_size // 2
        earth_y = self.screen_height // 2 - self.earth_size // 2
        
        for meteor in self.meteors[:]:  # 使用副本进行迭代，因为我们可能会修改列表
            # 检查与盾牌的碰撞
            if (self.shield_x < meteor['x'] < self.shield_x + self.shield_size and
                self.shield_y < meteor['y'] < self.shield_y + self.shield_size):
                self.meteors.remove(meteor)
                self.score += 10
                continue
            
            # 检查与地球的碰撞
            if (earth_x < meteor['x'] < earth_x + self.earth_size and
                earth_y < meteor['y'] < earth_y + self.earth_size):
                self.game_over = True
                break

    def draw_game(self):
        self.display.fill(0)  # 清空屏幕
        
        # 绘制地球
        earth_x = self.screen_width // 2 - self.earth_size // 2
        earth_y = self.screen_height // 2 - self.earth_size // 2
        self.display.blit(self.earth_image, earth_x, earth_y)
        
        # 绘制盾牌
        self.display.draw_rectangle(int(self.shield_x), int(self.shield_y), self.shield_size, self.shield_size, 1)
        
        # 绘制陨石
        for meteor in self.meteors:
            self.display.fill_circle(int(meteor['x']), int(meteor['y']), self.meteor_size // 2, 1)
        
        # 显示分数
        self.display.text(f"Score: {self.score}", 0, 0, 1)
        
        if self.game_over:
            self.display.text("Game Over", 30, 50, 1)
            self.display.text(f"Score: {self.score}", 30, 70, 1)
            self.display.text("Click to restart", 10, 90, 1)
        
        self.display.show()

    def mpu_callback(self, timer):
        self.mpu.update_mahony()

    def game_update(self, timer):
        if not self.game_over:
            self.update_shield_position()
            self.update_meteors()
            self.check_collisions()
            if random.random() < 0.1:  # 10% 概率生成新陨石
                self.generate_meteor()
            self.draw_game()

    def run(self):
        self.init_game()
        self.mpu_timer.init(period=10, mode=Timer.PERIODIC, callback=self.mpu_callback)
        self.game_timer.init(period=50, mode=Timer.PERIODIC, callback=self.game_update)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.mpu_timer.deinit()
            self.game_timer.deinit()

# 主程序
pico = PicoWear()
game = EarthDefenseGame(pico)
game.run()