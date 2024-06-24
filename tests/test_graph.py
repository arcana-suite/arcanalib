import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from arcanalib import Graph, invert, compose, lift

class TestGraphFunctions(unittest.TestCase):

    def setUp(self):
        self.graph_data = {
            "elements": {
                "nodes": [
                    {"data": {"id": "A", "labels": ["class"]}},
                    {"data": {"id": "B", "labels": ["class"]}},
                    {"data": {"id": "A1", "labels": ["method"]}},
                    {"data": {"id": "B1", "labels": ["method"]}},
                    {"data": {"id": "C", "labels": ["class"]}},
                    {"data": {"id": "C1", "labels": ["method"]}},
                    {"data": {"id": "C2", "labels": ["method"]}}
                ],
                "edges": [
                    {"data": {"source": "A", "target": "A1", "label": "contains"}},
                    {"data": {"source": "B", "target": "B1", "label": "contains"}},
                    {"data": {"source": "A1", "target": "B1", "label": "invokes"}},
                    {"data": {"source": "C", "target": "C1", "label": "contains"}},
                    {"data": {"source": "C", "target": "C2", "label": "contains"}},
                    {"data": {"source": "C1", "target": "C2", "label": "invokes"}}
                ]
            }
        }
        self.graph = Graph(self.graph_data)

    def test_invert(self):
        edges = [{"source": "A", "target": "A1", "label": "contains"},
                 {"source": "B", "target": "B1", "label": "contains"},
                 {"source": "A1", "target": "B1", "label": "invokes"}]
        inverted = invert(edges)
        expected = [{"source": "A1", "target": "A", "label": "inv_contains"},
                    {"source": "B1", "target": "B", "label": "inv_contains"},
                    {"source": "B1", "target": "A1", "label": "inv_invokes"}]
        self.assertEqual(inverted, expected)

    def test_compose_contains_invokes(self):
        edges1 = [{"source": "A", "target": "A1", "label": "contains"}]
        edges2 = [{"source": "A1", "target": "B1", "label": "invokes"}]
        composed = compose(edges1, edges2, "contains_invokes")
        expected = [{"source": "A", "target": "B1", "label": "contains_invokes"}]
        self.assertEqual(composed, expected)

    def test_lift_contains_invokes(self):
        edges1 = [{"source": "A", "target": "A1", "label": "contains"},
                  {"source": "B", "target": "B1", "label": "contains"}]
        edges2 = [{"source": "A1", "target": "B1", "label": "invokes"}]
        lifted = lift(edges1, edges2, "calls")
        expected = [{"source": "A", "target": "B", "label": "calls"}]
        self.assertEqual(lifted, expected)

    def test_graph_invert_edges(self):
        self.graph.invert_edges("contains", "inv_contains")
        inverted_edges = self.graph.edges["inv_contains"]
        expected = [{"source": "A1", "target": "A", "label": "inv_contains"},
                    {"source": "B1", "target": "B", "label": "inv_contains"},
                    {"source": "C1", "target": "C", "label": "inv_contains"},
                    {"source": "C2", "target": "C", "label": "inv_contains"}]
        self.assertEqual(inverted_edges, expected)

    def test_graph_compose_contains_invokes(self):
        self.graph.compose_edges("contains", "invokes", "contains_invokes")
        composed_edges = self.graph.edges["contains_invokes"]
        expected = [{"source": "A", "target": "B1", "label": "contains_invokes"},
                    {"source": "C", "target": "C2", "label": "contains_invokes"}]
        self.assertEqual(composed_edges, expected)

    def test_graph_lift_edges(self):
        self.graph.lift_edges("contains", "invokes", "calls")
        lifted_edges = self.graph.edges["calls"]
        expected = [{"source": "A", "target": "B", "label": "calls"},
                    {"source": "C", "target": "C", "label": "calls"}]
        self.assertEqual(lifted_edges, expected)

    def test_filter_nodes_by_labels(self):
        filtered_nodes = self.graph.filter_nodes_by_labels(["class"])
        expected = {"A": {"id": "A", "labels": ["class"]},
                    "B": {"id": "B", "labels": ["class"]},
                    "C": {"id": "C", "labels": ["class"]}}
        self.assertEqual(filtered_nodes, expected)

    def test_get_edges_with_node_labels(self):
        edges_with_labels = self.graph.get_edges_with_node_labels("invokes", "method")
        expected = [{'source': 'A1', 'target': 'B1', 'label': 'invokes'},
                    {'source': 'C1', 'target': 'C2', 'label': 'invokes'}]
        self.assertEqual(edges_with_labels, expected)

    def test_generate_ontology(self):
        ontology = self.graph.generate_ontology()
        expected = {
            "contains": {("class", "method")},
            "invokes": {("method", "method")}
        }
        self.assertEqual(ontology, expected)

if __name__ == '__main__':
    unittest.main()
