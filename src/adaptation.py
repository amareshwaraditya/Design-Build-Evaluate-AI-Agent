class FeedbackPolicy:
    def __init__(self):
        self.ratings = []
    def add(self, rating: int):
        self.ratings.append(max(1, min(5, rating)))
    def instructions(self) -> dict:
        average = sum(self.ratings[-10:]) / len(self.ratings[-10:]) if self.ratings else 3
        return {"tone": "empathetic" if average < 3 else "professional", "verbosity": "detailed" if average < 3 else "normal", "average": round(average, 2)}
