__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

# [START Bounding Boxes]
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/vision/cloud-client/document_text/doctext.py
from enum import Enum
import io

from google.cloud import vision
from PIL import Image, ImageDraw

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def draw_boxes(image, blocks, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for block in blocks:
        draw.polygon([
            block.vertices[0].x, block.vertices[0].y,
            block.vertices[1].x, block.vertices[1].y,
            block.vertices[2].x, block.vertices[2].y,
            block.vertices[3].x, block.vertices[3].y], None, color)
    return image


def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    vision_client = vision.Client()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision_client.image(content=content)
    document = image.detect_full_text()

# Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)

        if (feature == FeatureType.PAGE):
            bounds.append(block.bounding_box)

    return bounds


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.PAGE)
    draw_boxes(image, bounds, 'blue')
    bounds = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, 'red')
    bounds = get_document_bounds(filein, FeatureType.WORD)
    draw_boxes(image, bounds, 'yellow')

    if fileout is not 0:
        image.save(fileout)
    else:
        image.show()

# [START detect_text]
# https://github.com/GoogleCloudPlatform/cloud-vision/tree/master/python/text
import base64
from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa
BATCH_SIZE = 10

class VisionApi:
    """Construct and use the Google Vision API service."""

    def __init__(self, api_discovery_file='vision_api.json'):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_text(self, input_filenames, num_retries=3, max_results=6):
        """Uses the Vision API to detect text in the given file.
        """
        images = {}
        for filename in input_filenames:
            with open(filename, 'rb') as image_file:
                images[filename] = image_file.read()

        batch_request = []
        for filename in images:
            batch_request.append({
                'image': {
                    'content': base64.b64encode(
                            images[filename]).decode('UTF-8')
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': max_results,
                }]
            })
        request = self.service.images().annotate(
            body={'requests': batch_request})

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}
            text_response = {}
            for filename, response in zip(images, responses['responses']):
                if 'error' in response:
                    print("API Error for %s: %s" % (
                            filename,
                            response['error']['message']
                            if 'message' in response['error']
                            else ''))
                    continue
                if 'textAnnotations' in response:
                    text_response[filename] = response['textAnnotations']
                else:
                    text_response[filename] = []
            return text_response
        except errors.HttpError as e:
            print("Http Error for %s: %s" % (filename, e))
        except KeyError as e2:
            print("Key error: %s" % e2)

def recognize_text(cred_path, file_path):

# construct client
    vision_client = VisionApi(api_discovery_file=cred_path)

# detect text
    text_response = vision_client.detect_text([file_path])

# parse results
    recognized_text = ''
    if file_path in text_response.keys():
        if text_response[file_path]:
            if 'description' in text_response[file_path][0].keys():
                recognized_text = text_response[file_path][0]['description']

    return recognized_text

if __name__ == '__main__':

    cred_path = '../../cred/google-vision.json'
    file_path = '../../data/been-served-1.png'
    save_path = '../../data/been-served-1-english.txt'
    output = recognize_text(cred_path, file_path)
    with open(save_path, 'wt') as f:
        f.write(output)
        f.close()

# # box bound text
#     from os import path, environ
#     cred_file = '../../cred/google-vision.json'
#     cred_path = path.abspath(cred_file)
#     environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
#     save_path = '../../media/been-served-2-google.png'
#     render_doc_text(load_path, save_path)
