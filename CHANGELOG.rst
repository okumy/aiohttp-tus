=========
ChangeLog
=========

1.0.0rc0 (2020-03-26)
=====================

- Add example to ensure that upload via `Uppy <https://uppy.io>`_ JavaScript library
  works as expected
- Fix resuming uploads by passing missed ``Upload-Length`` header:
  `#5 <https://github.com/pylotcode/aiohttp-tus/pull/5>`_
- Add documentation about `CORS Headers <https://aiohttp-tus.readthedocs.io/en/latest/usage.html#cors-headers>`_
- Allow to provide upload resource name, which can be lately used for URL reversing

1.0.0b2 (2020-03-18)
====================

- Ensure trailing slash upload URLs working as well

1.0.0b1 (2020-03-18)
====================

- Add brief documentation
- Use canonical upload URL for tus config mapping

1.0.0b0 (2020-03-15)
====================

- Allow to setup tus upload URLs multiple times for one ``aiohttp.web`` application
- Allow to call callback after upload is done
- Provide many unit tests for tus views

1.0.0a1 (2020-03-12)
====================

- Allow to decorate upload views for authentication or other (for example *to check
  whether entity for upload exists or not*) needs
- Allow to upload on named upload paths, when using named upload URLs
- Ensure named upload URLs (e.g. ``/user/{username}/uploads``) works as well
- Ensure package is typed by adding ``py.typed``

1.0.0a0 (2020-03-11)
====================

- First public release with minimal valuable coverage of ``tus.io`` protocol for
  ``aiohttp.web`` applications
