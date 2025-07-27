import pytest

from einkaufzettel import Zettel, Item


@pytest.fixture
def zettel():
    result = Zettel('Netto')
    result.append('Apfel')
    result.append(
        Item(
            name='Käse',
            completed=True,
        )
    )
    result.append(Item('Tomaten', 1.5, 'kg'))
    result.append(Item('Zucchini', 2))
    return result


def test(zettel):
    """
    When the user comes back, a typical session might look like this.
    """
    # Einkaufszettel has a name
    assert zettel.name == 'Netto'
    # Einkaufszettel behaves like a list
    assert len(zettel) == 4
    # default order: by name asc
    assert (
        zettel.markdown()
        == """\
# Netto
- [ ] Apfel
- [ ] 1.5 kg Tomaten
- [ ] 2 Zucchini
"""
    )
    # completed items are hidden by default
    assert (
        zettel.markdown(completed=True)
        == """\
# Netto
- [ ] Apfel
- [x] Käse
- [ ] 1.5 kg Tomaten
- [ ] 2 Zucchini
"""
    )
    # add stuff by name
    zettel.append('Wurst')
    # or as a model
    zettel.append(
        Item(
            name='Salat',
            qty=1,
            unit='Kopf',
        )
    )
    # a dict works too
    # zettel.append(
    #     dict(
    #         name='Salat',
    #         qty='1',
    #         unit='Kopf',
    #     )
    # )
