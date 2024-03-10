import arxiv
from typing import Any, Generator, List, Dict

class ArxivClient:
    def __init__(self):
        self.arxiv_client = arxiv.Client()

    def _make_month_id_list(self, month_id: int, ids: List[int]):
        zero_padded_ids = [str(id).zfill(5) for id in ids]
        article_ids = [f'{month_id}.{zp_id}' for zp_id in zero_padded_ids]
        return article_ids

    def _get_ids_list(self, ids_dict: Dict):
        id_list = []
        for month_id, ids in ids_dict.items():
            id_list += self._make_month_id_list(month_id, ids)
        return id_list

    def _search_with_query_and_id_list(self, query: str, id_list: List[int]):
        search = arxiv.Search(query=query, id_list=id_list)
        gen = self.arxiv_client.results(search)
        return gen

    def _search_with_query(self, query: str, max_results: int):
        search = arxiv.Search(query=query, max_results=max_results)
        gen = self.arxiv_client.results(search)
        return gen

    def _search_with_id_list(self, id_list: List[int]):
        search = arxiv.Search(id_list=id_list)
        gen = self.arxiv_client.results(search)
        return gen

    def _get_articles_from_gen(self, gen: Generator[Any, None, None]):
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

    def get_articles_with_query_and_ids(self, query: str, ids_dict: Dict):
        id_list = self._get_ids_list(ids_dict)
        # split in groups of 100 to not make too big queries
        id_groups = [id_list[i:i+100] for i in range(0, len(id_list), 100)]
        articles = []
        # call search function for each group
        for group in id_groups:
            print("group:", group[0], group[-1])
            gen = self._search_with_query_and_id_list(
                query=query,
                id_list=group,
            )
            articles.extend(self._get_articles_from_gen(gen))
        return articles

    def get_articles_with_query(self, query: str, max_results: int = 100):
        gen = self._search_with_query(
            query=query,
            max_results=max_results,
        )
        articles = self._get_articles_from_gen(gen)
        return articles

    def get_articles_with_id_list(self, ids_dict: Dict):
        id_list = self._get_ids_list(ids_dict)
        # split in groups of 100 to not make too big queries
        id_groups = [id_list[i:i+100] for i in range(0, len(id_list), 100)]
        articles = []
        # call search function for each group
        for group in id_groups:
            print("group:", group[0], group[-1])
            gen = self._search_with_id_list(
                id_list=group,
            )
            articles.extend(self._get_articles_from_gen(gen))
        return articles
