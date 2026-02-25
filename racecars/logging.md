# Logging Guide

The project uses Python's standard `logging` module with centralized setup in `simulation/logging_utils.py`.

## Default behavior

- Logs go to console by default.
- Default level is `INFO`.

## CLI options

- `--supress-log`
  - Disables all logging output.
  - This overrides console and file logging.
- `--log-path PATH`
  - Also writes logs to the given file path.
  - Parent directories are created automatically if needed.
- `--log-level LEVEL`
  - Sets minimum severity that is emitted.
  - Accepted values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Examples:

```powershell
python main.py --log-level DEBUG
python main.py --log-path logs\\race.log --log-level WARNING
python main.py --supress-log
```

## Car-specific loggers

Each car receives a dedicated logger based on its name/id:

- Logger name pattern: `racecars.car.<name>.id_<n>`
- Script drivers can use `self.logger` directly once assigned by the engine.
- The current car object passed to `PickMove(...)` also exposes `auto.logger`.

Example:

```python
def PickMove(self, auto, world, targets, validity):
    self.logger.debug("Choosing move for %s at (%s, %s)", auto.name, auto.pos.x, auto.pos.y)
    return super().PickMove(auto, world, targets, validity)
```

## Log levels

- `DEBUG`: detailed diagnostics for development.
- `INFO`: normal runtime events.
- `WARNING`: recoverable problems, fallback paths, unexpected `None` values.
- `ERROR`: operation failed.
- `CRITICAL`: serious failure.

## Further reading

- Python logging HOWTO: https://docs.python.org/3/howto/logging.html
