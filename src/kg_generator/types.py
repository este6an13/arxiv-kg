from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class Link(BaseModel):
    source: str = Field(description="concept A")
    target: str = Field(description="concept B")
    label: str = Field(description="word or short sentence describing the relationship between the concepts")

class KnowledgeGraph(BaseModel):
    links: List[Link] = Field(description="list of links in the knowledge graph")