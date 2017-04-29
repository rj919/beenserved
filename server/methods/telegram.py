__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

def transcribe_voice(update_details):

    return True

def analyze_message(update_details, user_id, telegram_bot_client, telegram_data_client):

# import dependencies
    from time import time, sleep
    from os import environ, path
    data_path = environ['SERVER_DATA_PATH']
    vision_cred_path = environ['GOOGLE_VISION_KEYS']
    translate_cred_path = environ['GOOGLE_TRANSLATE_KEYS']
    user_path = path.join(data_path, 'users/%s' % user_id)

# retrieve user settings
    user_key = 'users/telegram_%s.yaml' % user_id
    user_filter = telegram_data_client.conditional_filter([{1:{'discrete_values':['telegram_%s.yaml' % user_id ]}}])
    if not telegram_data_client.list(user_filter):
        telegram_data_client.create(user_key, { 'feedback_type': 'text' })
    user_record = telegram_data_client.read(user_key)

# construct default strings
    message_string = ''
    document_reply = ''

# parse update
    if 'voice' in update_details['message'].keys():

    # retrieve audio file
        voice_id = update_details['message']['voice']['file_id']
        voice_mimetype = update_details['message']['voice']['mime_type']
        voice_duration = update_details['message']['voice']['duration']
        details = telegram_bot_client.get_route(voice_id)
        file_route = details['json']['result']['file_path']
        file_buffer = telegram_bot_client.get_file(file_route, file_name='voice_telegram_%s' % user_id)
        file_data = file_buffer.getvalue()
        file_name = file_buffer.name
        voice_path = path.join(user_path, 'voice')
        if not path.exists(voice_path):
            from os import makedirs
            makedirs(voice_path)
        file_extension = '.ogg'
        mimetype_extensions = { 'audio/ogg': '.ogg' }
        if voice_mimetype in mimetype_extensions.keys():
            file_extension = mimetype_extensions[voice_mimetype]
        file_path = path.join(voice_path, '%s%s' % (str(time()), file_extension))
        with open(file_path, 'wb') as f:
            f.write(file_data)
            f.close()

    # construct bluemix client
        from labpack.speech.watson import watsonSpeechClient
        bluemix_username = environ['bluemix_speech2text_username'.upper()]
        bluemix_password = environ['bluemix_speech2text_password'.upper()]
        watson_speech_client = watsonSpeechClient(bluemix_username, bluemix_password)

    # retrieve transcription
        transcription_details = watson_speech_client.transcribe_file(file_path)
        message_string = transcription_details['result']

    elif 'text' in update_details['message'].keys():
        if update_details['message']['text']:
            message_string = update_details['message']['text']

# TODO ocr processing
    elif 'photo' in update_details['message'].keys():
        if update_details['message']['photo']:

    # retrieve photo
            photo_list = update_details['message']['photo']
            photo_list = sorted(photo_list, key=lambda k: k['file_size'], reverse=True)
            photo_id = photo_list[0]['file_id']
            details = telegram_bot_client.get_route(photo_id)
            file_route = details['json']['result']['file_path']
            file_buffer = telegram_bot_client.get_file(file_route, file_name='photo_telegram_%s' % user_id)

    # save photo
            file_data = file_buffer.getvalue()
            file_name = file_buffer.name
            photo_path = path.join(user_path, 'photo')
            if not path.exists(photo_path):
                from os import makedirs
                makedirs(photo_path)
            file_path = path.join(photo_path, '%s.jpg' % str(time()))
            with open(file_path, 'wb') as f:
                f.write(file_data)
                f.close()
            sleep(.2)

    # recognize text in photo
            from server.methods.google_vision import recognize_text
            recognized_text = ''
            try:
                recognized_text = recognize_text(vision_cred_path, file_path)
                print(recognized_text)
            except:
                pass
            if recognized_text:
                current_time = time()
                document_key = 'documents/%s/%s.json' % (user_id, str(current_time))
    # TODO parse the case number, address, party and topic
                document_details = {
                    'user_id': user_id,
                    'dt': current_time,
                    'english': recognized_text
                }
                telegram_data_client.create(document_key, document_details)
                document_reply = recognized_text

# define default response
    print(message_string)
    response_details = {
        'function': 'send_message',
        'kwargs': {
            'user_id': user_id,
            'message_text': "Ooops! That's not a command. Try: /help"
        }
    }
    missing_message = {
        'english': 'Errr! You need to send a photo of your document before you can do that command.',
        'spanish': 'Errr! Necesitas enviar una foto de tu documento antes de poder hacer ese comando.',
        'french': 'Errr! Vous devez envoyer une photo de votre document avant de pouvoir effectuer cette commande.',
        'norweigan': 'Errr! Du må sende et bilde av dokumentet før du kan gjøre den kommandoen.',
        'chinese': '错误！您需要发送文档的照片才能执行该命令。'
    }

