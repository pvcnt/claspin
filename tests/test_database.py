import pytest

from claspin.database import Database
from claspin.model.common import Metadata
from claspin.model.datasource import Datasource, DatasourcePluginDefinition, DatasourceSpec
from claspin.model.project import Project
from claspin.model.variable import TextVariable, TextVariableSpec, Variable
from claspin.plugins.prometheus.datasource import PrometheusDatasource

DEFAULT_PROJECT = Project(metadata=Metadata(name="default"))
TOP_SECRET_PROJECT = Project(metadata=Metadata(name="top-secret"))
PUBLIC_PROJECT = Project(metadata=Metadata(name="public"))

PROMETHEUS_DATASOURCE = Datasource(
    metadata=Metadata(name="prometheus"),
    spec=DatasourceSpec(
        plugin=DatasourcePluginDefinition(
            spec=PrometheusDatasource(url="http://localhost"),
        ),
    ),
)

FOO_VARIABLE = Variable(
    metadata=Metadata(name="foo"),
    spec=TextVariable(spec=TextVariableSpec(value="Foo")),
)


@pytest.fixture
def db() -> Database:
    db = Database()
    db.create(PUBLIC_PROJECT)
    db.create(PROMETHEUS_DATASOURCE)
    db.create(FOO_VARIABLE)
    return db


def test_get(db: Database):
    project = db.get(Project, "does-not-exist")
    assert project is None

    project = db.get(Project, "default")
    assert project == DEFAULT_PROJECT

    datasource = db.get(Datasource, "prometheus", "does-not-exist")
    assert datasource is None

    datasource = db.get(Datasource, "prometheus", "default")
    assert datasource == PROMETHEUS_DATASOURCE


def test_create(db: Database):
    db.create(TOP_SECRET_PROJECT)
    project = db.get(Project, "top-secret")
    assert project == TOP_SECRET_PROJECT

    with pytest.raises(ValueError) as exc_info:
        db.create(TOP_SECRET_PROJECT)
    assert str(exc_info.value) == "Duplicate entity Project/top-secret"


def test_upsert(db: Database):
    db.upsert(Project(metadata=Metadata(name="top-secret", labels={"test": "foo"})))
    project = db.get(Project, "top-secret")
    assert project is not None
    assert project.metadata.labels == {"test": "foo"}


def test_query(db: Database):
    projects = list(db.query(Project))
    assert projects == [DEFAULT_PROJECT, PUBLIC_PROJECT]


def test_entities(db: Database):
    assert list(db.entities) == [
        DEFAULT_PROJECT,
        PUBLIC_PROJECT,
        PROMETHEUS_DATASOURCE,
        FOO_VARIABLE,
    ]
