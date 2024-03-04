import os
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from .types import KnowledgeGraph
from llm_cache import LLMCache

class KGGenerator:
    def __init__(self, model_name="gpt-3.5-turbo-0125"):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.model_name = model_name
        self.model = self.setup_model()
        self.llm_cache = LLMCache()
        self.templates = {
            "KEY_TAKEAWAY":
                    """
                        You are a a machine that extracts the key takeaway from a given paper abstract.\n
                        Paper Title: {title}
                        Paper Abstract: {abstract}
                    """,
            "KNOWLEDGE_GRAPH":
                    """
                        You are a a machine that generates graphs by extracting concepts (nodes) and their relations (links) from a given paper summary.\n
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

    def get_knowledge_graph(self, article) -> str:
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
