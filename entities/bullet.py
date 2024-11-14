import pygame
import math


class Bullet:
    instances = []
    BULLET_DELETE_TIME = 1.5
    BULLET_FIRE_COOLDOWN = 0.5

    def __init__(
        self,
        image_path,
        start_position,
        target_position,
        spawned_by,
        size=(10, 10),
        speed=4,
    ):
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.position = pygame.Vector2(start_position)
        self.target_position = pygame.Vector2(target_position)
        self.spawned_by = spawned_by

        direction = (self.target_position - self.position).normalize()
        self.velocity = direction * speed

        self.angle = math.degrees(math.atan2(direction.y, direction.x))
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
    def Instantiate(start_position, target_position, index):
        image_path = (
            "assets/images/bullet_one.png"
            if index == 0
            else "assets/images/bullet_two.png"
        )
        Bullet.instances.append(
            Bullet(image_path, start_position, target_position, index)
        )

    @staticmethod
    def Update_all(delta_time, player_one, player_two,enemy, screen):
        for bullet in Bullet.instances[:]:
            bullet.update(delta_time)

            if bullet.delete_time >= Bullet.BULLET_DELETE_TIME:
                Bullet.instances.remove(bullet)
                continue

            bullet_rect = bullet.render(screen)
            if Bullet.Check_collision(bullet, bullet_rect, player_one, player_two,enemy):
                Bullet.instances.remove(bullet)

    @staticmethod
    def Check_collision(bullet, bullet_rect, player_one, player_two,enemy):
        if bullet.spawned_by == 2:
            if player_one.check_intersection(bullet_rect):
                print(f"Player {bullet.spawned_by + 1} hit!")
                player_one.take_damage(10)
                return True
            if player_two.check_intersection(bullet_rect):
                print(f"Player {bullet.spawned_by + 1} hit!")
                player_two.take_damage(10)
                return True
            return False

        target_player = player_one if bullet.spawned_by == 1 else player_two
        if target_player.check_intersection(bullet_rect):
            print(f"Player {bullet.spawned_by + 1} hit!")
            target_player.take_damage(20)
            return True
        if enemy.check_intersection(bullet_rect):
            print(f"Player {bullet.spawned_by + 1} hit enemy!")
            enemy.take_damage(20)
            return True
        return False
