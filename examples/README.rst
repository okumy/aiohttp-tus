====================
aiohttp-tus Examples
====================

aiohttp_tus_app
===============

To illustrate that uploading via `tus.py <https://pypi.org/project/tus.py/>` library
works well.

To run,

.. code-block:: bash

    make -C .. EXAMPLE=aiohttp_tus_app example

After, upload large files as,

.. code-block:: bash

    poetry run tus-upload --chunk-size=1000000 /path/to/large-file http://localhost:8300/uploads

Then check that files uploaded to upload directory.

uploads
=======

To illustrate that uploading via `Uppy <https://uppy.io>`_ JavaScript library works
as expected.

To run,

.. code-block:: bash

    make -C .. EXAMPLE=uploads example

After, open ``http://localhost:8080`` to try upload. All uploads will be available in
temporary directory.

.. important::
    This example uses chunks size of 4MB, but you might want customize things by
    setting up other chunk size via ``AIOHTTP_CLIENT_MAX_SIZE`` env var.

    For example,

    .. code-block:: bash

        AIOHTTP_CLIENT_MAX_SIZE=10MB make -C .. EXAMPLE=uploads example

    will set `client_max_size <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application>`_
    param to ``10_000_000`` bytes.
