from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .browser import BrowserApex

class LibraryComponent:
    def __init__(self, library: "BrowserApex") -> None:
        """Base class exposing attributes from the common context.

        :param library: The library itself as a context object.
        """
        self.library = library