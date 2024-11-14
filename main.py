from operator import index

import pygame
from pygame.locals import *
from utility import *

from entities.player import Player, Enemy
from entities.bullet import Bullet
from entities.rocket import Rocket
from entities.collectable import Collectable, RocketItem
from scenes import *


def main():
    current_scene: Scene = None

    pygame.init()

    # Screen setup
    screen_width, screen_height = 576, 324
    screen = pygame.display.set_mode(
        (screen_width, screen_height), pygame.RESIZABLE | pygame.SCALED
    )
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pygame.display.set_caption("Break the Floor!")

    # Load Initial Scenes
    # current_scene = MenuScene()
    current_scene = GameScene(screen, surface, screen_width, screen_height)
    # current_scene = ResultScene()

    # Initialize joysticks
    Input.init()
    pygame.joystick.init()

    # Gameloop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_scene.update()
        pygame.display.update()
        pass

    pygame.quit()
    pass


if __name__ == "__main__":
    main()
