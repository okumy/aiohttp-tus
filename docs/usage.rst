=====
Usage
=====

Default
=======

To allow upload files to ``../uploads`` directory for all clients via ``/uploads`` URL,

.. code-block:: python

    from pathlib import Path

    from aiohttp import web
    from aiohttp_tus import setup_tus


    app = setup_tus(
        web.Application(),
        upload_path=Path(__file__).parent.parent / "uploads"
    )

User Uploads
============

To allow upload files to ``/files/{username}`` directory only for authenticated users
via ``/users/{username}/uploads`` URL,

.. code-block:: python

    from aiohttp_tus.annotations import Handler


    def upload_user_required(handler: Handler) -> Handler:
        async def decorator(request: web.Request) -> web.Response:
            # Change ``is_user_authenticated`` call to actual call,
            # checking whether user authetnicated for given request
            # or not
            if not is_user_authenticated(request):
                raise web.HTTPForbidden()
            return await handler(request)

        return decorator


    app = setup_tus(
        web.Application(),
        upload_path=Path("/files") / r"{username}",
        upload_url=r"/users/{username}/uploads",
        decorator=upload_user_required,
    )

Callback
========

There is a possibility to run any coroutine after upload is done. Example below,
illustrates how to achieve that,

.. code-block:: python

    from aiohttp_tus.data import Resource


    async def notify_on_upload(
        request: web.Request,
        resource: Resource,
        file_path: Path,
    ) -> None:
        redis = request.config_dict["redis"]
        await redis.rpush("uploaded_files", resource.file_name)


    app = setup_tus(
        web.Application(),
        upload_path=Path(__file__).parent.parent / "uploads",
        on_upload_done=notify_on_upload,
    )

Mutliple TUS upload URLs
========================

It is possible to setup multiple TUS upload URLs. Example below illustrates, how to
achieve anonymous & authenticated uploads in same time for one
:class:`aiohttp.web.Application` instance.

.. code-block:: python

    app = web.Application()
    base_upload_path = Path(__file__).parent.parent / "uploads"

    # Anonymous users uploads
    setup_tus(
        app,
        upload_path=base_upload_path / "anonymous"
    )

    # Authenticated users uploads
    setup_tus(
        app,
        upload_path=base_upload_path / r"{username}",
        upload_url=r"/users/{username}/uploads",
        decorator=upload_user_required,
    )
