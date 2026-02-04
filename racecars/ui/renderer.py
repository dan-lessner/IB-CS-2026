import random
import pygame
from simulation.game_state import GameState
from ui.controller import Controller

class Renderer:
    def __init__(self, game_state: GameState, screen_width: int = None, screen_height: int = None):
        pygame.init()
        self.game_state = game_state
        self.controller = Controller(game_state)
        self.cell_size = 20  # Size of each grid cell in pixels
        self.margin = 40  # Paper margin around the grid
        if screen_width is None or screen_height is None:
            screen_width, screen_height = self._compute_screen_size()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.car_colors = self._assign_car_colors()
        self.font = pygame.font.SysFont("consolas", 18)

    def _compute_screen_size(self):
        width_px = self.game_state.track.width * self.cell_size
        height_px = self.game_state.track.height * self.cell_size
        screen_width = width_px + self.margin * 2
        screen_height = height_px + self.margin * 2
        return screen_width, screen_height

    def draw_grid(self):
        width_px = self.game_state.track.width * self.cell_size
        height_px = self.game_state.track.height * self.cell_size

        x = 0
        while x <= width_px:
            line_x = self.margin + x
            color = (170, 200, 220)
            if x % (self.cell_size * 5) == 0:
                color = (120, 160, 190)
            pygame.draw.line(self.screen, color, (line_x, self.margin), (line_x, self.margin + height_px), 1)
            x += self.cell_size

        y = 0
        while y <= height_px:
            line_y = self.margin + y
            color = (170, 200, 220)
            if y % (self.cell_size * 5) == 0:
                color = (120, 160, 190)
            pygame.draw.line(self.screen, color, (self.margin, line_y), (self.margin + width_px, line_y), 1)
            y += self.cell_size

    def draw_track(self):
        x = 0
        while x < self.game_state.track.width:
            y = 0
            while y < self.game_state.track.height:
                rect = pygame.Rect(
                    self.margin + x * self.cell_size,
                    self.margin + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                if self.game_state.track.road_mask[x][y]:
                    pygame.draw.rect(self.screen, (235, 235, 235), rect)  # Light track
                y += 1
            x += 1

    def handle_click(self, position):
        # Convert click position to nearest vertex coordinates
        grid_x = round((position[0] - self.margin) / self.cell_size)
        grid_y = round((position[1] - self.margin) / self.cell_size)
        self.controller.apply_click(grid_x, grid_y)

    def draw_cars(self):
        for car in self.game_state.cars:
            color = self._get_car_color(car.id)
            # Draw the path as a polyline and vertex markers
            index = 0
            while index < len(car.path):
                segment = car.path[index]
                start_pos = self._vertex_to_screen(segment.start.x, segment.start.y)
                end_pos = self._vertex_to_screen(segment.end.x, segment.end.y)
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
                pygame.draw.circle(self.screen, color, start_pos, self.cell_size // 8)
                pygame.draw.circle(self.screen, color, end_pos, self.cell_size // 8)
                index += 1

            # Draw the car
            car_pos = self._vertex_to_screen(car.pos.x, car.pos.y)
            pygame.draw.circle(self.screen, color, car_pos, self.cell_size // 3)

    def draw_start_and_finish_lines(self):
        if self.game_state.track.start_line is None:
            return

        # Draw start line
        start = self.game_state.track.start_line.start
        end = self.game_state.track.start_line.end
        if start.x == end.x:
            y = start.y
            while y <= end.y:
                x0, y0 = self._vertex_to_screen(start.x, y)
                x1, y1 = self._vertex_to_screen(start.x, y + 1)
                pygame.draw.line(self.screen, (0, 180, 0), (x0, y0), (x1, y1), 2)
                y += 1
        else:
            x = start.x
            while x <= end.x:
                x0, y0 = self._vertex_to_screen(x, start.y)
                x1, y1 = self._vertex_to_screen(x + 1, start.y)
                pygame.draw.line(self.screen, (0, 180, 0), (x0, y0), (x1, y1), 2)
                x += 1

        # Draw finish line
        start = self.game_state.track.finish_line.start
        end = self.game_state.track.finish_line.end
        if start.x == end.x:
            y = start.y
            while y <= end.y:
                x0, y0 = self._vertex_to_screen(start.x, y)
                x1, y1 = self._vertex_to_screen(start.x, y + 1)
                pygame.draw.line(self.screen, (200, 0, 0), (x0, y0), (x1, y1), 2)
                y += 1
        else:
            x = start.x
            while x <= end.x:
                x0, y0 = self._vertex_to_screen(x, start.y)
                x1, y1 = self._vertex_to_screen(x + 1, start.y)
                pygame.draw.line(self.screen, (200, 0, 0), (x0, y0), (x1, y1), 2)
                x += 1

    def render(self):
        self.screen.fill((180, 180, 180))  # Gray background outside track
        self.draw_track()
        self.draw_grid()  # Grid on top for graph-paper look
        self.draw_start_and_finish_lines()
        self.draw_possible_targets()
        self.draw_cars()
        self.draw_status()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.controller.update()
            self.render()
            self.clock.tick(30)

        pygame.quit()

    def _vertex_to_screen(self, x: int, y: int):
        screen_x = self.margin + x * self.cell_size
        screen_y = self.margin + y * self.cell_size
        return (screen_x, screen_y)

    def _assign_car_colors(self):
        colors = {}
        index = 0
        while index < len(self.game_state.cars):
            car = self.game_state.cars[index]
            colors[car.id] = self._random_car_color()
            index += 1
        return colors

    def _random_car_color(self):
        r = random.randint(60, 255)
        g = random.randint(60, 255)
        b = random.randint(60, 255)
        return (r, g, b)

    def _get_car_color(self, car_id: int):
        if car_id in self.car_colors:
            return self.car_colors[car_id]
        color = self._random_car_color()
        self.car_colors[car_id] = color
        return color

    def _draw_target_preview_lines(self):
        if not self.game_state.cars:
            return

        car = self.game_state.cars[self.game_state.current_player_idx]
        options = self.controller.get_move_options()

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        start_pos = self._vertex_to_screen(car.pos.x, car.pos.y)

        index = 0
        while index < len(options):
            option = options[index]
            if option.valid:
                end_pos = self._vertex_to_screen(option.target.x, option.target.y)
                pygame.draw.line(overlay, (0, 120, 255, 80), start_pos, end_pos, 2)
            index += 1

        self.screen.blit(overlay, (0, 0))

    def draw_possible_targets(self):
        if self.game_state.finished:
            return

        self._draw_target_preview_lines()

        options = self.controller.get_move_options()
        penalty_mode = self._current_car_is_waiting()
        index = 0
        while index < len(options):
            option = options[index]
            pos = self._vertex_to_screen(option.target.x, option.target.y)
            if penalty_mode and option.target.x == self.game_state.cars[self.game_state.current_player_idx].pos.x and option.target.y == self.game_state.cars[self.game_state.current_player_idx].pos.y:
                pos = self._apply_penalty_marker_offset(pos)
            color = (255, 120, 60)
            if option.valid:
                color = (0, 120, 255)
            pygame.draw.circle(self.screen, color, pos, self.cell_size // 4, 2)
            index += 1

    def draw_status(self):
        if not self.game_state.cars:
            return

        x = self.margin
        y = 10
        if self.game_state.finished:
            if len(self.game_state.winners) == 1:
                winner_id = self.game_state.winners[0]
                winner = self._get_car_by_id(winner_id)
                winner_text = "Car " + str(winner_id + 1) + ": " + winner.name
                parts = [
                    ("Winner: ", (0, 0, 0)),
                    (winner_text, self._get_car_color(winner_id))
                ]
                self._blit_text_parts(x, y, parts)
            else:
                parts = [("Winners: ", (0, 0, 0))]
                parts.extend(self._winner_name_parts())
                self._blit_text_parts(x, y, parts)
        else:
            current = self.game_state.cars[self.game_state.current_player_idx]
            parts = [
                ("Turn: ", (0, 0, 0)),
                (current.name, self._get_car_color(current.id))
            ]
            self._blit_text_parts(x, y, parts)

    def _join_winners(self):
        text = ""
        index = 0
        while index < len(self.game_state.winners):
            if index > 0:
                text = text + ", "
            text = text + "Car " + str(self.game_state.winners[index])
            index += 1
        return text

    def _get_car_by_id(self, car_id: int):
        index = 0
        while index < len(self.game_state.cars):
            car = self.game_state.cars[index]
            if car.id == car_id:
                return car
            index += 1
        return self.game_state.cars[0]

    def _winner_name_parts(self):
        parts = []
        index = 0
        while index < len(self.game_state.winners):
            winner_id = self.game_state.winners[index]
            winner = self._get_car_by_id(winner_id)
            if index > 0:
                parts.append((", ", (0, 0, 0)))
            text = "Car " + str(winner_id + 1) + ": " + winner.name
            parts.append((text, self._get_car_color(winner_id)))
            index += 1
        return parts

    def _blit_text_parts(self, x: int, y: int, parts):
        offset_x = x
        index = 0
        while index < len(parts):
            text = parts[index][0]
            color = parts[index][1]
            label = self.font.render(text, True, color)
            self.screen.blit(label, (offset_x, y))
            offset_x += label.get_width()
            index += 1

    def _current_car_is_waiting(self):
        if not self.game_state.cars:
            return False
        car = self.game_state.cars[self.game_state.current_player_idx]
        return car.penalty_turns_left > 0

    def _apply_penalty_marker_offset(self, pos):
        offset = int(self.cell_size * 0.35)
        return (pos[0], pos[1] - offset)
