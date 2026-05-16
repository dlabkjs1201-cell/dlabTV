import tkinter as tk
from tkinter import messagebox
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# ==========================================
# 0. 전역 변수 및 Tkinter 함수
# ==========================================
destroyed_count = 0
placed_count = 0

def show_quit_dialog():
    pop = tk.Tk()
    pop.title("Quit")
    pop.geometry("450x200+500+400")
    pop.attributes('-topmost', True)
    pop.resizable(False, False)
    label = tk.Label(pop, text="정말 나가시겠습니까?", font=("맑은 고딕", 11))
    label.pack(pady=25)
    btn_frame = tk.Frame(pop)
    btn_frame.pack()
    exit_btn = tk.Button(btn_frame, text="나가기", width=10, height=2, command=lambda: [pop.destroy(), application.quit()])
    exit_btn.pack(side="left", padx=10)
    back_btn = tk.Button(btn_frame, text="돌아가기", width=10, height=2, command=pop.destroy)
    back_btn.pack(side="right", padx=10)
    pop.mainloop()

# ==========================================
# 1. 앱 및 환경 설정
# ==========================================
app = Ursina()
Sky(color=color.light_gray)
ground = Entity(model='plane', scale=(200, 1, 200), color=color.green,
                texture='white_cube', texture_scale=(50, 50), collider='box')

# ==========================================
# 2. 구조물 생성 로직
# ==========================================
world_parent = Entity()

