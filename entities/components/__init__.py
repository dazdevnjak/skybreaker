import math
import pygame
import utility


class Component:
    def __init__(self) -> None:
        pass

    def on_load(self, parent):
        pass

    def on_update(self, state, parent):
        pass

    def on_render(self, state, parent):
        pass


class AimIndicator(Component):
    def __init__(self) -> None:
        super().__init__()

        self.indicator_angle = 0
        self.indicator_radius = 30
        self.indicator_color = (255, 255, 255)
        pass

    def on_load(self, parent):
        self.parent = parent
        pass

    def on_update(self, state, parent):
        pass

    def on_render(self, state, parent):
        self.draw_indicator(state.screen)
        pass

    def adjust_indicator_angle(self, angle_change):
        self.indicator_angle = (self.indicator_angle + angle_change) % 360
        pass

    def set_indicator_angle(self, target_angle, speed):
        angle_diff = (target_angle - self.indicator_angle + 180) % 360 - 180
        if abs(angle_diff) < speed:
            self.indicator_angle = target_angle
        else:
            self.indicator_angle += speed * (1 if angle_diff > 0 else -1)
            self.indicator_angle %= 360
        pass

    def get_indicator_position(self):
        center_x, center_y = (
            self.parent.position[0] + self.parent.size[0] / 2,
            self.parent.position[1] + self.parent.size[1] / 2,
        )
        x = center_x + self.indicator_radius * math.cos(
            math.radians(self.indicator_angle)
        )
        y = center_y + self.indicator_radius * math.sin(
            math.radians(self.indicator_angle)
        )
        return pygame.Vector2(x, y)

    def draw_indicator(self, screen):
        start_position = pygame.Vector2(
            self.parent.position[0] + self.parent.size[0] / 2,
            self.parent.position[1] + self.parent.size[1] / 2,
        )
        target_position = self.get_indicator_position()
        direction = (target_position - start_position).normalize()
        distance = (target_position - start_position).length()
        dash_length = 4
        gap_length = 3
        total_segment_length = dash_length + gap_length
        num_segments = int(distance // total_segment_length)
        pygame.draw.circle(screen, (0, 0, 0, 150), start_position, 21, width=1)
        pygame.draw.circle(screen, (255, 255, 255, 150), start_position, 20, width=1)
        for i in range(num_segments):
            s = i + 5
            dash_start = start_position + direction * (s * total_segment_length)
            dash_end = dash_start + direction * dash_length
            pygame.draw.line(screen, (0, 0, 0, 150), dash_start, dash_end, 2)
            pygame.draw.line(screen, self.indicator_color, dash_start, dash_end, 1)
        pass


class HealthBarUI(Component):
    DAMAGE_ANIMATION_DURATION = 500

    def __init__(self) -> None:
        self.health_bar_size = (25, 7)
        self.health_fill_bar_size = (20, 3)
        self.lives_bar_size = (19, 6)
        self.shake_x_offset = 0
        self.shake_y_offset = 0

        self.health_bar_bg = pygame.transform.scale(
            pygame.image.load("assets/images/health_bar/bar_bg.png").convert_alpha(),
            self.health_bar_size,
        )
        self.health_bar_fill = pygame.transform.scale(
            pygame.image.load(
                "assets/images/health_bar/bar_fill_small.png"
            ).convert_alpha(),
            self.health_fill_bar_size,
        )

        self.lives_bar = [
            pygame.transform.scale(
                pygame.image.load(
                    f"assets/images/health_bar/lives_{i}.png"
                ).convert_alpha(),
                self.lives_bar_size,
            )
            for i in range(1, 4)
        ]

        self.lives_left = 2
        self.live_bar = self.lives_bar[-1]
        self.damage_anim = False
        self.anim_start_time = 0

        self.health_fill_width = 0

        super().__init__()

    def on_death(self):
        if self.lives_left > 0:
            self.lives_left -= 1

    def on_load(self, parent):
        pass

    def damage(self):
        self.damage_anim = True

        def reset():
            self.damage_anim = False

        utility.Executor.wait(HealthBarUI.DAMAGE_ANIMATION_DURATION, reset)
        self.anim_start_time = pygame.time.get_ticks()
        pass

    def on_update(self, state, parent):
        current_time = pygame.time.get_ticks()
        fill_alpha = 200

        elapsed = current_time - self.anim_start_time

        if self.damage_anim:
            start_width = int(
                (parent.previous_health / 100) * self.health_fill_bar_size[0]
            )
            end_width = int((parent.health / 100) * self.health_fill_bar_size[0])
            progress = elapsed / HealthBarUI.DAMAGE_ANIMATION_DURATION
            self.health_fill_width = int(
                start_width + (end_width - start_width) * progress
            )

            shake_amplitude = 3
            shake_offset = shake_amplitude * math.sin(elapsed * 0.05)
            self.shake_x_offset = int(shake_offset)
            self.shake_y_offset = int(shake_offset)

            color_progress = min(1.0, progress)
            white_color = (255, 255, 255)
            red_color = (255, 0, 0)
            fill_color = (
                int(
                    white_color[0] * (1 - color_progress)
                    + red_color[0] * color_progress
                ),
                int(
                    white_color[1] * (1 - color_progress)
                    + red_color[1] * color_progress
                ),
                int(
                    white_color[2] * (1 - color_progress)
                    + red_color[2] * color_progress
                ),
            )
            self.health_bar_fill.fill(fill_color)
        else:
            self.shake_x_offset = 0
            self.shake_y_offset = 0

            self.health_fill_width = int(
                (parent.health / 100) * self.health_fill_bar_size[0]
            )
            self.anim_start_time = 0.0

        self.health_bar_fill.set_alpha(fill_alpha)
        self.health_bar_bg.set_alpha(fill_alpha)
        pass

    def on_render(self, state, parent):
        health_bar_position = (
            parent.position[0] + 80 + self.shake_x_offset,
            parent.position[1] + 10 + self.shake_y_offset,
        )

        state.surface.blit(self.health_bar_bg, health_bar_position)

        if parent.is_player:
            self.live_bar = self.lives_bar[self.lives_left]
            live_bar_position = (
                parent.position[0] + 80 + self.shake_x_offset,
                parent.position[1] + 2 + self.shake_y_offset,
            )

            state.surface.blit(self.live_bar, live_bar_position)

        fill_position = (
            health_bar_position[0] + 2,
            health_bar_position[1] + 2,
        )

        health_fill_rect = pygame.Rect(
            fill_position, (self.health_fill_width, self.health_bar_size[1])
        )

        state.surface.blit(
            self.health_bar_fill,
            health_fill_rect,
            (0, 0, self.health_fill_width, self.health_bar_size[1]),
        )
        pass
