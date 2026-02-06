import random
from simulation.script_api import AutoAuto
from simulation.game_state import Vertex


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Random Driver"

    def PickMove(self, auto, world, allowed_moves) -> Vertex:
        if allowed_moves is None:
            return None
        if len(allowed_moves) == 0:
            return None

        index = random.randint(0, len(allowed_moves) - 1)
        return allowed_moves[index].target
