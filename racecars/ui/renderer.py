"""Pygame renderer for the racecars game.

Draws the track, cars, move hints, and status text each frame.
"""

import logging
import random
import pygame
from simulation.game_state import GameState
from simulation.controller import Controller

_LOGGER = logging.getLogger("racecars.renderer")

_CAR_COLOR_NAMES = [
    "darkred",
    "darkgreen",
    "navy",
    "teal",
    "darkmagenta",
    "chocolate",
    "dodgerblue",
    "crimson",
    "olivedrab",
    "saddlebrown",
    "firebrick",
    "midnightblue",
]

class Renderer:
    def __init__(
        self,
        game_state: GameState,
        screen_width: int = None,
        screen_height: int = None,
        framerate: int = 30
    ):
        pygame.init()
        self.game_state = game_state
        self.controller = Controller(game_state)
        self.cell_size = 20  # Size of each grid cell in pixels
        self.margin = 40  # Paper margin around the grid
        if screen_width is None or screen_height is None:
            screen_width, screen_height = self._compute_screen_size()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.framerate = framerate

        self.car_colors = []
        for color_name in _CAR_COLOR_NAMES:
            self.car_colors.append(pygame.colordict.THECOLORS[color_name])
        random.shuffle(self.car_colors)
        
        self.font = pygame.font.SysFont("consolas", 18)
        self._missing_start_line_warning_emitted = False
        self._missing_car_id_warnings = set()

    def _compute_screen_size(self):
        width_px = self.game_state.track.width * self.cell_size
        height_px = self.game_state.track.height * self.cell_size
        screen_width = width_px + self.margin * 2
        screen_height = height_px + self.margin * 2
        return screen_width, screen_height

    def draw_grid(self):
        # Grid lines mimic graph paper, which helps explain vector movement.
        width_px = self.game_state.track.width * self.cell_size
        height_px = self.game_state.track.height * self.cell_size

        for x in range(0, width_px + 1, self.cell_size):
            line_x = self.margin + x
            color = (170, 200, 220)
            if x % (self.cell_size * 5) == 0:
                color = (120, 160, 190)
            pygame.draw.line(self.screen, color, (line_x, self.margin), (line_x, self.margin + height_px), 1)

        for y in range(0, height_px + 1, self.cell_size):
            line_y = self.margin + y
            color = (170, 200, 220)
            if y % (self.cell_size * 5) == 0:
                color = (120, 160, 190)
            pygame.draw.line(self.screen, color, (self.margin, line_y), (self.margin + width_px, line_y), 1)

    def draw_track(self):
        # Paint only drivable cells; the background remains "off-road".
        for x in range(self.game_state.track.width):
            for y in range(self.game_state.track.height):
                rect = pygame.Rect(
                    self.margin + x * self.cell_size,
                    self.margin + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                if self.game_state.track.road_mask[x][y]:
                    pygame.draw.rect(self.screen, (235, 235, 235), rect)  # Light track

    def handle_click(self, position):
        # Convert click position to nearest vertex coordinates
        grid_x = round((position[0] - self.margin) / self.cell_size)
        grid_y = round((position[1] - self.margin) / self.cell_size)
        self.controller.apply_click(grid_x, grid_y)

    def draw_cars(self):
        for car in self.game_state.cars:
            color = self.car_colors[car.id]
            # Draw the historical path so students can replay decision outcomes.
            for segment in car.path:
                start_pos = self._vertex_to_screen(segment.start.x, segment.start.y)
                end_pos = self._vertex_to_screen(segment.end.x, segment.end.y)
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
                pygame.draw.circle(self.screen, color, start_pos, self.cell_size // 8)
                pygame.draw.circle(self.screen, color, end_pos, self.cell_size // 8)

            # Draw the car
            car_pos = self._vertex_to_screen(car.pos.x, car.pos.y)
            pygame.draw.circle(self.screen, color, car_pos, self.cell_size // 3)

    def draw_start_and_finish_lines(self):
        if self.game_state.track.start_line is None:
            if not self._missing_start_line_warning_emitted:
                _LOGGER.warning("Track.start_line is None. Start line rendering is skipped.")
                self._missing_start_line_warning_emitted = True
            return

        # Draw start line
        start = self.game_state.track.start_line.start
        end = self.game_state.track.start_line.end
        if start.x == end.x:
            for y in range(start.y, end.y + 1):
                x0, y0 = self._vertex_to_screen(start.x, y)
                x1, y1 = self._vertex_to_screen(start.x, y + 1)
                pygame.draw.line(self.screen, (0, 180, 0), (x0, y0), (x1, y1), 2)
        else:
            for x in range(start.x, end.x + 1):
                x0, y0 = self._vertex_to_screen(x, start.y)
                x1, y1 = self._vertex_to_screen(x + 1, start.y)
                pygame.draw.line(self.screen, (0, 180, 0), (x0, y0), (x1, y1), 2)

        # Draw finish line
        start = self.game_state.track.finish_line.start
        end = self.game_state.track.finish_line.end
        if start.x == end.x:
            for y in range(start.y, end.y + 1):
                x0, y0 = self._vertex_to_screen(start.x, y)
                x1, y1 = self._vertex_to_screen(start.x, y + 1)
                pygame.draw.line(self.screen, (200, 0, 0), (x0, y0), (x1, y1), 2)
        else:
            for x in range(start.x, end.x + 1):
                x0, y0 = self._vertex_to_screen(x, start.y)
                x1, y1 = self._vertex_to_screen(x + 1, start.y)
                pygame.draw.line(self.screen, (200, 0, 0), (x0, y0), (x1, y1), 2)

    def render(self):
        self.screen.fill((180, 180, 180))  # Gray background outside track
        self.draw_track()
        self.draw_grid()  # Grid on top for graph-paper look
        self.draw_start_and_finish_lines()
        self.draw_possible_targets()
        self.draw_cars()
        self.draw_status()
        self.draw_round_counter()
        pygame.display.flip()

    def run(self):
        # Main render loop: input -> game update -> redraw.
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.controller.update()
            self.render()
            self.clock.tick(self.framerate)

        pygame.quit()

    def _vertex_to_screen(self, x: int, y: int):
        screen_x = self.margin + x * self.cell_size
        screen_y = self.margin + y * self.cell_size
        return (screen_x, screen_y)

    def _draw_target_preview_lines(self):
        # Light guide lines make the acceleration options easier to read visually.
        if not self.game_state.cars:
            return

        car = self.game_state.cars[self.game_state.current_player_idx]
        targets, validity = self.controller.get_targets_and_validity()

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        start_pos = self._vertex_to_screen(car.pos.x, car.pos.y)

        for target, is_valid in zip(targets, validity):
            if is_valid:
                end_pos = self._vertex_to_screen(target.x, target.y)
                pygame.draw.line(overlay, (0, 120, 255, 80), start_pos, end_pos, 2)

        self.screen.blit(overlay, (0, 0))

    def draw_possible_targets(self):
        # Targets are shown every frame for the currently active car.
        if self.game_state.finished:
            return

        self._draw_target_preview_lines()

        targets, validity = self.controller.get_targets_and_validity()
        penalty_mode = self._current_car_is_waiting()
        current_car = self.game_state.cars[self.game_state.current_player_idx]
        for index, target in enumerate(targets):
            is_valid = index < len(validity) and validity[index]
            pos = self._vertex_to_screen(target.x, target.y)
            if penalty_mode and target == current_car.pos:
                pos = self._apply_penalty_marker_offset(pos)
            color = (255, 120, 60)
            if is_valid:
                color = (0, 120, 255)
            pygame.draw.circle(self.screen, color, pos, self.cell_size // 4, 2)

    def draw_status(self):
        # Status line switches between "current turn" and "winner(s)" mode.
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
                    (winner_text, self.car_colors[winner.id])
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
                (current.name, self.car_colors[current.id])
            ]
            self._blit_text_parts(x, y, parts)

    def draw_round_counter(self):
        round_text = "Round: " + str(self.game_state.race_round)
        label = self.font.render(round_text, True, (0, 0, 0))
        x = self.screen.get_width() - label.get_width() - 10
        y = 10
        self.screen.blit(label, (x, y))

    def _join_winners(self):
        text = ""
        for index, winner_id in enumerate(self.game_state.winners):
            if index > 0:
                text = text + ", "
            text = text + "Car " + str(winner_id)
        return text

    def _get_car_by_id(self, car_id: int):
        for car in self.game_state.cars:
            if car.id == car_id:
                return car
        if car_id not in self._missing_car_id_warnings:
            _LOGGER.warning("Requested car_id=%s was not found. Falling back to first car.", car_id)
            self._missing_car_id_warnings.add(car_id)
        return self.game_state.cars[0]

    def _winner_name_parts(self):
        parts = []
        for index, winner_id in enumerate(self.game_state.winners):
            winner = self._get_car_by_id(winner_id)
            if index > 0:
                parts.append((", ", (0, 0, 0)))
            text = "Car " + str(winner_id + 1) + ": " + winner.name
            parts.append((text, self.car_colors[winner.id]))
        return parts

    def _blit_text_parts(self, x: int, y: int, parts):
        offset_x = x
        for text, color in parts:
            label = self.font.render(text, True, color)
            self.screen.blit(label, (offset_x, y))
            offset_x += label.get_width()

    def _current_car_is_waiting(self):
        if not self.game_state.cars:
            return False
        car = self.game_state.cars[self.game_state.current_player_idx]
        return car.penalty > 0

    def _apply_penalty_marker_offset(self, pos):
        offset = int(self.cell_size * 0.35)
        return (pos[0], pos[1] - offset)
