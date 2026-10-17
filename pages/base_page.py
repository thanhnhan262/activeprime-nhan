from __future__ import annotations

from playwright.sync_api import FrameLocator


class BasePage:
    """Base class for page objects that live inside the application iframe."""

    def __init__(self, app: FrameLocator) -> None:
        self.app = app
