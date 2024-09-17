import math
from TimeToDoFile import TimeToDo
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
import Pico_Wear


class Camera:
    def __init__(self, position=(0.0, 0.0, -20.0), rotation_z=0.0, fov=60.0, width=128, height=128, near=0.1, far=100.0):
        self.position = position
        self.rotation_z = rotation_z
        self.fov = fov
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self.near = near
        self.far = far
        self.PMatrix = self.get_projection_matrix()

    def get_view_matrix(self):
        '''
        cos_z = math.cos(math.radians(self.rotation_z))
        sin_z = math.sin(math.radians(self.rotation_z))
        cx, cy, cz = self.position
        rotation_matrix = [
            [cos_z, -sin_z, 0.0, 0.0],
            [sin_z, cos_z, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        '''
        cx, cy, cz = self.position
        translation_matrix = [
            [1.0, 0.0, 0.0, -cx],
            [0.0, 1.0, 0.0, -cy],
            [0.0, 0.0, 1.0, -cz],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return translation_matrix
        #return self._multiply_matrices(rotation_matrix, translation_matrix)

    def get_projection_matrix(self):
        fov_rad = math.radians(self.fov)
        f = 1.0 / math.tan(fov_rad / 2.0)
        return [
            [f / self.aspect_ratio, 0.0, 0.0, 0.0],
            [0.0, f, 0.0, 0.0],
            [0.0, 0.0, (self.far + self.near) / (self.near - self.far), (2.0 * self.far * self.near) / (self.near - self.far)],
            [0.0, 0.0, -1.0, 0.0]
        ]

    def _multiply_matrices(self, m1, m2):
        result = [[0.0, 0.0, 0.0, 0.0] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                sum_value = 0.0
                for k in range(4):
                    sum_value += m1[i][k] * m2[k][j]
                result[i][j] = sum_value
        return result



    
class Model:
    def __init__(self, vertices, edges, position=[0, 0, 0], rotation=[0, 0, 0]):
        self.vertices = vertices
        self.edges = edges  # 使用邊而不是三角形索引
        self.position = position
        self.rotation = rotation

    @staticmethod
    def create_cube(size=2.0):
        half_size = float(size) / 2.0
        # Define the 8 vertices of a cube
        vertices = [
            (-half_size, -half_size, -half_size),  # Vertex 0: Bottom-front-left
            (half_size, -half_size, -half_size),   # Vertex 1: Bottom-front-right
            (-half_size, half_size, -half_size),   # Vertex 2: Top-front-left
            (half_size, half_size, -half_size),    # Vertex 3: Top-front-right
            (-half_size, -half_size, half_size),   # Vertex 4: Bottom-back-left
            (half_size, -half_size, half_size),    # Vertex 5: Bottom-back-right
            (-half_size, half_size, half_size),    # Vertex 6: Top-back-left
            (half_size, half_size, half_size)      # Vertex 7: Top-back-right
        ]
        # Define the 12 edges of the cube, connecting the vertices
        edges = [
            (0, 1), (1, 3), (3, 2), (2, 0),  # Edges of the front face
            (4, 5), (5, 7), (7, 6), (6, 4),  # Edges of the back face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Edges connecting front and back faces
        ]
        return Model(vertices, edges)
    
    @staticmethod
    def create_triangle( size=2, model_position=(0, 0, 0)):
                        
        half_size = size / 2
        height = math.sqrt(3) * half_size
        vertices = [
            (0, height / 2, 0),     # 頂點
            (-half_size, -height / 2, 0),  # 左下角
            (half_size, -height / 2, 0)    # 右下角
        ]
        indices = [(0, 1, 2)]                
        return Model(vertices, indices)
    
    @staticmethod
    def create_from_obj(file_path):
        vertices = []
        edges = set()

        with open(file_path, 'r') as obj_file:
            for line in obj_file:
                if line.startswith('v '):  # 頂點
                    _, x, y, z = line.split()
                    vertices.append((float(x), float(y), float(z)))
                    # 檢查內存使用情況並回收內存
                    gc.collect()
                elif line.startswith('f '):  # 面
                    face = line.split()[1:]
                    indices = [int(part.split('/')[0]) - 1 for part in face]
                    
                    for i in range(len(indices)):
                        v1 = indices[i]
                        v2 = indices[(i + 1) % len(indices)]
                        edge = (min(v1, v2), max(v1, v2))
                        edges.add(edge)
                        gc.collect()  # 在每次迭代後回收內存

        return Model(vertices, list(edges))
    
    def get_model_matrix(self):
        # Get rotation and translation matrices
        px, py, pz = self.position
        rx, ry, rz = self.rotation

        # Compute cosines and sines for each rotation axis
        #cos_x, sin_x = math.cos(math.radians(rx)), math.sin(math.radians(rx))
        cos_y, sin_y = math.cos(math.radians(ry)), math.sin(math.radians(ry))
        #cos_z, sin_z = math.cos(math.radians(rz)), math.sin(math.radians(rz))

        # Rotation matrices for X, Y, Z axes
        '''
        rotate_x = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cos_x, -sin_x, 0.0],
            [0.0, sin_x, cos_x, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        '''
        rotate_y = [
            [cos_y, 0.0, sin_y, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sin_y, 0.0, cos_y, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        '''
        rotate_z = [
            [cos_z, -sin_z, 0.0, 0.0],
            [sin_z, cos_z, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        '''
        # Combine rotation matrices
        #rotation_matrix = self._multiply_matrices(rotate_x, self._multiply_matrices(rotate_y, rotate_z))

        # Translation matrix
        translation_matrix = [
            [1.0, 0.0, 0.0, px],
            [0.0, 1.0, 0.0, py],
            [0.0, 0.0, 1.0, pz],
            [0.0, 0.0, 0.0, 1.0]
        ]

        # Model matrix combines rotation and translation
        #model_matrix = self._multiply_matrices(rotation_matrix, translation_matrix)
        model_matrix = self._multiply_matrices(rotate_y, translation_matrix)
        
        return model_matrix



    def _multiply_matrices(self, m1, m2):
        result = [[0.0, 0.0, 0.0, 0.0] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                sum_value = 0.0
                for k in range(4):
                    sum_value += m1[i][k] * m2[k][j]
                result[i][j] = sum_value
        return result

    
class Renderer:
    def __init__(self, display, camera):
        self.display = display
        self.camera = camera
        self.width = display.width
        self.height = display.height
        self.screen_vertices = None  # 初始化時不分配記憶體
        
        
    def render(self, model):
        if self.screen_vertices is None or len(self.screen_vertices) != len(model.vertices):
            # 只在首次渲染或頂點數量變更時重新分配記憶體
            self.screen_vertices = [(0, 0)] * len(model.vertices)

        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.PMatrix
        model_matrix = model.get_model_matrix()
        
        mvp_matrix = self.camera._multiply_matrices(projection_matrix, self.camera._multiply_matrices(view_matrix, model_matrix))
        
        self.transform_vertices(model.vertices, mvp_matrix)
        self.draw_model(model)

    def transform_vertices(self, vertices, mvp_matrix):
        half_width = self.width / 2
        half_height = self.height / 2
        # 提前提取矩陣值到局部變數
        m00, m01, m02, m03 = mvp_matrix[0]
        m10, m11, m12, m13 = mvp_matrix[1]
        m20, m21, m22, m23 = mvp_matrix[2]
        m30, m31, m32, m33 = mvp_matrix[3]

        screen_vertices = self.screen_vertices
        for i, (x, y, z) in enumerate(vertices):
            # 使用局部變量來計算轉換
            v_transformed_0 = m00 * x + m01 * y + m02 * z + m03
            v_transformed_1 = m10 * x + m11 * y + m12 * z + m13
            v_transformed_3 = m30 * x + m31 * y + m32 * z + m33

            if v_transformed_3 != 0:
                inv_w = 1.0 / v_transformed_3
                screen_x = int((v_transformed_0 * inv_w + 1) * half_width)
                screen_y = int((1 - v_transformed_1 * inv_w) * half_height)
            else:
                screen_x = int((v_transformed_0 + 1) * half_width)
                screen_y = int((1 - v_transformed_1) * half_height)

            screen_vertices[i] = (screen_x, screen_y)


    def draw_model(self, model):
        for edge in model.edges:
            v1_idx, v2_idx = edge
            screen_p1 = self.screen_vertices[v1_idx]
            screen_p2 = self.screen_vertices[v2_idx]
            # 繪製線段
            self.display.line(screen_p1[0], screen_p1[1], screen_p2[0], screen_p2[1], 1)

    
def CalButton():
    #按鈕按一下進行校正
    button = rp2.bootsel_button()
    if button == 1:
        # 只按一下
        while button == 1:
            button = rp2.bootsel_button()
        time.sleep(0.5)

def main():
    display , mpu = Pico_Wear.Pico_Wear_Init()
    update_timer = TimeToDo(60)  # 60 FPS
    #====================PICO WARE Init End====================================
    camera = Camera(position=(0, 0, 2), rotation_z=0, fov=60, width=128, height=128, near=1, far=100)
    renderer = Renderer(display, camera)
    MyModel = Model.create_from_obj('cloud.obj')
    #MyModel = Model.create_cube()

    MyModel.position[1] = -0.8
    last_time = time.ticks_ms()
    while True:
        current_time = time.ticks_ms()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time
        if delta_time > 0:
            fps = 1.0 / delta_time
        else:
            fps = float('inf')  # 避免除以零的錯誤

        # 更新位置和旋轉
        MyModel.rotation[1] = MyModel.rotation[1] + 5
        # 渲染畫面
        display.fill(0)  # 清空顯示屏
        display.text("FPS: {:.2f}".format(fps), 0, 0, 1)  # 顯示 FPS
        renderer.render(MyModel)
        display.show()
        #CalButton()  # Check for calibration button




if __name__ == '__main__':
    main()