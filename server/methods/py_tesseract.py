__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

# https://pythontips.com/2016/02/25/ocr-on-pdf-files-using-python/
# https://stackoverflow.com/questions/34293274/unicodedecodeerror-with-tesseract-ocr-in-python

'''
installations:
http://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows
https://ghostscript.com/download/gsdnld.html
https://github.com/tesseract-ocr/tesseract/wiki
'''

'''
alternatives:
http://finereaderonline.com/en-us
https://www.ibm.com/watson/developercloud/document-conversion.html
https://cloud.google.com/vision/docs/fulltext-annotations
'''

def convert_to_png(file_path):

    from wand.image import Image

    image_files = []

    image_original = Image(filename=file_path, resolution=300)
    image_png = image_original.convert('png')

    for img in image_png.sequence:
        image_page = Image(image=img)
        image_files.append(image_page.make_blob('jpeg'))

    return image_files

def recognize_text(file_path, tesseract_cmd=''):

    import re
    import builtins
    from wand.image import Image
    from PIL import Image as PI
    import io
    import pytesseract

    image_texts = []

# define tesseract command path
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        from labpack.platforms.localhost import localhostClient
        if localhostClient().os.sysname == 'Windows':
            raise IndexError('tesseract_cmd argument required on Windows.')

# open image file
    image_files = []
    png_regex = re.compile('\.png$')
    if not png_regex.findall(file_path):
        image_files = convert_to_png(file_path)
    else:
        image_png = Image(filename=file_path, resolution=300)
        for img in image_png.sequence:
            image_page = Image(image=img)
            image_files.append(image_page.make_blob('png'))

# bypass cp1252 errors in python3
    original_open = open
    def bin_open(filename, mode='rb'):
        return original_open(filename, mode)

# process ocr with tesseract
    try:
        builtins.open = bin_open
        for img in image_files:
            bts = pytesseract.image_to_string(PI.open(io.BytesIO(img)))
            text_string = str(bts, 'cp1252', 'ignore')
            image_texts.append(text_string)
    finally:
        builtins.open = original_open

    return image_texts

if __name__ == '__main__':
    tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    file_path = '../../media/been-served-1.png'
    image_texts = recognize_text(file_path, tesseract_cmd)
    print(image_texts)
