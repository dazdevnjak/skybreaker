import pygame
from pygame.locals import *
from utility import *

from entities.player import Player, Enemy
from entities.bullet import Bullet,Bomb
from entities.rocket import Rocket
from entities.collectable import Collectable


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
    ENEMY_SPAWN_TIME = 2000 #15000  # 15000ms / 15s
    ROCKETS_START_TIME = 5000  # 5000ms / 5s

    def __init__(self, screen, surface, window_width, window_height) -> None:
        super().__init__()
        self.state: GameState = GameState(screen, surface)
        self.state.window_width = window_width
        self.state.window_height = window_height

        # Load background images
        self.background_images = [
            pygame.image.load(f"assets/images/background/background_{i}.png")
            for i in range(1, 5)
        ]

        # Load players
        self.state.player_one = Player(
            [f"assets/images/player_one/player_{i}.png" for i in range(1, 9)],
            (220, 212),
        )
        self.state.player_two = Player(
            [f"assets/images/player_two/player_{i}.png" for i in range(1, 9)], (220, 50)
        )
        Executor.wait(GameScene.ENEMY_SPAWN_TIME, self.spawn_enemy)
        Executor.wait(GameScene.ROCKETS_START_TIME, self.spawn_rockets)

        # Parallax settings
        self.parallax_speeds = [0.2, 0.3, 0.4, 0.5]
        self.x_positions = [0, 0, 0, 0]

        Executor.init()
        pass

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
        self.state.player_one.render(self.state.surface)
        self.state.player_two.update(self.state)
        self.state.player_two.render(self.state.surface)
        if self.state.enemy is not None:
            self.state.enemy.update(self.state)
            if self.state.enemy.active:
                self.state.enemy.check_edges(
                    self.state.window_width, self.state.window_height
                )
            self.state.enemy.render(self.state.surface)
            if self.state.enemy.health <= 0:
                self.state.enemy = None  # Removing enemy

        self.state.player_one.update_ui()
        self.state.player_two.update_ui()

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
            self.state.delta_time
        )
        Collectable.Update_all(
            self.state.delta_time,
            self.state.player_one,
            self.state.player_two,
            self.state.surface,
        )

        if(Bomb._instance):
            Bomb._instance.update()
            Bomb._instance.render(self.state.screen)
            if(Bomb._instance.position.y > self.state.window_height):
                Bomb._instance = None

        self.state.screen.blit(self.state.surface, (0, 0))

        pass

    def handle_input(self):
        state = self.state

        if not Input.is_joystick_connected(0):
            if Input.is_key_pressed(KEYBOARD_PLAYER_ONE_CONTROLS[6]):
                if state.player_one.can_fire_bomb():
                    self.fire_bomb(state.player_one,0)
                elif state.player_one.can_fire():
                    self.fire_bullet(state.player_one, 0)
        else:
            if Input.is_joystick_button_pressed(
                0, JOYSTICK_PLAYER_CONTROLS[4][0]
            ) or Input.is_joystick_button_pressed(0, JOYSTICK_PLAYER_CONTROLS[4][1]):
                if state.player_one.can_fire_bomb():
                    self.fire_bomb(state.player_one,0)
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
                    self.fire_bomb(state.player_two,1)
                elif state.player_two.can_fire():
                    self.fire_bullet(state.player_two, 1)

        pass

    def fire_bullet(self, player, index):
        start_position = pygame.Vector2(
            player.position[0] + player.size[0] / 2,
            player.position[1] + player.size[1] / 2,
        )
        target_position = player.get_indicator_position()
        Bullet.Instantiate(start_position, target_position, index)
        player.fire_cooldown = Bullet.BULLET_FIRE_COOLDOWN

        pass

    def fire_bomb(self,player,index):
        start_position = pygame.Vector2(
            player.position[0] + player.size[0] / 2,
            player.position[1] + player.size[1] / 2,
        )
        target_position = player.get_indicator_position()
        Bomb.Instantiate(start_position, target_position, index)
        player.fire_cooldown = Bullet.BULLET_FIRE_COOLDOWN
        player.throw_bomb()

    # Players input
    def handle_movement(self, player, controls, joystick_index):
        move_velocity, aim_velocity = get_velocity(controls, joystick_index)
        player.move(move_velocity[0], move_velocity[1])

        if aim_velocity != 0:
            if Input.is_joystick_connected(joystick_index):
                player.set_indicator_angle(aim_velocity, 2)
            else:
                player.adjust_indicator_angle(aim_velocity)

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
        self.state.enemy = Enemy(
            [f"assets/images/enemy/enemy_{i}.png" for i in range(1, 9)],
            (-50, 100),
        )
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
