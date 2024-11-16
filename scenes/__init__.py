import threading
import pygame
from pygame.locals import *
from utility import *

from entities.player import Player, Enemy
from entities.bullet import Bullet, Bomb
from entities.rocket import Rocket
from entities.collectable import Collectable, BombItem


class Scene:
    active_scene = None

    def __init__(self) -> None:
        pass

    def update(self) -> None:
        pass

    pass


class MenuScene(Scene):
    def __init__(self, screen, surface, screen_width, screen_height) -> None:
        super().__init__()
        self.screen = screen
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.start_button = Button(300, 250, 200, 80, text="Start", font_size=36)

    def update(self):
        if Input.is_key_pressed(pygame.K_KP_ENTER):
            Scene.active_scene = GameScene(
                self.screen, self.surface, self.screen_width, self.screen_height
            )

        self.surface.fill((0, 0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if self.start_button.is_clicked(event):
                Scene.active_scene = GameScene(
                    self.screen, self.surface, self.screen_width, self.screen_height
                )

        self.start_button.update(mouse_pos)
        self.start_button.draw(self.screen)

        self.screen.blit(self.surface, (0, 0))
        pass

    pass

class GameScene(Scene):
    ENEMY_SPAWN_TIME = 2000  # 15000  # 15000ms / 15s
    ROCKETS_START_TIME = 5000  # 5000ms / 5s

    ENEMY_TUTORIAL_SPAWN_TIME = 10000
    ROCKETS_TUTORIAL_START_TIME = 5000

    def __init__(self, screen, surface, window_width, window_height, is_tutorial) -> None:
        super().__init__()
        self.state: GameState = GameState(screen, surface)
        self.state.window_width = window_width
        self.state.window_height = window_height
        self.is_tutorial = is_tutorial

        SoundSystem.load_background_music("assets/music/background.mp3")

        sounds_data = {
        "Projectile passing": "assets/music/projectile.mp3",
        "Fire bullet": "assets/music/bullet.mp3",
        "Fire cannon": "assets/music/cannon.mp3",
        "Explosion": "assets/music/explosion.mp3",
        "On damage": "assets/music/damage.mp3",
        "On damage projectile": "assets/music/projectile_damage.mp3",
        "Pick up": "assets/music/pickup.mp3"
        }

        SoundSystem.load_all_sounds(sounds_data)
        SoundSystem.play_background_music()

        # Load background images
        self.background_images = [
            pygame.image.load(f"assets/images/background/background_{i}.png")
            for i in range(1, 5)
        ]

        # Load players
        self.state.player_one = Player(
            [f"assets/images/player_one/player_{i}.png" for i in range(1, 9)],
            (220, 212)
        )

        self.state.player_two = Player(
            [f"assets/images/player_two/player_{i}.png" for i in range(1, 9)], 
            (220, 50)
        )

        analog_stick_side = ["top", "middle", "bottom", "middle", "left", "middle", "right", "middle"]

        self.tutorail_analog_stick = [
            pygame.transform.scale(
                pygame.image.load(f"assets/images/tutorial/analog_stick_{side}_white.png"), (170 // 6, 170 // 6)
            ).convert_alpha()
            for side in analog_stick_side 
        ]

        self.current_analog_stick_frame = 0
        self.last_animated_analog_stick = 0
        self.analog_stick_animation_delay = 200

        image_configs = [
        ('joystick', 'assets/images/tutorial/joystick_white.png', (760 // 6, 510 // 6)),
        ('r1_button', 'assets/images/tutorial/r1_button.png', (170 // 6, 170 // 6)),
        ('w_button', 'assets/images/tutorial/w_button.png', (170 // 6, 170 // 6)),
        ('a_button', 'assets/images/tutorial/a_button.png', (170 // 6, 170 // 6)),
        ('s_button', 'assets/images/tutorial/s_button.png', (170 // 6, 170 // 6)),
        ('d_button', 'assets/images/tutorial/d_button.png', (170 // 6, 170 // 6)),
        ('left_arrow_button', 'assets/images/tutorial/left_arrow_button.png', (170 // 6, 170 // 6)),
        ('right_arrow_button', 'assets/images/tutorial/right_arrow_button.png', (170 // 6, 170 // 6)),
        ('up_arrow_button', 'assets/images/tutorial/up_arrow_button.png', (170 // 6, 170 // 6)),
        ('down_arrow_button', 'assets/images/tutorial/down_arrow_button.png', (170 // 6, 170 // 6)),
        ('g_button', 'assets/images/tutorial/g_button.png', (170 // 6, 170 // 6)),
        ('h_button', 'assets/images/tutorial/h_button.png', (170 // 6, 170 // 6)),
        ('button_1', 'assets/images/tutorial/1_button.png', (170 // 6, 170 // 6)),
        ('button_2', 'assets/images/tutorial/2_button.png', (170 // 6, 170 // 6)),
        ('space_button', 'assets/images/tutorial/space_button.png', (200 // 3, 170 // 4)),
        ('ctrl_button', 'assets/images/tutorial/ctrl_button.png', (170 // 3, 170 // 4)),
        ]
        
        self.buttons = {}
        for name, filepath, size in image_configs:
            buttons = pygame.image.load(filepath).convert_alpha()
            buttons = pygame.transform.scale(buttons, size)
            self.buttons[name] = buttons

        Executor.wait(GameScene.ENEMY_SPAWN_TIME if not is_tutorial else GameScene.ENEMY_TUTORIAL_SPAWN_TIME, self.spawn_enemy)
        Executor.wait(GameScene.ROCKETS_START_TIME if not is_tutorial else GameScene.ROCKETS_TUTORIAL_START_TIME, self.spawn_rockets)

        # Parallax settings
        self.parallax_speeds = [0.2, 0.3, 0.4, 0.5]
        self.x_positions = [0, 0, 0, 0]

        Executor.init()
        pass

    def draw_joysticks(self, joystick, r1_button, analog_stick_1, analog_stick_2):
        if self.state.current_time - self.last_animated_analog_stick > self.analog_stick_animation_delay:
            self.current_analog_stick_frame = (self.current_analog_stick_frame + 1) % len(self.tutorail_analog_stick)
            self.last_animated_analog_stick = self.state.current_time

        buttons = [
            self.buttons["joystick"],
            self.buttons["r1_button"],
            self.tutorail_analog_stick[self.current_analog_stick_frame],
            self.tutorail_analog_stick[self.current_analog_stick_frame - 2]
        ]
        positions = [joystick, r1_button, analog_stick_1, analog_stick_2]

        for button, pos in zip(buttons, positions):
            blit_position = (self.state.window_width - pos[0], self.state.window_height - pos[1])
            self.state.screen.blit(button, blit_position)

    def draw_keyboard(self, w, a, s, d, g, h, space, index):
        button_sets = {
            0: [
                (self.buttons["w_button"], w),
                (self.buttons["a_button"], a),
                (self.buttons["s_button"], s),
                (self.buttons["d_button"], d),
                (self.buttons["g_button"], g),
                (self.buttons["h_button"], h),
                (self.buttons["space_button"], space)
            ],
            1: [
                (self.buttons["up_arrow_button"], w),
                (self.buttons["left_arrow_button"], a),
                (self.buttons["down_arrow_button"], s),
                (self.buttons["right_arrow_button"], d),
                (self.buttons["button_1"], g),
                (self.buttons["button_2"], h),
                (self.buttons["ctrl_button"], space)
            ]
        }

        buttons_to_draw = button_sets.get(index, [])

        for button, pos in buttons_to_draw:
            blit_position = (self.state.window_width - pos[0], self.state.window_height - pos[1])
            self.state.screen.blit(button, blit_position)

    def render_ui(self):
        if self.is_tutorial:
            if Input.is_joystick_connected(0):
                self.draw_joysticks((550, 90), (460, 110), (485, 55), (518, 55))
            else:
                self.draw_keyboard((520, 90), (550, 60), (520, 60), (490, 60), (450, 90), (420, 90), (450, 65), 0)
            if Input.is_joystick_connected(1):
                self.draw_joysticks((150, 90), (60, 110), (85, 55), (118, 55))
            else:
                self.draw_keyboard((170, 90), (200, 60), (170, 60), (140, 60), (100, 90), (70, 90), (100, 65), 1)

    def update(self) -> None:
        # Update time
        self.state.current_time = pygame.time.get_ticks()
        self.state.delta_time = (
            self.state.current_time - self.state.previous_time
        ) / 1000.0
        self.state.previous_time = self.state.current_time

        Executor.update()

        # Update input
        self.handle_input()

        self.handle_movement(self.state.player_one, KEYBOARD_PLAYER_ONE_CONTROLS, 0)
        self.handle_movement(self.state.player_two, KEYBOARD_PLAYER_TWO_CONTROLS, 1)

        self.state.surface.fill((0, 0, 0, 0))

        self.render_background(self.state.screen)

        self.state.player_one.check_other_player_edges(self.state.player_two)
        if self.state.enemy is not None:
            self.state.enemy.check_other_player_edges(self.state.player_one)
            self.state.enemy.check_other_player_edges(self.state.player_two)

        self.state.player_one.update(self.state)
        self.state.player_one.render(self.state)
        self.state.player_two.update(self.state)
        self.state.player_two.render(self.state)
        if self.state.enemy is not None:
            self.state.enemy.update(self.state)
            if self.state.enemy.active:
                self.state.enemy.check_edges(
                    self.state.window_width, self.state.window_height
                )
            self.state.enemy.render(self.state)
            if self.state.enemy.health <= 0 and not self.state.enemy.animate_explosion:
                self_center = pygame.Vector2(
                    self.state.enemy.position[0] + self.state.enemy.size[0] / 2, self.state.enemy.position[1] + self.state.enemy.size[1] / 2
                )
                BombItem.Instantiate(self_center)
                self.state.enemy = None  
                # Removing enemy
        
        #Tutorail UI
        self.render_ui()

        # self.state.player_one.update_ui()
        # self.state.player_two.update_ui()

        Bullet.Update_all(
            self.state.player_one,
            self.state.player_two,
            self.state.enemy,
            self.state.surface,
        )
        Rocket.Update_all(
            self.state.player_one,
            self.state.player_two,
            self.state.surface,
            self.state.delta_time,
        )
        Collectable.Update_all(
            self.state.delta_time,
            self.state.player_one,
            self.state.player_two,
            self.state.surface,
        )
        Bomb.Update(
            self.state.screen,
            self.state.window_height,
            self.state.player_one,
            self.state.player_two,
        )

        self.state.screen.blit(self.state.surface, (0, 0))

        pass

    def handle_input(self):
        state = self.state

        if not Input.is_joystick_connected(0):
            if Input.is_key_pressed(KEYBOARD_PLAYER_ONE_CONTROLS[6]):
                if state.player_one.can_fire_bomb():
                    self.fire_bomb(state.player_one, 0)
                elif state.player_one.can_fire():
                    self.fire_bullet(state.player_one, 0)
        else:
            if Input.is_joystick_button_pressed(
                0, JOYSTICK_PLAYER_CONTROLS[4][0]
            ) or Input.is_joystick_button_pressed(0, JOYSTICK_PLAYER_CONTROLS[4][1]):
                if state.player_one.can_fire_bomb():
                    self.fire_bomb(state.player_one, 0)
                elif state.player_one.can_fire():
                    self.fire_bullet(state.player_one, 0)

        if not Input.is_joystick_connected(1):
            if Input.is_key_pressed(KEYBOARD_PLAYER_TWO_CONTROLS[6]):
                if state.player_two.can_fire_bomb():
                    self.fire_bomb(state.player_two, 1)
                elif state.player_two.can_fire():
                    self.fire_bullet(state.player_two, 1)

        else:
            if Input.is_joystick_button_pressed(
                1, JOYSTICK_PLAYER_CONTROLS[4][0]
            ) or Input.is_joystick_button_pressed(1, JOYSTICK_PLAYER_CONTROLS[4][1]):
                if state.player_two.can_fire_bomb():
                    self.fire_bomb(state.player_two, 1)
                elif state.player_two.can_fire():
                    self.fire_bullet(state.player_two, 1)
        pass

    def fire_bullet(self, player, index):
        start_position = pygame.Vector2(
            player.position[0] + player.size[0] / 2,
            player.position[1] + player.size[1] / 2,
        )
        if player.get_component(AimIndicator) is not None:
            target_position = player.get_component(
                AimIndicator
            ).get_indicator_position()

            Bullet.Instantiate(start_position, target_position, index)
            SoundSystem.play_sound("Fire bullet")
            player.fire_cooldown = Bullet.BULLET_FIRE_COOLDOWN
        pass

    def fire_bomb(self, player, index):
        start_position = pygame.Vector2(
            player.position[0] + player.size[0] / 2,
            player.position[1] + player.size[1] / 2,
        )
        if player.get_component(AimIndicator) is not None:
            target_position = player.get_component(
                AimIndicator
            ).get_indicator_position()
            Bomb.Instantiate(start_position, target_position, index)
            SoundSystem.play_sound("Fire cannon")
            player.fire_cooldown = Bullet.BULLET_FIRE_COOLDOWN
            player.throw_bomb()

    # Players input
    def handle_movement(self, player, controls, joystick_index):
        move_velocity, aim_velocity = get_velocity(controls, joystick_index)
        player.move(move_velocity[0], move_velocity[1])

        if aim_velocity != 0:
            if Input.is_joystick_connected(joystick_index):
                player.get_component(AimIndicator).set_indicator_angle(aim_velocity, 2)
            else:
                player.get_component(AimIndicator).adjust_indicator_angle(aim_velocity)

        player.check_edges(self.state.window_width, self.state.window_height)
        pass

    # Render background with parallax
    def render_background(self, screen):
        for i, background_image in enumerate(self.background_images):
            speed = self.parallax_speeds[i]
            self.x_positions[i] -= speed
            if self.x_positions[i] <= -self.state.window_width:
                self.x_positions[i] = 0
            screen.blit(background_image, (self.x_positions[i], 0))
            screen.blit(
                background_image, (self.x_positions[i] + self.state.window_width, 0)
            )
        pass

    def spawn_enemy(self):
        def spawn():
            self.state.enemy = Enemy(
                [f"assets/images/enemy/enemy_{i}.png" for i in range(1, 5)],
                (-50, 100),
            )
            pass

        threading.Thread(target=spawn).start()
        pass

    def spawn_rockets(self):
        Executor.repeat(
            Rocket.PROJECTILE_DURATION,
            lambda: Rocket.LaunchRockets(
                self.state.window_height, self.state.window_width
            ),
        )
        pass

    pass


class ResultScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    pass
