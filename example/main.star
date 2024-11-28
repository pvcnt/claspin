load("dep.star", "foo")

prometheus_datasource(
    "default",
    {
        "url": "https://prometheus.demo.do.prometheus.io",
    }
)

text_variable(
    "foo",
    {
        "display_name": "Foo",
        "value": "foo",
    }
)

prometheus_label_names_variable("bar", {"matchers": ["up"]})

prometheus_label_values_variable("bar", {"label_name": "service.name"})

prometheus_promql_query("up", {"query": "up"})

stat_chart("stat", {"calculation": "mean"}, ["up"])