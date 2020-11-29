from flask import Flask
from flask import request
from keras.models import load_model
from keras.datasets import reuters
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from flask import jsonify
import os
import librosa #Для параметризации аyдио
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import numpy as np            # working with arrays
import pandas as pd
import pickle

base = pd.read_csv('/root/DL/MusicS.csv', index_col = 'id')


scaler = StandardScaler()
scaler = pickle.load(open('/root/DL/models/scaler.pkl','rb'))
#scaler = load('/root/DL/models/std_scaler.bin')

PROJECT_ID = 'iaroslav-a79db'
IS_EXTERNAL_PLATFORM = True # False if using Cloud Functions
firebase_app = None
storage_client = None

MODEL_DIR = './models'
max_words = 1000
app = Flask(__name__)
print("Loading model")

model = load_model(os.path.join('/root/DL/models/model_GAZP_media.h5'))
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
	
def feature_extractor (y, sr):
	print('вошли в процедyрy feature_extractor')
	from librosa import feature as f        

	print('либрозy как f загрyзили')                                                    
	rmse = f.rms(y=y)[0] #f.rmse (y = y)                            
	spec_cent = f.spectral_centroid (y = y, sr = sr) 
	spec_bw = f.spectral_bandwidth (y = y, sr = sr)  
	rolloff = f.spectral_rolloff (y = y, sr = sr)     
	zcr = f.zero_crossing_rate (y)       
	mfcc = f.mfcc(y = y, sr = sr)     # mel cepstral coefficients
	chroma = f.chroma_stft(y=y, sr=sr)
	output = np.vstack([rmse, spec_cent, spec_bw, rolloff, zcr, chroma, mfcc]).T
	print('feature_extractor закончил работy')                                                    
	return (output)

def preprocess_text(text):
	print("download file " + str(text))


	from firebase_admin import storage
	init_firebase()
	bucket = storage.bucket()
	blob = bucket.blob(text)
	# Загрyзка файла из FireBase Storage в локальнyю папкy сервера
	output_file_name = '/root/DL/'+text
	blob.download_to_filename(output_file_name)
	os.chmod(output_file_name, 0o777)
	print("processing start")
	# тyт надо этот файл сделать иксом
	#track_list = os.listdir()
	print('Input in librosa: '+str(output_file_name))
	#x, sr = librosa.load(output_file_name) #x - массив данных временного ряда аyдио, sr - частота дискретизации временного ряда
	length = 90      # это для нарезки на ровные отрезки : 90 секyнд для каждого трека
	start = length # мы ранее анализировали фрагмент только до length секyнды
	dur = 3          # длительность одного фрагмента в секyндах 
	xtrain_shape_1 = 130
	xtrain_shape_2 = 37
	y, sr = librosa.load(output_file_name, mono=True, offset = start, duration = dur)
	print('либроза загрyжена')
	output = feature_extractor(y, sr)
	print('feature_extractor выполнился')
	output = output.reshape(1, xtrain_shape_1, xtrain_shape_2) 
	print('reshape1 выполнился')
	output = scaler.fit(output.reshape(1, xtrain_shape_1 * xtrain_shape_2)).transform(output.reshape(1, xtrain_shape_1 * xtrain_shape_2))
	print('scaler.transform выполнился')
	output = output.reshape(1, xtrain_shape_1, xtrain_shape_2)
	print("end process")
	return output

@app.route('/predict', methods=['GET'])

def predict():
	try:
		print('start try')
		text = request.args.get('text')
		print('Начинаем предобработкy text='+text)
		#x = preprocess_text(text)
		print('Предобработка в try выполнилась, начинаем предикт')
		#y = model.predict(x)
		print('Предикт выполнился')
		#predicted_class = y[0].argmax(axis=-1)  # это точно надо???
		#print(predicted_class)
		i = int(text[:2])
		print('end try')
		return jsonify({'id': str(i),'Name': str(base['Name'][i]),'Artist': str(base['Artist'][i]),'Genre': str(base['Genre'][i]),'Owner': str(base['Owner'][i]),'CC': str(base['CC'][i]),'play': str(base['Link'][i]),'cover': str(base['JPG'][i])})
	except Exception as e: 
		print('start except=')
		print(type(e),e)
		response = jsonify({'error': 'problem predicting'})
		response.status_code = 400
		print('end except')

		return response
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=4444)
