import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Random Driver"

    def PickMove(self, auto, world, targets, validity):
        # Pick a random valid target if validity list is provided.
        if targets is None:
            return None
        if validity is None:
            if len(targets) == 0:
                return None
            index = random.randint(0, len(targets) - 1)
            return targets[index]

        valid_indices = []
        i = 0
        while i < len(validity):
            if validity[i]:
                valid_indices.append(i)
            i += 1

        if len(valid_indices) == 0:
            return None

        choice_idx = random.randint(0, len(valid_indices) - 1)
        return targets[valid_indices[choice_idx]]
