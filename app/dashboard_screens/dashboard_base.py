from abc import ABC, abstractmethod

from flask import Flask


class DashboardScreen(ABC):
    def __init__(self, app: Flask, static_directory: str, filename: str):
        self.app = app
        self.static_directory = static_directory
        self.filename = filename

    @abstractmethod
    def process_image(self):
        """
        Process the page in a manner specific to the implementation of this display page.
        This method must be implemented by any subclass of DashboardScreen.

        This method is expected to save a BMP image to static_directory/filename.
        """
        pass
