BASE_DATUM = '0'
ITER_DATUM = "1"


class BaseDatum(object):
    TYPE = BASE_DATUM

    def __init__(self, value):
        self.value = value
        self.path = []

    def __getattr__(self, item):
        return getattr(self.value, item)


class IterDatum(BaseDatum):
    TYPE = ITER_DATUM

    def __iter__(self):
        pass

    def __next__(self):
        pass
