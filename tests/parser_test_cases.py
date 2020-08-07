# json_path, value, parsed_str, parsed_repr
PATH_CASES = (
    ("$.name", ["data"], "$.name", "Child(Root(), Fields('name'))"),
    (
        "$.data[0].id",
        ["1"],
        "$.data.[0].id",
        "Child(Child(Child(Root(), Fields('data')), Index(0)), Fields('id'))",
    ),
    (
        "$.data[0].type",
        ["articles"],
        "$.data.[0].type",
        "Child(Child(Child(Root(), Fields('data')), Index(0)), Fields('type'))",
    ),
    (
        "$.data[0].attributes.title",
        ["JSON:API paints my bikeshed!"],
        "$.data.[0].attributes.title",
        "Child(Child(Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('title'))",
    ),
    (
        "$.data[0].attributes.body",
        ["The shortest article. Ever."],
        "$.data.[0].attributes.body",
        "Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), Fields('body'))",
    ),
    (
        "$.data[0].attributes.created",
        ["2015-05-22T14:56:29.000Z"],
        "$.data.[0].attributes.created",
        "Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), Fields('created'))",
    ),
    (
        "$.data[0].attributes.updated",
        ["2015-05-22T14:56:28.000Z"],
        "$.data.[0].attributes.updated",
        "Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), Fields('updated'))",
    ),
    (
        "$.data[0].attributes.info.meta.totalPages",
        [13],
        "$.data.[0].attributes.info.meta.totalPages",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('meta')), Fields('totalPages'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].id",
        ["3"],
        "$.data.[0].attributes.info.data_2.[*].id",
        "Child(Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('id'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].type",
        ["articles"],
        "$.data.[0].attributes.info.data_2.[*].type",
        "Child(Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('type'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.title",
        ["JSON:API paints my bikeshed!"],
        "$.data.[0].attributes.info.data_2.[*].attributes.title",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), "
        "Fields('data')), Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('attributes')), Fields('title'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.body",
        ["The shortest article. Ever."],
        "$.data.[0].attributes.info.data_2.[*].attributes.body",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), "
        "Fields('data')), Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('attributes')), Fields('body'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.created",
        ["2015-05-22T14:56:29.000Z"],
        "$.data.[0].attributes.info.data_2.[*].attributes.created",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), "
        "Fields('data')), Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('attributes')), Fields('created'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.updated",
        ["2015-05-22T14:56:28.000Z"],
        "$.data.[0].attributes.info.data_2.[*].attributes.updated",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), "
        "Fields('data')), Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('data_2')), AllIndex()), Fields('attributes')), Fields('updated'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].status",
        ["422"],
        "$.data.[0].attributes.info.data_2.[*].attributes.others.errors.[1].status",
        "Child(Child(Child(Child(Child(Child(Child(Child(Child("
        "Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('info')), Fields('data_2')), AllIndex()), "
        "Fields('attributes')), Fields('others')), Fields('errors')), "
        "Index(1)), Fields('status'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].source.pointer",
        ["/data/attributes/volume"],
        "$.data.[0].attributes.info.data_2.[*].attributes.others.errors.[1].source.pointer",
        "Child(Child(Child(Child(Child(Child(Child(Child(Child(Child("
        "Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), Fields('info')), Fields('data_2')), AllIndex()), "
        "Fields('attributes')), Fields('others')), Fields('errors')), "
        "Index(1)), Fields('source')), Fields('pointer'))",
    ),
    (
        "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].detail",
        ["go to 11."],
        "$.data.[0].attributes.info.data_2.[*].attributes.others.errors.[1].detail",
        "Child(Child(Child(Child(Child(Child(Child(Child(Child(Child("
        "Child(Root(), Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('info')), Fields('data_2')), AllIndex()), "
        "Fields('attributes')), Fields('others')), Fields('errors')), "
        "Index(1)), Fields('detail'))",
    ),
    (
        "$.data[0].attributes.info.links.self",
        ["http://example.com/articles?page[number]=3&page[size]=1"],
        "$.data.[0].attributes.info.links.self",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('links')), Fields('self'))",
    ),
    (
        "$.data[0].attributes.info.links.first",
        ["http://example.com/articles?page[number]=1&page[size]=1"],
        "$.data.[0].attributes.info.links.first",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('links')), Fields('first'))",
    ),
    (
        "$.data[0].attributes.info.links.prev",
        ["http://example.com/articles?page[number]=2&page[size]=1"],
        "$.data.[0].attributes.info.links.prev",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('links')), Fields('prev'))",
    ),
    (
        "$.data[0].attributes.info.links.next",
        ["http://example.com/articles?page[number]=4&page[size]=1"],
        "$.data.[0].attributes.info.links.next",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('links')), Fields('next'))",
    ),
    (
        "$.data[0].attributes.info.links.last",
        ["http://example.com/articles?page[number]=13&page[size]=1"],
        "$.data.[0].attributes.info.links.last",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), "
        "Index(0)), Fields('attributes')), "
        "Fields('info')), Fields('links')), Fields('last'))",
    ),
    (
        "$.data[0].attributes.info.other.errors[0].source.parameter",
        ["include"],
        "$.data.[0].attributes.info.other.errors.[0].source.parameter",
        "Child(Child(Child(Child(Child(Child(Child(Child(Child(Root(), "
        "Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('info')), Fields('other')), Fields('errors')), Index(0)), "
        "Fields('source')), Fields('parameter'))",
    ),
    (
        "$.data[0].attributes.info.other.errors[0].title",
        ["Invalid Query Parameter"],
        "$.data.[0].attributes.info.other.errors.[0].title",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('info')), Fields('other')), Fields('errors')), "
        "Index(0)), Fields('title'))",
    ),
    (
        "$.data[0].attributes.info.other.errors[0].detail",
        ["The resource does not have an `author`."],
        "$.data.[0].attributes.info.other.errors.[0].detail",
        "Child(Child(Child(Child(Child(Child(Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('attributes')), Fields('info')), Fields('other')), Fields('errors')), Index(0)), "
        "Fields('detail'))",
    ),
    (
        "$.data[0].relationships.author.data.id",
        ["42"],
        "$.data.[0].relationships.author.data.id",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('relationships')), Fields('author')), Fields('data')), Fields('id'))",
    ),
    (
        "$.data[0].relationships.author.data.type",
        ["people"],
        "$.data.[0].relationships.author.data.type",
        "Child(Child(Child(Child(Child(Child(Root(), Fields('data')), Index(0)), "
        "Fields('relationships')), Fields('author')), Fields('data')), Fields('type'))",
    ),
    (
        "$.included[0].type",
        ["people"],
        "$.included.[0].type",
        "Child(Child(Child(Root(), Fields('included')), Index(0)), Fields('type'))",
    ),
    (
        "$.included[0].id",
        [42],
        "$.included.[0].id",
        "Child(Child(Child(Root(), Fields('included')), Index(0)), Fields('id'))",
    ),
    (
        "$.data..totalPages",
        [13],
        "$.data..totalPages",
        "Descendants(Child(Root(), Fields('data')), Fields('totalPages'))",
    ),
    (
        "$.data..created",
        ["2015-05-22T14:56:29.000Z", "2015-05-22T14:56:29.000Z"],
        "$.data..created",
        "Descendants(Child(Root(), Fields('data')), Fields('created'))",
    ),
    (
        "$.list_items[0::3]",
        ["item_1", "item_4", "item_7"],
        "$.list_items.[0::3]",
        "Child(Child(Root(), Fields('list_items')), Slice(start=0,end='',step=3))",
    ),
    (
        "$.list_items[:6:2]",
        ["item_1", "item_3", "item_5"],
        "$.list_items.[:6:2]",
        "Child(Child(Root(), Fields('list_items')), Slice(start='',end=6,step=2))",
    ),
    (
        "$.list_items_2[::]",
        ["item_1", "item_2"],
        "$.list_items_2.[::]",
        "Child(Child(Root(), Fields('list_items_2')), Slice(start='',end='',step=''))",
    ),
    (
        "$.data_3.items.products[?(@.name=='dishes')].price",
        [12],
        "$.data_3.items.products.[?(@.name==dishes)].price",
        "Child(Child(Child(Child(Child(Root(), Fields('data_3')), Fields('items')), "
        "Fields('products')), Filter(Expression(target=Child(This(), "
        "Fields('name')),op='==',value='dishes'))), Fields('price'))",
    ),
    (
        "$.objects_4[?(@.cow>5 & @.cat==2)]",
        [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}],
        "$.objects_4.[?(@.cow>5&@.cat==2)]",
        "Child(Child(Root(), Fields('objects_4')), Filter(And("
        "Expression(target=Child(This(), Fields('cow')),op='>',value=5),"
        "Expression(target=Child(This(), Fields('cat')),op='==',value=2))))",
    ),
)

STR_REPR_CASES = (
    ("$", "$", "Root()"),
    ("$.name", "$.name", "Child(Root(), Fields('name'))"),
    (
        "$.[3:5:8].name",
        "$.[3:5:8].name",
        "Child(Child(Root(), Slice(start=3,end=5,step=8)), Fields('name'))",
    ),
    (
        "$.value[?(@.value>45)]",
        "$.value.[?(@.value>45)]",
        "Child(Child(Root(), Fields('value')), Filter(Expression(target="
        "Child(This(), Fields('value')),op='>',value=45)))",
    ),
    (
        "$.value[?(@.value)]",
        "$.value.[?(@.value)]",
        "Child(Child(Root(), Fields('value')), Filter("
        "Expression(target=Child(This(), Fields('value')),op='',value='')))",
    ),
    (
        "$.items[?(@.value>=45)]",
        "$.items.[?(@.value>=45)]",
        "Child(Child(Root(), Fields('items')), Filter(Expression(target="
        "Child(This(), Fields('value')),op='>=',value=45)))",
    ),
)
