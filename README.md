# Einkaufszettel
Ever wanted to manage your (in-memory) shopping list with Python?
Then look no further!

```doctest
>>> from einkaufszettel import Zettel, Item
>>>
>>> zettel = Zettel('Netto')
>>> zettel.append('Apfel')
>>> zettel.append(
...     Item(
...         name='Käse',
...         completed=True,
...     )
... )
>>> zettel.append(Item('Tomaten', 1.5, 'kg'))
>>> zettel.append(Item('Zucchini', 2))
>>>
>>> zettel
Zettel(name='Netto')
>>> list(zettel)
[Item(name='Apfel', qty=1.0, unit='Stück', completed=False), Item(name='Tomaten', qty=1.5, unit='kg', completed=False), Item(name='Zucchini', qty=2, unit='Stück', completed=False)]
>>>
```


# Development
```bash
mise install
uv sync
make
```
