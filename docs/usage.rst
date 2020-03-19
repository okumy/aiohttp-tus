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

Understanding tus.io Chunk Size
===============================

By default, `Uppy <https://uppy.io>`_ and some other tus.io clients do not setup chunk
size and tries to upload as large chunk, as possible. However as
:class:`aiohttp.web.Application` setting up ``client_max_size`` on app initialization
you might need to configure server to receive larger chunks as well as setup tus.io
client to use respected chunk sizes.

Examples below shown on how to config different parts to upload files with chunk size
of **4MB** (``4_000_000`` bytes)

aiohttp.web configuration
-------------------------

.. code-block:: python

    from aiohttp import web
    from aiohttp_tus import setup_tus

    app = web.Application(client_max_size=4_000_000)

nginx configuration
-------------------

.. code-block:: nginx

    location ~ ^/uploads.*$ {
        client_max_body_size 4M;
        proxy_pass http://localhost:8080;
    }

tus.py configuration
--------------------

.. code-block:: bash

    tus-upload --chunk-size=4000000 \
        /path/to/large-file http://localhost:8080/uploads

uppy.io Configuration
---------------------

.. code-block:: javascript

    uppy.use(Uppy.Tus, {
        endpoint: "http://localhost:8080/uploads",
        chunkSize: 3999999
    })

.. important::
    To make `Uppy.Tus <https://uppy.io/docs/tus/>`_ plugin work you need to specify
    chunk size **at least 1 byte smaller** than ``client_max_size``. If you'll provide
    chunk size equals to client max size upload will not work properly.

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
