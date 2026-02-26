"""Container for game configuration values shared across setup and runtime."""

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
        framerate: int = 30,
        seed: int = None,
        measure_performance: bool = False,
        car_collision_penalty_enabled: bool = True,
        shuffle_turn_order_each_round: bool = False,
        strict_target_check: bool = False,
        penalty_mode: str = "fixed",
        penalty_value: int = 2
    ):
        self.width = width
        self.height = height
        self.players = players
        self.track_width_mean = track_width_mean
        self.track_width_var = track_width_var
        self.turn_sharpness = turn_sharpness
        self.turn_density = turn_density
        self.framerate = framerate
        self.seed = seed
        self.measure_performance = measure_performance
        self.car_collision_penalty_enabled = car_collision_penalty_enabled
        self.shuffle_turn_order_each_round = shuffle_turn_order_each_round
        self.strict_target_check = strict_target_check
        self.penalty_mode = penalty_mode
        self.penalty_value = penalty_value

    def clone(self):
        # Defensive copy so dialogs/CLI parsing can edit params without side effects.
        return GameParams(
            width=self.width,
            height=self.height,
            players=self.players,
            track_width_mean=self.track_width_mean,
            track_width_var=self.track_width_var,
            turn_sharpness=self.turn_sharpness,
            turn_density=self.turn_density,
            framerate=self.framerate,
            seed=self.seed,
            measure_performance=self.measure_performance,
            car_collision_penalty_enabled=self.car_collision_penalty_enabled,
            shuffle_turn_order_each_round=self.shuffle_turn_order_each_round,
            strict_target_check=self.strict_target_check,
            penalty_mode=self.penalty_mode,
            penalty_value=self.penalty_value
        )
