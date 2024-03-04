import arxiv
from typing import List

class ArxivClient:
    def __init__(self):
        self.arxiv_client = arxiv.Client()

    def _get_article_ids_list(self, month_id: int, ids: List[int]):
        zero_padded_ids = [str(id).zfill(5) for id in ids]
        article_ids = [f'{month_id}.{zp_id}' for zp_id in zero_padded_ids]
        return article_ids

    def get_articles(self, month_id: int, ids: list[int]):
        id_list = self._get_article_ids_list(month_id, ids)
        search = arxiv.Search(id_list=id_list)
        gen = self.arxiv_client.results(search)
        articles = []
        while True:
            try:
                result = next(gen)
                article_id = result.get_short_id()
                title = result.title
                abstract = result.summary
                articles.append({
                    "id": article_id,
                    "title": title,
                    "abstract": abstract,
                })
            except StopIteration:
                break
        return articles
