class GameParams:
    def __init__(
        self,
        width: int = 60,
        height: int = 40,
        players: int = 2,
        track_width_mean: int = 6,
        track_width_var: int = 2,
        turn_sharpness: int = 50,
        turn_density: int = 50,
        seed: int = None,
        measure_performance: bool = False
    ):
        self.width = width
        self.height = height
        self.players = players
        self.track_width_mean = track_width_mean
        self.track_width_var = track_width_var
        self.turn_sharpness = turn_sharpness
        self.turn_density = turn_density
        self.seed = seed
        self.measure_performance = measure_performance

    def clone(self):
        return GameParams(
            width=self.width,
            height=self.height,
            players=self.players,
            track_width_mean=self.track_width_mean,
            track_width_var=self.track_width_var,
            turn_sharpness=self.turn_sharpness,
            turn_density=self.turn_density,
            seed=self.seed,
            measure_performance=self.measure_performance
        )
