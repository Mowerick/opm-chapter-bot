import os
from PIL import Image
from io import BytesIO
import requests
import img2pdf
import logging

logger = logging.getLogger(__name__)

def download_images(image_urls, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    paths = []
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(img_path, format='JPEG', quality=85, optimize=True)

        paths.append(img_path)
        logger.info(f"Downloaded image {i + 1}/{len(image_urls)}")
    return paths

def generate_pdf(image_paths, output_pdf):
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(image_paths))
    logger.info(f"PDF created: {output_pdf}")
    for img in image_paths:
        try:
            os.remove(img)
        except Exception as e:
            logger.warning(f"Could not delete {img}: {e}")
    logger.info("Cleaned up images.")
    return output_pdf