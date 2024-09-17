import TimeToDo
from machine import Pin, I2C, RTC,Timer
    
import utime as time
import math
import gc
import sh1107
from Mpu6050_mahony import MPU6050
import micropython
import rp2
from machine import mem32
import network
import time
#====================PICO WARE Init====================================
# OLED 的電源
PAD_CONTROL_REGISTER = 0x4001c024
mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

# 設定 GP9 為輸出，並設置輸出(GND), GP8 為輸出，並設置輸出 1
pin9 = Pin(9, Pin.OUT, value=0)
pin8 = Pin(8, Pin.OUT, value=0)
time.sleep(1)
pin8 = Pin(8, Pin.OUT, value=1)

# mpu6050 的電源
PAD_CONTROL_REGISTER = 0x4001c05c
mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

# GP22 為輸出，並設置輸出 1
pin22 = Pin(22, Pin.OUT, value=0)
time.sleep(1)
pin22 = Pin(22, Pin.OUT, value=1)
time.sleep(1)
# 初始化I2C
i2c0 = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
i2c1 = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
display = sh1107.SH1107_I2C(128, 128, i2c1, None, 0x3c)

# 清空顯示屏
display.fill(0)
display.show()

# 初始化MPU6050
mpu = MPU6050(i2c0)

#====================PICO WARE Init End====================================
OnUpdateScreenTimeTo = TimeToDo.TimeToDo(16) #每秒60張
OnTiltAnglesTimeTo = TimeToDo.TimeToDo(10) #每秒100次


        
def CalButton():
    #按鈕按一下進行校正
    button = rp2.bootsel_button()
    if button == 1:
        # 只按一下
        while button == 1:
            button = rp2.bootsel_button()
        mpu.calibrate_tilt()
        time.sleep(1)#等待手的抖動停止才校正
        mpu.calibrate_tilt()
        

def calculate_tilt_angles():
    mpu.calculate_tilt_angles()
    
def DrowScreen():
    tilt = mpu.last_tilt_angle
    display.fill(0)
    # 定義圓心和半徑
    center_x, center_y = 64, 64
    radius = 45
    tick_length = 5  # 普通刻度線的長度
    long_tick_length = 10  # 90度刻度線的長度

    # 畫出外圓
    display.draw_circle(center_x, center_y, radius, 1)

    # 繪製刻度、數字、和指向0度的線
    for angle in range(-180, 180, 30):
        # 計算實際角度（加上 tilt 進行旋轉）
        rotated_angle = angle + tilt
        radian = math.radians(rotated_angle)

        # 根據角度選擇刻度線長度
        if angle == 90 or angle == -90:
            length = long_tick_length
        else:
            length = tick_length

        # 計算刻度的位置（外圓上的點）
        x_out = center_x + int(radius * math.cos(radian))
        y_out = center_y + int(radius * math.sin(radian))

        # 計算刻度的起點位置（內圈上的點）
        x_in = center_x + int((radius - length) * math.cos(radian))
        y_in = center_y + int((radius - length) * math.sin(radian))

        # 畫出刻度線
        display.line(x_in, y_in, x_out, y_out, 1)

        # 計算數字的位置（隨刻度旋轉）
        x_text = center_x + int((radius + 10) * math.cos(radian)) - 5
        y_text = center_y + int((radius + 10) * math.sin(radian)) - 3
        display.text(str(-angle), x_text, y_text, 1)
        
        # 畫從圓心到0度位置的線
        if angle == 0:
            display.line(center_x, center_y, x_out, y_out, 1)

    # 繪製固定的水平線
    display.hline(center_x, center_y, 128, 1)

    # 在水平線上顯示當前 tilt 角度
    tilt_text = f"T:{tilt:.1f}'"
    text_width = len(tilt_text) * 8  # 假設每個字母寬度為8像素
    display.text(tilt_text, center_x - text_width // 2, center_y - 10, 1)
    
    # 顯示結果
    display.show()


if __name__ == '__main__':
    while True:
        CalButton()
        OnTiltAnglesTimeTo.Do(calculate_tilt_angles)
        OnUpdateScreenTimeTo.Do(DrowScreen)
        