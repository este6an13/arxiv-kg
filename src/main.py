import articles
import kg_generator

arxiv_client = articles.ArxivClient()

query = "(ti:mamba) AND " + \
        "(cat:cs.AI OR cat:cs.CC OR cat:cs.CL OR cat:cs.CR OR " + \
        "cat:cs.FL OR cat:cs.LG OR cat:cs.MA OR cat:cs.NE OR " + \
        "cat:cs.PL OR cat:cs.SI)"

articles = arxiv_client.get_articles_with_query(query=query, max_results=200)

generator = kg_generator.KGGenerator()
knowledge_graph = generator.get_knowledge_graph(article=articles[0])

print(knowledge_graph)

query = "(ti:hallucination) AND " + \
        "(cat:cs.AI OR cat:cs.CC OR cat:cs.CL OR cat:cs.CR OR " + \
        "cat:cs.FL OR cat:cs.LG OR cat:cs.MA OR cat:cs.NE OR " + \
        "cat:cs.PL OR cat:cs.SI)"

ids_dict = {
    2403: range(1, 1000),
}

articles = arxiv_client.get_articles_with_query_and_ids(query=query, ids_dict=ids_dict)

generator = kg_generator.KGGenerator()
knowledge_graph = generator.get_knowledge_graph(article=articles[0])

print(knowledge_graph)

ids_dict = {
    2401: range(10, 20),
    2402: range(40, 50),
    2403: range(100, 150),
}

articles = arxiv_client.get_articles_with_id_list(ids_dict=ids_dict)

generator = kg_generator.KGGenerator()
knowledge_graph = generator.get_knowledge_graph(article=articles[0])

print(knowledge_graph)

# TODO:
# implement visualizer?: networkx, igraph or return GML
# how to unify nodes that mean the same?
# add typing and doc strings
# add tests
