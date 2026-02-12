import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0

    def GetName(self) -> str:
        return "Random Driver"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or validity is None:
            return None
        if len(targets) == 0:
            return None
        best = None
        i = 0
        while i < len(targets):
            if i < len(validity) and validity[i]:
                t = targets[i]
                if best is None or t.x > best.x:
                    best = t
            i += 1
        return best
