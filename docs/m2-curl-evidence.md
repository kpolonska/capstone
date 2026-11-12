# M2 evidence: curl checks through the coordinator

Run against the deployed `kv-app` stack: coordinator `44.202.60.0`, shard a `10.0.10.97`, shard b `10.0.11.44`.

## Setup
- Both shards registered with the coordinator: `POST /shards` returned `201 Created`.

## Results
| Step | Request | Status | Body |
|---|---|---|---|
| Create table | `PUT /tables/demo` | 200 | `{"table": "demo"}` |
| Write item | `PUT /tables/demo/items/hello` | 200 | empty |
| Read item | `GET /tables/demo/items/hello` | 200 | `world` |
| Head item | `HEAD /tables/demo/items/hello` | 200 | no body |
| Delete item | `DELETE /tables/demo/items/hello` | 200 | empty |
| Read after delete | `GET /tables/demo/items/hello` | 404 | `{"error": "no such item"}` |

## Known gap
The coordinator sends `Content-Length: 0` on HEAD, while GET reports the real length (5 bytes for `world`). A HEAD response should report the length the GET would return. Recorded for the M2 AI critique.

## Balance measurement
The 100,000-key split (51.18% / 48.82%) was measured on the ring locally, using the same code as the deployed shards. It has not been measured through the live stack.
