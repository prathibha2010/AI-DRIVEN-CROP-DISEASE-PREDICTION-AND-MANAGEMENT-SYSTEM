from flask import Flask, render_template, request, send_from_directory, redirect
import random, os
from werkzeug.utils import secure_filename
from functions import img_predict, get_diseases_classes,
get_crop_recommendation,
get_fertilizer_recommendation, soil_types, Crop_types,
crop_list.get_fertilizer_from_crop_disease
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import json
import os
import pickle
app Flask(name
random.seed(0)
app.config['SECRET_KEY'] = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Load crop prediction model and class indices
model_path=r"C:\Users\pooji\OneDrive\档\majorproject|\AgriGo-
main\AgriGo\models\DL_models\predfer_model.h5"
model load model(model_path)
class_indices_path =
os.path.join(os.path.dirname(os.path.dirname(file))'class_indices.json')
with open(class_indices_path, 'r') as f:
class_indices = json.load(f)
class_indices = {int(k): v for k, v in class_indices.items()}
def load_and_preprocess_image(image_path, target_size=(224, 224)):
img Image.open(image_path)
img img.resize(target_size)
img_array = np.array(img)
img_array = np.expand_dims(img_array, axis-0)img_array = img_array.astype('float32')/255.
return img_array
def predict_image_class(model, image_path, class_indices):
preprocessed_image = load_and_preprocess_image(image_path)
predictions = model.predict(preprocessed_image)
predicted_class_index = np.argmax(predictions, axis=1)[0]
predicted_class_name = class_indices.get(predicted_class_index, "Unknown")
return predicted_class_name
@app.route('/uploads/<filename>')
def send_file(filename):
return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
dir_path = os.path.dirname(os.path.realpath(__file__))@app.route('/', methods=['GET', 'POST'])
def index():
return render_template('index.html')
@app.route('/crop-prediction-redirect')
def crop_prediction_redirect():
return redirect('/crop-prediction')
@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
if request.method == "POST":
to_predict_list = request.form.to_dict()
to_predict_list = list(to_predict_list.values())
to_predict_list = list(map(float, to_predict_list))
result = get_crop_recommendation(to_predict_list)
return render_template("recommend_result.html", result-result)
else:
notebook_url = 'crop-recommendation.ipynb'
return render_template('crop-recommend.html', notebook_url=notebook_url)
@app.route('/fertilizer-recommendation', methods=['GET', 'POST'])
def fertilizer_recommendation():
import pickle
from sklearn.preprocessing import LabelEncoder
if request.method == "POST":
form_data = request.form.to_dict()
#Extract features from form data
temperature = float(form_data.get('temperature', 0))
humidity = float(form_data.get('humidity', 0))
0)) moisture = float(form_data.get('moisture',
nitrogen = float(form_data.get('N', 0))
potassium = float(form_data.get('K', 0))
phosphorous = float(form_data.get('P', 0))
soil_type = form_data.get('soil', ").strip()
crop_type = form_data.get('crop', ").strip())
#Validate categorical inputs
if not soil_type or not crop_type:
error_msg = "Soil Type and Crop Type must be selected."
return render_template('fertilizer recommend.html',soil_types=enumerate(soil_types),
crop_types=enumerate(Crop_types), error-error_msg)
#Load label encoders
soil_le_path = os.path.join(os.path.dirname(file), 'models', 'ML_models',
'soil_type_le.pkl')
= crop_le_path os.path.join(os.path.dirname(file), 'models', 'ML_models',
'crop_type_le.pkl)
with open(soil_le_path, 'rb') as f:
soil_le = pickle.load(f)
with open(crop_le_path, 'rb') as f:
crop_le pickle.load(f)
# Encode categorical feature:
try:
soil_encoded = soil_le.transform([soil_type])[0]
crop_encoded = crop_le.transform([crop_type])[0]
except ValueError as e:
error_msg = f"Invalid Soil Type or Crop Type: {e}"return render_template('fertilizer
recommend.html',soil_types=enumerate(soil_types),
crop_types=enumerate(Crop_types), error=error_msg)
# Prepare feature list in correct order
features=[temperature,humidity,moisture,soil_encoded,crop_encoded,nitrogen,
potassium, phosphorous]
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Features for prediction: (features}")
result = get_fertilizer_recommendation(features)
logging.debug(f"Prediction result: {result}"
return render_template("recommend_result.html", result=result)
else:
notebook_url = 'fertilizer_recommendation.ipynb'
return render_template ('fertilizer-recommend.html', soil_types=enumerate(soil_types),
crop_types=enumerate(Crop_types), notebook_url=notebook_url)@app.route('/crop-prediction', methods=['GET', 'POST'])
def crop_prediction():
if request.method == 'POST':
file = request.files['file']
if not file:
return render_template('crop-prediction.html', error="No file uploaded")
filename = secure_filename(file.filename)
basepath = os.path.dirname(_file_)
file_path = os.path.join(basepath, UPLOAD_FOLDER, filename)
file.save(file_path)
print("Saved file to:", file_path)
if not os.path.exists(file_path):
return render_template('crop-prediction.html', error="File save failed or not found.")
predicted_class_name = predict_image_class(model, file_path, class_indices)
fertilizer-get_fertilizer_from_crop_disease(predicted_class_name)
print("Predicted crop/disease:", predicted_class_name)print("Recommended fertilizer:", fertilizer)
return render_template('crop-prediction-result.html', image_file_name=filename,
result-predicted_class_name,fertilizer-fertilizer)
else:
return render_template('crop-prediction.html')
@app.route('/crop-disease')
def crop_disease_redirect():
return redirect('/crop-prediction')
if __name__=='__ main__':
app.run(debug=True)#functions code
import os
import pickle
import numpy as np
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.models import load_model
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
def get_model(path):
model = load_model(path, compile=False)
return modeldef img_predict(path, crop):
# Load and preprocess image
data = load_img(path, target_size=(224, 224, 3))
data = np.asarray(data).astype('float32') / 255.0
data = np.expand_dims(data, axis=0) # Add batch dimension
# Load model
model = get_model(os.path.join(BASE_DIR, 'models', 'DL_models', f' {crop}_model.h5'))
# Predict
preds = model.predict(data)if len(crop_diseases_classes[crop]) > 2:
predicted = np.argmax(preds[0])
else:
p = preds[0]
predicted = int(np.round(p)[0])
return predicted
def get_diseases_classes(crop, prediction):
crop_classes = crop_diseases_classes[crop]
return crop_classes [prediction][1].replace("_", "")
def get_crop_recommendation(item):
scaler_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'crop_scaler.pkl')
model_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'crop_model.pkl')
with open(scaler_path, 'rb') as f:crop_scaler = pickle.load(f)
with open(model_path, 'rb') as f:
crop_model = pickle.load(f)
scaled_item = crop_scaler.transform(np.array(item).reshape(-1, len(item)))
prediction = crop_model.predict(scaled_item)[0]
return crops[prediction]
def get_fertilizer_recommendation(features):
model_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'fertilizer_model.pkl')
with open(model_path, 'rb') as f:
fertilizer_model = pickle.load(f)
prediction = fertilizer_model.predict([features])[0]
return predictioncrop_diseases_classes = {'strawberry': [(0, 'Leaf_scorch'), (1, 'healthy')],
'patato':
[(0, 'Early_blight'),
(1, 'Late_blight'),
(2, 'healthy')],
'
corn': [(0, 'Cercospora_leaf_spot Gray_leaf_spot'),
Cre
(1, 'Common_rust_'),
(2, 'Northern_Leaf_Blight'),
(3, 'healthy')],
'apple': [(0, 'Apple_scab'),
(1, 'Black_rot'),
(2, 'Cedar_apple_rust'),
(3, 'healthy')],
'cherry': [(0, 'Powdery_mildew'),
(1, 'healthy')],
'grape': [(0, 'Black_rot'),
(1, 'Esca_(Black_Measles)'),
(2, 'Leaf_blight_(Isariopsis_Leaf_Spot)'),
(3, 'healthy')],
'peach': [(0, 'Bacterial_spot'), (1, 'healthy')],
'pepper': [(0, 'Bacterial_spot'),
(1, 'healthy')],
'tomato': [(0, 'Bacterial_spot'),
(1, 'Early_blight'),
(2, 'Late_blight'),
(3, 'Leaf Mold'),
(4, 'Septoria_leaf_spot'),
(5, 'Spider_mites Two-spotted_spider_mite'),
(6, 'Target_Spot'),
(7, "Tomato_Yellow_Leaf_Curl_Virus'),
(8, 'Tomato mosaic_virus'),
(9, 'healthy')]}crop_list = list(crop_diseases_classes.keys())
crops = {'apple': 1, 'banana': 2, 'blackgram': 3, 'chickpea': 4, 'coconut': 5, 'coffee': 6, 'cotton': 7, 'grapes': 8, 'jute': 9, 'kidneybeans': 10, 'lentil': 11, 'maize': 12, 'mango': 13, 'mothbeans': 14, 'mungbean': 15, 'muskmelon': 16, 'orange': 17, 'papaya': 18, 'pigeonpeas': 19, 'pomegranate': 20, 'rice': 21, 'watermelon': 22}
crops = list(crops.keys())
soil_types = ['Black', 'Clayey', 'Loamy', 'Red', 'Sandy']
Crop_types = ['Barley', 'Cotton', 'Ground Nuts', 'Maize', 'Millets', 'Oil seeds', 'Paddy', 'Pulses', 'Sugarcane', 'Tobacco', 'Wheat']
fertilizer_classes = ['10-26-26', '14-35-14', '17-17-17', '20-20', '28-28', 'DAP', 'Urea']
