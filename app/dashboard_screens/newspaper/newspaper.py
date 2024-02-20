from datetime import datetime

import fitz  # PyMuPDF
import requests

from app.dashboard_screens.dashboard_base import DashboardScreen
from app.dashboard_screens.render import pdf_to_bmp


class NewspaperScreen(DashboardScreen):
    """ Renders the current frontpage of the NY Times
    """
    NYT_SCAN_URL = 'https://static01.nyt.com/images/{year}/{month:02}/{day:02}/nytfrontpage/scan.pdf'
    PDF_FILENAME = 'nytfrontpage.pdf'

    def process_image(self):
        self.app.logger.info('Processing NYT frontpage screen...')
        pdf_path = f'{self.static_directory}/{self.PDF_FILENAME}'

        self.__download_todays_nyt_frontpage(pdf_path)
        pdf_to_bmp(pdf_path=pdf_path,
                   output_path=f'{self.static_directory}/{self.filename}',
                   sharpen=2.0, y_offset=20)
        self.app.logger.info(f'Final newspaper image saved to {self.static_directory}/{self.filename}')

    def __download_todays_nyt_frontpage(self, pdf_path: str):
        """ Downloads the NY Times frontpage as a PDF to the Flask static directory
        """
        # Construct the URL based on the current date
        today = datetime.now()
        nyt_url = self.NYT_SCAN_URL.format(year=today.year, month=today.month, day=today.day)

        # Make a request to the NYT URL
        response = requests.get(nyt_url)
        if response.status_code == 200:
            # Save the content to a file in the static directory
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            self.app.logger.info(f'NYT frontpage for {today.month}/{today.day}/{today.year} saved to {pdf_path}')
        else:
            self.app.logger.info(f'Failed to download the NYT scan. Status code: {response.status_code}')

    def __render_pdf_for_eink_display(self):
        """ Scales, crops, and converts the nytfrontpage.pdf file for e-ink display;
            saves output to self.filename
        """
        # Open the PDF file
        pdf_doc = fitz.open(f'{self.static_directory}/{self.PDF_FILENAME}')

        # Convert the pixmap to a PIL Image
        pdf_bytes = pdf_doc.load_page(0).get_pixmap(dpi=100).tobytes()
        pdf_to_bmp(pdf_bytes, f'{self.static_directory}/{self.filename}', sharpen=2.0, y_offset=20)
