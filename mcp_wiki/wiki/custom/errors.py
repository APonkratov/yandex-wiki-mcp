class WikiError(Exception):
    """Base class for Wiki API errors."""


class PageNotFound(WikiError):
    def __init__(self, page_identifier: int | str):
        super().__init__(f"Wiki page not found: {page_identifier}")
        self.page_identifier = page_identifier
