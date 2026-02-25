"""Optional timing helper for measuring driver decision speed."""

class PerformanceTracker:
    def __init__(self, car_count: int, log_path: str):
        self.log_path = log_path
        self.enabled = True
        self.reported = False
        self.total_seconds = [0.0] * car_count
        self.call_counts = [0] * car_count

    def record(self, car_id: int, seconds: float):
        if not self.enabled:
            return
        if car_id < 0 or car_id >= len(self.total_seconds):
            return
        self.total_seconds[car_id] = self.total_seconds[car_id] + seconds
        self.call_counts[car_id] = self.call_counts[car_id] + 1

    def report_if_ready(self, cars):
        # Print/write once at the end of the game.
        if self.reported:
            return
        self.reported = True
        self._print_summary(cars)
        self._write_log(cars)

    def _print_summary(self, cars):
        print("Performance summary:")
        for index, car in enumerate(cars):
            total = self.total_seconds[index]
            count = self.call_counts[index]
            avg = 0.0
            if count > 0:
                avg = total / count
            total_text = str(round(total, 6))
            avg_text = str(round(avg, 6))
            print("Car " + str(car.id + 1) + " " + car.name + ": calls=" + str(count) + " total_s=" + total_text + " avg_s=" + avg_text)

    def _write_log(self, cars):
        file = open(self.log_path, "w", encoding="utf-8")
        file.write("car_id,car_name,calls,total_seconds,avg_seconds\n")
        for index, car in enumerate(cars):
            total = self.total_seconds[index]
            count = self.call_counts[index]
            avg = 0.0
            if count > 0:
                avg = total / count
            line = str(car.id + 1) + "," + _escape_csv(car.name) + "," + str(count) + "," + str(total) + "," + str(avg) + "\n"
            file.write(line)
        file.close()


def _escape_csv(text: str) -> str:
    if text is None:
        return ""
    needs_quotes = any(ch == "," or ch == "\"" for ch in text)

    if not needs_quotes:
        return text

    return "\"" + text.replace("\"", "\"\"") + "\""
