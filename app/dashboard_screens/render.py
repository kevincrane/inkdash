import io
import os

from PIL import Image, ImageEnhance
from fitz import fitz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app.config import INKPLATE_SCREEN_HEIGHT, INKPLATE_SCREEN_WIDTH


def html_to_bmp(html_path: str, output_path: str):
    png_output_path = output_path.rsplit('.bmp', 1)[0] + '.png'

    # Setup Chrome options
    options = Options()
    options.add_argument('--headless')  # Ensure GUI is off
    options.add_argument(f'--window-size={INKPLATE_SCREEN_WIDTH},{INKPLATE_SCREEN_HEIGHT}')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--force-device-scale-factor=1')
    # options.add_argument('--no-sandbox')  # Required for Docker/containerized environments
    # options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    # options.add_argument('--font-render-hinting=none')  # Preserve original font rendering

    # Choose Chrome as the browser; screenshot as a PNG
    with webdriver.Chrome(options=options) as driver:
        driver.set_page_load_timeout(30)  # Prevent hanging on page load
        driver.set_script_timeout(30)  # Prevent hanging on script execution
        driver.set_window_size(INKPLATE_SCREEN_WIDTH, INKPLATE_SCREEN_HEIGHT)
        driver.set_network_conditions(offline=False,
                                      latency=0,  # additional latency (ms)
                                      download_throughput=500 * 1024,  # maximal throughput
                                      upload_throughput=500 * 1024)  # maximal throughput)
        driver.get(f"file://{html_path}")
        driver.implicitly_wait(2)

        # Take screenshot and save it to the given path
        driver.save_screenshot(png_output_path)

    # Convert PNG to BMP and delete interim image
    with Image.open(png_output_path) as png_img:
        image_to_bmp(png_img, output_path)
        os.remove(png_output_path)


def pdf_to_bmp(pdf_path: str, output_path: str, sharpen=1.0, y_offset=0):
    pdf_doc = fitz.open(pdf_path)

    # Convert the pixmap to a PIL Image
    pdf_bytes = pdf_doc.load_page(0).get_pixmap(dpi=100).tobytes()
    img = Image.open(io.BytesIO(pdf_bytes))

    # Save PDF bytes to a BMP
    image_to_bmp(img, output_path, sharpen=sharpen, y_offset=y_offset)


def image_to_bmp(input_image: Image, output_path: str, sharpen=1.0, y_offset: int = 0):
    """ Resize, crop, and convert an image to grayscale; save to output_path
    """
    # Resize to the same width as the e-ink display
    orig_width, orig_height = input_image.size
    aspect_ratio = orig_height / orig_width
    new_height = int(INKPLATE_SCREEN_WIDTH * aspect_ratio)
    resized_img = input_image.resize(size=(INKPLATE_SCREEN_WIDTH, new_height))

    # Crop to the dimensions of the display (offset slightly
    cropped_img = resized_img.crop(
        box=(0, y_offset, INKPLATE_SCREEN_WIDTH, INKPLATE_SCREEN_HEIGHT + y_offset))

    # Convert to grayscale
    gray_img = cropped_img.convert('L')

    # Sharpen the grayscale image
    enhancer = ImageEnhance.Sharpness(gray_img)
    gray_img = enhancer.enhance(sharpen)
    gray_img.save(output_path)
