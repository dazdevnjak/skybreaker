from operator import index

import pygame
from pygame.locals import *
from utility import *

from entities.player import Player, Enemy
from entities.bullet import Bullet
from entities.rocket import Rocket
from entities.collectable import Collectable, RocketItem

# Players input
def handle_movement(player, controls, joystick_index):
    move_velocity, aim_velocity = get_velocity(controls, joystick_index)
    player.move(move_velocity[0], move_velocity[1])

    if aim_velocity != 0:
        if Input.is_joystick_connected(joystick_index):
            player.set_indicator_angle(aim_velocity, 2)
        else:
            player.adjust_indicator_angle(aim_velocity)

    player.check_edges(screen_width, screen_height)


pygame.init()

# Screen setup
screen_width, screen_height = 576, 324
screen = pygame.display.set_mode(
    (screen_width, screen_height), pygame.RESIZABLE | pygame.SCALED
)
surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
pygame.display.set_caption("Break the Floor!")

state: GameState = GameState(screen, surface)
state.window_width = screen_width
state.window_height = screen_height

# Load background images
background_images = [
    pygame.image.load(f"assets/images/background/background_{i}.png")
    for i in range(1, 5)
]

# Load players
state.player_one = Player(
    [f"assets/images/player_one/player_{i}.png" for i in range(1, 9)], (220, 212)
)
state.player_two = Player(
    [f"assets/images/player_two/player_{i}.png" for i in range(1, 9)], (220, 50)
)
state.enemy = Enemy(
    [f"assets/images/enemy/enemy_{i}.png" for i in range(1, 9)], (220, 100)
)

# Parallax settings
parallax_speeds = [0.2, 0.3, 0.4, 0.5]
x_positions = [0, 0, 0, 0]

# Initialize joysticks
Input.init()
pygame.joystick.init()


# Render background with parallax
def render_background(screen):
    for i, background_image in enumerate(background_images):
        speed = parallax_speeds[i]
        x_positions[i] -= speed
        if x_positions[i] <= -screen_width:
            x_positions[i] = 0
        screen.blit(background_image, (x_positions[i], 0))
        screen.blit(background_image, (x_positions[i] + screen_width, 0))


def fire_bullet(player, index):
    start_position = pygame.Vector2(
        player.position[0] + player.size[0] / 2,
        player.position[1] + player.size[1] / 2,
    )
    target_position = player.get_indicator_position()
    Bullet.Instantiate(start_position, target_position, index)
    player.fire_cooldown = Bullet.BULLET_FIRE_COOLDOWN


def handle_input():
    Input.update()

    global running
    global state

    if not Input.is_joystick_connected(0):
        if Input.is_key_pressed(KEYBOARD_PLAYER_ONE_CONTROLS[6]):
            if state.player_one.can_fire():
                fire_bullet(state.player_one, 0)
    else:
        if Input.is_joystick_button_pressed(0, JOYSTICK_PLAYER_CONTROLS[4][0]) or Input.is_joystick_button_pressed(0, JOYSTICK_PLAYER_CONTROLS[4][1]):
            if state.player_one.can_fire():
                fire_bullet(state.player_one, 0)

    if not Input.is_joystick_connected(1):
        if Input.is_key_pressed(KEYBOARD_PLAYER_TWO_CONTROLS[6]):
            if state.player_two.can_fire():
                fire_bullet(state.player_two, 1)
    else:
        if Input.is_joystick_button_pressed(1, JOYSTICK_PLAYER_CONTROLS[4][0]) or Input.is_joystick_button_pressed(1, JOYSTICK_PLAYER_CONTROLS[4][1]):
            if state.player_two.can_fire():
                fire_bullet(state.player_two, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pass

# TODO : Remove this later(only for testing)
RocketItem.Instantiate(pygame.Vector2(20,20))
RocketItem.Instantiate(pygame.Vector2(20,300))

# Gameloop
running = True

while running:
    state.current_time = pygame.time.get_ticks()
    state.delta_time = (state.current_time - state.previous_time) / 1000.0
    state.previous_time = state.current_time

    handle_input()
    Rocket.InstantiateRandom(screen_width, screen_height, (-1, 0), state.delta_time)

    handle_movement(state.player_one, KEYBOARD_PLAYER_ONE_CONTROLS, 0)
    handle_movement(state.player_two, KEYBOARD_PLAYER_TWO_CONTROLS, 1)

    surface.fill((0, 0, 0, 0))

    render_background(screen)

    state.player_one.check_other_player_edges(state.player_two)
    state.enemy.check_other_player_edges(state.player_one)
    state.enemy.check_other_player_edges(state.player_two)

    state.player_one.update(state)
    state.player_one.render(surface)
    state.player_two.update(state)
    state.player_two.render(surface)
    state.enemy.update(state)
    state.enemy.check_edges(screen_width, screen_height)
    state.enemy.render(surface)

    state.player_one.update_ui()
    state.player_two.update_ui()

    Bullet.Update_all(state.delta_time, state.player_one, state.player_two, state.enemy, surface)
    Rocket.Update_all(state.delta_time, state.player_one, state.player_two, surface)
    Collectable.Update_all(state.delta_time,state.player_one,state.player_two, surface)

    screen.blit(surface, (0, 0))

    pygame.display.update()

pygame.quit()


# if __name__ == "__main__":
#     main()
