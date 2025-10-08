[![Try Free](https://img.shields.io/badge/Try%20Free-FalkorDB%20Cloud-FF8101?labelColor=FDE900&link=https://app.falkordb.cloud)](https://app.falkordb.cloud)
[![Dockerhub](https://img.shields.io/docker/pulls/falkordb/falkordb?label=Docker)](https://hub.docker.com/r/falkordb/falkordb/)
[![Discord](https://img.shields.io/discord/1146782921294884966?style=flat-square)](https://discord.com/invite/6M4QwDXn2w)

## Getting Started

[Live Demo](https://code-graph.falkordb.com/)

## Running locally

### Run FalkorDB

Free cloud instance: https://app.falkordb.cloud/signup

Or by running locally with docker:

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

### Config

Create your own `.env` file from the `.env.template` file

Start the server:
```bash
flask --app api/index.py run --debug
```

### Creating a graph

Process a local source folder:

```bash
curl -X POST http://127.0.0.1:5000/analyze_folder -H "Content-Type: application/json" -d '{"path": "<FULL_PATH_TO_FOLDER>", "ignore": [<OPTIONAL_IGNORE_LIST>]}' -H "Authorization: <.ENV_SECRET_TOKEN>"
```

For example:

```bash
curl -X POST http://127.0.0.1:5000/analyze_folder -H "Content-Type: application/json" -d '{"path": "/Users/roilipman/Dev/GraphRAG-SDK", "ignore": ["./.github", "./build"]}' -H "Authorization: OpenSesame"
```

## Working with your graph

Once the source code analysis completes your FalkorDB DB will be populated with
a graph representation of your source code, the graph name should be the same as
the name of the folder you've requested to analyze, for the example above a graph named:
"GraphRAG-SDK".

At the moment only the Python and C languages are supported, we do intend to support additional languages.

At this point you can explore and query your source code using various tools
Here are several options:

1. [Code-Graph UI](https://github.com/FalkorDB/code-graph)
1. FalkorDB [Browser](https://github.com/FalkorDB/falkordb-browser/)
2. One of FalkorDB's [clients](https://docs.falkordb.com/clients.html)
3. Use FalkorDB [GraphRAG-SDK](https://github.com/FalkorDB/GraphRAG-SDK) to connect an LLM for natural language exploration.
