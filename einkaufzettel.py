from dataclasses import dataclass
from typing import Iterator


DEFAULT_UNIT = 'Stück'


def format_qty(num):
    if num == int(num):
        return str(int(num))
    else:
        return f'{num:.1f}'


@dataclass
class Item:
    name: str
    qty: float = 1.0
    unit: str = DEFAULT_UNIT
    completed: bool = False

    def _iter_markdown_line(self):
        yield '- [x]' if self.completed else '- [ ]'
        if self.qty != 1:
            yield format_qty(self.qty)
        if self.unit != DEFAULT_UNIT:
            yield self.unit
        yield self.name

    def markdown_line(self):
        return ' '.join(self._iter_markdown_line())


@dataclass
class Zettel(list[Item]):
    name: str

    # completed items are hidden by default
    def __iter__(self) -> Iterator[Item]:
        for x in super().__iter__():
            if not x.completed:
                yield x

    def iter_all(self) -> Iterator[Item]:
        yield from super().__iter__()

    def _markdown_lines(self, completed: bool):
        yield f'# {self.name}'
        iterator = self.iter_all() if completed is True else self
        for item in iterator:
            yield item.markdown_line()

    def markdown(self, completed=False):
        return '\n'.join(self._markdown_lines(completed)) + '\n'

    def append(self, x: str | Item):
        if isinstance(x, Item):
            item = x
        else:
            item = Item(name=x)
        super().append(item)


class Zettelwirtschaft:
    def get_latest_list(self) -> Zettel:
        zettel = Zettel('Netto')
        zettel.append('Apfel')
        zettel.append(
            Item(
                name='Käse',
                completed=True,
            )
        )
        zettel.append(Item('Tomaten', 1.5, 'kg'))
        zettel.append(Item('Zucchini', 2))
        return zettel
