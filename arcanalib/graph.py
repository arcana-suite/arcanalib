from collections.abc import Iterable


def invert(edge_list, new_label=None):
	"""
	Inverts the direction of edges in the given edge list.

	Args:
		edge_list (list): A list of edges to invert.
		new_label (str, optional): A new label for the inverted edges. Defaults to None.

	Returns:
		list: A list of inverted edges with updated labels.
	"""
	prefix = "inv_"
	return [{**edge,
	         'source': edge['target'],
	         'target': edge['source'],
	         'label': new_label if new_label else prefix + edge.get('label', 'edge'),
	         } for edge in edge_list]


def compose(edges1, edges2, new_label=None):
	"""
	Composes two lists of edges.

	Args:
		edges1 (list): The first list of edges.
		edges2 (list): The second list of edges.
		new_label (str, optional): A new label for the composed edges. Defaults to None.

	Returns:
		list: A list of composed edges.
	"""
	mapping = {
		edge['source']: {
			'target': edge['target'],
			'label': edge['label']
		} for edge in edges2
	}
	composed_edges = []
	for edge in edges1:
		if edge['target'] in mapping:
			composed_edges.append({
				'source': edge['source'],
				'target': mapping[edge['target']]['target'],
				'label': new_label if new_label else f"{edge['label']},{mapping[edge['target']]['label']}"
			})
	return composed_edges


def lift(edges1, edges2, new_label=None):
	"""
	Lifts relations by composing two lists of edges and their inverses.

	Args:
		edges1 (list): The first list of edges.
		edges2 (list): The second list of edges.
		new_label (str, optional): A new label for the lifted edges. Defaults to None.

	Returns:
		list: A list of lifted edges.
	"""
	return compose(compose(edges1, edges2), invert(edges1), new_label)


class Graph:
	"""
	A class to represent a graph with nodes and edges.

	Attributes:
		nodes (dict): A dictionary of nodes.
		edges (dict): A dictionary of edges categorized by labels.
	"""

	def __init__(self, graph_data):
		"""
		Initializes the Graph with nodes and edges from the provided data.

		Args:
			graph_data (dict): A dictionary containing graph data with nodes and edges.
		"""
		self.nodes = {node['data']['id']: node['data'] for node in graph_data['elements']['nodes']}
		self.edges = {}
		for edge in graph_data['elements']['edges']:
			if 'label' in edge['data']:
				label = edge['data']['label']
			else:
				label = ','.join(edge['data']['labels'])
				edge['data']['label'] = label

			if label not in self.edges:
				self.edges[label] = []
			self.edges[label].append(edge['data'])

	def invert_edges(self, edge_label, new_label=None):
		"""
		Inverts the edges with the specified label and saves them under a new label.

		Args:
			edge_label (str): The label of the edges to invert.
			new_label (str, optional): The label for the inverted edges. Defaults to None.
		"""
		if edge_label in self.edges:
			inverted = invert(self.edges[edge_label], new_label)
			new_label = new_label or f"inv_{edge_label}"
			self.edges[new_label] = inverted

	def compose_edges(self, edge_label1, edge_label2, new_label=None):
		"""
		Composes edges with the specified labels and saves them under a new label.

		Args:
			edge_label1 (str): The label of the first list of edges.
			edge_label2 (str): The label of the second list of edges.
			new_label (str, optional): The label for the composed edges. Defaults to None.
		"""
		if edge_label1 in self.edges and edge_label2 in self.edges:
			new_label = new_label or f"{edge_label1}_{edge_label2}"
			composed = compose(self.edges[edge_label1], self.edges[edge_label2], new_label)
			self.edges[new_label] = composed

	def lift_edges(self, edge_label1, edge_label2, new_label=None):
		"""
		Lifts relations by composing edges with the specified labels and their inverses, then saves them under a new label.

		Args:
			edge_label1 (str): The label of the first list of edges.
			edge_label2 (str): The label of the second list of edges.
			new_label (str, optional): The label for the lifted edges. Defaults to None.
		"""
		if edge_label1 in self.edges and edge_label2 in self.edges:
			lifted = lift(self.edges[edge_label1], self.edges[edge_label2], new_label)
			new_label = new_label or f"lifted_{edge_label1}_{edge_label2}"
			self.edges[new_label] = lifted

	def filter_nodes_by_labels(self, labels):
		"""
		Filters nodes by the specified labels.

		Args:
			labels (list, set): A list of labels to filter nodes by.

		Returns:
			dict: A dictionary of filtered nodes.
		"""
		filtered_nodes = {}
		for key, node in self.nodes.items():
			if any(label in labels for label in node['labels']):
				filtered_nodes[key] = node
		return filtered_nodes

	def get_all_node_labels(self):
		return {label for _, node in self.nodes.items() for label in node['labels']}

	def get_all_edge_labels(self):
		return set(self.edges.keys())

	def get_edges_with_node_labels(self, edge_label, node_label):
		"""
		Retrieves edges whose source and target nodes have the specified label.

		Args:
			edge_label (str): The label of the edges to retrieve.
			node_label (str): The label of the nodes to filter by.

		Returns:
			list: A list of edges that match the criteria.
		"""
		if edge_label in self.edges:
			return [edge for edge in self.edges[edge_label] if
			        node_label in self.nodes[edge['source']].get('labels', []) and node_label in self.nodes[
				        edge['target']].get('labels', [])]
		return []

	def get_edge_node_labels(self, edge):
		"""
		Gets the labels of the source and target nodes for a given edge.

		Args:
			edge (dict): The edge to retrieve node labels for.

		Returns:
			list: A list of tuples containing source and target node labels.
		"""
		src_labels = self.nodes.get(edge['source'], {}).get('labels', [])
		tgt_labels = self.nodes.get(edge['target'], {}).get('labels', [])
		return [(src_label, tgt_label) for src_label in src_labels for tgt_label in tgt_labels]

	def get_source_and_target_labels(self, edge_label):
		"""
		Gets the set of source and target labels for a given list of edges.

		Args:
			edge_list (list): The list of edges to retrieve labels for.

		Returns:
			set: A set of source and target labels.
		"""
		edge_node_labels = {label for edge in self.edges[edge_label] for label in self.get_edge_node_labels(edge)}
		return edge_node_labels

	def generate_ontology(self):
		"""
		Generates the ontology from the graph's edges and nodes.

		Returns:
			dict: A dictionary representing the ontology.
		"""
		return {label: self.get_source_and_target_labels(edges) for label, edges in self.edges.items()}

	def to_dict(self, *args, node_labels=None):
		included_edge_labels = list(args) if args else list(self.edges.keys())
		if node_labels == 'all':
			# include all nodes
			included_node_labels = self.get_all_node_labels()
		else:
			# include nodes that are involved with the included edges
			included_node_labels = {node_label for edge_label in included_edge_labels for node_label in
			                        self.get_source_and_target_labels(edge_label)}
			# additional nodes as specified in the argument
			if isinstance(node_labels, str):
				included_node_labels.add(node_labels)
			elif isinstance(node_labels, Iterable):
				included_node_labels += node_labels

		included_nodes = self.filter_nodes_by_labels(included_node_labels)
		included_edges = {label: edge_list for label, edge_list in self.edges.items() if label in included_edge_labels}
		return {
			"elements": {
				"nodes": [{"data": node} for node in list(included_nodes.values())],
				"edges": [{"data": edge} for edge in sum(list(included_edges.values()), [])]
			}
		}
