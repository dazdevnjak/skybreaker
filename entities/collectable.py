import pygame

from utility import SoundSystem

class Collectable:
    instances = []

    def __init__(self, image_path, position, size=(10, 10)) -> None:
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.position = pygame.Vector2(position)
        Collectable.instances.append(self)
        pass

    def render(self, screen):
        rect = self.image.get_rect(center=self.position)
        screen.blit(self.image, rect)
        return rect

    @staticmethod
    def Update_all(delta_time, player_one, player_two, screen):
        for collectable in Collectable.instances[:]:
            # collectable.update(delta_time)

            collectable_rect = collectable.render(screen)
            if Collectable.Check_collision(
                collectable, collectable_rect, player_one, player_two
            ):
                Collectable.instances.remove(collectable)

    @staticmethod
    def Check_collision(collectable, collectable_rect, player_one, player_two):
        if player_one.check_intersection(collectable_rect):
            player_one.add_bomb()
            SoundSystem.play_sound("Pick up")
            return True
        if player_two.check_intersection(collectable_rect):
            player_two.add_bomb()
            SoundSystem.play_sound("Pick up")
            return True
        return False


class BombItem(Collectable):
    def __init__(self, image_path, position, size=(30, 15)):
        super().__init__(image_path, position, size)

    @staticmethod
    def Instantiate(position):
        BombItem("assets/images/bomb.png", position)
        pass
