import pygame
import math
from utility import *
from entities.bullet import Bullet
from entities.collectable import BombItem
from entities.components import *
import random


class Player(ControllableObject):
    fire_cooldown = 0.0

    INVISIBLE_TIME_MS = 1000
    VULNERABLE_TIME_MS = 3000

    def __init__(self, image_paths, position, size=(128, 72), animation_delay=100):
        super().__init__(position, size)

        self.frames = [
            pygame.transform.scale(pygame.image.load(path), size).convert_alpha()
            for path in image_paths
        ]
        self.animation_delay = animation_delay
        self.current_frame = random.randrange(0, len(self.frames))
        self.last_update = pygame.time.get_ticks()
        self.lives = 3
        self.previous_health = 100
        self.bomb_count = 0

        self.explosion_frames = [
            pygame.transform.scale(
                pygame.image.load(f"assets/images/explosion/explosion_{i}.png"), size
            ).convert_alpha()
            for i in range(1, 7)
        ]
        self.current_explosion_frame = random.randrange(0, len(self.explosion_frames))
        self.animate_explosion = False
        self.last_animatet_explosion = 0

        self.is_invincible = False
        self.is_vulnerable = False
        self.invincible_start_time = 0
        self.blink_interval = 35
        self.last_blink_time = 0

    def add_bomb(self):
        self.bomb_count += 1

    def throw_bomb(self):
        self.bomb_count = max(self.bomb_count - 1, 0)

    def take_damage(self, damage):
        if not self.is_invincible:
            self.previous_health = self.health
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.on_death()
            else:
                self.is_invincible = True
                self.invincible_start_time = pygame.time.get_ticks()
            self.get_component(HealthBarUI).damage()
            self.damage_animation_start_time = pygame.time.get_ticks()

    def update(self, state) -> None:
        current_time = state.current_time

        self.fire_cooldown -= state.delta_time

        if self.is_invincible:
            if (current_time - self.invincible_start_time) >= (
                self.VULNERABLE_TIME_MS
                if self.is_vulnerable
                else self.INVISIBLE_TIME_MS
            ):
                self.is_invincible = False
                self.is_vulnerable = False
                for frame in self.frames:
                    frame.set_alpha(255)
            else:
                alpha_value = 128 + int(
                    127
                    * (abs(math.sin((current_time - self.invincible_start_time) / 100)))
                )
                for frame in self.frames:
                    frame.set_alpha(alpha_value)

        if current_time - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
        if self.animate_explosion:
            if current_time - self.last_animatet_explosion > self.animation_delay:
                self.current_explosion_frame = self.current_explosion_frame + 1
                if self.current_explosion_frame == len(self.explosion_frames):
                    self.animate_explosion = False
                    self.current_explosion_frame = 0
                    self.last_animatet_explosion = 0
                else:
                    self.last_animatet_explosion = current_time

        super().update(state)

    def render(self, state):
        screen = state.surface

        super().render(state)
        screen.blit(self.frames[self.current_frame], self.position)

        if self.animate_explosion:
            screen.blit(
                self.explosion_frames[self.current_explosion_frame], self.position
            )

    def can_fire(self) -> bool:
        return self.fire_cooldown <= 0

    def can_fire_bomb(self) -> bool:
        return self.can_fire() and self.bomb_count > 0

    def on_death(self) -> None:
        self.animate_explosion = True
        self.lives -= 1
        if self.lives > 0:
            self.reset()
        else:
            # TODO : Game should end here
            print("End game!")
            pass
        pass

    def reset(self) -> None:
        self.health = 100
        self.is_invincible = True
        self.is_vulnerable = True
        self.invincible_start_time = pygame.time.get_ticks()
        self.damage_animation_start_time = pygame.time.get_ticks()
        pass


