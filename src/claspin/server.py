import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from claspin.workspace import Workspace


def start_server(host: str, port: int, workspace: Workspace) -> None:
    app = FastAPI()

    @app.get("/health", response_class=PlainTextResponse)
    async def health():
        return "OK"

    @app.get("/api/plugin/datasources")
    async def list_datasources():
        return list(workspace.db.datasources)

    @app.get("/api/plugin/datasources/{name}")
    async def get_datasource(name: str):
        ds = workspace.db.get_datasource(name)
        if ds is None:
            raise HTTPException(status_code=404)
        return ds

    @app.get("/api/plugin/queries")
    async def list_queries():
        return list(workspace.db.queries)

    @app.get("/api/plugin/queries/{name}")
    async def get_query(name: str):
        query = workspace.db.get_query(name)
        if query is None:
            raise HTTPException(status_code=404)
        return query

    @app.get("/api/plugin/variables")
    async def list_variables():
        return list(workspace.db.variables)

    @app.get("/api/plugin/variables/{name}")
    async def get_variable(name: str):
        variable = workspace.db.get_variable(name)
        if variable is None:
            raise HTTPException(status_code=404)
        return variable

    uvicorn.run(app, host=host, port=port)
