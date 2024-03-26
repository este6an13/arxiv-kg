import os
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from .types import KnowledgeGraph
from llm_cache import LLMCache
# from itertools import combinations
from langchain_openai import OpenAIEmbeddings
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np

class KGGenerator:
    def __init__(self, model_name="gpt-3.5-turbo-0125"):
        self.api_key = os.environ["OPENAI_API_KEY"]
        # self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.model_name = model_name
        self.model = self.setup_model()
        self.llm_cache = LLMCache()
        self.templates = {
            "KEY_TAKEAWAY":
                    """
                        You are a machine that extracts the key takeaway from a given paper abstract.\n
                        Paper Title: {title}
                        Paper Abstract: {abstract}
                    """,
            "KNOWLEDGE_GRAPH":
                    """
                        You are a machine that generates graphs by extracting concepts (nodes) and their relations (links) from a given paper summary.\n
                        Each link must have a word or short sentence describing the relationship.\n
                        The graph must be printed in JSON format. See the format instructions.\n
                        Format Instructions: {format_instructions}\n
                        Paper Summary: {summary}
                    """,
        }

    def generate_prompt(self, template, input_variables):
        prompt = PromptTemplate(
            template=template,
            input_variables=input_variables,
        )
        return prompt

    def generate_prompt_with_partial_variables(self, template, input_variables, partial_variables):
        prompt = PromptTemplate(
            template=template,
            input_variables=input_variables,
            partial_variables=partial_variables,
        )
        return prompt

    def setup_model(self, temperature=0):
        model = ChatOpenAI(api_key=self.api_key, model_name=self.model_name, temperature=temperature)
        return model

    def setup_chain(self, prompt, model):
        chain = (
            prompt | model | StrOutputParser()
        )
        return chain

    def setup_json_chain(self, prompt, model, parser):
        json_chain = (
            prompt | model | parser
        )
        return json_chain

    def get_result(self, title, abstract):
        key_takeaway_template = self.templates["KEY_TAKEAWAY"]
        key_takeaway_prompt = self.generate_prompt(
            template=key_takeaway_template,
            input_variables=["title", "abstract"],
        )
        key_takeaway_chain = self.setup_chain(key_takeaway_prompt, self.model)
        key_takeaway = str(key_takeaway_chain.invoke({"title": title, "abstract": abstract}))

        knowledge_graph_template = self.templates["KNOWLEDGE_GRAPH"]
        parser = PydanticOutputParser(pydantic_object=KnowledgeGraph)
        knowledge_graph_prompt = self.generate_prompt_with_partial_variables(
            template=knowledge_graph_template,
            input_variables=["summary"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )
        knowledge_graph_chain = self.setup_json_chain(knowledge_graph_prompt, self.model, parser)
        knowledge_graph = knowledge_graph_chain.invoke({"summary": key_takeaway})

        res = {
            "key_takeaway": key_takeaway,
            "knowledge_graph": knowledge_graph,
        }

        return res

    def get_article_knowledge_graph(self, article) -> str:
        article_id = article["id"]
        title = article["title"]
        abstract = article["abstract"]
        res = self.llm_cache.read(article_id)
        if res is None:
            res = self.get_result(
                title=title,
                abstract=abstract,
            )
            self.llm_cache.write(article_id, res)
        return res

    def get_knowledge_graph(self, articles, threshold=0.95) -> str:
        articles_knowledge_graphs = []
        nodes = set()
        links = []
        for article in articles:
            article_knowledge_graph = self.get_article_knowledge_graph(article)
            print(article_knowledge_graph, "\n")
            articles_knowledge_graphs.append(article_knowledge_graph)
            for link in article_knowledge_graph["knowledge_graph"].links:
                nodes.add(link.source)
                nodes.add(link.target)
                links.append(link)
        merged_knowledge_graph = KnowledgeGraph(links = links)
        # it takes too long: maybe using a vector database is faster
        """
        pairs = combinations(nodes, 2)
        i = 0
        tokens = 0
        for pair in list(pairs):
            x = np.array(self.embeddings.embed_query(pair[0])).reshape(1, -1)
            y = np.array(self.embeddings.embed_query(pair[1])).reshape(1, -1)
            tokens += len(pair[0].split())
            tokens += len(pair[1].split())
            i+=1
            if i % 500 == 0:
                print(i, tokens)
            similarity = cosine_similarity(x, y)[0][0]
            if similarity >= threshold and similarity < 1.0:
                print(pair[0], pair[1], similarity)
                # arbitrary selection
                node_new_label = pair[0]
                node_old_label = pair[1]
                print(node_new_label, node_old_label)
                for link in merged_knowledge_graph.links:
                    if link.source == node_old_label:
                        link.source = node_new_label
                    if link.target == node_old_label:
                        link.target = node_new_label
        """
        result = {
            "articles_knowledge_graphs": articles_knowledge_graphs,
            "merged_knowledge_graph": merged_knowledge_graph,
        }
        return result