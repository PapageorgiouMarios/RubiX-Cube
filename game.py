from ursina import *


def create_sensor(name, pos, scale):
    return Entity(
        name=name,
        position=pos,
        model='cube',
        color=color.dark_gray,
        scale=scale,
        collider='box',
        visible=False
    )


def set_up_camera():
    EditorCamera()
    camera.world_position = (0, 0, 15)


class Game:
    def __init__(self):
        self.app = Ursina(icon="assets/ursina.ico", title="RubiX Cube")

        self.cursor = None

        self.ground = None
        self.sphere = None
        self.parent_entity = None
        self.cubes = []

        self.rotation_axes = {}
        self.side_positions = {}

        self.animation_time = 0
        self.action_trigger = False
        self.action_mode = False

        self.message = None
        self.rotation = 0

        self.LEFT_sensor = None
        self.FACE_sensor = None
        self.BACK_sensor = None
        self.RIGHT_sensor = None
        self.TOP_sensor = None
        self.BOTTOM_sensor = None

    def set_window(self, width, height):
        self.cursor = Cursor(texture='cursor', color=color.black)
        window.size = (width, height)
        window.center = True
        window.borderless = False

    def load_environment(self):
        self.ground = Entity(model='quad', scale=60, texture='white_cube', texture_scale=(60, 60), rotation_x=90, y=-4,
                             color=color.light_gray)
        self.sphere = Entity(model='sphere', scale=100, texture='assets/sky0', double_sided=True)

        self.parent_entity = Entity(model='cube.obj', texture='white_cube')

    def load_cubes(self):
        # Load the Rubik's Cube model
        cube_model = 'assets/cube.obj'  # 3d Object file used to represent the cubes
        cube_texture = 'assets/cube_color_texture.png'  # colors the cubes have

        # All possible directions
        LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}
        SIDE_POSITIONS = LEFT | BOTTOM | FACE | BACK | RIGHT | TOP

        self.cubes = [Entity(model=cube_model, texture=cube_texture, position=pos) for pos in SIDE_POSITIONS]

    def load_sensors(self):
        self.LEFT_sensor = create_sensor(name='LEFT', pos=(-0.99, 0, 0), scale=(1.01, 3.01, 3.01))
        self.FACE_sensor = create_sensor(name='FACE', pos=(0, 0, -0.99), scale=(3.01, 3.01, 1.01))
        self.BACK_sensor = create_sensor(name='BACK', pos=(0, 0, 0.99), scale=(3.01, 3.01, 1.01))
        self.RIGHT_sensor = create_sensor(name='RIGHT', pos=(0.99, 0, 0), scale=(1.01, 3.01, 3.01))
        self.TOP_sensor = create_sensor(name='TOP', pos=(0, 1, 0), scale=(3.01, 1.01, 3.01))
        self.BOTTOM_sensor = create_sensor(name='BOTTOM', pos=(0, -1, 0), scale=(3.01, 1.01, 3.01))

    def configure_settings(self):
        LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}

        self.rotation_axes = {'LEFT': 'x', 'RIGHT': 'x', 'TOP': 'y', 'BOTTOM': 'y', 'FACE': 'z', 'BACK': 'z'}
        self.side_positions = {'LEFT': LEFT, 'BOTTOM': BOTTOM, 'RIGHT': RIGHT, 'FACE': FACE, 'BACK': BACK, 'TOP': TOP}

        self.message = Text(origin=(0, 19), color=color.black)
        self.message.text = dedent(f"{'ACTION mode ON' if self.action_mode else 'VIEW mode ON'} "
                                   f"(to switch press K)").strip()

        self.animation_time = 0.5
        self.action_trigger = True
        self.action_mode = False
        self.rotation = 0

    def toggle_animation_trigger(self):
        self.action_trigger = not self.action_trigger

    def reparent_scene(self):
        for cube in self.cubes:
            if cube.parent == self.parent_entity:
                world_position = round(cube.world_position, 1)
                world_rotation = cube.world_rotation
                cube.parent = scene
                cube.position = world_position
                cube.rotation = world_rotation
        self.parent_entity.rotation = 0

    def rotate_side(self, side):

        LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}

        cube_side_positions = {'LEFT': LEFT, 'BOTTOM': BOTTOM, 'RIGHT': RIGHT, 'FACE': FACE, 'BACK': BACK, 'TOP': TOP}

        self.action_trigger = False
        cube_positions = cube_side_positions[side]
        rotation_axis = self.rotation_axes[side]

        self.reparent_scene()

        for cube in self.cubes:
            if cube.position in cube_positions:
                cube.parent = self.parent_entity
                eval(f'self.parent_entity.animate_rotation_{rotation_axis}(90, duration=self.animation_time)')
        invoke(self.toggle_animation_trigger, delay=self.animation_time + 0.11)

    def random_state(self, rotations):
        for _ in range(rotations + 1):
            self.rotate_side_no_animation(random.choice(list(self.rotation_axes)))

    def rotate_side_no_animation(self, side):

        LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}

        cube_side_positions = {'LEFT': LEFT, 'BOTTOM': BOTTOM, 'RIGHT': RIGHT, 'FACE': FACE, 'BACK': BACK, 'TOP': TOP}

        cube_positions = cube_side_positions[side]
        rotation_axis = self.rotation_axes[side]

        self.reparent_scene()

        for cube in self.cubes:
            if cube.position in cube_positions:
                cube.parent = self.parent_entity
                exec(f'self.parent_entity.rotation_{rotation_axis} = 90')


def input(key):
    if (mouse.left or mouse.right) and game.action_mode and game.action_trigger:
        for hit in mouse.collisions:
            collider_name = hit.entity.name
            if (mouse.left and collider_name in 'LEFT RIGHT FACE BACK' or
                    mouse.right and collider_name in 'TOP BOTTOM'):
                game.rotate_side(collider_name)
                break
    if key == 'k':
        game.action_mode = not game.action_mode
        game.message.text = dedent(f"{'ACTION mode ON' if game.action_mode else 'VIEW mode ON'} "
                                   f"(to switch press K)").strip()


if __name__ == "__main__":
    game = Game()
    game.set_window(1280, 720)
    game.load_environment()
    game.load_cubes()
    game.load_sensors()
    game.configure_settings()
    set_up_camera()
    game.random_state(10)
    game.app.run()
