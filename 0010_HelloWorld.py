from Pico_Wear import PicoWear  # 從 Pico_Wear 模組導入 PicoWear 類別
import random  # 導入 random 模組，用於生成隨機數
import time  # 導入 time 模組，用於時間處理

pico = PicoWear()  # 初始化 PicoWear 物件
display = pico.display  # 獲取顯示設備物件

# 定義字母的初始位置和速度
letters = list("HELLO WORLD")  # 將字串 "HELLO WORLD" 轉為字母列表
positions = []  # 初始化字母位置列表
velocities = []  # 初始化字母速度列表

def init_positions():  # 定義初始化字母位置和速度的函數
    global positions, velocities  # 聲明全局變量 positions 和 velocities
    positions = []  # 重置字母位置列表
    velocities = []  # 重置字母速度列表
    start_x = 64 - len(letters) * 4  # 計算字母初始水平位置的起點
    for i, letter in enumerate(letters):  # 遍歷每個字母
        positions.append([start_x + i * 8, 60])  # 設定字母的初始位置
        velocities.append([0, 0])  # 設定字母的初始速度為 0

def explode_letters():  # 定義字母爆炸效果的函數
    for i in range(len(letters)):  # 遍歷每個字母
        velocities[i] = [random.uniform(-10, 10), random.uniform(-10, 10)]  # 為每個字母隨機生成速度

def update_positions():  # 定義更新字母位置的函數
    for i in range(len(letters)):  # 遍歷每個字母
        positions[i][0] += velocities[i][0]  # 更新字母的 X 座標
        positions[i][1] += velocities[i][1]  # 更新字母的 Y 座標
        
        # 邊界檢查
        if positions[i][0] < 0 or positions[i][0] > 120:  # 檢查字母是否超出水平邊界
            velocities[i][0] *= -1  # 若超出，反轉水平速度
        if positions[i][1] < 0 or positions[i][1] > 120:  # 檢查字母是否超出垂直邊界
            velocities[i][1] *= -1  # 若超出，反轉垂直速度

def draw_letters():  # 定義繪製字母的函數
    display.fill(0)  # 清空顯示器內容
    for i, letter in enumerate(letters):  # 遍歷每個字母
        display.text(letter, int(positions[i][0]), int(positions[i][1]), 1)  # 在指定位置繪製字母
    display.show()  # 更新顯示內容

def animation_loop():  # 定義動畫循環函數
    while True:  # 無限循環
        # 顯示靜態文字
        display.fill(0)  # 清空顯示器內容
        display.text("HELLO WORLD", 24, 60, 1)  # 在屏幕上繪製靜態字串 "HELLO WORLD"
        display.show()  # 更新顯示內容
        time.sleep(1)  # 停留 1 秒鐘
        
        # 爆炸效果
        init_positions()  # 初始化字母位置和速度
        explode_letters()  # 觸發字母爆炸效果
        start_time = time.ticks_ms()  # 獲取當前時間戳
        while time.ticks_diff(time.ticks_ms(), start_time) < 3000:  # 持續 3 秒鐘的爆炸效果
            update_positions()  # 更新字母位置
            draw_letters()  # 繪製更新後的字母
            time.sleep(0.01)  # 等待 10 毫秒

# 開始動畫循環
animation_loop()  # 調用動畫循環函數
