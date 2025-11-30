from django.test import TestCase
from .scoring import score_tasks, detect_cycles

class ScoringTests(TestCase):
    def test_overdue_task_has_high_urgency(self):
        tasks = [{"id":"t1","title":"old","due_date":"2000-01-01","estimated_hours":1,"importance":5,"dependencies":[]}]
        scored = score_tasks(tasks)
        self.assertEqual(scored[0]['_score'] > 0, True)

    def test_cycle_detection(self):
        tasks = [{"id":"1","dependencies":["2"]},{"id":"2","dependencies":["1"]}]
        cycles = detect_cycles(tasks)
        self.assertTrue(len(cycles) >= 1)
