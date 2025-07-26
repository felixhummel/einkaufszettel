from einkaufzettel import Zettelwirtschaft, Item


def test_welcome_back():
    """
    When the user comes back, a typical session might look like this.
    """
    # Zettelwirtschaft is the central place to manage state that is *not* global.
    zettelwirtschaft = Zettelwirtschaft()
    zettel = zettelwirtschaft.get_latest_list()
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
