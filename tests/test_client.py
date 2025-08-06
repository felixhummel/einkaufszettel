from einkaufszettel.client import ZettelClient

client = ZettelClient(
    url='https://einkaufszettel.0-main.de',
    token='geheim',
    cafile='~/ingress/root.crt',
)


def test_health():
    assert client.health() is True
