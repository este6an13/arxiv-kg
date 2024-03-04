import articles
import kg_generator

arxiv_client = articles.ArxivClient()
articles = arxiv_client.get_articles(month_id=2402, ids=[262])

generator = kg_generator.KGGenerator()
knowledge_graph = generator.get_knowledge_graph(articles[0])

print(knowledge_graph)

# TODO:
# support query search, and make ids optional
# implement pagination with for loop to not make too big queries
# implement visualizer?: networkx, igraph or return GML
# how to unify nodes that mean the same?
# add typing and doc strings
# add tests
