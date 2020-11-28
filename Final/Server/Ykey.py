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
        cred = credentials.Certificate('key.json')
    else:
        cred = credentials.ApplicationDefault()

    firebase_app = firebase_admin.initialize_app(cred, {
        # 'projectId': PROJECT_ID,
        'storageBucket': f"{PROJECT_ID}.appspot.com"
    })

    return firebase_app

print(f"{PROJECT_ID}.appspot.com")

storage_client = None

def init_storage():
    global storage_client
    if storage_client:
        return storage_client

    from google.cloud import storage
    if IS_EXTERNAL_PLATFORM:
        storage_client = storage.Client.from_service_account_json('key.json')

    else:
       storage_client = storage.Client()

    '''
    app = init_firebase()
    storage_client = storage.Client(credentials=app.credential.get_credential(), project=app.project_id)
    '''

    return storage_client

from firebase_admin import storage
init_firebase()

# Создание текстового файла в хранилище
bucket = storage.bucket()
blob = bucket.blob('hello.txt')
blob.upload_from_string('hello world')
# upload via file
# blob.upload_from_filename(source_file_name)

# download
output = blob.download_as_string()
# download to file
# blob.download_to_filename(output_file_name)

from firebase_admin import storage
init_firebase()

# Создание текстового файла в хранилище
bucket = storage.bucket()
blob = bucket.blob('output20201124.txt')
# blob.upload_from_string('hello world')
#  Так можно загрузить файл из гугл-диска в FireBase Storage
#source_file_name = '/content/drive/My Drive/Hacaton_LD2020/20201127-Final/output20201124.txt'
#blob.upload_from_filename(source_file_name)

# download
#output = blob.download_as_string()
# download to file
# blob.download_to_filename(output_file_name)

from firebase_admin import storage
init_firebase()

# Создание текстового файла в хранилище
bucket = storage.bucket()
blob = bucket.blob('output20201124.txt')
# blob.upload_from_string('hello world')
#  Так можно загрузить файл из гугл-диска в FireBase Storage
#source_file_name = '/content/drive/My Drive/Hacaton_LD2020/20201127-Final/output20201124.txt'
#blob.upload_from_filename(source_file_name)

# download
#output = blob.download_as_string()
# Загрузка файла из FireBase Storage в гугл-диск 
#output_file_name = '/content/drive/My Drive/Hacaton_LD2020/20201127-Final/output20201125.txt'
#blob.download_to_filename(output_file_name)

 # Прочитать файлы и папки в FireBase Storage
 #files = bucket.list_blobs(prefix='')
 #for f in files:
 #    print(f.name)