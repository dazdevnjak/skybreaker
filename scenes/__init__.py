import threading
import pygame
from pygame.locals import *
from utility import *

from entities.player import Player, Enemy
from entities.bullet import Bullet, Bomb
from entities.rocket import Rocket
from entities.collectable import Collectable, BombItem

import random


class Scene:
    active_scene = None
    running = False
    async_scene = None
    loading = False
    alpha = 0
    fade_in = True
    scene_loaded = False

    def __init__(self, width, height) -> None:
        self.screen_width = width
        self.screen_height = height
        pass

    def update(self, screen) -> None:
        if Scene.loading:
            if Scene.fade_in:
                Scene.alpha = min(Scene.alpha + 5, 255)
                if Scene.alpha == 255:
                    if Scene.scene_loaded:
                        Scene.fade_in = False
                        Scene.active_scene = Scene.async_scene
            else:
                Scene.alpha = max(Scene.alpha - 5, 0)
                if Scene.alpha == 0:
                    Scene.loading = False
                    Scene.fade_in = True

            color = (0, 0, 0, Scene.alpha)
            fade_surface = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            fade_surface.fill(color)
            screen.blit(fade_surface, (0, 0))
            pass
        pass

    @staticmethod
    def load_async(scene, screen, surface, screen_width, screen_height, is_tutorial):
        Scene.loading = True
        Scene.alpha = 0
        Scene.fade_in = True
        Scene.scene_loaded = False

        def change_scene():
            Scene.async_scene = scene(
                screen, surface, screen_width, screen_height, is_tutorial
            )
            Scene.scene_loaded = True
            pass

        thread = threading.Thread(target=change_scene)
        thread.start()
        pass

    pass


