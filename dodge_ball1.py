import sh1107
from Mpu6050_mahony import MPU6050
import Pico_Wear
import rp2
import time
import random
from TimeToDoFile import TimeToDo

# 初始化设备
display, mpu = Pico_Wear.Pico_Wear_Init()

# 游戏常量
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
PLAYER_SIZE = 10
BULLET_SIZE = 3
MAX_BULLETS = 20

# 游戏变量
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
bullets = []
start_time = 0
game_over = False

mpu_scheduler = TimeToDo(100)  # 每秒100次更新姿态
game_scheduler = TimeToDo(60)  # 每秒60次更新游戏

def update_player():
    global player_x, player_y
    mpu.update_mahony()
    roll, pitch, _ = mpu.get_angles()
    
    # 将角度限制在-20到20度之间，并映射到屏幕坐标
    player_x = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, 
                          SCREEN_WIDTH // 2 + (roll / 20) * (SCREEN_WIDTH // 2 - PLAYER_SIZE)))
    player_y = max(0, min(SCREEN_HEIGHT - PLAYER_SIZE, 
                          SCREEN_HEIGHT // 2 + (pitch / 20) * (SCREEN_HEIGHT // 2 - PLAYER_SIZE)))

def create_bullet():
    side = random.randint(0, 3)
    if side == 0:  # 上
        return [random.randint(0, SCREEN_WIDTH), 0, random.uniform(-1, 1), random.uniform(0.5, 1)]
    elif side == 1:  # 右
        return [SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT), random.uniform(-1, -0.5), random.uniform(-1, 1)]
    elif side == 2:  # 下
        return [random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT, random.uniform(-1, 1), random.uniform(-1, -0.5)]
    else:  # 左
        return [0, random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 1), random.uniform(-1, 1)]

def update_bullets():
    global bullets
    for bullet in bullets:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
    bullets = [b for b in bullets if 0 <= b[0] < SCREEN_WIDTH and 0 <= b[1] < SCREEN_HEIGHT]
    
    if len(bullets) < min(MAX_BULLETS, int((time.time() - start_time) / 5) + 5):
        bullets.append(create_bullet())

def check_collision():
    for bullet in bullets:
        if (player_x < bullet[0] < player_x + PLAYER_SIZE and
            player_y < bullet[1] < player_y + PLAYER_SIZE):
            return True
    return False

def draw_game():
    display.fill(0)
    
    # 绘制玩家
    display.fill_rectangle(int(player_x), int(player_y), PLAYER_SIZE, PLAYER_SIZE, 1)
    
    # 绘制子弹
    for bullet in bullets:
        display.fill_circle(int(bullet[0]), int(bullet[1]), BULLET_SIZE, 1)
    
    # 显示时间
    elapsed_time = int(time.time() - start_time)
    display.text(f"Time: {elapsed_time}", 0, 0, 1)
    
    display.show()

def update_and_draw_game():
    global game_over
    if not game_over:
        update_bullets()
        if check_collision():
            game_over = True
            game_over_screen()
        else:
            draw_game()

def game_over_screen():
    display.fill(0)
    display.text("GAME OVER", 20, 50, 1)
    score = int(time.time() - start_time)
    display.text(f"Score: {score}", 20, 70, 1)
    display.text("Press button", 10, 90, 1)
    display.text("to restart", 20, 100, 1)
    display.show()

def reset_game():
    global player_x, player_y, bullets, start_time, game_over
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    bullets = []
    start_time = time.time()
    game_over = False

def main():
    global game_over
    reset_game()
    
    while True:
        mpu_scheduler.Do(update_player)
        game_scheduler.Do(update_and_draw_game)
        
        if rp2.bootsel_button():
            while rp2.bootsel_button():
                pass
            time.sleep(0.5)
            reset_game()

if __name__ == "__main__":
    main()