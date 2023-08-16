import unittest
import sys

sys.path.append("..")
from src.scheduling.node import Tag, Anchor
from src.scheduling.communication import Ranging, Forwarding
from src.scheduling.network import NetworkTopology

class TestNetworkTopology(unittest.TestCase):

    def setUp(self):
        self.network = NetworkTopology()

        self.tag1 = Tag("tag1")
        self.tag2 = Tag("tag2")
        self.anchor1 = Anchor("anchor1")
        self.anchor2 = Anchor("anchor2")

    def test_add_node(self):
        self.network.add_node(self.tag1)
        self.assertEqual(len(self.network.get_nodes()), 1)
        self.assertEqual(self.network.get_nodes()[0], self.tag1)

    def test_find_node_by_name(self):
        self.network.add_node(self.anchor1)
        found_node = self.network.find_node_by_name("anchor1")
        self.assertEqual(found_node, self.anchor1)

    def test_add_edges(self):
        self.network.add_node(self.tag1)
        self.network.add_node(self.anchor1)
        self.network.add_edges(self.tag1, self.anchor1)

        edges = self.network.get_edges()
        self.assertEqual(len(edges), 1)
        self.assertTrue(isinstance(edges[0], Ranging))
        self.assertEqual(edges[0].get_nodes(), (self.tag1, self.anchor1))

    def test_get_ranging(self):
        self.network.add_node(self.tag1)
        self.network.add_node(self.anchor1)
        self.network.add_edges(self.tag1, self.anchor1)

        ranging_edges = self.network.get_ranging()
        self.assertEqual(len(ranging_edges), 1)
        self.assertTrue(isinstance(ranging_edges[0], Ranging))

    def test_get_forwarding(self):
        self.network.add_node(self.anchor1)
        self.network.add_node(self.anchor2)
        self.network.add_edges(self.anchor1, self.anchor2)

        forwarding_edges = self.network.get_forwarding()
        self.assertEqual(len(forwarding_edges), 1)
        self.assertTrue(isinstance(forwarding_edges[0], Forwarding))


if __name__ == "__main__":
    unittest.main()
