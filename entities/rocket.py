import pygame
import math
import random
from utility import Executor


class Indicator:
    def __init__(
        self, position, image_path="assets/images/indicator.png", size=(10, 25)
    ):
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.position = pygame.Vector2(position)

    def render(self, screen):
        rect = self.image.get_rect(center=self.position)
        screen.blit(self.image, rect)
        return rect


class Rocket:
    instances = []
    indicator_instances = []

    INDICATOR_DURATION = 2000  # 2000ms = 2s
    PROJECTILE_DURATION = 5000  # 5000ms = 5s

    ROCKET_ROW_COUNT = 2
    ROCKET_COL_COUNT = 3
    ROCKET_COL_SPACING = 80
    IMAGE_PATH = "assets/images/projectail.png"

    projectile_positions = []

    def __init__(
        self,
        rocket_image,
        start_position,
        target_direction=(-1, 0),
        size=(30, 15),
        speed=2,
    ):
        self.image = pygame.transform.scale(pygame.image.load(rocket_image), size)
        self.position = pygame.Vector2(start_position)
        self.target_direction = pygame.Vector2(target_direction)
        self.velocity = self.target_direction * speed

        self.angle = math.degrees(
            math.atan2(self.target_direction.y, self.target_direction.x)
        )

    def update(self):
        self.position += self.velocity
        pass

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect.topleft)
        return rotated_rect

    def out_of_bounds(self) -> bool:
        return self.position.x < 0

    @staticmethod
    def InstantiateIndicator(start_position):
        indicator = Indicator(start_position)
        Rocket.indicator_instances.append(indicator)

    @staticmethod
    def Instantiate(start_position, target_direction):
        Rocket.instances.append(
            Rocket(Rocket.IMAGE_PATH, start_position, target_direction)
        )

    @staticmethod
    def LaunchRockets(max_height, start_x):
        Rocket.projectile_positions.clear()
        Rocket.indicator_instances.clear()

        for _ in range(random.randint(1, Rocket.ROCKET_ROW_COUNT)):
            height = max_height * random.random()
            for col in range(random.randint(1, Rocket.ROCKET_COL_COUNT)):
                position_x = start_x + col * Rocket.ROCKET_COL_SPACING
                Rocket.projectile_positions.append((position_x, height))

        for i in range(len(Rocket.projectile_positions)):
            Rocket.InstantiateIndicator(
                (
                    Rocket.projectile_positions[i][0] - 50,
                    Rocket.projectile_positions[i][1],
                )
            )
            Executor.wait(
                Rocket.INDICATOR_DURATION,
                lambda: Rocket.Instantiate(Rocket.projectile_positions[i], (-1, 0)),
            )

        def spawn_all_rockets():
            Rocket.indicator_instances.clear()
            for pos in Rocket.projectile_positions:
                Rocket.Instantiate(pos, (-1, 0))
            Rocket.projectile_positions.clear()

        Executor.wait(Rocket.INDICATOR_DURATION, spawn_all_rockets)
        pass

    @staticmethod
    def Update_all(player_one, player_two, screen):
        for rocket in Rocket.instances[:]:
            rocket.update()

            if rocket.out_of_bounds():
                Rocket.instances.remove(rocket)
                continue

            rocket_rect = rocket.render(screen)

            if Rocket.Check_collision(rocket, rocket_rect, player_one, player_two):
                Rocket.instances.remove(rocket)

        for indicator in Rocket.indicator_instances[:]:
            indicator.render(screen)

    @staticmethod
    def Check_collision(rocket, rocket_rect, player_one, player_two):
        if player_one.check_intersection(rocket_rect):
            print(f"Player one hit by rocket!")
            player_one.take_damage(10)
            return True

        if player_two.check_intersection(rocket_rect):
            print(f"Player two hit by rocket!")
            player_two.take_damage(10)
            return True

        return False
