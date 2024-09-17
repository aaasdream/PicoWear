import time
from machine import Pin, I2C, mem32
import sh1107
from Mpu6050_mahony import MPU6050
import rp2
import random

# 初始化设备
def init_devices():
    # MPU6050 电源设置
    PAD_CONTROL_REGISTER = 0x4001c05c
    mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000
    pin22 = Pin(22, Pin.OUT, value=1)
    time.sleep(1)

    # OLED 电源设置
    PAD_CONTROL_REGISTER = 0x4001c024
    mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000
    pin9 = Pin(9, Pin.OUT, value=0)
    pin8 = Pin(8, Pin.OUT, value=1)
    time.sleep(1)

    # 初始化I2C
    i2c0 = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
    i2c1 = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)

    # 初始化MPU6050和OLED
    mpu = MPU6050(i2c0)
    display = sh1107.SH1107_I2C(128, 128, i2c1)

    return mpu, display

# 游戏类
class BrickBreaker:
    def __init__(self, display, mpu):
        self.display = display
        self.mpu = mpu
        self.bar_width = 30
        self.bar_height = 5
        self.bar_y = 120
        self.ball_radius = 2
        self.ball_x = 64
        self.ball_y = 100
        self.ball_dx = 2
        self.ball_dy = -2
        self.bricks = []
        self.init_bricks()

    def init_bricks(self):
        self.bricks = []
        for y in range(20, 60, 10):
            for x in range(10, 120, 20):
                self.bricks.append((x, y, 15, 5))

    def update(self):
        # 更新挡板位置
        roll, _, _ = self.mpu.get_angles()
        bar_x = int(64 + (roll / 20) * 32)
        bar_x = max(0, min(bar_x, 128 - self.bar_width))

        # 更新球的位置
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # 检查球是否碰到墙壁
        if self.ball_x <= 0 or self.ball_x >= 128:
            self.ball_dx = -self.ball_dx
        if self.ball_y <= 0:
            self.ball_dy = -self.ball_dy

        # 检查球是否碰到挡板
        if (self.ball_y + self.ball_radius >= self.bar_y and
            self.ball_x >= bar_x and self.ball_x <= bar_x + self.bar_width):
            self.ball_dy = -self.ball_dy

        # 检查球是否碰到砖块
        for brick in self.bricks[:]:
            if (self.ball_x >= brick[0] and self.ball_x <= brick[0] + brick[2] and
                self.ball_y >= brick[1] and self.ball_y <= brick[1] + brick[3]):
                self.bricks.remove(brick)
                self.ball_dy = -self.ball_dy
                break

        # 绘制游戏画面
        self.display.fill(0)
        self.display.fill_rectangle(bar_x, self.bar_y, self.bar_width, self.bar_height, 1)
        self.display.fill_circle(int(self.ball_x), int(self.ball_y), self.ball_radius, 1)
        for brick in self.bricks:
            self.display.fill_rectangle(brick[0], brick[1], brick[2], brick[3], 1)
        self.display.show()

        # 检查游戏是否结束
        if self.ball_y > 128:
            return "GAME OVER"
        elif not self.bricks:
            return "YOU WIN"
        return None

def main():
    mpu, display = init_devices()
    game = BrickBreaker(display, mpu)

    while True:
        mpu.update_mahony()
        result = game.update()
        if result:
            display.fill(0)
            display.text(result, 30, 60, 1)
            display.show()
            while not rp2.bootsel_button():
                time.sleep(0.1)
            game = BrickBreaker(display, mpu)

        time.sleep(0.01)

if __name__ == "__main__":
    main()