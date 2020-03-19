from aiohttp import web
from aiohttp_jinja2 import render_template


async def index(request: web.Request) -> web.Response:
    return render_template(
        "index.html", request, {"chunk_size": request.app._client_max_size - 1}
    )
