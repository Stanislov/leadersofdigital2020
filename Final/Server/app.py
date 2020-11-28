from flask import Flask
from flask import request
from keras.models import load_model
from keras.datasets import reuters
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from flask import jsonify
import os

PROJECT_ID = 'iaroslav-a79db'
IS_EXTERNAL_PLATFORM = True # False if using Cloud Functions
firebase_app = None
storage_client = None

MODEL_DIR = './models'
max_words = 1000
app = Flask(__name__)
print("Loading model")

model = load_model(os.path.join(MODEL_DIR, 'reuters_model.hdf5'))
#model.load_model('reuters_model.hdf5')
print('model loaded')

# we need the word index to map words to indices
word_index = reuters.get_word_index()
tokenizer = Tokenizer(num_words=max_words)


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

def preprocess_text(text):
	print("download file " + str(text))

	from firebase_admin import storage
	init_firebase()
	bucket = storage.bucket()
	blob = bucket.blob(text)
	# Загрузка файла из FireBase Storage в локальную папку сервера
	output_file_name = '/root/DL/hello.txt'
	blob.download_to_filename(output_file_name)

	print("processing start")
	word_sequence = text_to_word_sequence(text)
	indices_sequence = [[word_index[word] if word in word_index else 0 for word in word_sequence]]
	x = tokenizer.sequences_to_matrix(indices_sequence, mode='binary')
		
	print("end process")
	return x

@app.route('/predict', methods=['GET'])

def predict():
	try:
		print('start try')
		text = request.args.get('text')
		x = preprocess_text(text)
		y = model.predict(x)
		predicted_class = y[0].argmax(axis=-1)
		print(predicted_class)
		print('end try')
		return jsonify({'id': str(predicted_class),'Name': str('Поболело и прошло'),'Artist': str('HENSY'),'Genre': str('Поп'),'Owner': str('GOLDEN SOUND'),'CC': str(1)})
	except:
		print('start except')
		response = jsonify({'error': 'problem predicting'})
		response.status_code = 400
		print('end except')

		return response
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=4444)
