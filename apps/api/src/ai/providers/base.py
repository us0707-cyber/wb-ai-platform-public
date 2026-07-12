from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    name = "base"

    @abstractmethod
    async def generate_json(self, *, system: str, user: str, schema_name: str) -> dict[str, Any]:
        raise NotImplementedError
