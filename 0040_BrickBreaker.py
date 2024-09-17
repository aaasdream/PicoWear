import time
from machine import Timer
from Pico_Wear import PicoWear

class BrickGame:
    def __init__(self, pico_wear):
        self.pico = pico_wear
        self.display = self.pico.display
        self.mpu = self.pico.mpu
        
        # 游戏参数
        self.paddle_width = 20
        self.paddle_height = 5
        self.ball_radius = 2
        self.brick_width = 20
        self.brick_height = 10
        self.brick_rows = 3
        self.brick_cols = 5
        
        self.reset_game()
        
        # 设置定时器更新MPU数据
        self.mpu_timer = Timer(period=10, mode=Timer.PERIODIC, callback=self.update_mpu)
        
        # 注册按钮回调
        self.pico.register_button_callback(self.on_button_click)
        
    def reset_game(self):
        self.paddle_x = 64 - self.paddle_width // 2
        self.ball_x = 64
        self.ball_y = 100
        self.ball_dx = 2
        self.ball_dy = -2
        self.score = 0
        self.game_over = False
        self.game_win = False
        
        # 初始化砖块
        self.bricks = []
        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                self.bricks.append({
                    'x': col * (self.brick_width + 5) + 5,
                    'y': row * (self.brick_height + 5) + 5,
                    'active': True
                })
    
    def update_mpu(self, timer):
        self.mpu.update_mahony()
    
    def on_button_click(self):
        if self.game_over or self.game_win:
            self.reset_game()
    
    def update(self):
        if self.game_over or self.game_win:
            return
        
        # 更新打击棒位置
        roll, _, _ = self.mpu.get_angles()
        self.paddle_x = max(0, min(128 - self.paddle_width, 64 + int(roll * 4)))
        
        # 更新球的位置
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # 检测边界碰撞
        if self.ball_x <= 0 or self.ball_x >= 128:
            self.ball_dx = -self.ball_dx
        if self.ball_y <= 0:
            self.ball_dy = -self.ball_dy
        
        # 检测打击棒碰撞
        if (self.ball_y + self.ball_radius >= 128 - self.paddle_height and
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_dy = -self.ball_dy
        
        # 检测砖块碰撞
        for brick in self.bricks:
            if brick['active']:
                if (brick['x'] <= self.ball_x <= brick['x'] + self.brick_width and
                    brick['y'] <= self.ball_y <= brick['y'] + self.brick_height):
                    brick['active'] = False
                    self.ball_dy = -self.ball_dy
                    self.score += 10
                    break
        
        # 检查游戏结束
        if self.ball_y > 128:
            self.game_over = True
        
        # 检查胜利
        if all(not brick['active'] for brick in self.bricks):
            self.game_win = True
    
    def draw(self):
        self.display.fill(0)
        
        # 绘制打击棒
        self.display.fill_rectangle(self.paddle_x, 128 - self.paddle_height, self.paddle_width, self.paddle_height, 1)
        
        # 绘制球
        self.display.fill_circle(int(self.ball_x), int(self.ball_y), self.ball_radius, 1)
        
        # 绘制砖块
        for brick in self.bricks:
            if brick['active']:
                self.display.draw_rectangle(brick['x'], brick['y'], self.brick_width, self.brick_height, 1)
        
        # 显示分数
        self.display.text(f"Score: {self.score}", 0, 0, 1)
        
        # 显示游戏结束或胜利信息
        if self.game_over:
            self.display.text("Game Over", 30, 60, 1)
            self.display.text(f"Score: {self.score}", 30, 70, 1)
        elif self.game_win:
            self.display.text("YOU WIN", 35, 60, 1)
            self.display.text(f"Score: {self.score}", 30, 70, 1)
        
        self.display.show()

    def run(self):
        while True:
            self.update()
            self.draw()
            time.sleep(0.02)  # 控制游戏速度

# 主程序
pico = PicoWear()
game = BrickGame(pico)

try:
    game.run()
except KeyboardInterrupt:
    game.mpu_timer.deinit()  # 停止MPU更新定时器