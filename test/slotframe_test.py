import unittest
from unittest.mock import MagicMock, patch
# from prettytable import PrettyTable, ALL
from z3 import And, Int

import sys

sys.path.append("..")
from src.scheduling.slotframe import Slotframe
from src.scheduling.exception import SharedException, DependencyException, ConcurrencyException

class TestSlotframe(unittest.TestCase):

    def setUp(self):
        self.slotframe = Slotframe()
        self.edges = ['edge1', 'edge2']
        self.communications = [('node1', 'node2'), ('node2', 'node1')]
        self.edge1 = MagicMock()
        self.edge1.get_node1.return_value = MagicMock(is_tag=lambda: True, is_anchor=lambda: False)
        self.edge1.get_node2.return_value = MagicMock(is_tag=lambda: False, is_anchor=lambda: True)
        self.edge2 = MagicMock()
        self.edge2.get_node1.return_value = MagicMock(is_tag=lambda: False, is_anchor=lambda: True)
        self.edge2.get_node2.return_value = MagicMock(is_tag=lambda: True, is_anchor=lambda: False)

    def test_set_timeslot(self):
        self.slotframe.set_timeslot([1, 2, 3])
        self.assertEqual(self.slotframe.timeslot_assignment, [1, 2, 3])

    def test_get_timeslot(self):
        self.slotframe.timeslot_assignment = [1, 2, 3]
        self.assertEqual(self.slotframe.get_timeslot(), [1, 2, 3])

    # def test_get_timeslot_to_string(self):
    #     self.slotframe.timeslot_assignment = [1, 2, 3]
    #     self.assertEqual(self.slotframe.get_timeslot_to_string(), ['1', '2', '3'])

    def test_set_channel(self):
        self.slotframe.set_channel([0, 1, 2])
        self.assertEqual(self.slotframe.channel_assignment, [0, 1, 2])

    def test_get_channel(self):
        self.slotframe.channel_assignment = [0, 1, 2]
        self.assertEqual(self.slotframe.get_channel(), [0, 1, 2])

    # @patch.object(PrettyTable, 'add_row')
    # def test_show_as_table(self, mock_add_row):
    #     self.slotframe.get_solution = MagicMock(return_value=[('edge1', 1, 0), ('edge2', 2, 1)])
    #     table = self.slotframe.show_as_table(self.edges, self.communications)
    #     self.assertIsInstance(table, PrettyTable)
    #     self.assertTrue(mock_add_row.called)

    def test_display_solution(self):
        self.slotframe.set_timeslot([1, 2])
        self.slotframe.set_channel([0, 1])
        self.slotframe.display_solution(self.edges)


if __name__ == "__main__":
    unittest.main()
