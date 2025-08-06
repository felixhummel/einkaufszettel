import pytest

from einkaufszettel import Zettel, Item
from einkaufszettel.domain import ZettelSammlung


@pytest.fixture
def netto_zettel():
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


@pytest.fixture
def edeka_zettel():
    result = Zettel('Edeka')
    result.append('Jever Fun')
    return result


@pytest.fixture
def sammlung(netto_zettel, edeka_zettel):
    return ZettelSammlung([netto_zettel, edeka_zettel])


def test_sammlung(sammlung):
    assert len(sammlung) == 2
    assert [x.name for x in sammlung.sorted_by_name()] == [
        'Edeka',
        'Netto',
    ]


def test(netto_zettel):
    """
    When the user comes back, a typical session might look like this.
    """
    zettel = netto_zettel
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
