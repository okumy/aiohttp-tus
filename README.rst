===========
aiohttp-tus
===========

`tus.io <https://tus.io>`_ server implementation for
`aiohttp.web <https://docs.aiohttp.org/en/stable/web.html>`_ applications.

For uploading large files, please consider using
`aiotus <https://pypi.org/project/aiotus/>`_ (Python 3.7+) library instead.

- Works on Python 3.6+
- Works with aiohttp 3.5+
- BSD licensed
- Source, issues, and pull requests `on GitHub
  <https://github.com/pylotcode/aiohttp-tus>`_

Quickstart
==========

.. code-block:: python

    from pathlib import Path

    from aiohttp import web
    from aiohttp_tus import setup_tus


    app = web.Application()
    setup_tus(
        app,
        upload_url="/uploads",
        upload_path=Path(__file__).parent.parent / "uploads",
    )
