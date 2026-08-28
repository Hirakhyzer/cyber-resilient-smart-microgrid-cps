from .base import BaseAgent
class SecurityAgent(BaseAgent):
    def __init__(self): super().__init__("security")
    def classify(self, anomaly_score: float) -> str:
        return "alarm" if anomaly_score >= 1.0 else "normal"
