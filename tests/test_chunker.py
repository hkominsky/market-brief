import os
import sys
from chunker import Chunker

sys.path.insert(0, os.path.dirname(__file__))

class TestChunker:
    def test_stores_chunk_size(self):
        assert Chunker(chunk_size=500, overlap=50).chunk_size == 500

    def test_stores_overlap(self):
        assert Chunker(chunk_size=500, overlap=50).overlap == 50

    def test_defaults(self):
        c = Chunker()
        assert c.chunk_size == 2000 and c.overlap == 200

    def test_overlap_equal_to_chunk_size_raises(self):
        import pytest
        with pytest.raises(ValueError):
            Chunker(chunk_size=100, overlap=100)

    def test_overlap_greater_than_chunk_size_raises(self):
        import pytest
        with pytest.raises(ValueError):
            Chunker(chunk_size=100, overlap=150)

    def test_overlap_zero_is_valid(self):
        assert Chunker(chunk_size=100, overlap=0).overlap == 0

    def test_single_chunk_when_short(self):
        c = Chunker(chunk_size=100, overlap=10)
        assert len(c.chunk("word " * 50)) == 1

    def test_empty_string_returns_no_chunks(self):
        chunks = Chunker(chunk_size=10, overlap=2).chunk("")
        assert chunks == []

    def test_exact_chunk_size_produces_overlap_chunk(self):
        words = " ".join(["w"] * 10)
        chunks = Chunker(chunk_size=10, overlap=2).chunk(words)
        assert len(chunks) == 2
        assert len(chunks[0].split()) == 10

    def test_multiple_chunks_produced(self):
        words = " ".join(["w"] * 20)
        chunks = Chunker(chunk_size=10, overlap=2).chunk(words)
        assert len(chunks) > 1

    def test_overlap_words_repeated(self):
        words = list("abcdefghijklmnopqrst")
        text = " ".join(words)
        c = Chunker(chunk_size=5, overlap=2)
        chunks = c.chunk(text)
        tail = chunks[0].split()[-2:]
        head = chunks[1].split()[:2]
        assert tail == head

    def test_chunk_size_honored(self):
        c = Chunker(chunk_size=5, overlap=1)
        for chunk in c.chunk(" ".join(["x"] * 50)):
            assert len(chunk.split()) <= 5

    def test_all_words_covered(self):
        words = [str(i) for i in range(30)]
        text = " ".join(words)
        c = Chunker(chunk_size=7, overlap=2)
        joined = " ".join(c.chunk(text))
        for w in words:
            assert w in joined

    def test_single_word_text(self):
        chunks = Chunker(chunk_size=5, overlap=1).chunk("hello")
        assert chunks == ["hello"]

    def test_returns_list_of_strings(self):
        chunks = Chunker(chunk_size=5, overlap=1).chunk("a b c d e f g")
        assert all(isinstance(c, str) for c in chunks)

    def test_no_overlap_no_repetition(self):
        c = Chunker(chunk_size=5, overlap=0)
        chunks = c.chunk(" ".join(["w"] * 10))
        assert len(chunks) == 2

    def test_large_overlap_many_chunks(self):
        text = " ".join(["w"] * 20)
        c = Chunker(chunk_size=5, overlap=4)
        assert len(c.chunk(text)) > 4
