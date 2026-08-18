from abc import ABC, abstractmethod


class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Split text into a list of chunk strings."""
        raise NotImplementedError