from typing import List

class Chunker:
    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        # Stores the max words per chunk and how many words to repeat between chunks
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        # Splits text into overlapping word chunks and returns them as a list of strings
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i : i + self.chunk_size]
            chunks.append(" ".join(chunk))
            i += self.chunk_size - self.overlap
        return chunks