class Enemy(ControllableObject):
    fire_cooldown = 0.0
    POSITION_SEARCH_INTERVAL: float = 200  # 200ms = 0.2s
    FIRE_RATE = 3
    current_target = None

    def __init__(self, image_paths, _position, _size=(128, 72), animation_delay=100):
        ControllableObject.__init__(self, _position, _size)
        self.frames = [
            pygame.transform.scale(pygame.image.load(path), _size).convert_alpha()
            for path in image_paths
        ]
        self.speed /= 2
        self.max_speed /= 2

        self.animation_delay = animation_delay
        self.current_frame = random.randrange(0, len(self.frames))
        self.last_update = pygame.time.get_ticks()
        self.previous_health = 100
        self.start_damage_animation = False
        self.damage_animation_start_time = 0

        self.blink_interval = 35
        self.last_blink_time = 0
        self.damage_animation_start_time = None
        self.damage_animation_duration = 500

        self.state = None
        self.target = None
        self.further = None

        self.active = False
        self.velocity[0] = 5
        self.speed = self.max_speed / 6
        Executor.wait(500, self.activate, self.in_screen)

    def take_damage(self, damage):
        self.previous_health = self.health
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.on_death()

        self.get_component(HealthBarUI).damage()
        self.damage_animation_start_time = pygame.time.get_ticks()
        self.start_damage_animation = True

    def in_screen(self) -> bool:
        return self.position[0] >= 120

    def activate(self):
        self.active = True
        self.velocity[0] = 0
        self.speed = self.max_speed

    def animate_enemy_taking_damage(self, state):
        current_time = state.current_time

        if (current_time - self.damage_animation_start_time) >= 1000:
            for frame in self.frames:
                frame.set_alpha(255)
            self.start_damage_animation = False
        else:
            alpha_value = 128 + int(
                127
                * (
                    abs(
                        math.sin(
                            (current_time - self.damage_animation_start_time) / 100
                        )
                    )
                )
            )
            for frame in self.frames:
                frame.set_alpha(alpha_value)

    def render(self, state):
        screen = state.surface
        super().render(state)
        screen.blit(self.frames[self.current_frame], self.position)

    def lambda_search(self):
        distances = self.closest_player_position(self.state)
        self.current_target = self.target = distances[0]
        self.further = distances[1]
        pass

    def update(self, state):
        self.state = state
        self.fire_cooldown -= state.delta_time

        if self.start_damage_animation:
            self.animate_enemy_taking_damage(state)

        if state.current_time - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = state.current_time

        if self.active == True:
            target = self.target
            further = self.further
            Executor.wait(Enemy.POSITION_SEARCH_INTERVAL, self.lambda_search)

            self_center = pygame.Vector2(
                self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2
            )

            dx = 0
            dy = 0

            if self.current_target is not None:
                dx = self.current_target.x - self_center.x
                dy = self.current_target.y - self_center.y

                angle_radii = math.atan2(dy, dx)
                self.get_component(AimIndicator).indicator_angle = math.degrees(angle_radii)

            if target is not None:
                gp1, gp2 = self.find_optimal_position(target, 100, further, 100, 150)
                if gp1 is not None:
                    good_position = self.find_better_area(
                        gp1, gp2, state.window_width, state.window_height
                    )

                    dx = good_position[0] - self_center.x
                    dy = good_position[1] - self_center.y

                    self.move(dx, dy)
                else:
                    self.velocity = [0, 0]

        super().update(state)

        if self.active and self.can_fire():
            start_position = pygame.Vector2(
                self.position[0] + self.size[0] / 2,
                self.position[1] + self.size[1] / 2,
            )
            target_position = self.get_component(AimIndicator).get_indicator_position()

            Bullet.Instantiate(start_position, target_position, 2)
            self.fire_cooldown = Enemy.FIRE_RATE
            pass

    def closest_player_position(self, state) -> pygame.Vector2:
        self_center = pygame.Vector2(
            self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2
        )
        player_one_center = pygame.Vector2(
            state.player_one.position[0] + state.player_one.size[0] / 2,
            state.player_one.position[1] + state.player_one.size[1] / 2,
        )
        player_one_distance = self_center.distance_to(player_one_center)
        player_two_center = pygame.Vector2(
            state.player_two.position[0] + state.player_two.size[0] / 2,
            state.player_two.position[1] + state.player_two.size[1] / 2,
        )
        player_two_distance = self_center.distance_to(player_two_center)

        # if abs(player_one_distance - player_two_distance) <= 5:
        #     return self_center,(
        #         pygame.Vector2(-(player_one_center.x - self_center.x),-(player_one_center.y - self_center.y)),
        #         pygame.Vector2(-(player_two_center.x - self_center.x),-(player_two_center.y - self_center.y))
        #         )

        return (
            (player_one_center, player_two_center)
            if player_one_distance < player_two_distance
            else (player_two_center, player_one_center)
        )  # Favorizujemo enemy da targetuje igraca 2 :))

    def find_optimal_position(self, player_one, radii_a, player_two, radii_b, radii_c):
        x1, x2 = player_one.x, player_two.x
        y1, y2 = player_one.y, player_two.y

        d_a = radii_a + radii_c
        d_b = radii_b + radii_c

        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if d >= d_a + d_b:
            """No solution: Circles cannot intersect at their outer boundaries."""
            return None
            # return (player_one.x,player_one.y)
        if d <= abs(d_a - d_b):
            """No solution: One circle would be entirely inside the other."""
            return None
            # return (player_one.x,player_one.y)

        a = (d_a**2 - d_b**2 + d**2) / (2 * d)
        h = math.sqrt(d_a**2 - a**2)

        p2_x = x1 + a * (x2 - x1) / d
        p2_y = y1 + a * (y2 - y1) / d

        x_int1 = p2_x + h * (y2 - y1) / d
        y_int1 = p2_y - h * (x2 - x1) / d

        x_int2 = p2_x - h * (y2 - y1) / d
        y_int2 = p2_y + h * (x2 - x1) / d

        c1 = (x_int1, y_int1)
        c2 = (x_int2, y_int2)
        return c1, c2

    def clamp_area(self, area, min_x, max_x, min_y, max_y):
        return (
            (min_x if area[0] < min_x else (max_x if area[0] > max_x else area[0])),
            (min_y if area[1] < min_y else (max_y if area[1] > max_y else area[1])),
        )

    def find_better_area(self, area1, area2, screen_width, screen_height):
        better_area = area1

        area1 = self.clamp_area(area1, 0, screen_width, 0, screen_height)
        area2 = self.clamp_area(area2, 0, screen_width, 0, screen_height)

        # Find optimal X
        if area1[0] > area2[0]:
            min_x = area2[0]
            max_x = screen_width - area1[0]
            min_y = area2[1]
            max_y = screen_height - area1[1]

            if min_x > max_x and min_y > max_y:
                return area2
        elif area1[0] <= area2[0]:
            min_x = area1[0]
            max_x = screen_width - area2[0]
            min_y = area1[1]
            max_y = screen_height - area2[1]

            if min_x > max_x and min_y > max_y:
                return area1

        return better_area

    def can_fire(self) -> bool:
        return self.fire_cooldown <= 0

    def on_death(self) -> None:
        self_center = pygame.Vector2(
            self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2
        )
        BombItem.Instantiate(self_center)
        pass

    pass
