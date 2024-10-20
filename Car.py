import time
import random
from machine import Pin, I2C, mem32
from Mpu6050_mahony import MPU6050
import rp2
from Pico_Wear import PicoWear
#====================PICO WARE Init====================================
# 初始化
# 主程序
pico = PicoWear()

# 遊戲參數
CAR_WIDTH = 10
CAR_HEIGHT = 15
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
OBSTACLE_WIDTH = 10
OBSTACLE_HEIGHT = 10
OBSTACLE_SPEED = 4
LANE_SPEED = 4
LANE_WIDTH = 2
LANE_GAP = 20

class Car:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
        self.y = SCREEN_HEIGHT - CAR_HEIGHT - 5

    def move(self, roll):
        move = int(roll * 2 + 64)
        self.x = max(0, min(SCREEN_WIDTH - CAR_WIDTH, move))

    def draw(self):
        pico.display.fill_rectangle(self.x, self.y, CAR_WIDTH, CAR_HEIGHT, 1)

class Obstacle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
        self.y = 0

    def move(self):
        self.y += OBSTACLE_SPEED
        return self.y > SCREEN_HEIGHT

    def draw(self):
        pico.display.fill_rectangle(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, 1)

class RoadLanes:
    def __init__(self):
        self.lanes = [LANE_GAP, LANE_GAP * 2, LANE_GAP * 3, LANE_GAP * 4, LANE_GAP * 5]
        self.y = 0

    def move(self):
        self.y = (self.y + LANE_SPEED) % LANE_GAP

    def draw(self):
        for x in self.lanes:
            y = self.y
            while y < SCREEN_HEIGHT:
                pico.display.fill_rectangle(x, y, LANE_WIDTH, LANE_GAP // 2, 1)
                y += LANE_GAP

def check_collision(car, obstacle):
    return (car.x < obstacle.x + OBSTACLE_WIDTH and
            car.x + CAR_WIDTH > obstacle.x and
            car.y < obstacle.y + OBSTACLE_HEIGHT and
            car.y + CAR_HEIGHT > obstacle.y)

def game_over():
    pico.display.fill(0)
    pico.display.text("Game Over", 30, 60, 1)
    pico.display.show()
    time.sleep(3)

def main():
    car = Car()
    obstacles = []
    road_lanes = RoadLanes()
    score = 0
    game_speed = 0.02

    while True:
        pico.mpu.calculate_tilt_angle()
        roll = -pico.mpu.Get_tilt_angle()

        car.move(roll)
        road_lanes.move()

        if random.random() < 0.2:
            obstacles.append(Obstacle())

        pico.display.fill(0)
        road_lanes.draw()
        car.draw()

        for obstacle in obstacles[:]:
            if obstacle.move():
                obstacles.remove(obstacle)
                score += 1
            else:
                obstacle.draw()
                if check_collision(car, obstacle):
                    game_over()
                    return

        pico.display.text(f"Score: {score}", 0, 0, 1)
        pico.display.show()
        time.sleep(game_speed)

if __name__ == "__main__":
    while True:
        main()
        while not rp2.bootsel_button():
            time.sleep(0.1)