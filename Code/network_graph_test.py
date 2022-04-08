# https://plotly.com/python/network-graphs/
# https://stackabuse.com/graphs-in-python-breadth-first-search-bfs-algorithm/
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
nodes = ["Health_Worker", "Medical_Staff", "Nursing_Staff", "Person", "MedicalEntity", "Medical_Records"]
# from A to B
edges = [
    ("Health_Worker", "Medical_Staff"),
    ("Health_Worker", "Nursing_Staff"),
    ("Person", "Health_Worker"),
    ("MedicalEntity", "Medical_Records")
]

G.add_nodes_from(nodes)
G.add_edges_from(edges)
nx.topological_sort(G)

print("the edges are:")
print(list(nx.topological_sort((nx.line_graph(G)))))

roots = []
for component in nx.weakly_connected_components(G):
    G_sub = G.subgraph(component)
    roots.extend([n for n,d in G_sub.in_degree() if d==0])
print("The roots are:")
print(roots)

# depth_limit=2
# se ricerca al contrario: reverse = True
print("the queue with BFS")
for root in roots:
    print(list(nx.bfs_edges(G, source=root)))


# edge_labels = nx.get_edge_attributes(G,'label')
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos=pos)
nx.draw_networkx_labels(G, pos=pos)
nx.draw_networkx_edges(G, pos=pos)
# nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
plt.show()
