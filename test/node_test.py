import unittest
from unittest.mock import MagicMock
import sys

sys.path.append("..")
from src.scheduling.node import Tag, Anchor

class TestNodeClasses(unittest.TestCase):

    def setUp(self):
        self.tag_name = "tag1"
        self.anchor_name = "anchor1"
        self.tag = Tag(self.tag_name)
        self.anchor = Anchor(self.anchor_name)

    def test_node_properties(self):
        self.assertEqual(str(self.tag), self.tag_name)
        self.assertEqual(str(self.anchor), self.anchor_name)
        self.assertFalse(self.tag.is_anchor())
        self.assertFalse(self.anchor.is_tag())
        self.assertIsNone(self.tag.get_parent())
        self.assertIsNone(self.anchor.get_parent())
        self.assertEqual(self.tag.get_queue(), [])
        self.assertEqual(self.anchor.get_queue(), [])

        edge = MagicMock()
        self.tag.set_communication(edge)
        self.assertEqual(self.tag.get_communication(), [edge])
        self.assertEqual(self.anchor.get_communication(), [])

    def test_tag_communication(self):
        other = MagicMock()
        self.assertEqual(self.tag.communicate(other), (self.tag_name, other.name))

    def test_anchor_communication(self):
        other = MagicMock()
        self.assertEqual(self.anchor.communicate(other), (self.anchor_name, other.name))


if __name__ == "__main__":
    unittest.main()
