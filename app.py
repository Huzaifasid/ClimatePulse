from flask import Flask, render_template, jsonify, request
import data_utils
import os

app = Flask(__name__)

# Load data once at startup
try:
    df = data_utils.load_data()
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    df = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    locations = data_utils.get_locations(df)
    return jsonify(locations)

@app.route('/api/summary/<location>')
def get_summary(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    summary = data_utils.get_stats_summary(df, location)
    return jsonify(summary)

@app.route('/api/trends/<location>')
def get_trends(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    trends = data_utils.get_annual_trends(df, location)
    return jsonify(trends)

@app.route('/api/monthly/<location>/<int:year>')
def get_monthly(location, year):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    monthly = data_utils.get_monthly_averages(df, location, year)
    return jsonify(monthly)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
