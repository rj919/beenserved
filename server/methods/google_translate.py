__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

def translate_text(cred_path, original_text, target_language):

# import dependencies
    from os import path, environ
    from google.cloud import translate

# authenticate with google
    path_absolute = path.abspath(cred_path)
    environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_absolute

# construct client
    translate_client = translate.Client()

# prepare text
    text_lines = original_text.split('\n')

# translate text
    translate_kwargs = {
        'values': text_lines,
        'target_language': target_language
    }
    translation = translate_client.translate(**translate_kwargs)

# parse translation
    translated_text = ''
    if translation:
        for i in range(len(translation)):
            translated_text += '%s\n' % translation[i]['translatedText']

    return translated_text


if __name__ == '__main__':
    text = u'Hello, world!'
    russian = 'ru'
    french = 'fr'
    spanish = 'es'
    mandarin = 'zh-CN'
    norweigan = 'no'
    test = '中文'
    cred = '../../cred/google-translate.json'
    file_path = '../../data/been-served-1-english.txt'
    save_file = '../../data/been-served-1-spanish.txt'
    # file_text = open(file_path).read()
    # output = translate_text(cred, file_text, spanish)
    # with open(save_file, 'wt', encoding='utf-8', errors='ignore') as f:
    #     f.write(output)
    #     f.close()

    # output = translate_text(cred, 'Errr! You need to send a photo of your document before you can do that command.', mandarin)
    # print(output)
    # output = translate_text(cred, 'translate into French', french)
    # print(output)
    # output = translate_text(cred, 'translate into Chinese', mandarin)
    # print(output)
    # output = translate_text(cred, 'translate into Norweigan', norweigan)
    # print(output)
    # output = translate_text(cred, 'translate into Spanish', spanish)
    # print(output)