import articles
import kg_generator
from graphviz import Digraph
import networkx as nx

def generate_knowledge_graph_output_files(name, knowledge_graph):
    # generate SVG, DOT and GML files
    # Create a directed graph
    graph = Digraph()

    # Add nodes and edges to the graph
    for link in knowledge_graph.links:
        source = link.source
        target = link.target
        label = link.label
        graph.edge(source, target, label=label)

    # Render the graph to SVG format
    graph.render(name, format='svg', cleanup=True)
    graph.render(name, format='dot', cleanup=True)

    # Generate GML
    # We concatenate parallel edges because Gephi doesn't support them
    G = nx.nx_pydot.read_dot(f'{name}.dot')
    G_concatenated = nx.MultiDiGraph()
    # Concatenate edge labels for edges with the same source and target nodes
    for u, v, data in G.edges(data=True):
        key = (u, v)
        if key not in G_concatenated.edges:
            G_concatenated.add_edge(u, v, label=data['label'])
        else:
            # Concatenate the labels if the edge already exists
            G_concatenated[u][v][0]['label'] += '\n' + data['label']

    # Write the concatenated graph to a GML file
    nx.write_gml(G_concatenated, f'{name}.gml')

arxiv_client = articles.ArxivClient()

query = "(ti:mamba) AND " + \
        "(cat:cs.AI OR cat:cs.CC OR cat:cs.CL OR cat:cs.CR OR " + \
        "cat:cs.FL OR cat:cs.LG OR cat:cs.MA OR cat:cs.NE OR " + \
        "cat:cs.PL OR cat:cs.SI)"

articles = arxiv_client.get_articles_with_query(query=query, max_results=200)
generator = kg_generator.KGGenerator()
result = generator.get_knowledge_graph(articles=articles)
knowledge_graph = result["merged_knowledge_graph"]

print(knowledge_graph)
generate_knowledge_graph_output_files('mamba', knowledge_graph)

"""
query = "(ti:hallucination) AND " + \
        "(cat:cs.AI OR cat:cs.CC OR cat:cs.CL OR cat:cs.CR OR " + \
        "cat:cs.FL OR cat:cs.LG OR cat:cs.MA OR cat:cs.NE OR " + \
        "cat:cs.PL OR cat:cs.SI)"

ids_dict = {
    2403: range(1, 1000),
}

articles = arxiv_client.get_articles_with_query_and_ids(query=query, ids_dict=ids_dict)

generator = kg_generator.KGGenerator()
result = generator.get_knowledge_graph(article=articles[0])
knowledge_graph = result["knowledge_graph"]

print(knowledge_graph)
generate_graphviz_knowledge_graph('hallucination', knowledge_graph)

ids_dict = {
    2401: range(10, 20),
    2402: range(40, 50),
    2403: range(100, 150),
}

articles = arxiv_client.get_articles_with_id_list(ids_dict=ids_dict)

generator = kg_generator.KGGenerator()
result = generator.get_knowledge_graph(article=articles[0])
knowledge_graph = result["knowledge_graph"]

print(knowledge_graph)
generate_graphviz_knowledge_graph('random', knowledge_graph)

"""

# TODO:
# improve SVG graph layout
# use vector db to unify nodes? : if so, cache the merged graph using
# hash (from paper ids sorted) as identifier
# fix parallel edges concatenation
# generate graphs output files for individual articles too: use a folder
# to store these files in an organized way
# add typing and doc strings
# add tests
