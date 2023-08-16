import unittest
from unittest.mock import MagicMock
import sys

sys.path.append("..")
from src.scheduling.solver import UWBTSCHSolver


class TestUWBTSCHSolver(unittest.TestCase):

    def setUp(self):
        self.network = MagicMock()
        self.solver = UWBTSCHSolver(self.network, max_solutions=5, max_slots=10, max_channels=3, max_retries=3)

    def test_get_tsch_parameters(self):
        tsch_parameters = self.solver.get_tsch_parameters()
        expected_parameters = {
            'max_slots': 10,
            'max_channels': 3
        }
        self.assertEqual(tsch_parameters, expected_parameters)

    def test_get_solutions(self):
        self.assertEqual(self.solver.get_solutions(), [])

    def test_get_result_summary(self):
        self.assertEqual(self.solver.get_result_summary(), {})

    def test_solutions_to_string(self):
        self.solver.solutions = [
            MagicMock(get_timeslot_to_string=lambda: '1,2,3', get_channel_to_string=lambda: '1,1,2'),
            MagicMock(get_timeslot_to_string=lambda: '2,3,4', get_channel_to_string=lambda: '3,2,2')
        ]
        solutions_str = self.solver.solutions_to_string()
        expected_solutions_str = [
            {'timeslot': '1,2,3', 'channel': '1,1,2'},
            {'timeslot': '2,3,4', 'channel': '3,2,2'}
        ]
        self.assertEqual(solutions_str, expected_solutions_str)
        

if __name__ == "__main__":
    unittest.main()