def setup_world():
    global world_parent
    destroy(world_parent)
    world_parent = Entity()

    # Main Tower
    tower = Entity(parent=world_parent, model='cylinder', color=color.light_gray, scale=(4, 10, 4),
                   position=(-15, 5, 15), collider='box')
    tower_roof = Entity(parent=world_parent, model='cone', color=color.dark_gray, scale=(5, 3, 5),
                        position=(-15, 11.5, 15))

    # Additional Tower behind spawn (여러 큐브로 구성)
    tower_behind_pos = (0, 0, -25)
    tower_height = 5
    for i in range(tower_height):
        for x in range(4):
            for z in range(4):
                cube_pos = (tower_behind_pos[0] + x * 1 - 1.5,
                            i * 1 + 0.5,
                            tower_behind_pos[2] + z * 1 - 1.5)
                Entity(parent=world_parent, model='cube', color=color.gray,
                       texture='white_cube', scale=(1, 1, 1),
                       position=cube_pos, collider='box')

    # Maze
    maze_data = [
        [1, 1, 2, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 3],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    maze_p = Entity(parent=world_parent, position=(12, 0, -5))
    for z, row in enumerate(maze_data):
        for x, cell in enumerate(row):
            pos = (x * 2, 1.5, z * 2)
            if cell == 1:
                Entity(parent=maze_p, model='cube', color=color.orange, texture='white_cube', position=pos,
                       scale=(2, 3, 2), collider='box')
            elif cell == 2:
                Entity(parent=maze_p, model='cube', color=color.lime, position=(pos[0], 0.1, pos[2]), scale=(2, 0.2, 2))
            elif cell == 3:
                Entity(parent=maze_p, model='cube', color=color.red, position=(pos[0], 0.1, pos[2]), scale=(2, 0.2, 2))

    # Car and Stairs
    car_e = Entity(parent=world_parent, position=(-10, 0, 5))
    Entity(parent=car_e, model='cube', color=color.red, scale=(3, 1.5, 5), position=(0, 1, 0), collider='box')

    for i in range(10):
        Entity(parent=world_parent, model='cube', color=color.white, texture='white_cube', position=(5, i * 0.5, 5 + i),
               scale=(4, 0.5, 2), collider='box')

setup_world()

# ==========================================
# 3. 플레이어 및 캐릭터 설정
# ==========================================
player = FirstPersonController(model='cube', y=2, z=-10, color=color.clear, mouse_sensitivity=Vec2(0, 0))
player.cursor.visible = False
mouse.locked = False

avatar = Entity(parent=player)
head = Entity(parent=avatar, model='sphere', color=color.yellow, scale=(0.9, 0.9, 0.9), position=(0, 2.5, 0))
torso = Entity(parent=avatar, model='cube', color=color.blue, scale=(1, 1, 0.5), position=(0, 1.5, 0))
l_arm = Entity(parent=avatar, model='cube', color=color.green, scale=(0.4, 1, 0.4), position=(-0.7, 1.5, 0))
r_arm = Entity(parent=avatar, model='cube', color=color.green, scale=(0.4, 1, 0.4), position=(0.7, 1.5, 0))
l_leg = Entity(parent=avatar, model='cube', color=color.green, scale=(0.4, 1, 0.4), position=(-0.25, 0.5, 0))
r_leg = Entity(parent=avatar, model='cube', color=color.green, scale=(0.4, 1, 0.4), position=(0.25, 0.5, 0))

pickaxe_handle = Entity(parent=r_arm, model='cylinder', color=color.brown,
                        scale=(0.2, 1.5, 0.2), position=(1.0, -0.5, 0.5), rotation=(0, 0, 0))
pickaxe_head = Entity(parent=pickaxe_handle, model='cube', color=color.dark_gray,
                      scale=(5, 1.5, 1.5), position=(0, 0.5, 0), collider='box')

camera_pivot = Entity(parent=player, y=1.5)
camera.parent = camera_pivot
camera.position = (0, 2, -12)
camera.rotation_x = 15

# ==========================================
# 4. 인트로
# ==========================================
intro_parent = Entity(parent=camera.ui, z=-20)
intro_bg = Entity(parent=intro_parent, model='quad', scale=(2, 2), color=color.white, z=1)
intro_text = Text(text='HELLOBLOCKS', parent=intro_parent, origin=(0, 0), scale=7, color=color.black, z=0)
version_text = Text(text='V1.2.2', parent=intro_parent, position=(-0.72, -0.4), scale=2, color=color.black, z=-1)

def start_game():
    destroy(intro_parent)
invoke(start_game, delay=5.0)

# ==========================================
# 5. 시스템 로직 및 입력 처리
# ==========================================
# UI 텍스트 위치 정렬
counter_text = Text(text='Destroyed: 0', position=(-0.40, 0.476), scale=1.5, color=color.white)
placed_text = Text(text='Placed: 0', position=(-0.16, 0.476), scale=1.5, color=color.white)

def update():
    if held_keys['right mouse']:
        player.rotation_y += mouse.velocity[0] * 200
        camera_pivot.rotation_x -= mouse.velocity[1] * 200
        camera_pivot.rotation_x = clamp(camera_pivot.rotation_x, -15, 45)
    if player.y < -10:
        player.position = (0, 5, -10)

def input(key):
    global destroyed_count, placed_count
    # Q to destroy
    if key == 'q':
        hit_info = pickaxe_head.intersects()
        if hit_info.hit and hit_info.entity != ground and hit_info.entity != player:
            destroy(hit_info.entity)
            destroyed_count += 1
            counter_text.text = f'Destroyed: {destroyed_count}'

    # E to place
    if key == 'e':
        if mouse.hovered_entity:
            raw_pos = mouse.world_point + mouse.normal * 0.5
            snapped_pos = Vec3(round(raw_pos.x), round(raw_pos.y), round(raw_pos.z))
            Entity(parent=world_parent, model='cube', color=color.white, texture='white_cube',
                   position=snapped_pos, scale=(1, 1, 1), collider='box')
            placed_count += 1
            placed_text.text = f'Placed: {placed_count}'

def reset_world():
    global destroyed_count, placed_count
    destroyed_count = 0
    placed_count = 0
    counter_text.text = 'Destroyed: 0'
    placed_text.text = 'Placed: 0'
    setup_world()
    player.position = (0, 2, -10)
    player.rotation = (0, 0, 0)
    camera_pivot.rotation = (0, 0, 0)

# ==========================================
# 6. UI 버튼 및 Reset 기능
# ==========================================
leave_btn = Button(text='LEAVE', color=color.rgba(0, 0, 255, 120), position=(-0.67, 0.46), scale=(0.15, 0.05), on_click=show_quit_dialog)
reset_btn = Button(text='RESET', color=color.rgba(255, 0, 0, 120), position=(-0.51, 0.46), scale=(0.15, 0.05), on_click=reset_world)

app.run()