import random
from simulation.game_state import Track, Vertex, Segment
from typing import List

def generate_track(
    width: int = 60,
    height: int = 40,
    players: int = 2,
    track_width_mean: int = 6,
    track_width_var: int = 2,
    turn_density: int = 50,
    turn_sharpness: int = 50,
    seed: int = None
) -> Track:
    if seed is not None:
        random.seed(seed)

    track_width_mean, track_width_var = _clamp_track_width_for_players(players, height, track_width_mean, track_width_var)
    min_width, max_width = _track_width_bounds(players, height)
    attempts = 0
    max_attempts = 200
    last_track = None

    while True:
        # Generate start and finish lines
        start_line_length = track_width_mean
        min_line_length = players
        reserve = 1
        desired_length = min_line_length + reserve
        if desired_length > start_line_length:
            start_line_length = desired_length
        if start_line_length < 1:
            start_line_length = 1
        if start_line_length > height:
            start_line_length = height
        start_x = 0
        finish_x = width

        max_start_y = height - start_line_length
        if max_start_y < 0:
            max_start_y = 0

        start_y = random.randint(0, max_start_y)
        finish_y = random.randint(0, max_start_y)

        start_vertices: List[Vertex] = []
        i = 0
        while i < start_line_length:
            start_vertices.append(Vertex(start_x, start_y + i))
            i += 1

        finish_line = Segment(Vertex(finish_x, finish_y), Vertex(finish_x, finish_y + start_line_length))

        # Generate road mask
        road_mask: List[List[bool]] = []
        x = 0
        while x < width:
            column: List[bool] = []
            y = 0
            while y < height:
                column.append(False)
                y += 1
            road_mask.append(column)
            x += 1

        centerline = _generate_centerline(width, height, start_y, finish_y, turn_density, turn_sharpness)
        _apply_thickness(road_mask, width, height, centerline, track_width_mean, track_width_var, min_width, max_width)
        _ensure_start_finish(road_mask, width, height, start_y, finish_y, start_line_length)

        if _track_is_valid(road_mask, width, height, start_y, finish_y, start_line_length):
            return Track(width, height, road_mask, start_vertices, finish_line)

        last_track = Track(width, height, road_mask, start_vertices, finish_line)
        attempts += 1
        track_width_mean, track_width_var, turn_density, turn_sharpness = _relax_params(
            attempts,
            track_width_mean,
            track_width_var,
            turn_density,
            turn_sharpness,
            min_width,
            max_width
        )
        if attempts >= max_attempts:
            attempts = 0

    return last_track

def _generate_centerline(
    width: int,
    height: int,
    start_y: int,
    finish_y: int,
    turn_density: int,
    turn_sharpness: int
) -> List[Vertex]:
    path: List[Vertex] = []

    x = 0
    y = start_y
    direction_y = 0

    target_x = width - 1
    waypoints_x, waypoints_y = _build_waypoints(width, height, start_y, finish_y)
    next_wp_index = len(waypoints_y)
    target_y = finish_y
    if len(waypoints_y) > 1:
        next_wp_index = 1
        target_y = waypoints_y[next_wp_index]

    approach_window = width // 10
    if approach_window < 4:
        approach_window = 4
    if approach_window > width // 2:
        approach_window = width // 2

    force_window = width // 8
    if force_window < 4:
        force_window = 4
    if force_window > width // 2:
        force_window = width // 2

    while x < target_x:
        path.append(Vertex(x, y))

        if next_wp_index < len(waypoints_x):
            wp_x = waypoints_x[next_wp_index]
            wp_y = waypoints_y[next_wp_index]
            if x >= wp_x - approach_window:
                target_y = wp_y
            if x >= wp_x + force_window and y != wp_y:
                y = _force_vertical_to_target(path, x, y, wp_y)
            if x >= wp_x and y == wp_y:
                next_wp_index += 1
                if next_wp_index < len(waypoints_y):
                    target_y = waypoints_y[next_wp_index]

        direction_y = _pick_direction_with_bias(direction_y, y, target_y, height, turn_density, turn_sharpness)

        next_y = y + direction_y
        if next_y < 0 or next_y >= height:
            direction_y = -direction_y
            next_y = y + direction_y

        x += 1
        y = next_y

    path.append(Vertex(target_x, y))
    while y != finish_y:
        if y < finish_y:
            y += 1
        else:
            y -= 1
        path.append(Vertex(target_x, y))
    return path


def _force_vertical_to_target(path: List[Vertex], x: int, y: int, target_y: int) -> int:
    if y == target_y:
        return y
    step = 1
    if target_y < y:
        step = -1
    while y != target_y:
        y = y + step
        path.append(Vertex(x, y))
    return y

