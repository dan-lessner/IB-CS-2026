# Exercises for Autonomous Car Scripts

This file contains a sequence of exercises from trivial behaviors to more advanced movement strategies. 

## 1) Move back-and-forth (very simple)
Goal: Make the car move left-right (or forward-back) repeatedly to check that you are in control.

<details>
<summary>Hints</summary>

- Keep state: remember current direction as `dx, dy`.
- Each turn, propose a move in that direction.
- If collision or obstacle, reverse direction.
- Test on an empty corridor first.

<details>
<summary>detail-summary</summary>

```python
# Critical snippet: flip horizontal direction on collision
import math

def pick_move_bounce_simple(position, direction, collision):
    # position: (x, y)
    # direction: [dx, dy]
    # collision: boolean from last attempted move
    if collision:
        # reverse direction
        direction[0] = -direction[0]
        direction[1] = -direction[1]
    # propose next move using direction
    next_x = position[0] + direction[0]
    next_y = position[1] + direction[1]
    return (next_x, next_y), direction
```

</details>

</details>



## 2) Follow a square or octagon vertex list
Goal: Drive the car from vertex to vertex around a polygon (square, octagon).

<details>
<summary>Hints</summary>

- Represent vertices as an ordered list of coordinates.
- Move toward the current target vertex until close enough, then advance to the next vertex.
- Keep the car speed constant; prefer unit steps or scaled steps.
- Use a distance function to decide when the vertex is "reached".

<details>
<summary>detail-summary</summary>

```python
import math

def euclidean(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx*dx + dy*dy)

# choose next vertex:
# vertices: list of (x,y)
# position: (x,y)
# idx: current target index

def pick_nearest_vertex(vertices, position, visited):
    best_idx = None
    best_dist = None
    i = 0
    while i < len(vertices):
        v = vertices[i]
        if v in visited:
            i = i + 1
            continue
        d = euclidean(position, v)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_idx = i
        i = i + 1
    return best_idx
```

</details>

</details>



## 3) Keep direction until collision, then bounce to a random new direction (no acceleration)
Goal: Maintain current heading; if you hit something, pick a new random heading and continue. Do not accelerate during this process.

<details>
<summary>Hints</summary>

- Keep speed constant (for example 1 cell per tick).
- On collision, compute a new heading randomly (but normalized to desired speed).
- Implement a cooldown or small step-back to avoid getting stuck in a wall.

<details>
<summary>detail-summary</summary>

```python
import random
import math

def random_unit_step():
    # choose one of eight directions or normalized random
    angle = random.random() * 2.0 * math.pi
    dx = math.cos(angle)
    dy = math.sin(angle)
    return dx, dy

# on collision:
dx, dy = random_unit_step()
# next move: x + dx, y + dy
```

</details>

</details>



## 4) Reflect by "angle of incidence" for oblique collisions
Goal: When moving at an angle and colliding with a wall, compute the reflection direction using the angle of incidence (mirror by wall normal).

<details>
<summary>Hints</summary>

- Represent direction as a vector (dx, dy) normalized.
- Represent wall contact with a normal vector `n` (unit vector pointing away from wall).
- Reflection formula: r = d - 2*(d·n)*n (where d is incoming direction).
- Normalize `r` and use it for the next move.

<details>
<summary>detail-summary</summary>

```python
import math

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1])
    if l == 0:
        return (0.0, 0.0)
    return (v[0]/l, v[1]/l)

# reflect incoming direction d across normal n
# both d and n should be unit vectors

def reflect(d, n):
    dp = dot(d, n)
    rx = d[0] - 2.0 * dp * n[0]
    ry = d[1] - 2.0 * dp * n[1]
    return normalize((rx, ry))
```

</details>

</details>



## 5) Detect a collision vs merely touching the wall; optionally avoid it entirely
Goal: Experiment with two behaviors: (A) just touch walls (stop at contact or slide along them) and (B) proactively avoid them by choosing alternative moves.

<details>
<summary>Hints</summary>

