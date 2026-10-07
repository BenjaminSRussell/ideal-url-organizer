import pytest
from pathlib import Path

from src.organizers.stubs.embedder import StubSentenceEmbedder
from src.organizers.method_25_by_semantic_similarity import BySemanticSimilarityOrganizer
from src.core.web_crawler import PageContent


def _page(url: str, title: str, text: str) -> PageContent:
    return PageContent(
        url=url,
        final_url=url,
        status_code=200,
        response_time_ms=1,
        redirect_chain=[],
        title=title,
        text_content=text,
    )


def test_stub_embedder_deterministic():
    emb = StubSentenceEmbedder(dim=16)
    a = emb.encode(["hello world"])
    b = emb.encode(["hello world"])
    assert a.shape == (1, 16)
    assert (a == b).all()


def test_semantic_organizer_with_stub(tmp_path):
    org = BySemanticSimilarityOrganizer(tmp_path, n_clusters=2, use_stub=True)
    assert org.using_stub is True
    pages = [
        _page("https://a.example/1", "Alpha cats", "cats meow"),
        _page("https://a.example/2", "Beta dogs", "dogs bark"),
        _page("https://a.example/3", "Gamma cats", "more cats"),
    ]
    result = org.organize(pages)
    assert isinstance(result, dict)
    assert sum(len(v) for v in result.values()) == 3


@pytest.mark.gpu
def test_real_sentence_transformers_optional():
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("torch")
    assert True
