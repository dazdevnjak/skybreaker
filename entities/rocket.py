import pygame
import math
import random


class Indicator:
    def __init__(self, position, image_path="assets/images/indicator.png", size = (10, 25)):
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.position = pygame.Vector2(position)

    def render(self, screen):
        rect = self.image.get_rect(center=self.position)
        screen.blit(self.image,rect)
        return rect


class Rocket:
    instances = []
    indicator_instances = []

    current_state_indicator = True
    state_timer = 2.0

    INDICATOR_DURATION = 2.0
    PROJECTILE_DURATION = 5.0

    ROCKET_DELETE_TIME = 5
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
        self.delete_time = 0.0

    def update(self, delta_time):
        self.position += self.velocity
        self.delete_time += delta_time

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect.topleft)
        return rotated_rect

    @staticmethod
    def InstantiateRandom(start_x, max_height, direction, delta_time):
        Rocket.state_timer -= delta_time

        if Rocket.current_state_indicator:
            if Rocket.state_timer <= 0:
                Rocket.current_state_indicator = False
                Rocket.state_timer = Rocket.PROJECTILE_DURATION

                Rocket.indicator_instances.clear()

                for position in Rocket.projectile_positions:
                    Rocket.Instantiate(position, direction)

        elif not Rocket.current_state_indicator:
            if Rocket.state_timer <= 0:
                Rocket.current_state_indicator = True
                Rocket.state_timer = Rocket.INDICATOR_DURATION

                Rocket.projectile_positions.clear()
                Rocket.indicator_instances.clear()

                for _ in range(random.randint(1, Rocket.ROCKET_ROW_COUNT)):
                    height = max_height * random.random()
                    for col in range(random.randint(1, Rocket.ROCKET_COL_COUNT)):
                        position_x = start_x + col * Rocket.ROCKET_COL_SPACING
                        Rocket.projectile_positions.append((position_x, height))

                for pos in Rocket.projectile_positions:
                    Rocket.InstantiateIndicator((pos[0] - 50, pos[1]))

        if Rocket.current_state_indicator == True and Rocket.state_timer == Rocket.INDICATOR_DURATION:
            Rocket.projectile_positions.clear()
            Rocket.indicator_instances.clear()

            for _ in range(random.randint(1, Rocket.ROCKET_ROW_COUNT)):
                height = max_height * random.random()
                for col in range(random.randint(1, Rocket.ROCKET_COL_COUNT)):
                    position_x = start_x + col * Rocket.ROCKET_COL_SPACING
                    Rocket.projectile_positions.append((position_x, height))

            for pos in Rocket.projectile_positions:
                Rocket.InstantiateIndicator((pos[0] - 50, pos[1]))


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
    def Update_all(delta_time, player_one, player_two, screen):
        for rocket in Rocket.instances[:]:
            rocket.update(delta_time)

            if rocket.delete_time >= Rocket.ROCKET_DELETE_TIME:
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
