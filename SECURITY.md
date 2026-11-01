# Security policy

## Supported versions

The latest release on the `main` branch receives fixes.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Email
porttek0@gmail.com with:

* a description of the issue and its impact
* steps to reproduce (a proof of concept is ideal)
* the version/commit you tested

You will get an acknowledgement within a few days.

## Scope notes

Terminally Simple stores notes, tasks and settings as plain files in the user's
config/data/documents folders and talks only to `api.open-meteo.com` and
`geocoding-api.open-meteo.com`. Things we care about:

* path traversal or writes outside the configured notes folder
* unsafe deserialisation or command execution
* data loss (silent truncation of notes/tasks/config)
