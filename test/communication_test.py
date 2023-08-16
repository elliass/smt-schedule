import unittest
from unittest.mock import MagicMock
import sys

sys.path.append("..")
from src.scheduling.communication import UWBCommunication, CAP, Ranging, Forwarding

class TestUWBCommunication(unittest.TestCase):

    def setUp(self):
        self.tag_node = MagicMock()
        self.anchor_node = MagicMock()

    def test_uwb_communication_properties(self):
        uwb_comm = UWBCommunication(self.tag_node, self.anchor_node, "uwb1")
        self.assertEqual(uwb_comm.get_node1(), self.tag_node)
        self.assertEqual(uwb_comm.get_node2(), self.anchor_node)
        self.assertEqual(uwb_comm.get_nodes(), (self.tag_node, self.anchor_node))
        self.assertFalse(uwb_comm.is_cap())
        self.assertFalse(uwb_comm.is_ranging())
        self.assertFalse(uwb_comm.is_forwarding())

        timeslot, channel = 1, 2
        uwb_comm.set_cell(timeslot, channel)
        self.assertEqual(uwb_comm.get_cell(), {'timeslot': timeslot, 'channel': channel})

    def test_cap_properties(self):
        cap = CAP(self.tag_node, self.anchor_node, "cap1")
        self.assertTrue(cap.is_cap())
        self.assertEqual(cap.get_tag(), self.tag_node)
        self.assertEqual(cap.get_anchor(), self.anchor_node)

    def test_ranging_properties(self):
        ranging = Ranging(self.tag_node, self.anchor_node, "ranging1")
        self.assertTrue(ranging.is_ranging())
        self.assertEqual(ranging.get_tag(), self.tag_node)
        self.assertEqual(ranging.get_anchor(), self.anchor_node)

    def test_forwarding_properties(self):
        forwarding = Forwarding(self.tag_node, self.anchor_node, "forwarding1")
        self.assertTrue(forwarding.is_forwarding())
        self.assertEqual(forwarding.get_child(), self.tag_node)
        self.assertEqual(forwarding.get_parent(), self.anchor_node)


if __name__ == "__main__":
    unittest.main()
