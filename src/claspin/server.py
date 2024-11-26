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
        return list(workspace.datasources)

    @app.get("/api/plugin/datasources/{name}")
    async def get_datasource(name: str):
        ds = workspace.get_datasource(name)
        if ds is None:
            raise HTTPException(status_code=404)
        return ds

    @app.get("/api/plugin/queries")
    async def list_queries():
        return list(workspace.queries)

    @app.get("/api/plugin/queries/{name}")
    async def get_query(name: str):
        query = workspace.get_query(name)
        if query is None:
            raise HTTPException(status_code=404)
        return query

    uvicorn.run(app, host=host, port=port)
