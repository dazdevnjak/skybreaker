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
        (screen_width, screen_height),
        pygame.RESIZABLE | pygame.SCALED | pygame.FULLSCREEN,
    )
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pygame.display.set_caption("Break the Floor!")

    pygame.mouse.set_visible(False)

    # Load Initial Scenes
    Scene.active_scene = MenuScene(screen, surface, screen_width, screen_height, False)

    # Initialize joysticks
    Input.init()
    pygame.joystick.init()

    # Gameloop
    Scene.running = True

    while Scene.running:
        Input.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Scene.running = False
            if event.type == pygame.JOYBUTTONDOWN:  # TODO : For testing, remove later
                print(f"Button {event.button} pressed on joystick.")

        Scene.active_scene.update(screen)
        pygame.display.update()
        pass

    pygame.mouse.set_visible(True)
    pygame.quit()
    pass


if __name__ == "__main__":
    main()
