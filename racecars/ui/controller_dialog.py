"""UI for assigning each player to mouse control or a script controller."""

import pygame


class ControllerDialog:
    def __init__(self, players: int, options, default_selection):
        self.players = players
        self.options = options
        self.default_selection = default_selection
        self.screen = None
        self.font = None
        self.clock = None
        self.fields = []

    def run(self):
        # Show one selector per player and return selected controller names.
        pygame.init()
        width = 640
        height = 180 + self.players * 34
        if height < 320:
            height = 320
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont("consolas", 18)
        self.clock = pygame.time.Clock()
        self._build_fields()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse(event.pos)

            self._render()
            self.clock.tick(30)

        pygame.quit()
        return self._collect_values()

    def _build_fields(self):
        self.fields = []
        for index in range(self.players):
            label = "Player " + str(index + 1)
            default_name = ""
            if index < len(self.default_selection):
                default_name = self.default_selection[index]
            option_index = self._index_for_name(default_name)
            self.fields.append(_ControllerField(label, self.options, option_index))

    def _handle_mouse(self, pos):
        # Clicking a field cycles through available controller options.
        x, y = pos
        field_index = self._field_index_at(y)
        if field_index is not None:
            field = self.fields[field_index]
            field.index += 1
            if field.index >= len(field.options):
                field.index = 0
            return

        if self._button_hit(x, y, 500, 20, 110, 40):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _render(self):
        self.screen.fill((230, 230, 230))
        title = self.font.render("Controllers", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        y = 70
        for field in self.fields:
            label = self.font.render(field.label, True, (0, 0, 0))
            self.screen.blit(label, (20, y))
            box_rect = pygame.Rect(260, y - 4, 260, 26)
            pygame.draw.rect(self.screen, (255, 255, 255), box_rect)
            pygame.draw.rect(self.screen, (120, 120, 120), box_rect, 1)
            value = field.options[field.index]
            value_label = self.font.render(value, True, (0, 0, 0))
            self.screen.blit(value_label, (265, y))
            y += 34

        self._draw_button(500, 20, 110, 40, "Start")
        pygame.display.flip()

    def _draw_button(self, x, y, w, h, text):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (210, 210, 210), rect)
        pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)
        label = self.font.render(text, True, (0, 0, 0))
        label_x = x + (w - label.get_width()) // 2
        label_y = y + (h - label.get_height()) // 2
        self.screen.blit(label, (label_x, label_y))

    def _button_hit(self, x, y, bx, by, bw, bh):
        if x < bx or x > bx + bw:
            return False
        if y < by or y > by + bh:
            return False
        return True

    def _field_index_at(self, y):
        top = 70
        for index in range(len(self.fields)):
            field_top = top + index * 34
            if y >= field_top - 4 and y <= field_top + 22:
                return index
        return None

    def _index_for_name(self, name):
        if name == "":
            return 0
        for index, option in enumerate(self.options):
            if option == name:
                return index
        return 0

    def _collect_values(self):
        # Return plain strings so main.py can map names back to drivers.
        result = []
        for field in self.fields:
            result.append(field.options[field.index])
        return result


class _ControllerField:
    def __init__(self, label: str, options, index: int):
        self.label = label
        self.options = options
        self.index = index
