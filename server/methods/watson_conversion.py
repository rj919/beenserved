__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

from labpack.records.settings import load_settings
from watson_developer_cloud import DocumentConversionV1

if __name__ == '__main__':
    file_path = '../../media/test-pdf-4.pdf'
    save_path = '../../media/test-pdf-4.json'
    watson_config = load_settings('../../cred/watson.yaml')
    username = watson_config['watson_conversion_username']
    password = watson_config['watson_conversion_password']
    document_conversion = DocumentConversionV1(username=username, password=password, version='2015-12-15')
    convert_config = { 'conversion_target': 'ANSWER_UNITS' }
    file_data = open(file_path, "rb")
    response = document_conversion.convert_document(document=file_data, config=convert_config)
    print(response.status_code)
    with open(save_path, 'wt', encoding='utf-8', errors='ignore') as save_file:
        import json
        save_file.write(json.dumps(response.json(), indent=2))
        save_file.close()
