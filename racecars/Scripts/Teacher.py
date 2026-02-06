import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0

    def GetName(self) -> str:
        return "Random Driver"

    def PickMove(self, auto, world, allowed_moves):
        
        if allowed_moves is None:
            return None
        if len(allowed_moves) == 0:
            return None
        x = 0
        for move in allowed_moves:
            if move.x > x:
                x = move.x
                solution = move

        return solution
