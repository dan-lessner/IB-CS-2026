from simulation.script_api import AutoAuto, Vertex

# tohle je celý zbytečný, já můžu přirážet ke zdi nebo nenápadně moc zrychlovat, ale musím pořád po validní trase, nemůžu tunelovat zdi :-()

class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.track = track
        self.turn_number = 0    #TODO - no need for this, use the world object instead

    def GetName(self) -> str:
        return "Chell"

    def PickMove(self, auto, world, targets, validity):

        if self.turn_number == 1:
            return Vertex(auto.pos.x + 1, auto.pos.y)

        if self.turn_number == 2:
            final_target = world.finish_vertices[len(world.finish_vertices)/2]
            return Vertex(final_target.x-1, final_target.y)
        
        if self.turn_number == 3:
            return Vertex(auto.pos.x + 1, auto.pos.y)
