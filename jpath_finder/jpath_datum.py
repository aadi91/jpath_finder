ROOT = "$"
EMPTY = ""
INDEX_TEMPLATE = "[{}]"
EMPTY_TEMPLATE = "{}"
KEYS = "keys"
VALUES = "values"


class Datum(object):

    def __init__(self, value, path=ROOT, context=EMPTY, template=EMPTY_TEMPLATE):
        self.value = value
        self.path = path
        self.context = context
        self.template = template

    def __getitem__(self, item):
        return self.__call__(self.value[item], item, self, INDEX_TEMPLATE)

    def __str__(self):
        return EMPTY.join([str(self.context), self.template.format(self.path)])

    def __repr__(self):
        return str(self.value)

    def __call__(self, value, path, context, template=EMPTY_TEMPLATE):
        return Datum(value, path, context, template)

    def __getattr__(self, item):
        return getattr(self.value, item)

    @property
    def __class__(self):
        return self.value.__class__

    def keys(self):
        return [self.__call__(k, k, self, INDEX_TEMPLATE) for k in self.value.keys()]

    def values(self):
        return [self.__call__(v, k, self, INDEX_TEMPLATE) for k, v in self.value.items()]

    def __eq__(self, datum):
        if not isinstance(datum, Datum):
            return NotImplemented
        return self.value == datum.value

    def __hash__(self):
        return hash(self.value)
