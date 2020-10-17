BASE_DATUM = '0'
ITER_DATUM = "1"
ROOT = "$"
EMPTY = ""
INDEX_TEMPLATE = "[{}]"
EMPTY_TEMPLATE = "{}"


class Datum(object):

    def __init__(self, value, path=ROOT, context=EMPTY, template=EMPTY_TEMPLATE):
        self.value = value
        self.path = path
        self.context = context
        self.template = template

    def __getitem__(self, item):
        # if isinstance(item, slice):
        #     return
        return self.__call__(self.value[item], item, self, INDEX_TEMPLATE)

    def __str__(self):
        return EMPTY.join([str(self.context), self.template.format(self.path)])

    def __call__(self, value, path, context, template):
        return Datum(value, path, context, template)

    def __getattr__(self, item):
        return getattr(self.value, item)

    @property
    def __class__(self):
        return self.value.__class__
