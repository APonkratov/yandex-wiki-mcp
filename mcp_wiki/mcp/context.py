from dataclasses import dataclass

from mcp_wiki.wiki.proto.pages import WikiProtocol


@dataclass
class AppContext:
    wiki: WikiProtocol
