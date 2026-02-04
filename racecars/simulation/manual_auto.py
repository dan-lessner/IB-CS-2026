from simulation.script_api import AutoAuto


class MouseAuto(AutoAuto):
    def __init__(self):
        self._queued_target = None

    def SetTarget(self, target):
        self._queued_target = target

    def PickMove(self, world, allowed_moves):
        if self._queued_target is None:
            return None
        target = self._queued_target
        self._queued_target = None
        return target