# reply to document submission
    if document_reply:
        response_details['kwargs']['message_text'] = 'Sweet! Your document has been scanned and saved.\n\nTo view your document:\n\t__/view__ : view document in English\n\t__/french__ : traduisez en francais\n\t__/spanish__ : traducir al español\n\t__/norweigan__ : sette til Norweigan\n\t__/chinese__ : 翻译成中文'
        response_details['kwargs']['message_style'] = 'markdown'

# handle navigation
    elif message_string.lower() in ('start', '/start', 'help', '/help', 'about', '/about'):
        response_details['kwargs']['message_text'] = 'Been Served is a bot that translates legalese into normal speak. Simply take a photo of a document you have received from the court, send it in a message and Been Served will help you understand it. \n\nOnce you have uploaded the document, you can also type the following commands:\n\t__/view__ : retrieve english text\n\t__/language__ : selection of translation options\n\t__/location__ : link to court address\n\t__/resources__ : link to topic resources'
        response_details['kwargs']['message_style'] = 'markdown'

# # update feedback types
#     elif message_string.lower() == 'audio':
#         user_details = { 'feedback_type': 'audio' }
#         telegram_data_client.create(user_key, user_details, overwrite=True)
#         response_details['kwargs']['message_text'] = 'Sweet! Your feedback type has been updated to audio.'
#     elif message_string.lower() == 'text':
#         user_details = {'feedback_type': 'text'}
#         telegram_data_client.create(user_key, user_details, overwrite=True)
#         response_details['kwargs']['message_text'] = 'Sweet! Your feedback type has been updated to normal text.'
#     elif message_string.lower() in ('feedback', '/feedback'):
#         response_details['kwargs']['message_text'] = 'Select a type of feedback:'
#         response_details['kwargs']['button_list'] = [ 'Text', 'Audio' ]

# handle unavailable options
    elif message_string.lower() in ('resources', '/resources', 'location', '/location'):
        response_details['kwargs']['message_text'] = 'Ooops. That function is not yet available.'

# handle translation options
    elif message_string.lower() in ('language', '/language', 'languages', '/languages'):
        response_details['kwargs']['message_text'] = 'Translate document into:'
        response_details['kwargs']['button_list'] = [ 'Français', 'Español', 'Norweigan', '中文' ]
    elif message_string.lower() in ('english', '/english', 'view', '/view'):
        doc_conditions = [{
            0: {'discrete_values':['documents']},
            1: {'discrete_values':[ str(user_id) ]}
        }]
        doc_filter = telegram_data_client.conditional_filter(doc_conditions)
        doc_results = telegram_data_client.list(doc_filter)
        if not doc_results:
            response_details['kwargs']['message_text'] = missing_message['english']
        else:
            document_details = telegram_data_client.read(doc_results[0])
            response_details['kwargs']['message_text'] = document_details['english']

    elif message_string.lower() in ('français', 'french', '/français', '/french'):
        doc_conditions = [{
            0: {'discrete_values':['documents']},
            1: {'discrete_values':[ str(user_id) ]}
        }]
        doc_filter = telegram_data_client.conditional_filter(doc_conditions)
        doc_results = telegram_data_client.list(doc_filter)
        if not doc_results:
            response_details['kwargs']['message_text'] = missing_message['french']
        else:
            document_details = telegram_data_client.read(doc_results[0])
            if not 'french' in document_details.keys():
                from server.methods.google_translate import translate_text
                english_text = document_details['english']
                translated_text = translate_text(translate_cred_path, english_text, 'fr')
                if translated_text:
                    document_details['french'] = translated_text
                    telegram_data_client.create(doc_results[0], document_details, overwrite=True)
                    response_details['kwargs']['message_text'] = translated_text
                else:
                    response_details['kwargs']['message_text'] = 'Ooops! Il y a eu un problème de traduction en français.'
            else:
                response_details['kwargs']['message_text'] = document_details['french']

    elif message_string.lower() in ('español', 'spanish', '/español', '/spanish'):
        doc_conditions = [{
            0: {'discrete_values':['documents']},
            1: {'discrete_values':[ str(user_id) ]}
        }]
        doc_filter = telegram_data_client.conditional_filter(doc_conditions)
        doc_results = telegram_data_client.list(doc_filter)
        if not doc_results:
            response_details['kwargs']['message_text'] = missing_message['spanish']
        else:
            document_details = telegram_data_client.read(doc_results[0])
            if not 'spanish' in document_details.keys():
                from server.methods.google_translate import translate_text
                english_text = document_details['english']
                translated_text = translate_text(translate_cred_path, english_text, 'es')
                if translated_text:
                    document_details['spanish'] = translated_text
                    telegram_data_client.create(doc_results[0], document_details, overwrite=True)
                    response_details['kwargs']['message_text'] = translated_text
                else:
                    response_details['kwargs']['message_text'] = '¡Ooops! Hubo un problema al traducir al español.'
            else:
                response_details['kwargs']['message_text'] = document_details['spanish']

    elif message_string.lower() in ('norweigan', '/norweigan'):
        doc_conditions = [{
            0: {'discrete_values':['documents']},
            1: {'discrete_values':[ str(user_id) ]}
        }]
        doc_filter = telegram_data_client.conditional_filter(doc_conditions)
        doc_results = telegram_data_client.list(doc_filter)
        if not doc_results:
            response_details['kwargs']['message_text'] = missing_message['norweigan']
        else:
            document_details = telegram_data_client.read(doc_results[0])
            if not 'norweigan' in document_details.keys():
                from server.methods.google_translate import translate_text
                english_text = document_details['english']
                translated_text = translate_text(translate_cred_path, english_text, 'no')
                if translated_text:
                    document_details['norweigan'] = translated_text
                    telegram_data_client.create(doc_results[0], document_details, overwrite=True)
                    response_details['kwargs']['message_text'] = translated_text
                else:
                    response_details['kwargs']['message_text'] = 'Beklager! Det var et problem å oversette til Norweigan.'
            else:
                response_details['kwargs']['message_text'] = document_details['norweigan']

    elif message_string.lower() in ('中文', '/中文', 'chinese', '/chinese'):
        doc_conditions = [{
            0: {'discrete_values':['documents']},
            1: {'discrete_values':[ str(user_id) ]}
        }]
        doc_filter = telegram_data_client.conditional_filter(doc_conditions)
        doc_results = telegram_data_client.list(doc_filter)
        if not doc_results:
            response_details['kwargs']['message_text'] = missing_message['chinese']
        else:
            document_details = telegram_data_client.read(doc_results[0])
            if not 'chinese' in document_details.keys():
                from server.methods.google_translate import translate_text
                english_text = document_details['english']
                translated_text = translate_text(translate_cred_path, english_text, 'zh-CN')
                if translated_text:
                    document_details['chinese'] = translated_text
                    telegram_data_client.create(doc_results[0], document_details, overwrite=True)
                    response_details['kwargs']['message_text'] = translated_text
                else:
                    response_details['kwargs']['message_text'] = 'Ooops！中文翻译有问题。'
            else:
                response_details['kwargs']['message_text'] = document_details['chinese']

    elif message_string == '.':
        response_details['function'] = 'pass'

