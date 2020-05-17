===========
aiohttp-tus
===========

.. image:: https://github.com/pylotcode/aiohttp-tus/workflows/ci/badge.svg
    :target: https://github.com/pylotcode/aiohttp-tus/actions?query=workflow%3A%22ci%22
    :alt: CI Workflow

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit
    :alt: pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black

.. image:: https://img.shields.io/pypi/v/aiohttp-tus.svg
    :target: https://pypi.org/project/aiohttp-tus/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/aiohttp-tus.svg
    :target: https://pypi.org/project/aiohttp-tus/
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/aiohttp-tus.svg
    :target: https://github.com/pylotcode/aiohttp-tus/blob/master/LICENSE
    :alt: BSD License

.. image:: https://readthedocs.org/projects/aiohttp-tus/badge/?version=latest
    :target: http://aiohttp-tus.readthedocs.org/en/latest/
    :alt: Documentation

`tus.io <https://tus.io>`_ server implementation for
`aiohttp.web <https://docs.aiohttp.org/en/stable/web.html>`_ applications.

For uploading large files, please consider using
`aiotus <https://pypi.org/project/aiotus/>`_ (Python 3.7+) library instead.

- Works on Python 3.6+
- Works with aiohttp 3.5+
- BSD licensed
- Latest documentation `on Read The Docs
  <https://aiohttp-tus.readthedocs.io/>`_
- Source, issues, and pull requests `on GitHub
  <https://github.com/pylotcode/aiohttp-tus>`_

Quickstart
==========

Code belows shows how to enable tus-compatible uploads on ``/uploads`` URL for
``aiohttp.web`` application. After upload, files will be available at ``../uploads``
directory.

.. code-block:: python

    from pathlib import Path

    from aiohttp import web
    from aiohttp_tus import setup_tus


    app = setup_tus(
        web.Application(),
        upload_url="/uploads",
        upload_path=Path(__file__).parent.parent / "uploads",
    )

Chunk Size
==========

Please, make sure to configure ``client_max_size`` for ``aiohttp.web`` Application and
supply proper ``chunkSize`` for Uppy.io or other tus.io client.

`Documentation <https://aiohttp-tus.readthedocs.io/en/latest/usage.html#understanding-tus-io-chunk-size>`__

CORS Headers
============

To setup CORS headers you need to use `cors_middleware <https://aiohttp-middlewares.readthedocs.io/en/latest/usage.html#cors-middleware>`_
from `aiohttp-middlewares`_ package. `aiohttp-cors <https://pypi.org/project/aiohttp-cors/>`_
library not supported cause of
`aio-libs/aiohttp-cors#241 <https://github.com/aio-libs/aiohttp-cors/issues/241>`_
issue.

`Documentation <https://aiohttp-tus.readthedocs.io/en/latest/usage.html#cors-headers>`__

.. _aiohttp-middlewares: https://pypi.org/project/aiohttp-middlewares/

Reverse proxy and HTTPS
=======================

When ``aiohttp`` application deployed under the reverse proxy (such as nginx) with HTTPS
support, it is needed to use `https_middleware  <https://aiohttp-middlewares.readthedocs.io/en/latest/usage.html#https-middleware>`_
from `aiohttp-middlewares`_ package to ensure that ``web.Request`` instance has proper
schema.

`Documentation <https://aiohttp-tus.readthedocs.io/en/latest/usage.html#reverse-proxy-and-https>`__

Examples
========

`examples/ <https://github.com/pylotcode/aiohttp-tus/tree/master/examples>`_ directory
contains several examples, which illustrate how to use ``aiohttp-tus`` with some tus.io
clients, such as `tus.py <https://pypi.org/project/tus.py/>`_ and
`Uppy.io <https://uppy.io>`_.
