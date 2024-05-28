![GitHub Release](https://img.shields.io/github/v/release/caubios/aioopendoors?style=for-the-badge&link=https%3A%2F%2Fgithub.com%2Fcaubios%2Faioopendoors%2Freleases)
![GitHub License](https://img.shields.io/github/license/caubios/aioopendoors?style=for-the-badge)
# aioopendoors

Asynchronous library to communicate with the Opendoors API

> [!IMPORTANT]
> As for now there is no easy way to get OAuth Client Id and Client Secret for this library. No support will be provide for all Credentials matters.
> Sharing, selling, or distribution access and refresh tokens is strictly prohibited. Sharing them could case serious issues for you as user!

> [!IMPORTANT]
> This library have been implemented without any access to API documentation. Thus it is *NOT* an official support of Opendoors API.

> [!WARNING]
> Use this library at your own risk as it purpose is to open/close your main house door.

## Quickstart

In order to use the library, you'll need to do some work yourself to get authentication
credentials.

You will have to implement `AbstractAuth` to provide an access token. Your implementation
will handle any necessary refreshes. You can invoke the service with your auth implementation
to access the API.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

For a first start you can run the `example.py`, by doing the following steps

- `git clone https://github.com/caubios/aioopendoors.git`
- `cd aioopendoors`
- `poetry install`
- Enter your personal credentials in the `_secrets.yaml` and rename it to `secrets.yaml`
- Run with `poetry run python ./example.py`


## Contributing

This is an active open-source project. We are always open to people who want to use the code or contribute to it.
This Python project is fully managed using the [Poetry][poetry] dependency manager.

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com/
