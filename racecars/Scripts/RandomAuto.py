import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Random Driver"

    def PickMove(self, auto, world, targets, validity):
        # Pick a random valid target if validity list is provided.
        valid_indices = []
        for i in range(min(len(validity), len(targets))):
            if validity[i]:
                valid_indices.append(i)

        if len(valid_indices) == 0:
            index = random.randint(0, len(targets) - 1)
            return targets[index]

        choice_idx = random.randint(0, len(valid_indices) - 1)
        return targets[valid_indices[choice_idx]]
