from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from claspin.model.common import Entity
from claspin.model.datasource import Datasource
from claspin.model.project import Project
from claspin.model.query import Query
from claspin.model.variable import Variable
from claspin.runtime import Runtime


def make_webapp(runtime: Runtime) -> FastAPI:
    app = FastAPI()

    @app.get("/health", response_class=PlainTextResponse)
    async def health():
        return "OK"

    @app.get("/api/v1/projects")
    async def list_projects():
        return list(runtime.db.query(Project))

    @app.get("/api/v1/projects/{name}")
    async def get_project(name: str):
        return _if_present(runtime.db.get(Project, name))

    @app.get("/api/v1/projects/{project_name}/datasources")
    async def list_datasources(project_name: str):
        return list(runtime.db.query(Datasource, project_name))

    @app.get("/api/v1/projects/{project_name}/datasources/{name}")
    async def get_datasource(project_name: str, name: str):
        return _if_present(runtime.db.get(Datasource, name, project_name))

    @app.get("/api/v1/projects/{project_name}/variables")
    async def list_variables(project_name: str):
        return list(runtime.db.query(Variable, project_name))

    @app.get("/api/v1/projects/{project_name}/variables/{name}")
    async def get_variable(project_name: str, name: str):
        return _if_present(runtime.db.get(Variable, name, project_name))

    @app.get("/api/v1/projects/{project_name}/queries")
    async def list_queries(project_name: str):
        return list(runtime.db.query(Query, project_name))

    @app.get("/api/v1/projects/{project_name}/queries/{name}")
    async def get_query(project_name: str, name: str):
        return _if_present(runtime.db.get(Query, name, project_name))

    return app


def _if_present[T: Entity](obj: T | None) -> T:
    if obj is None:
        raise HTTPException(status_code=404)
    return obj
