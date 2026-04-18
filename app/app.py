from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load all models
rf = pickle.load(open('../models/rf_model.pkl', 'rb'))
xgb = pickle.load(open('../models/xgb_model.pkl', 'rb'))
lr = pickle.load(open('../models/lr_model.pkl', 'rb'))
scaler = pickle.load(open('../models/scaler.pkl', 'rb'))

def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 200:
        return "Poor"
    elif aqi <= 300:
        return "Very Poor"
    else:
        return "Severe"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    features = np.array([[
        data['city'], data['pm25'], data['pm10'],
        data['no'], data['no2'], data['nox'],
        data['nh3'], data['co'], data['so2'],
        data['o3'], data['benzene']
    ]])

    model_choice = data.get('model', 'rf')  # default = RF

    if model_choice == 'rf':
        prediction = rf.predict(features)

    elif model_choice == 'xgb':
        prediction = xgb.predict(features)

    elif model_choice == 'lr':
        features_scaled = scaler.transform(features)
        prediction = lr.predict(features_scaled)

    else:
        return jsonify({"error": "Invalid model choice"}), 400

    return jsonify({
        "model_used": model_choice,
        "AQI": float(prediction[0]),
        "category": get_aqi_category(float(prediction[0]))
    })


if __name__ == '__main__':
    app.run(debug=True)