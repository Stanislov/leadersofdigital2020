#-*- coding: UTF-8 -*-
from sys import argv
script, first = argv

print("-"+str(argv)+"-")


PROJECT_ID = 'iaroslav-a79db'

IS_EXTERNAL_PLATFORM = True # False if using Cloud Functions

firebase_app = None

def init_firebase():
    global firebase_app
    if firebase_app:
        return firebase_app

    import firebase_admin
    from firebase_admin import credentials

    if IS_EXTERNAL_PLATFORM:
        print('get key for init_firebase')
        cred = credentials.Certificate('/root/DL/key.json')
    else:
        cred = credentials.ApplicationDefault()

    firebase_app = firebase_admin.initialize_app(cred, {'storageBucket': 'iaroslav-a79db.appspot.com'})      #f'{PROJECT_ID}.appspot.com'})

    return firebase_app

storage_client = None

def init_storage():
    global storage_client
    if storage_client:
        return storage_client

    from google.cloud import storage
    if IS_EXTERNAL_PLATFORM:
        print('get key for init_firebase')
        storage_client = storage.Client.from_service_account_json('/root/DL/key.json')
    else:
       storage_client = storage.Client()

    '''
    app = init_firebase()
    storage_client = storage.Client(credentials=app.credential.get_credential(), project=app.project_id)
    '''

    return storage_client

from firebase_admin import storage
#from google.cloud import storage

init_firebase()

# Создание текстового файла в хранилище
bucket = storage.bucket()
blob = bucket.blob(first)
# Загрузка файла из FireBase Storage в гугл-диск 
output_file_name = '/root/DL/hello.txt'
blob.download_to_filename(output_file_name)