class MenuScene(Scene):
    NAMES_FILE_PATH = "assets/player_names.txt"
    player_one_name_placeholder = None
    player_two_name_placeholder = None

    PLAYER_ONE_HOVER_COLOR = (101, 131, 174)
    PLAYER_TWO_HOVER_COLOR = (86, 138, 117)

    def __init__(
        self, screen, surface, screen_width, screen_height, is_tutorial
    ) -> None:
        super().__init__(screen_width, screen_height)
        self.screen = screen
        self.surface = surface

        MenuScene.player_one_name_placeholder = None
        MenuScene.player_two_name_placeholder = None

        sounds_data = {
            "Button hover": "assets/music/hover.mp3",
            "Button click": "assets/music/click.mp3",
        }

        SoundSystem.load_all_sounds(sounds_data)

        SoundSystem.load_background_music("assets/music/main_backgorund.mp3")
        SoundSystem.play_background_music()

        # Load background images
        self.background_image = [
            pygame.transform.scale(
                pygame.image.load(f"assets/images/scenes/main_menu_screen.png"),
                (576, 324),
            ),
            pygame.transform.scale(
                pygame.image.load(
                    f"assets/images/scenes/select_player_name_screen.png"
                ),
                (576, 324),
            ),
        ]

        self.name_check = False
        self.selected_index = -1

        self.buttons = []
        self.buttons.append(
            Button(
                screen_width / 2,
                screen_height - 50,
                120,
                40,
                text="Start",
                font_size=36,
            )
        )
        self.buttons.append(
            Button(
                screen_width / 2 + 140,
                screen_height - 50,
                120,
                40,
                text="Quit",
                font_size=36,
            )
        )

        self.player_one_name_selected_index = 0
        self.ready_player_one = False
        self.player_two_name_selected_index = 1
        self.ready_player_two = False

        with open(MenuScene.NAMES_FILE_PATH, "r") as file:
            self.player_names = [line.strip() for line in file]

        COL_COUNT = 4

        init_x = ((screen_width - (COL_COUNT * 80 + 10 * COL_COUNT)) / 2) - 90
        init_y = 20 + 10
        x, y = init_x, init_y
        index = 0

        self.name_buttons = []
        for name in self.player_names:
            self.name_buttons.append(Button(x, y, 100, 30, text=name, font_size=18))
            x += 80 + 30
            index += 1
            if (index - 1) == COL_COUNT:
                x = init_x
                y += 20 + 20
                index = 0

        player_one_image_paths = [
            f"assets/images/player_one/player_{i}.png" for i in range(1, 9)
        ]
        player_two_image_paths = [
            f"assets/images/player_two/player_{i}.png" for i in range(1, 9)
        ]

        self.player_one_frames = [
            pygame.transform.scale(pygame.image.load(path), (128, 72)).convert_alpha()
            for path in player_one_image_paths
        ]
        self.player_two_frames = [
            pygame.transform.scale(pygame.image.load(path), (128, 72)).convert_alpha()
            for path in player_two_image_paths
        ]
        self.animation_delay = 100
        self.player_one_current_frame = random.randrange(0, len(self.player_one_frames))
        self.player_two_current_frame = random.randrange(0, len(self.player_two_frames))

        self.last_update = pygame.time.get_ticks()

        self.font = pygame.font.Font(None, 12)
        self.player_one_name_ui = None
        self.player_two_name_ui = None

        self.player_one_ready_text = self.font.render(
            "For ready", False, (0,0,0)
        )
        self.player_two_ready_text = self.font.render(
            "For ready", False, (0,0,0)
        )

        self.title_font = pygame.font.Font(None, 24)
        self.title_text = self.title_font.render("Choose Names", False, (255, 255, 255))
        self.title_position = (
            (self.screen_width - self.title_text.get_rect().width) / 2,
            0,
        )

        image_configs = [
            (
                "space_button",
                "assets/images/tutorial/space_button.png",
                (200 // 3, 170 // 4),
            ),
            (
                "ctrl_button",
                "assets/images/tutorial/ctrl_button.png",
                (170 // 3, 170 // 4),
            ),
            ("r1_button", "assets/images/tutorial/r1_button.png", (170 // 6, 170 // 6)),
        ]

        self.input_buttons = {}
        for name, filepath, size in image_configs:
            button = pygame.image.load(filepath).convert_alpha()
            button = pygame.transform.scale(button, size)
            self.input_buttons[name] = button

    def handle_player_input(self, player_index, INPUT):
        index = (
            self.player_one_name_selected_index
            if player_index == 0
            else self.player_two_name_selected_index
        )
        self.name_buttons[index].is_hovered = False
        if Input.is_joystick_connected(player_index):
            if Input.is_joystick_button_pressed(player_index, 11):
                index = self.change_name_index(index, player_index, -5)
                pass  # GO UP
            elif Input.is_joystick_button_pressed(player_index, 12):
                index = self.change_name_index(index, player_index, 5)
                pass  # GO DOWN
            elif Input.is_joystick_button_pressed(player_index, 14):
                index = self.change_name_index(index, player_index, 1)
                pass  # GO RIGHT
            elif Input.is_joystick_button_pressed(player_index, 13):
                index = self.change_name_index(index, player_index, -1)
                pass  # GO LEFT
            if Input.is_joystick_button_pressed(player_index, 1):
                self.font = pygame.font.SysFont("calibri", 12)
                if player_index == 0:
                    SoundSystem.play_sound("Button click")
                    MenuScene.player_one_name_placeholder = self.player_names[index]
                    self.player_one_name_ui = self.font.render(
                        self.player_names[index],
                        False,
                        MenuScene.PLAYER_ONE_HOVER_COLOR,
                    )
                    self.ready_player_one = True
                else:
                    SoundSystem.play_sound("Button click")
                    MenuScene.player_two_name_placeholder = self.player_names[index]
                    self.player_two_name_ui = self.font.render(
                        self.player_names[index],
                        False,
                        MenuScene.PLAYER_TWO_HOVER_COLOR,
                    )
                    self.ready_player_two = True
                pass  # ACCEPT
        else:
            if Input.is_key_pressed(INPUT[0]):
                index = self.change_name_index(index, player_index, -5)
                pass  # UP
            elif Input.is_key_pressed(INPUT[1]):
                index = self.change_name_index(index, player_index, -1)
                pass  # LEFT
            elif Input.is_key_pressed(INPUT[2]):
                index = self.change_name_index(index, player_index, 5)
                pass  # DOWN
            elif Input.is_key_pressed(INPUT[3]):
                index = self.change_name_index(index, player_index, 1)
                pass  # RIGHT
            if Input.is_key_pressed(INPUT[6]):
                self.font = pygame.font.SysFont("calibri", 12)

                if player_index == 0:
                    SoundSystem.play_sound("Button click")
                    MenuScene.player_one_name_placeholder = self.player_names[index]
                    self.player_one_name_ui = self.font.render(
                        self.player_names[index],
                        False,
                        MenuScene.PLAYER_ONE_HOVER_COLOR,
                    )
                    self.ready_player_one = True
                else:
                    SoundSystem.play_sound("Button click")
                    MenuScene.player_two_name_placeholder = self.player_names[index]
                    self.player_two_name_ui = self.font.render(
                        self.player_names[index],
                        False,
                        MenuScene.PLAYER_TWO_HOVER_COLOR,
                    )
                    self.ready_player_two = True
                pass  # ACCEPT
            pass
        index = max(0, min(index, len(self.name_buttons) - 1))

        if player_index == 0:
            self.player_one_name_selected_index = index
        else:
            self.player_two_name_selected_index = index
        self.name_buttons[index].hover_color = (
            MenuScene.PLAYER_ONE_HOVER_COLOR
            if player_index == 0
            else MenuScene.PLAYER_TWO_HOVER_COLOR
        )
        self.name_buttons[index].is_hovered = True
        pass

    def change_name_index(self, index, player_index, offset):
        changed_index = index + offset
        if player_index == 0:
            if self.player_two_name_selected_index == changed_index:
                changed_index = changed_index + (-1 if offset < 0 else 1)
        elif player_index == 1:
            if self.player_one_name_selected_index == changed_index:
                changed_index = changed_index + (-1 if offset < 0 else 1)
        if changed_index < 0:
            changed_index = len(self.name_buttons) - 1
        elif changed_index > len(self.name_buttons) - 1:
            changed_index = 0
        return changed_index

    def process_input(self):
        if Scene.loading:
            return

        if self.name_check:
            if not self.ready_player_one:
                self.handle_player_input(0, KEYBOARD_PLAYER_ONE_CONTROLS)
            if not self.ready_player_two:
                self.handle_player_input(1, KEYBOARD_PLAYER_TWO_CONTROLS)
            pass
        else:
            if Input.is_joystick_connected(0):
                if Input.is_joystick_button_pressed(0, 13):  # LEFT
                    self.selected_index = max(self.selected_index - 1, 0)
                    for i in range(len(self.buttons)):
                        self.buttons[i].is_hovered = i == self.selected_index
                if Input.is_joystick_button_pressed(0, 14):  # RIGHT
                    self.selected_index = min(self.selected_index + 1, 1)
                    for i in range(len(self.buttons)):
                        self.buttons[i].is_hovered = i == self.selected_index
                if Input.is_joystick_button_pressed(0, 1):  # ACCEPT
                    if self.selected_index == 0:
                        SoundSystem.play_sound("Button click")
                        self.name_check = True
                    elif self.selected_index == 1:
                        SoundSystem.play_sound("Button click")
                        Scene.running = False
                    pass
                pass
            if Input.is_joystick_connected(1):
                if Input.is_joystick_button_pressed(1, 13):  # LEFT
                    self.selected_index = max(self.selected_index - 1, 0)
                    for i in range(len(self.buttons)):
                        self.buttons[i].is_hovered = i == self.selected_index
                if Input.is_joystick_button_pressed(1, 14):  # RIGHT
                    self.selected_index = min(self.selected_index + 1, 1)
                    for i in range(len(self.buttons)):
                        self.buttons[i].is_hovered = i == self.selected_index
                if Input.is_joystick_button_pressed(1, 1):  # ACCEPT
                    if self.selected_index == 0:
                        SoundSystem.play_sound("Button click")
                        self.name_check = True
                    elif self.selected_index == 1:
                        SoundSystem.play_sound("Button click")
                        Scene.running = False
                    pass
                pass
            if Input.is_key_pressed(pygame.K_LEFT) or Input.is_key_pressed(
                pygame.K_w
            ):  # UP
                self.selected_index = max(self.selected_index - 1, 0)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_key_pressed(pygame.K_RIGHT) or Input.is_key_pressed(
                pygame.K_s
            ):  # DOWN
                self.selected_index = min(self.selected_index + 1, 1)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_key_pressed(pygame.K_SPACE) or Input.is_key_pressed(
                pygame.K_RETURN
            ):
                if self.selected_index == 0:
                    SoundSystem.play_sound("Button click")
                    self.name_check = True
                elif self.selected_index == 1:
                    SoundSystem.play_sound("Button click")
                    Scene.running = False
                pass
            pass
        pass

    def update(self, screen):

        self.surface.fill((0, 0, 0, 0))

        self.process_input()

        self.render_background(self.screen)
        if not self.name_check:
            for button in self.buttons:
                button.draw(self.screen)
        else:
            screen.blit(self.title_text, self.title_position)
            for name_button in self.name_buttons:
                name_button.draw(self.screen)

            if not Scene.loading:
                if self.ready_player_one and self.ready_player_two:
                    Scene.load_async(
                        GameScene,
                        self.screen,
                        self.surface,
                        self.screen_width,
                        self.screen_height,
                        True,
                    )

        current_time = pygame.time.get_ticks()
        if (current_time - self.last_update) > self.animation_delay:
            self.player_one_current_frame = (self.player_one_current_frame + 1) % len(
                self.player_one_frames
            )
            self.player_two_current_frame = (self.player_two_current_frame + 1) % len(
                self.player_two_frames
            )
            self.last_update = current_time

        if self.name_check:
            if self.ready_player_one:
                position = (self.screen_width / 2 - 50 - 128, 220)
                screen.blit(self.player_one_name_ui, position)
                screen.blit(
                    self.player_one_frames[self.player_one_current_frame],
                    position,
                )
            else:
                position = (self.screen_width / 2 - 50 - 128, 220)
                screen.blit(self.player_one_ready_text, position)
                screen.blit(
                    self.input_buttons[
                        (
                            "space_button"
                            if not Input.is_joystick_connected(0)
                            else "r1_button"
                        )
                    ],
                    position,
                )
            if self.ready_player_two:
                position = (self.screen_width / 2 - 50 + 128 + 20, 220)
                screen.blit(self.player_two_name_ui, position)
                screen.blit(
                    self.player_two_frames[self.player_two_current_frame],
                    position,
                )
            else:
                position = (self.screen_width / 2 - 50 + 128 + 20, 220)
                screen.blit(self.player_two_ready_text, position)
                screen.blit(
                    self.input_buttons[
                        (
                            "ctrl_button"
                            if not Input.is_joystick_connected(1)
                            else "r1_button"
                        )
                    ],
                    position,
                )

        self.screen.blit(self.surface, (0, 0))
        super().update(screen)
        pass

    # Render background with parallax
    def render_background(self, screen):
        if self.name_check:
            screen.blit(self.background_image[1], (0, 0))
        else:
            screen.blit(self.background_image[0], (0, 0))

    pass


class GameScene(Scene):
    ENEMY_SPAWN_TIME = 10000  # 15000  # 15000ms / 15s
    ROCKETS_START_TIME = 5000  # 5000ms / 5s

    ENEMY_TUTORIAL_SPAWN_TIME = 10000
    ROCKETS_TUTORIAL_START_TIME = 5000

    def on_player_death(self):
        ResultScene.winner, ResultScene.loser = (
            ((self.state.player_one.name, True), (self.state.player_two.name, False))
            if self.state.player_one.lives > self.state.player_two.lives
            else (
                (self.state.player_two.name, False),
                (self.state.player_one.name, True),
            )
        )

        def end_game():
            state = self.state
            Scene.load_async(
                ResultScene,
                state.screen,
                state.surface,
                state.window_width,
                state.window_height,
                False,
            )

        Executor.wait(500, end_game)
        pass

    def __init__(
        self, screen, surface, window_width, window_height, is_tutorial
    ) -> None:
        super().__init__(window_width, window_height)

        Executor.reset()
        Bullet.instances.clear()
        Rocket.instances.clear()
        Rocket.indicator_instances.clear()
        Bomb._instance = None

        self.state: GameState = GameState(screen, surface)
        self.state.window_width = window_width
        self.state.window_height = window_height
        self.state.is_tutorial = is_tutorial
        self.is_tutorial = is_tutorial
        self.player_one_skiping = False
        self.player_two_skiping = False

        sounds_data = {
            "Projectile passing": "assets/music/projectile.mp3",
            "Fire bullet": "assets/music/bullet.mp3",
            "Fire cannon": "assets/music/cannon.mp3",
            "Explosion": "assets/music/explosion.mp3",
            "On damage": "assets/music/damage.mp3",
            "On damage projectile": "assets/music/projectile_damage.mp3",
            "Pick up": "assets/music/pickup.mp3",
        }

        SoundSystem.stop_background_music()
        SoundSystem.load_background_music("assets/music/background.mp3")
        SoundSystem.load_all_sounds(sounds_data)
        SoundSystem.play_background_music()

        # Load background images
        self.background_images = [
            pygame.image.load(f"assets/images/background/background_{i}.png")
            for i in range(1, 5)
        ]

        # Load players
        self.state.player_one = Player(
            MenuScene.player_one_name_placeholder,
            [f"assets/images/player_one/player_{i}.png" for i in range(1, 9)],
            (220, 212),
        )
        self.state.player_one.death_callback = self.on_player_death

        self.state.player_two = Player(
            MenuScene.player_two_name_placeholder,
            [f"assets/images/player_two/player_{i}.png" for i in range(1, 9)],
            (220, 50),
        )
        self.state.player_two.death_callback = self.on_player_death

        analog_stick_side = [
            "top",
            "middle",
            "bottom",
            "middle",
            "left",
            "middle",
            "right",
            "middle",
        ]

        self.tutorail_analog_stick = [
            pygame.transform.scale(
                pygame.image.load(
                    f"assets/images/tutorial/analog_stick_{side}_white.png"
                ),
                (170 // 6, 170 // 6),
            ).convert_alpha()
            for side in analog_stick_side
        ]

        self.current_analog_stick_frame = 0
        self.last_animated_analog_stick = 0
        self.analog_stick_animation_delay = 200

        image_configs = [
            (
                "joystick",
                "assets/images/tutorial/joystick_white.png",
                (760 // 6, 510 // 6),
            ),
            ("r1_button", "assets/images/tutorial/r1_button.png", (170 // 6, 170 // 6)),
            ("w_button", "assets/images/tutorial/w_button.png", (170 // 6, 170 // 6)),
            ("a_button", "assets/images/tutorial/a_button.png", (170 // 6, 170 // 6)),
            ("s_button", "assets/images/tutorial/s_button.png", (170 // 6, 170 // 6)),
            ("d_button", "assets/images/tutorial/d_button.png", (170 // 6, 170 // 6)),
            (
                "left_arrow_button",
                "assets/images/tutorial/left_arrow_button.png",
                (170 // 6, 170 // 6),
            ),
            (
                "right_arrow_button",
                "assets/images/tutorial/right_arrow_button.png",
                (170 // 6, 170 // 6),
            ),
            (
                "up_arrow_button",
                "assets/images/tutorial/up_arrow_button.png",
                (170 // 6, 170 // 6),
            ),
            (
                "down_arrow_button",
                "assets/images/tutorial/down_arrow_button.png",
                (170 // 6, 170 // 6),
            ),
            ("g_button", "assets/images/tutorial/g_button.png", (170 // 6, 170 // 6)),
            ("h_button", "assets/images/tutorial/h_button.png", (170 // 6, 170 // 6)),
            ("button_1", "assets/images/tutorial/1_button.png", (170 // 6, 170 // 6)),
            ("button_2", "assets/images/tutorial/2_button.png", (170 // 6, 170 // 6)),
            (
                "space_button",
                "assets/images/tutorial/space_button.png",
                (200 // 3, 170 // 4),
            ),
            (
                "ctrl_button",
                "assets/images/tutorial/ctrl_button.png",
                (170 // 3, 170 // 4),
            ),
            ("t_button", "assets/images/tutorial/t_button.png", (170 // 6, 170 // 6)),
            ("3_button", "assets/images/tutorial/3_button.png", (170 // 6, 170 // 6)),
            ("o_button", "assets/images/tutorial/o_button.png", (170 // 5, 170 // 6)),
        ]

        self.buttons = {}
        for name, filepath, size in image_configs:
            buttons = pygame.image.load(filepath).convert_alpha()
            buttons = pygame.transform.scale(buttons, size)
            self.buttons[name] = buttons

        self.font = pygame.font.Font(None, 26)
        self.text_surface = self.font.render("Hold to skip", False, (255, 255, 255))

        Executor.wait(
            (
                GameScene.ENEMY_SPAWN_TIME
                if not is_tutorial
                else GameScene.ENEMY_TUTORIAL_SPAWN_TIME
            ),
            self.spawn_enemy,
        )
        Executor.wait(
            (
                GameScene.ROCKETS_START_TIME
                if not is_tutorial
                else GameScene.ROCKETS_TUTORIAL_START_TIME
            ),
            self.spawn_rockets,
        )

        # Parallax settings
        self.parallax_speeds = [0.2, 0.3, 0.4, 0.5]
        self.x_positions = [0, 0, 0, 0]

        Executor.init()
        pass

    def draw_joysticks(
        self, joystick, r1_button, analog_stick_1, analog_stick_2, skip, index
    ):
        if (
            self.state.current_time - self.last_animated_analog_stick
            > self.analog_stick_animation_delay
        ):
            self.current_analog_stick_frame = (
                self.current_analog_stick_frame + 1
            ) % len(self.tutorail_analog_stick)
            self.last_animated_analog_stick = self.state.current_time

        buttons = [
            self.buttons["joystick"],
            self.buttons["r1_button"],
            self.tutorail_analog_stick[self.current_analog_stick_frame],
            self.tutorail_analog_stick[self.current_analog_stick_frame - 2],
        ]
        positions = [joystick, r1_button, analog_stick_1, analog_stick_2]

        for button, pos in zip(buttons, positions):
            blit_position = (
                self.state.window_width - pos[0],
                self.state.window_height - pos[1],
            )
            self.state.screen.blit(button, blit_position)

        last_button, last_pos = self.buttons["o_button"], skip
        blit_position = (
            self.state.window_width - last_pos[0],
            self.state.window_height - last_pos[1],
        )
        pos = last_pos

        if index == 0 and not self.player_one_skiping:
            self.state.screen.blit(last_button, blit_position)
            self.state.screen.blit(
                self.text_surface,
                (
                    (self.state.window_width - 520) + (170 // 6),
                    (self.state.window_height - pos[1]) + 26 / 6,
                ),
            )
        elif index == 1 and not self.player_two_skiping:
            self.state.screen.blit(last_button, blit_position)
            self.state.screen.blit(
                self.text_surface,
                (
                    (self.state.window_width - 100)
                    - self.text_surface.get_rect().width,
                    (self.state.window_height - pos[1]) + 26 / 6,
                ),
            )

    def draw_keyboard(self, w, a, s, d, g, h, space, skip, index):
        button_sets = {
            0: [
                (self.buttons["w_button"], w),
                (self.buttons["a_button"], a),
                (self.buttons["s_button"], s),
                (self.buttons["d_button"], d),
                (self.buttons["g_button"], g),
                (self.buttons["h_button"], h),
                (self.buttons["space_button"], space),
                (self.buttons["t_button"], skip),
            ],
            1: [
                (self.buttons["up_arrow_button"], w),
                (self.buttons["left_arrow_button"], a),
                (self.buttons["down_arrow_button"], s),
                (self.buttons["right_arrow_button"], d),
                (self.buttons["button_1"], g),
                (self.buttons["button_2"], h),
                (self.buttons["ctrl_button"], space),
                (self.buttons["3_button"], skip),
            ],
        }

        buttons_to_draw = button_sets.get(index, [])

        for button, pos in buttons_to_draw[:-1]:
            blit_position = (
                self.state.window_width - pos[0],
                self.state.window_height - pos[1],
            )
            self.state.screen.blit(button, blit_position)

        last_button, last_pos = buttons_to_draw[-1]
        blit_position = (
            self.state.window_width - last_pos[0],
            self.state.window_height - last_pos[1],
        )
        pos = last_pos

        if index == 0 and not self.player_one_skiping:
            self.state.screen.blit(last_button, blit_position)
            self.state.screen.blit(
                self.text_surface,
                (
                    (self.state.window_width - 520) + (170 // 6),
                    (self.state.window_height - pos[1]) + 26 / 6,
                ),
            )
        elif index == 1 and not self.player_two_skiping:
            self.state.screen.blit(last_button, blit_position)
            self.state.screen.blit(
                self.text_surface,
                (
                    (self.state.window_width - 100)
                    - self.text_surface.get_rect().width,
                    (self.state.window_height - pos[1]) + 26 / 6,
                ),
            )

    def render_ui(self):
        if self.is_tutorial:
            if Input.is_joystick_connected(0):
                self.draw_joysticks(
                    (550, 90),
                    (460, 110),
                    (485, 55),
                    (518, 55),
                    (530, self.state.window_height),
                    0,
                )
            else:
                self.draw_keyboard(
                    (520, 90),
                    (550, 60),
                    (520, 60),
                    (490, 60),
                    (450, 90),
                    (420, 90),
                    (450, 65),
                    (530, self.state.window_height),
                    0,
                )
            if Input.is_joystick_connected(1):
                self.draw_joysticks(
                    (150, 90),
                    (60, 110),
                    (85, 55),
                    (118, 55),
                    (90, self.state.window_height),
                    1,
                )
            else:
                self.draw_keyboard(
                    (170, 90),
                    (200, 60),
                    (170, 60),
                    (140, 60),
                    (100, 90),
                    (70, 90),
                    (100, 65),
                    (90, self.state.window_height),
                    1,
                )

    def handle_tutorial(self):
        if not self.is_tutorial:
            return

        if Input.is_joystick_connected(0):
            self.player_one_skiping = Input.is_joystick_button_hold(
                0, JOYSTICK_PLAYER_CONTROLS[5]
            )
        else:
            self.player_one_skiping = Input.is_key_hold(KEYBOARD_PLAYER_ONE_CONTROLS[7])

        if Input.is_joystick_connected(1):
            self.player_two_skiping = Input.is_joystick_button_hold(
                1, JOYSTICK_PLAYER_CONTROLS[5]
            )
        else:
            self.player_two_skiping = Input.is_key_hold(KEYBOARD_PLAYER_TWO_CONTROLS[7])

        if self.player_one_skiping and self.player_two_skiping:
            Scene.load_async(
                GameScene,
                self.state.screen,
                self.state.surface,
                self.state.window_width,
                self.state.window_height,
                False,
            )
            pass
        pass

    def update(self, screen) -> None:
        # Update time
        self.state.current_time = pygame.time.get_ticks()
        self.state.delta_time = (
            self.state.current_time - self.state.previous_time
        ) / 1000.0
        self.state.previous_time = self.state.current_time

        if not Scene.loading:
            Executor.update()

            # Update input
            self.handle_input()

            self.handle_tutorial()

            self.handle_movement(self.state.player_one, KEYBOARD_PLAYER_ONE_CONTROLS, 0)
            self.handle_movement(self.state.player_two, KEYBOARD_PLAYER_TWO_CONTROLS, 1)

        self.state.surface.fill((0, 0, 0, 0))

        self.render_background(self.state.screen)
        if not Scene.loading:
            self.state.player_one.check_other_player_edges(self.state.player_two)
            if self.state.enemy is not None:
                self.state.enemy.check_other_player_edges(self.state.player_one)
                self.state.enemy.check_other_player_edges(self.state.player_two)

            self.state.player_one.update(self.state)
        self.state.player_one.render(self.state)
        if not Scene.loading:
            self.state.player_two.update(self.state)
        self.state.player_two.render(self.state)
        if not Scene.loading:
            if self.state.enemy is not None:
                self.state.enemy.update(self.state)
                if self.state.enemy.active:
                    self.state.enemy.check_edges(
                        self.state.window_width, self.state.window_height
                    )
                self.state.enemy.render(self.state)
                if (
                    self.state.enemy.health <= 0
                    and not self.state.enemy.animate_explosion
                ):
                    self_center = pygame.Vector2(
                        self.state.enemy.position[0] + self.state.enemy.size[0] / 2,
                        self.state.enemy.position[1] + self.state.enemy.size[1] / 2,
                    )
                    BombItem.Instantiate(self_center)
                    self.state.enemy = None
                    Executor.wait(GameScene.ENEMY_SPAWN_TIME, self.spawn_enemy)
                    # Removing enemy

            # Tutorail UI
            self.render_ui()

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
            for bullet in Bullet.instances[:]:
                for rocket in Rocket.instances[:]:
                    if rocket.check_intersection(bullet.rect):
                        Bullet.instances.remove(bullet)
                        Rocket.instances.remove(rocket)
                        break

        self.state.screen.blit(self.state.surface, (0, 0))
        super().update(screen)
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
    winner, loser = None, None

    def __init__(
        self, screen, surface, screen_width, screen_height, is_tutorial
    ) -> None:
        super().__init__(screen_width, screen_height)
        self.surface = surface
        self.screen = screen

        sounds_data = {
            "Button hover": "assets/music/hover.mp3",
            "Button click": "assets/music/click.mp3",
        }

        SoundSystem.load_all_sounds(sounds_data)

        SoundSystem.load_background_music("assets/music/main_backgorund.mp3")
        SoundSystem.play_background_music()

        # Load background images
        self.background_images = [
            pygame.transform.scale(
                pygame.image.load(f"assets/images/scenes/blue_player_win_screen.png"),
                (576, 324),
            ),  # Player 1
            pygame.transform.scale(
                pygame.image.load(f"assets/images/scenes/green_player_win_screen.png"),
                (576, 324),
            ),  # Player 2
        ]

        self.names = {
            "acepilot": "assets/images/names/acepilot.png",
            "airwolf": "assets/images/names/airwolf.png",
            "blaze": "assets/images/names/blaze.png",
            "blueleader": "assets/images/names/blueleader.png",
            "eagleeye": "assets/images/names/eagleeye.png",
            "falcon": "assets/images/names/falcon.png",
            "ironeagle": "assets/images/names/ironeagle.png",
            "jetstream": "assets/images/names/jetstream.png",
            "maverick": "assets/images/names/maverick.png",
            "nighthawk": "assets/images/names/nighthawk.png",
            "redbaron": "assets/images/names/redbaron.png",
            "shadowwing": "assets/images/names/shadowwing.png",
            "skyhunter": "assets/images/names/skyhunter.png",
            "skyrider": "assets/images/names/skyrider.png",
            "skyviper": "assets/images/names/skyviper.png",
            "stormchaser": "assets/images/names/stormchaser.png",
            "stormrider": "assets/images/names/stormrider.png",
            "thunderbolt": "assets/images/names/thunderbolt.png",
            "viper": "assets/images/names/viper.png",
            "wingman": "assets/images/names/wingman.png",
        }

        self.names_images = [
            pygame.transform.scale(pygame.image.load(path), (576, 324))
            for name, path in self.names.items()
        ]

        self.index = 0
        for i, name in enumerate(self.names.keys()):
            if name == ResultScene.winner[0].lower():
                self.index = i

        self.selected_index = -1

        self.buttons = []
        self.buttons.append(
            Button(
                screen_width / 2,
                screen_height - 50,
                120,
                40,
                text="Again",
                font_size=36,
            )
        )
        self.buttons.append(
            Button(
                screen_width / 2 + 140,
                screen_height - 50,
                120,
                40,
                text="Give Up",
                font_size=36,
            )
        )

    def update(self, screen) -> None:

        self.surface.fill((0, 0, 0, 0))

        if Input.is_joystick_connected(0):
            if Input.is_joystick_button_pressed(0, 13):  # LEFT
                self.selected_index = max(self.selected_index - 1, 0)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_joystick_button_pressed(0, 14):  # RIGHT
                self.selected_index = min(self.selected_index + 1, 1)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_joystick_button_pressed(0, 1):  # ACCEPT
                if self.selected_index == 0:
                    SoundSystem.play_sound("Button click")
                    Scene.load_async(
                        GameScene,
                        self.screen,
                        self.surface,
                        self.screen_width,
                        self.screen_height,
                        True,
                    )
                elif self.selected_index == 1:
                    SoundSystem.play_sound("Button click")
                    ResultScene.winner = None
                    Scene.load_async(
                        MenuScene,
                        self.screen,
                        self.surface,
                        self.screen_width,
                        self.screen_height,
                        False,
                    )
                pass
            pass
        if Input.is_joystick_connected(1):
            if Input.is_joystick_button_pressed(1, 13):  # LEFT
                self.selected_index = max(self.selected_index - 1, 0)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_joystick_button_pressed(1, 14):  # RIGHT
                self.selected_index = min(self.selected_index + 1, 1)
                for i in range(len(self.buttons)):
                    self.buttons[i].is_hovered = i == self.selected_index
            if Input.is_joystick_button_pressed(1, 1):  # ACCEPT
                if self.selected_index == 0:
                    SoundSystem.play_sound("Button click")
                    Scene.load_async(
                        GameScene,
                        self.screen,
                        self.surface,
                        self.screen_width,
                        self.screen_height,
                        True,
                    )
                elif self.selected_index == 1:
                    SoundSystem.play_sound("Button click")
                    ResultScene.winner = None
                    Scene.load_async(
                        MenuScene,
                        self.screen,
                        self.surface,
                        self.screen_width,
                        self.screen_height,
                        False,
                    )
                pass
            pass

        if Input.is_key_pressed(pygame.K_LEFT) or Input.is_key_pressed(
            pygame.K_w
        ):  # UP
            self.selected_index = max(self.selected_index - 1, 0)
            for i in range(len(self.buttons)):
                self.buttons[i].is_hovered = i == self.selected_index
        if Input.is_key_pressed(pygame.K_RIGHT) or Input.is_key_pressed(
            pygame.K_s
        ):  # DOWN
            self.selected_index = min(self.selected_index + 1, 1)
            for i in range(len(self.buttons)):
                self.buttons[i].is_hovered = i == self.selected_index
        if Input.is_key_pressed(pygame.K_SPACE) or Input.is_key_pressed(
            pygame.K_RETURN
        ):
            if self.selected_index == 0:
                SoundSystem.play_sound("Button click")
                Scene.load_async(
                    GameScene,
                    self.screen,
                    self.surface,
                    self.screen_width,
                    self.screen_height,
                    True,
                )
            elif self.selected_index == 1:
                SoundSystem.play_sound("Button click")
                ResultScene.winner = None
                Scene.load_async(
                    MenuScene,
                    self.screen,
                    self.surface,
                    self.screen_width,
                    self.screen_height,
                    False,
                )
            pass
        pass

        self.render_background(self.screen)

        for button in self.buttons:
            button.draw(self.screen)

        self.screen.blit(
            self.names_images[self.index],
            (0, 0),
        )

        self.screen.blit(self.surface, (0, 0))
        super().update(screen)
        pass

    def render_background(self, screen):
        if ResultScene.winner is None:
            return
        if ResultScene.winner[1]:
            screen.blit(self.background_images[0], (0, 0))
        else:
            screen.blit(self.background_images[1], (0, 0))

    pass
