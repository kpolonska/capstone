# ADR-004: API protocol and format

## Context

M2 needs table registration and CRUD over records. The M4 MCP server must call the same operations, and the demo must be checkable with curl.

## Decision

REST over HTTP with JSON bodies:

* PUT /tables/{table}
* PUT /tables/{table}/items/{key}
* GET /tables/{table}/items/{key}
* HEAD /tables/{table}/items/{key}
* DELETE /tables/{table}/items/{key}



\*\*Alternatives rejected\*\*

* gRPC: binary and faster, but needs a protobuf toolchain and cannot be demoed with curl.
* GraphQL: too much.

