from typing import Any, Iterator

from pixeltable import type_system as ts
from pixeltable.iterators.base import ComponentIterator


class CustomAugmentIterator(ComponentIterator):
    def __init__(self, caption: str, sentence: str):
        self._caption = caption
        self._sentence = sentence
        self.iter = self._iter()

    def _iter(self) -> Iterator[dict[str, Any]]:
        print(f"CustomAugmentIterator: {self._caption=}, {self._sentence=}")
        yield {"augmented": self._caption + self._sentence}

    def __next__(self) -> dict[str, Any]:
        return next(self.iter)

    @classmethod
    def input_schema(cls, *args: Any, **kwargs: Any) -> dict[str, ts.ColumnType]:
        return {"caption": ts.StringType(), "sentence": ts.StringType()}

    @classmethod
    def output_schema(cls, *args: Any, **kwargs: Any) -> tuple[dict[str, ts.ColumnType], list[str]]:
        return {"text": ts.StringType()}, []