- Distinguish between collision (attempted move blocked) and proximity (adjacent cell occupied).
- For avoidance, examine candidate moves (neighbors) and choose one that increases distance to the obstacle.
- Keep a small list of fallback moves to escape corners.

<details>
<summary>detail-summary</summary>

```python
# choose neighbor that increases clearance
def choose_clear_neighbor(position, neighbors, is_free):
    best = None
    best_clear = None
    i = 0
    while i < len(neighbors):
        nb = neighbors[i]
        if not is_free(nb):
            i = i + 1
            continue
        # measure clearance as number of free adjacent cells (simple heuristic)
        clear = 0
        j = 0
        while j < len(neighbors):
            adj = neighbors[j]
            if is_free(adj):
                clear = clear + 1
            j = j + 1
        if best_clear is None or clear > best_clear:
            best_clear = clear
            best = nb
        i = i + 1
    return best
```

</details>

</details>



## 6) Drive along the wall at speed 1 and find the goal gradually
Goal: Use wall-following (keep one side touching the wall) moving one cell per turn to slowly explore and eventually find the goal.

<details>
<summary>Hints</summary>

- Use a simple wall-following rule: keep right (or left) hand on the wall.
- At each step, try the preferred forward direction; if blocked, turn appropriately to follow.
- Keep speed constant (1 cell per tick).
- Record visited positions to avoid loops.

<details>
<summary>detail-summary</summary>

```python
# right-hand wall follower (grid, cardinal moves)
# orientation is one of up/down/left/right stored as (dx,dy)

def turn_right(orient):
    # orient: (dx,dy)
    if orient == (0, -1):
        return (1, 0)
    if orient == (1, 0):
        return (0, 1)
    if orient == (0, 1):
        return (-1, 0)
    if orient == (-1, 0):
        return (0, -1)
    return orient

# then attempt moves in this priority: right, straight, left, back
```

</details>

</details>



## 7) Nearest-vertex strategy with visited blocking
Goal: Maintain a vertex list (waypoints). Compute Euclidean distance to the goal and always pick the vertex that is nearest to the goal from the set of available vertices. Keep a list of visited vertices and avoid revisiting.

<details>
<summary>Hints</summary>

- Use the `euclidean` helper from earlier.
- Keep `visited_vertices` as a list; before selecting a vertex skip those already in it.
- After reaching a vertex, append to `visited_vertices`.
- If all vertices visited, fallback to a random or exploration strategy.

<details>
<summary>detail-summary</summary>

```python
# pick next vertex from list that is closest to goal and not yet visited

def pick_vertex_by_goal(vertices, goal, visited):
    best_idx = None
    best_dist = None
    i = 0
    while i < len(vertices):
        v = vertices[i]
        skip = False
        j = 0
        while j < len(visited):
            if v == visited[j]:
                skip = True
                break
            j = j + 1
        if skip:
            i = i + 1
            continue
        d = euclidean(v, goal)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_idx = i
        i = i + 1
    return best_idx
```

</details>

</details>



## 8) Additional ideas and optional challenges
- Build a memory of explored corridors and try not to re-enter them.
- Use a breadcrumb map with integer visit counts and prefer lower-count cells.
- Combine strategies: wall-following until a waypoint is visible, then switch to nearest-vertex.
- Implement a small finite-state machine for modes: Explore, FollowWall, GoToVertex, EscapeStuck.

<details>
<summary>Hints</summary>

- Keep each behavior as a small function; a top-level `PickMove` should dispatch based on mode.
- Make state explicit: `mode`, `orientation`, `current_vertex`, `visited_vertices`, `last_collision`.

<details>
<summary>detail-summary</summary>

```python
# sketch of a dispatcher

def pick_move(state):
    mode = state['mode']
    if mode == 'FollowWall':
        return pick_move_followwall(state)
    if mode == 'GoToVertex':
        return pick_move_gotovtx(state)
    # fallback
    return pick_move_explore(state)
```

</details>

</details>



**Final notes**
- These exercises are intentionally partial and didactic; they are meant to inspire incremental development.
- Insert your helpers into your control loop and keep the interfaces small.



File created as a starting point for exercises and hints.
