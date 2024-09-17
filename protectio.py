import sh1107
from Mpu6050_mahony import MPU6050
import Pico_Ware_tool
import rp2
import time
import random
from TimeToDoFile import TimeToDo

# 初始化设备
display, mpu = Pico_Ware_tool.Pico_Ware_Init()

# 游戏常量
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
TRIANGLE_SIZE = 20
SHIELD_SIZE = 10
BULLET_SIZE = 3

# 游戏变量
shield_x = SCREEN_WIDTH // 2
shield_y = SCREEN_HEIGHT // 2
bullets = []
score = 0

mpu_scheduler = TimeToDo(100)  # 每秒100次更新姿态
game_scheduler = TimeToDo(60)  # 游戏主循环60FPS

def update_mpu():
    mpu.update_mahony()

def create_bullet():
    side = random.randint(0, 3)
    if side == 0:  # 上
        return [random.randint(0, SCREEN_WIDTH), 0]
    elif side == 1:  # 右
        return [SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)]
    elif side == 2:  # 下
        return [random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT]
    else:  # 左
        return [0, random.randint(0, SCREEN_HEIGHT)]

def move_bullets():
    global bullets
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    new_bullets = []
    for bullet in bullets:
        dx = center_x - bullet[0]
        dy = center_y - bullet[1]
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            bullet[0] += dx / distance
            bullet[1] += dy / distance
        if 0 <= bullet[0] < SCREEN_WIDTH and 0 <= bullet[1] < SCREEN_HEIGHT:
            new_bullets.append(bullet)
    bullets = new_bullets

def check_collision():
    global score, bullets
    # 检查与护盾的碰撞
    new_bullets = []
    for bullet in bullets:
        if (shield_x - SHIELD_SIZE // 2 <= bullet[0] <= shield_x + SHIELD_SIZE // 2 and
            shield_y - SHIELD_SIZE // 2 <= bullet[1] <= shield_y + SHIELD_SIZE // 2):
            score += 1
        else:
            new_bullets.append(bullet)
    bullets = new_bullets

    # 检查与三角形的碰撞
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    for bullet in bullets:
        if ((center_x - TRIANGLE_SIZE // 2 <= bullet[0] <= center_x + TRIANGLE_SIZE // 2) and
            (center_y - TRIANGLE_SIZE // 2 <= bullet[1] <= center_y + TRIANGLE_SIZE // 2)):
            return True
    return False

def draw_game():
    display.fill(0)
    
    # 绘制三角形
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    display.fill_triangle(
        center_x, center_y - TRIANGLE_SIZE // 2,
        center_x - TRIANGLE_SIZE // 2, center_y + TRIANGLE_SIZE // 2,
        center_x + TRIANGLE_SIZE // 2, center_y + TRIANGLE_SIZE // 2,
        1
    )
    
    # 绘制护盾
    display.fill_rectangle(int(shield_x - SHIELD_SIZE // 2), int(shield_y - SHIELD_SIZE // 2), SHIELD_SIZE, SHIELD_SIZE, 1)
    
    # 绘制子弹
    for bullet in bullets:
        display.fill_circle(int(bullet[0]), int(bullet[1]), BULLET_SIZE, 1)
    
    # 绘制分数
    display.text(f"Score: {score}", 0, 0, 1)
    
    display.show()

def game_over():
    display.fill(0)
    display.text("GAME OVER", 20, 50, 1)
    display.text(f"Score: {score}", 20, 70, 1)
    display.show()
    time.sleep(2)

def reset_game():
    global shield_x, shield_y, bullets, score
    shield_x = SCREEN_WIDTH // 2
    shield_y = SCREEN_HEIGHT // 2
    bullets = []
    score = 0

def main():
    global shield_x, shield_y, bullets
    
    while True:
        mpu_scheduler.Do(update_mpu)
        
        def update_game():
            global shield_x, shield_y, bullets
            
            # 更新护盾位置
            roll, pitch, _ = mpu.get_angles()
            shield_x = max(SHIELD_SIZE // 2, min(SCREEN_WIDTH - SHIELD_SIZE // 2, SCREEN_WIDTH // 2 + roll))
            shield_y = max(SHIELD_SIZE // 2, min(SCREEN_HEIGHT - SHIELD_SIZE // 2, SCREEN_HEIGHT // 2 + pitch))
            
            # 移动子弹
            move_bullets()
            
            # 随机生成新子弹
            if random.random() < 0.05:  # 10%的概率生成新子弹
                bullets.append(create_bullet())
            
            # 检查碰撞
            if check_collision():
                game_over()
                reset_game()
            
            # 绘制游戏
            draw_game()
        
        game_scheduler.Do(update_game)
        
        # 检查按钮
        if rp2.bootsel_button():
            while rp2.bootsel_button():
                pass
            time.sleep(0.5)
            reset_game()

if __name__ == "__main__":
    main()