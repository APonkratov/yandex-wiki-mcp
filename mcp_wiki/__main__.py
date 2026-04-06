import sys
from typing import Any

from mcp.server import FastMCP
from pydantic import ValidationError

from mcp_wiki.mcp.server import create_mcp_server
from mcp_wiki.settings import Settings


def create_mcp() -> tuple[FastMCP[Any], Settings]:
    """Main entry point for the ya-yandex-wiki-mcp command."""
    try:
        settings = Settings()
    except ValidationError as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(1)

    return create_mcp_server(settings), settings


mcp, settings = create_mcp()


def main() -> None:
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
