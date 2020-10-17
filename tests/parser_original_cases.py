# json_path, result_expected
SORTED_CASES = (
    (
        "$.objects.`sorted`",
        [["alpha", "beta", "gamma"]]
    ),
    (
        "$.objects.`sorted`[1]",
        ["beta"]
    ),
    (
        "$.objects_2.`sorted`",
        [["cat", "cow", "horse"]]
    ),
    (
        "$.objects_2.`sorted`[0]",
        ["cat"]
    ),
)

LEN_CASES = (
    (
        "$.objects.`len`",
        [3]
    ),
    (
        "$.objects_2.`len`",
        [3]
    ),
    (
        "$.objects[0].`len`",
        [5]
    ),
)

FILTER_CASES = (
    (
        "$.objects_4[?(@.cow>5)]",
        [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}, {"cow": 8, "cat": 3}],
    ),
    (
        "$.objects_4[?(@.cow>5 & @.cat=2)]",
        [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}]
    ),
    (
        "$.objects_5[?(@.confidence>=0.5)].prediction",
        ["Bad"]
    ),
    (
        "$.objects_4[?(@.cow==8|@.cat==3)]",
        [{"cow": 8, "cat": 2}, {"cow": 5, "cat": 3}, {"cow": 8, "cat": 3}],
    ),
    (
        "$.objects_4[?(@.cow=8 & (@.cat=2 | @.cat=3))]",
        [{"cow": 8, "cat": 2}, {"cow": 8, "cat": 3}],
    ),
    (
        "$.objects_4[?(@.dog=1|@.cat=3&@.cow=8)]",
        [{"cow": 8, "cat": 3}]
    ),
    (
        "$.objects_4[?(@.cow>5&@.cat=2)]",
        [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}]
    ),
    (
        "$.items[?(@.quotas[*].limit<=21)].id",
        ["1000", "1001"]
    ),
    (
        "$.items[?(@.quotas[*].metric='SSD' & @.quotas[*].usage>0) | "
        "(@.quotas[*].metric='CPU' & @.quotas[*].usage>0) | "
        "(@..quotas[*].metric='DISKS' & @.quotas[*].usage>0)].id",
        ["1000", "1002"],
    ),
    (
        "$.items[?(@.quotas[?((@.metric='SSD' & @.usage>0) | (@.metric='CPU' "
        "& @.usage>0) | (@.metric='DISKS' & @.usage>0))])].quotas[?(@.usage>4)].limit",
        [40960.0, 20480.0],
    ),
)
ARITHMETIC_CASES = (
    ("3 * 3", "3*3", "Operator(3,3,*)", [9]),
    (
        "$.objects_4[0].cow * 10",
        "$.objects_4.[0].cow*10",
        "Operator(Child(Child(Child(Root(), Fields('objects_4')), "
        "Index(0)), Fields('cow')),10,*)",
        [80],
    ),
    (
        "10 * $.objects_4[0].cow",
        "$.objects_4.[0].cow*10",
        "Operator(Child(Child(Child(Root(), Fields('objects_4')), "
        "Index(0)), Fields('cow')),10,*)",
        [80],
    ),
    (
        "$.objects_5[0].prediction[0] * 3",
        "$.objects_5.[0].prediction.[0]*3",
        "Operator(Child(Child(Child(Child(Root(), Fields('objects_5')), "
        "Index(0)), Fields('prediction')), Index(0)),3,*)",
        ["GGG"],
    ),
    ("'foo' * 3", "foo*3", "Operator('foo',3,*)", ["foofoofoo"]),
    (
        "($.objects_4[2].cow * 10 * $.objects_4[4].cow) + 2",
        "$.objects_4.[2].cow*$.objects_4.[4].cow*10+2",
        "Operator(Operator(Child(Child(Child(Root(), Fields('objects_4')), "
        "Index(2)), Fields('cow')),Operator(Child(Child(Child(Root(), "
        "Fields('objects_4')), Index(4)), Fields('cow')),10,*),*),2,+)",
        [162],
    ),
    (
        "($.objects_4[4].cat * 10 * $.objects_4[4].cat) + 2",
        "$.objects_4.[4].cat*$.objects_4.[4].cat*10+2",
        "Operator(Operator(Child(Child(Child(Root(), Fields('objects_4')), "
        "Index(4)), Fields('cat')),Operator(Child(Child(Child(Root(), "
        "Fields('objects_4')), Index(4)), Fields('cat')),10,*),*),2,+)",
        [92],
    ),
    ("'foo' + 'bar'", "foo+bar", "Operator('foo','bar',+)", ["foobar"]),
    (
        "$.objects_3[0].cow + '_' + $.objects_3[1].cat",
        "$.objects_3.[0].cow+_+$.objects_3.[1].cat",
        "Operator(Operator(Child(Child(Child(Root(), Fields('objects_3')), "
        "Index(0)), Fields('cow')),'_',+),Child(Child(Child(Root(), "
        "Fields('objects_3')), Index(1)), Fields('cat')),+)",
        ["moo_neigh"],
    ),
    (
        "$.objects_3[0].cow + $.objects_3[1].cat",
        "$.objects_3.[0].cow+$.objects_3.[1].cat",
        "Operator(Child(Child(Child(Root(), Fields('objects_3')), "
        "Index(0)), Fields('cow')),Child(Child(Child(Root(), "
        "Fields('objects_3')), Index(1)), Fields('cat')),+)",
        ["mooneigh"],
    ),
    (
        "$.objects_4[*].cow * 2",
        "$.objects_4.[*].cow*2",
        "Operator(Child(Child(Child(Root(), Fields('objects_4')), AllIndex()), Fields('cow')),2,*)",
        [16, 14, 4, 10, 16],
    ),
    (
        "$.objects_6[*].cow * $.objects_6[*].cow",
        "$.objects_6.[*].cow*$.objects_6.[*].cow",
        "Operator(Child(Child(Child(Root(), Fields('objects_6')), "
        "AllIndex()), Fields('cow')),Child(Child(Child(Root(), "
        "Fields('objects_6')), AllIndex()), Fields('cow')),*)",
        [4, 1, 9],
    ),
    (
        "$.objects_4[*].cow * $.objects_6[*].cow",
        "$.objects_4.[*].cow*$.objects_6.[*].cow",
        "Operator(Child(Child(Child(Root(), Fields('objects_4')), "
        "AllIndex()), Fields('cow')),Child(Child(Child(Root(), "
        "Fields('objects_6')), AllIndex()), Fields('cow')),*)",
        [16, 8, 24, 14, 7, 21, 4, 2, 6, 10, 5, 15, 16, 8, 24],
    ),
    (
        "$.payload.metrics[?(@.name='cpu.frequency')].value * 100",
        "$.payload.metrics.[?(@.name=cpu.frequency)].value*100",
        "Operator(Child(Child(Child(Child(Root(), Fields('payload')), "
        "Fields('metrics')), Filter(Expression(target=Child(This(), "
        "Fields('name')),op='=',value='cpu.frequency'))), Fields('value')),100,*)",
        [160000],
    ),
    (
        "$.payload.metrics[*].id",
        "$.payload.metrics.[*].id",
        "Child(Child(Child(Child(Root(), Fields('payload')), "
        "Fields('metrics')), AllIndex()), Fields('id'))",
        [1, 2],
    ),
)
