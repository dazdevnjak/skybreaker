import pygame
import math
from utility import Executor


class Bullet:
    instances = []
    BULLET_DELETE_TIME = 1500  # 1500ms = 1.5s
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
        self.rect = None

    def update(self):
        self.position += self.velocity

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
        bullet = Bullet(image_path, start_position, target_position, index)
        Bullet.instances.append(bullet)
        Executor.wait(
            Bullet.BULLET_DELETE_TIME,
            lambda: (
                Bullet.instances.remove(bullet) if bullet in Bullet.instances else None
            ),
        )

    @staticmethod
    def Update_all(player_one, player_two, enemy, screen):
        for bullet in Bullet.instances:
            bullet.update()

            bullet_rect = bullet.render(screen)
            bullet.rect = bullet_rect

            if Bullet.Check_collision(
                bullet, bullet_rect, player_one, player_two, enemy
            ):
                Bullet.instances.remove(bullet)

    @staticmethod
    def Check_collision(bullet, bullet_rect, player_one, player_two, enemy):
        if bullet.spawned_by == 2:
            if player_one.check_intersection(bullet_rect):
                player_one.take_damage(10)
                return True
            if player_two.check_intersection(bullet_rect):
                player_two.take_damage(10)
                return True
            return False

        target_player = player_one if bullet.spawned_by == 1 else player_two
        if target_player.check_intersection(bullet_rect):
            target_player.take_damage(10)
            return True
        if enemy is not None and enemy.check_intersection(bullet_rect):
            enemy.take_damage(10)
            return True
        return False


class Bomb:
    _instance = None
    BOMB_DELETE_TIME = 1500  # 1500ms = 1.5s
    GRAVITY_COEF = 0.05

    def __init__(
        self,
        image_path,
        start_position,
        target_position,
        spawned_by,
        size=(30, 15),
        speed=4,
    ):
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.start_position = pygame.Vector2(start_position)
        self.target_position = pygame.Vector2(target_position)
        self.spawned_by = spawned_by
        self.position = pygame.Vector2(start_position)
        self.rect = None

        direction = (self.target_position - self.position).normalize()
        self.velocity = direction * speed
        self.angle = math.degrees(math.atan2(direction.y, direction.x))
        pass

    def update(self):
        self.velocity.y += Bomb.GRAVITY_COEF
        self.angle = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
        self.position += self.velocity

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect.topleft)
        return rotated_rect

    @staticmethod
    def Destroy_bomb():
        Bomb._instance = None

    @staticmethod
    def Instantiate(start_position, target_position, index):
        image_path = "assets/images/bomb.png"
        bomb = Bomb(image_path, start_position, target_position, index)
        Bomb._instance = bomb

    @staticmethod
    def Update(screen, window_height, player_one, player_two):
        if Bomb._instance is None:
            return
        Bomb._instance.update()
        rect = Bomb._instance.render(screen)
        Bomb._instance.rect = rect
        if Bomb._instance.position.y > window_height:
            Bomb._instance = None
            return
        if Bomb.Check_collision(rect, player_one, player_two):
            Bomb._instance = None
            return

    @staticmethod
    def Check_collision(bomb_rect, player_one, player_two):
        target_player = player_one if Bomb._instance.spawned_by == 1 else player_two
        if target_player.check_intersection(bomb_rect):
            target_player.take_damage(30)
            return True
        if target_player.check_intersection(bomb_rect):
            target_player.take_damage(30)
            return True
        return False
