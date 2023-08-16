import unittest
from unittest.mock import MagicMock
from z3 import And, Int
import sys

sys.path.append("..")
from src.scheduling.schedule import Schedule
from src.scheduling.communication import UWBCommunication


class TestScheduleClass(unittest.TestCase):

    def setUp(self):
        self.network = MagicMock()
        self.network.get_edges_str.return_value = ["e1", "e2", "e3"]
        self.network.get_edges.return_value = [UWBCommunication, UWBCommunication, UWBCommunication]
        self.schedule = Schedule(self.network, max_slots=5, max_channels=3)

    def test_get_assignments(self):
        assignments = self.schedule.get_assignments()
        expected_assignments = [
            (Int("e1_timeslot"), Int("e1_channel")),
            (Int("e2_timeslot"), Int("e2_channel")),
            (Int("e3_timeslot"), Int("e3_channel"))
        ]
        self.assertEqual(assignments, expected_assignments)

    def test_get_timeslots_channels(self):
        timeslots, channels = self.schedule.get_timeslots_channels()
        expected_timeslots = (
            Int("e1_timeslot"),
            Int("e2_timeslot"),
            Int("e3_timeslot")
        )
        expected_channels = (
            Int("e1_channel"),
            Int("e2_channel"),
            Int("e3_channel")
        )
        self.assertEqual(timeslots, expected_timeslots)
        self.assertEqual(channels, expected_channels)

    def test_add_constraint(self):
        constraint = And(Int(1) == Int(1))
        self.schedule.add_constraint([constraint])
        self.assertEqual(self.schedule.model_constraints, [constraint])

    def test_get_constraint(self):
        constraint1 = And(Int(1) == Int(1))
        constraint2 = And(Int(2) == Int(2))
        self.schedule.model_constraints = [[constraint1], [constraint2]]
        constraints = self.schedule.get_constraint()
        expected_constraints = [constraint1, constraint2]
        self.assertEqual(constraints, expected_constraints)

    def test_compute(self):
        # Mocking for the methods called within compute()
        self.schedule.get_dependency_constraints = MagicMock(return_value=[])
        self.schedule.get_conflict_constraints = MagicMock(return_value=[])
        self.schedule.get_default_constraints = MagicMock(return_value=[])
        self.schedule.get_timeslot_constraints = MagicMock(return_value=[])
        self.schedule.get_channel_constraints = MagicMock(return_value=[])
        
        constraints = self.schedule.compute()

        self.assertEqual(self.schedule.model_constraints, [
            [], [], [], [], []
        ])

    def test_get_default_constraints(self):
        constraints = self.schedule.get_default_constraints()
        self.assertEqual(len(constraints), 9)  # 3 for time_domain, 3 for frequency_domain, 3 for shared_constraint

    def test_to_int(self):
        self.assertEqual(self.schedule.to_int("e1"), 1)
        self.assertEqual(self.schedule.to_int("e2"), 2)
        self.assertEqual(self.schedule.to_int("e3"), 3)
        self.assertEqual(self.schedule.to_int(["e1", "e2", "e3"]), [1, 2, 3])
        

if __name__ == "__main__":
    unittest.main()
