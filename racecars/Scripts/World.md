# World object in controller scripts

The `world` argument passed to `Auto.PickMove(self, world, allowed_moves)` is a
`WorldState` snapshot created in `simulation/script_api.py`. It is read-only;
changing it will not affect the game.

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
- `car.vel`: `Vector2i` velocity with `vx` and `vy`.

**Access examples**
```python
from simulation.script_api import AutoAuto

class Auto(AutoAuto):
    def PickMove(self, world, allowed_moves):
        # Check a road cell.
        if world.road[10][5]:
            pass

        # Read positions of all cars.
        for car in world.cars:
            x = car.pos.x
            y = car.pos.y
            speed = abs(car.vel.vx) + abs(car.vel.vy)

        # Find your car by name (if you return a name in GetName()).
        me = None
        for car in world.cars:
            if car.name == self.GetName():
                me = car
                break

        # Pick one of the provided targets.
        if allowed_moves:
            return allowed_moves[0]
        return None
```
