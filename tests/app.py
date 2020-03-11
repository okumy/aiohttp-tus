"""
===================================
python -m aiohttp.web tests.app:app
===================================

aiohttp_tus test app.

Usage
=====

To test how aiohttp_tus uploading files,

1. Run test app as,

.. code-block:: bash

    poetry run python -m aiohttp.web --port 8300 tests.app:create_app

2. Upload some large file as,

.. code-block:: bash

    poetry run tus-upload --chunk-size=1000000 /path/to/large-file http://localhost:8300/uploads

3. Check that file uploaded and is available at ``./test-uploads/aiohttp_tus``
   directory

"""

import shutil
from pathlib import Path
from typing import List

from aiohttp import web
from aiohttp_tus import setup_tus


def create_app(argv: List[str] = None) -> web.Application:
    upload_path = Path(__file__).parent / "test-uploads"
    upload_path.mkdir(mode=0o755, exist_ok=True)

    print("aiohttp_tus test app")
    print(f"Uploading files to {upload_path.absolute()}")

    try:
        return setup_tus(web.Application(), upload_path=upload_path)
    finally:
        print(f"Removing {upload_path.absolute()} directory")
        shutil.rmtree(upload_path)