def _build_waypoints(width: int, height: int, start_y: int, finish_y: int):
    if width < 2:
        return [0], [start_y]

    segment_count = width // 6
    if segment_count < 6:
        segment_count = 6
    if segment_count > 14:
        segment_count = 14

    step_x = width // (segment_count - 1)
    if step_x < 1:
        step_x = 1

    waypoints_x: List[int] = []
    waypoints_y: List[int] = []

    waypoints_x.append(0)
    waypoints_y.append(start_y)

    last_x = 0
    index = 1
    while index < segment_count - 1:
        wx = index * step_x
        if wx <= last_x:
            wx = last_x + 1
        if wx >= width - 1:
            break
        waypoints_x.append(wx)
        last_x = wx
        index += 1

    if last_x != width - 1:
        waypoints_x.append(width - 1)

    internal_count = len(waypoints_x) - 2
    prev_y = start_y
    edge_toggle = False
    first_edge = _edge_target_for_start(height, start_y)
    edge_y = first_edge

    index = 0
    while index < internal_count:
        use_edge = True
        if index % 2 == 1:
            use_edge = False
        if use_edge:
            if edge_toggle:
                edge_y = _flip_edge(height, edge_y)
            edge_toggle = True
            wy = edge_y
        else:
            wy = _pick_waypoint_y(height, prev_y)

        waypoints_y.append(wy)
        prev_y = wy
        index += 1

    waypoints_y.append(finish_y)
    return waypoints_x, waypoints_y


def _pick_waypoint_y(height: int, prev_y: int) -> int:
    if height <= 0:
        return 0
    tries = 0
    while tries < 8:
        y = random.randint(0, height - 1)
        if abs(y - prev_y) > 3:
            return y
        tries += 1
    return random.randint(0, height - 1)


def _edge_target_for_start(height: int, start_y: int) -> int:
    if height <= 1:
        return 0
    mid = height // 2
    if start_y < mid:
        return height - 1
    return 0


def _flip_edge(height: int, current: int) -> int:
    if height <= 1:
        return 0
    if current == 0:
        return height - 1
    return 0


