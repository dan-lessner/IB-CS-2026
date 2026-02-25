import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self, track) -> None:
        super().__init__()
        self.track = track
        self.logger.info("Teacher script initialized.")
        self.logger.info("The track is this big: %d, %d", self.track.width, self.track.height)

    def GetName(self) -> str:
        return "Driver with a compass"

    def PickMove(self, auto, world, targets, validity):
        if len(validity) == 0 or sum(validity) == 0:
            self.logger.warning("None of the targets is valid, choosing random.")
            return targets[random.randint(0, len(targets) - 1)]
        
        best_x = None
        for i in range(0, len(targets)):
            if validity[i] and (best_x is None or targets[i].x > best_x):
                    best_x = targets[i].x
        
        best_targets = []
        for i in range(len(targets)):
            if validity[i] and targets[i].x == best_x:
                best_targets.append(targets[i])
        if len(best_targets) == 0:
            self.logger.error("No best targets found:", targets,validity)

        return best_targets[random.randint(0, len(best_targets) - 1)]
