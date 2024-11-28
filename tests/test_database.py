import pytest

from claspin.database import Database
from claspin.model.common import Metadata
from claspin.model.datasource import Datasource, DatasourcePluginDefinition, DatasourceSpec
from claspin.model.project import Project
from claspin.model.variable import TextVariable, TextVariableSpec, Variable
from claspin.plugins.prometheus.datasource import PrometheusDatasource


@pytest.fixture
def db() -> Database:
    return Database()


def test_get(db: Database):
    project = db.get(Project, "does-not-exist")
    assert project is None

    project = db.get(Project, "default")
    assert project is not None
    assert project.metadata.name == "default"


def test_create(db: Database):
    db.create(Project(metadata=Metadata(name="top-secret")))
    project = db.get(Project, "top-secret")
    assert project is not None

    with pytest.raises(ValueError) as exc_info:
        db.create(Project(metadata=Metadata(name="top-secret")))
    assert str(exc_info.value) == "Duplicate entity Project/top-secret"


def test_upsert(db: Database):
    db.upsert(Project(metadata=Metadata(name="top-secret", labels={"test": "foo"})))
    project = db.get(Project, "top-secret")
    assert project is not None
    assert project.metadata.labels == {"test": "foo"}

    db.upsert(Project(metadata=Metadata(name="top-secret", labels={"test": "bar"})))
    project = db.get(Project, "top-secret")
    assert project is not None
    assert project.metadata.labels == {"test": "bar"}


def test_query(db: Database):
    db.create(Project(metadata=Metadata(name="public")))
    db.create(Project(metadata=Metadata(name="top-secret")))

    projects = list(db.query(Project))
    assert projects == [
        Project(metadata=Metadata(name="default")),
        Project(metadata=Metadata(name="public")),
        Project(metadata=Metadata(name="top-secret")),
    ]


def test_entities(db: Database):
    datasource = Datasource(
        metadata=Metadata(name="prom"),
        spec=DatasourceSpec(
            plugin=DatasourcePluginDefinition(
                spec=PrometheusDatasource(url="http://localhost"),
            ),
        ),
    )
    db.create(datasource)
    variable = Variable(
        metadata=Metadata(name="foo"),
        spec=TextVariable(spec=TextVariableSpec(value="Foo")),
    )
    db.create(variable)

    assert list(db.entities) == [
        Project(metadata=Metadata(name="default")),
        datasource,
        variable,
    ]
