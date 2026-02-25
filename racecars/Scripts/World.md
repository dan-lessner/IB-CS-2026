# World and auto objects in controller scripts

The `world` argument passed to `Auto.PickMove(self, auto, world, allowed_moves)`
is a `WorldState` snapshot created in `simulation/script_api.py`. It is
read-only; changing it will not affect the game.

The `auto` argument is the `CarInfo` object for the car whose script is being
called. It is the same type and structure as the objects inside
`world.cars`. Treat it as read-only.

**WorldState fields**
- `world.road`: 2D list of `bool`. Access with `world.road[x][y]` to check if a
  road cell exists. Valid indices are `0 <= x < track_width` and
  `0 <= y < track_height`.
- `world.start_vertices`: list of `Vertex` objects for the start line.
- `world.finish_vertices`: list of `Vertex` objects for the finish line. These
  can include `x == track_width`, so do not index them into `world.road`.
- `world.cars`: list of `CarInfo` objects for every car on the track.

**CarInfo fields**
- `car.id`: integer id.
- `car.name`: car name (from `GetName()` if provided, otherwise the script name).
- `car.pos`: `Vertex` position with `x` and `y`.
- `car.vel`: `Vector2i` velocity with `x` and `y`.

**Auto parameter (your car)**
- `auto.id`
- `auto.name`
- `auto.pos.x`, `auto.pos.y`
- `auto.vel.x`, `auto.vel.y`
- `auto.logger` (car-specific logger)

**Logging in scripts**
- The engine assigns a logger to each script instance as `self.logger`.
- Use normal logging calls: `self.logger.debug(...)`, `self.logger.info(...)`, `self.logger.warning(...)`, etc.
- CLI controls from `main.py`:
  - `--supress-log`
  - `--log-path PATH`
  - `--log-level LEVEL`

**Access examples**
```python
from simulation.script_api import AutoAuto

class Auto(AutoAuto):
    def PickMove(self, auto, world, targets, validity):
        self.logger.debug("Turn for %s at (%s, %s)", auto.name, auto.pos.x, auto.pos.y)

        # Check a road cell.
        if world.road[10][5]:
            pass

        # Read positions of all cars.
        for car in world.cars:
            x = car.pos.x
            y = car.pos.y
            speed = abs(car.vel.x) + abs(car.vel.y)

        # Your car is provided as `auto`.
        my_x = auto.pos.x
        my_y = auto.pos.y

        # Pick one of the provided targets.
        if allowed_moves:
            return allowed_moves[0]
        return None
```

**Create and run your own primitive script (step by step)**
1. Copy `Scripts\RandomAuto.py` to a new file, for example `Scripts\MyAuto.py`.
2. Open `Scripts\MyAuto.py`.
3. Keep the class name as `Auto` and update the name:
   `def GetName(self): return "My Auto"`
4. Replace `PickMove` with a basic rule like: "move left if it doesn't collide
   with another car, otherwise take the first allowed move."
5. Save the file.
6. Open a terminal and go to the game folder:
   `cd personal-playground\\racecars`
7. Run the game:
   `python main.py`
8. In the controller selection dialog, choose `MyAuto` for a player.
9. Start the game.

**Primitive example (move left if it doesn't collide)**
```python
from simulation.script_api import AutoAuto

class Auto(AutoAuto):
    def GetName(self) -> str:
        return "My Auto"

    def PickMove(self, auto, world, targets, validity):
        if not allowed_moves:
            return None

        target_left = None
        for target in allowed_moves:
            if target.x < auto.pos.x:
                target_left = target
                break

        if target_left is not None and not _target_occupied(world, auto, target_left):
            return target_left

        return allowed_moves[0]

def _target_occupied(world, auto, target):
    for car in world.cars:
        if car.id != auto.id and car.pos.x == target.x and car.pos.y == target.y:
            return True
    return False
```
