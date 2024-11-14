from operator import index

import pygame
from pygame.locals import *
from utility import *
from scenes import *


def main():
    pygame.init()
    pygame.mixer.init()

    # Setup SoundSystem
    SoundSystem.Init()

    # Screen setup
    screen_width, screen_height = 576, 324
    screen = pygame.display.set_mode(
        (screen_width, screen_height), pygame.RESIZABLE | pygame.SCALED
    )
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pygame.display.set_caption("Break the Floor!")

    # Load Initial Scenes
    Scene.active_scene = GameScene(screen, surface, screen_width, screen_height)
    # current_scene = MenuScene()

    # Initialize joysticks
    Input.init()
    pygame.joystick.init()

    # Gameloop
    running = True

    while running:
        Input.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        Scene.active_scene.update()
        pygame.display.update()
        pass

    pygame.quit()
    pass


if __name__ == "__main__":
    main()