def _pick_direction_with_bias(
    current_dir: int,
    current_y: int,
    target_y: int,
    height: int,
    turn_density: int,
    turn_sharpness: int
) -> int:
    if height <= 1:
        return 0

    diff = target_y - current_y
    weight_up = 1
    weight_down = 1
    weight_zero = 1

    if diff > 0:
        weight_up += 2 + (turn_sharpness // 25)
    elif diff < 0:
        weight_down += 2 + (turn_sharpness // 25)

    if current_dir == 1:
        weight_up += 2
    elif current_dir == -1:
        weight_down += 2
    else:
        weight_zero += 1

    if abs(diff) <= 1:
        weight_zero += 3

    change_bias = turn_density // 20
    if current_dir == 1:
        weight_down += change_bias
        weight_zero += change_bias
    elif current_dir == -1:
        weight_up += change_bias
        weight_zero += change_bias
    else:
        weight_up += change_bias
        weight_down += change_bias

    if current_y <= 0:
        weight_down = 0
    if current_y >= height - 1:
        weight_up = 0

    total = weight_up + weight_down + weight_zero
    if total <= 0:
        return 0

    pick = random.randint(1, total)
    if pick <= weight_down:
        return -1
    if pick <= weight_down + weight_zero:
        return 0
    return 1

def _apply_thickness(
    road_mask: List[List[bool]],
    width: int,
    height: int,
    centerline: List[Vertex],
    track_width_mean: int,
    track_width_var: int,
    min_width: int,
    max_width: int
):
    if min_width < 1:
        min_width = 1
    if max_width < min_width:
        max_width = min_width

    change_interval = 1
    if len(centerline) > 0:
        change_interval = len(centerline) // 6
    if change_interval < 3:
        change_interval = 3

    current_base = _clamp_int(track_width_mean, min_width, max_width)

    index = 0
    while index < len(centerline):
        point = centerline[index]
        if index % change_interval == 0:
            current_base = _random_between(min_width, max_width)
        width_offset = random.randint(-track_width_var, track_width_var)
        track_width = current_base + width_offset
        track_width = _clamp_int(track_width, min_width, max_width)
        if track_width < 1:
            track_width = 1
        radius = track_width // 2

        dx = -radius
        while dx <= radius:
            dy = -radius
            while dy <= radius:
                x = point.x + dx
                y = point.y + dy
                if 0 <= x < width and 0 <= y < height:
                    road_mask[x][y] = True
                dy += 1
            dx += 1

        index += 1

def _ensure_start_finish(
    road_mask: List[List[bool]],
    width: int,
    height: int,
    start_y: int,
    finish_y: int,
    line_length: int
):
    y = start_y
    while y < start_y + line_length and y < height:
        if 0 <= 0 < width:
            road_mask[0][y] = True
        y += 1

    y = finish_y
    while y < finish_y + line_length and y < height:
        if 0 <= width - 1 < width:
            road_mask[width - 1][y] = True
        y += 1

def _track_is_valid(
    road_mask: List[List[bool]],
    width: int,
    height: int,
    start_y: int,
    finish_y: int,
    line_length: int
) -> bool:
    if width <= 0 or height <= 0:
        return False

    start_cells = []
    y = start_y
    while y < start_y + line_length and y < height:
        if road_mask[0][y]:
            start_cells.append((0, y))
        y += 1

    if len(start_cells) == 0:
        return False

    if not _start_has_exit(road_mask, width, height, start_cells):
        return False

    visited: List[List[bool]] = []
    x = 0
    while x < width:
        column: List[bool] = []
        y = 0
        while y < height:
            column.append(False)
            y += 1
        visited.append(column)
        x += 1

    queue = []
    queue.append(start_cells[0])
    visited[start_cells[0][0]][start_cells[0][1]] = True
    index = 0
    while index < len(queue):
        cx, cy = queue[index]
        index += 1

        nx = cx - 1
        ny = cy
        if nx >= 0 and road_mask[nx][ny] and not visited[nx][ny]:
            visited[nx][ny] = True
            queue.append((nx, ny))

        nx = cx + 1
        ny = cy
        if nx < width and road_mask[nx][ny] and not visited[nx][ny]:
            visited[nx][ny] = True
            queue.append((nx, ny))

        nx = cx
        ny = cy - 1
        if ny >= 0 and road_mask[nx][ny] and not visited[nx][ny]:
            visited[nx][ny] = True
            queue.append((nx, ny))

        nx = cx
        ny = cy + 1
        if ny < height and road_mask[nx][ny] and not visited[nx][ny]:
            visited[nx][ny] = True
            queue.append((nx, ny))

    y = finish_y
    finish_reached = False
    while y < finish_y + line_length and y < height:
        if visited[width - 1][y]:
            finish_reached = True
            break
        y += 1

    if not finish_reached:
        return False

    x = 0
    while x < width:
        y = 0
        while y < height:
            if road_mask[x][y] and not visited[x][y]:
                return False
            y += 1
        x += 1

    return True

def _start_has_exit(
    road_mask: List[List[bool]],
    width: int,
    height: int,
    start_cells
) -> bool:
    index = 0
    while index < len(start_cells):
        x = start_cells[index][0]
        y = start_cells[index][1]
        has_exit = False
        if x + 1 < width and road_mask[x + 1][y]:
            has_exit = True
        if y > 0 and road_mask[x][y - 1]:
            has_exit = True
        if y + 1 < height and road_mask[x][y + 1]:
            has_exit = True
        if not has_exit:
            return False
        index += 1
    return True

def _relax_params(
    attempts: int,
    track_width_mean: int,
    track_width_var: int,
    turn_density: int,
    turn_sharpness: int,
    min_width: int,
    max_width: int
):
    if attempts % 5 != 0:
        return track_width_mean, track_width_var, turn_density, turn_sharpness

    if track_width_mean < max_width:
        track_width_mean += 1
    if track_width_var > 0:
        track_width_var -= 1
    if turn_density > 10:
        turn_density -= 5
    if turn_sharpness > 10:
        turn_sharpness -= 5

    track_width_mean = _clamp_int(track_width_mean, min_width, max_width)
    if track_width_var < 0:
        track_width_var = 0

    return track_width_mean, track_width_var, turn_density, turn_sharpness

def _track_width_bounds(players: int, height: int):
    min_width = int(players * 0.8)
    if min_width < 2:
        min_width = 2
    max_width = players * 2
    if height > 0 and height < max_width:
        max_width = height
    if max_width < min_width:
        max_width = min_width
    return min_width, max_width

def _clamp_track_width_for_players(players: int, height: int, track_width_mean: int, track_width_var: int):
    min_width, max_width = _track_width_bounds(players, height)

    if track_width_mean < min_width or track_width_mean > max_width:
        track_width_mean = min_width + (max_width - min_width) // 2

    max_var = track_width_mean - min_width
    if max_width - track_width_mean < max_var:
        max_var = max_width - track_width_mean
    if max_var < 0:
        max_var = 0

    if track_width_var > max_var:
        track_width_var = max_var
    if track_width_var < 0:
        track_width_var = 0

    return track_width_mean, track_width_var

def _clamp_int(value: int, low: int, high: int) -> int:
    if value < low:
        return low
    if value > high:
        return high
    return value

def _random_between(min_value: int, max_value: int) -> int:
    if min_value >= max_value:
        return min_value
    return random.randint(min_value, max_value)
