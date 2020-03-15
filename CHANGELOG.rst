1.0.0b0 (In Development)
========================

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