# add entry to record
    else:
        if not message_string and 'voice' in update_details['message'].keys():
            response_details['kwargs']['message_text'] = 'Transcription failed. Can you type that out instead?'
        elif not document_reply and 'photo' in update_details['message'].keys():
            response_details['kwargs']['message_text'] = 'Recognition failed. Can you try again?'
        else:
            response_details['function'] = 'pass'

    return response_details

def monitor_telegram():

    from os import environ
    from time import time
    from labpack.storage.appdata import appdataClient
    telegram_data_client = appdataClient('Telegram', prod_name='beenServedBot')

# construct bot client
    from labpack.messaging.telegram import telegramBotClient
    init_kwargs = {
        'access_token': environ['TELEGRAM_ACCESS_TOKEN'],
        'bot_id': int(environ['TELEGRAM_BOT_ID'])
    }
    admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
    telegram_bot_client = telegramBotClient(**init_kwargs)

# retrieve update record
    update_key = 'last-update.yaml'
    update_filter = telegram_data_client.conditional_filter([{ 0: { 'must_contain': ['%s$' % update_key ]}}])
    if not telegram_data_client.list(update_filter):
        telegram_data_client.create(update_key, { 'last_update': 0 })
    update_record = telegram_data_client.read(update_key)

# get updates from telegram
    last_update = update_record['last_update']
    updates_details = telegram_bot_client.get_updates(last_update)
    update_list = []
    if updates_details['json']['result']:
        update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
        offset_details = { 'last_update': update_list[-1]['update_id']}
        telegram_data_client.create(update_key, offset_details)

# process updates
    from pprint import pprint
    for update in update_list:
        pprint(update)
        user_id = update['message']['from']['id']
        contact_id = 'telegram_%s' % user_id
        record_key = 'incoming/%s/%s.json' % (contact_id, str(time()))
        telegram_data_client.create(record_key, update)

    # analyze message
        analyze_kwargs = {
            'update_details': update,
            'user_id': user_id,
            'telegram_bot_client': telegram_bot_client,
            'telegram_data_client': telegram_data_client
        }
        response_details = analyze_message(**analyze_kwargs)
        if response_details['function'] == 'send_message':
            telegram_bot_client.send_message(**response_details['kwargs'])
        elif response_details['function'] == 'send_photo':
            telegram_bot_client.send_photo(**response_details['kwargs'])

    # save response
        record_key = 'outgoing/%s/%s.json' % (contact_id, str(time()))
        telegram_data_client.create(record_key, response_details)

    return True

if __name__ == '__main__':

    from os import path, environ
    if path.exists('../../cred'):
        from server.utils import inject_envvar
        inject_envvar('../../cred')
    environ['SERVER_DATA_PATH'] = '../../data'
    environ['GOOGLE_VISION_KEYS'] = '../../keys/google-vision.json'
    environ['GOOGLE_TRANSLATE_KEYS'] = '../../keys/google-vision.json'
    monitor_telegram()
