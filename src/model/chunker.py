from typing import List
import nltk

nltk.download("punkt", quiet=True)

class Chunker:
    # Splits text into sentence-aware chunks with optional overlapping words

    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        # Initialize chunker with max chunk size and overlap size
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        # Split text into overlapping sentence-aware chunks
        sentences = nltk.sent_tokenize(text)
        return self._build_chunks(sentences)

    def _build_chunks(self, sentences: List[str]) -> List[str]:
        # Build chunks from a list of sentences
        chunks = []
        current, current_len = [], 0

        for sentence in sentences:
            word_count = len(sentence.split())
            if current and current_len + word_count > self.chunk_size:
                chunks.append(" ".join(current))
                current, current_len = self._get_overlap(current)
            current.append(sentence)
            current_len += word_count

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _get_overlap(self, current: List[str]) -> tuple[List[str], int]:
        # Return sentences and length to carry over for overlap
        overlap_sentences = []
        overlap_len = 0
        for s in reversed(current):
            s_len = len(s.split())
            if overlap_len + s_len <= self.overlap:
                overlap_sentences.insert(0, s)
                overlap_len += s_len
            else:
                break
        return overlap_sentences, overlap_len