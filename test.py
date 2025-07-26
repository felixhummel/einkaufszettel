def test_welcome_back():
    """
    When the user comes back, a typical session might look like this.
    """
    x = get_latest_list()
    assert x.name == 'Netto'
