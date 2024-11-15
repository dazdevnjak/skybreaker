import math
import pygame


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
