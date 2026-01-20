from flask import Flask, render_template, jsonify, request
import data_utils
import ml_models
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

# ========== ML MODEL ENDPOINTS ==========

@app.route('/api/ml/train-all/<location>')
def train_all_models(location):
    """Train all ML models for a location and return summary"""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        results = ml_models.get_all_models_summary(df, location)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/linear-regression/<location>')
def ml_linear_regression(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_linear_regression(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/decision-tree/<location>')
def ml_decision_tree(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_decision_tree(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/random-forest/<location>')
def ml_random_forest(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_random_forest(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/logistic-regression/<location>')
def ml_logistic_regression(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_logistic_regression(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/knn/<location>')
def ml_knn(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        n_neighbors = request.args.get('n', 5, type=int)
        result = ml_models.train_knn_classifier(df, location, n_neighbors)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/kmeans/<location>')
def ml_kmeans(location):
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        n_clusters = request.args.get('n', 4, type=int)
        result = ml_models.train_kmeans(df, location, n_clusters)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/reinforcement-learning/<location>')
def ml_reinforcement_learning(location):
    """Reinforcement Learning - Irrigation Policy Optimization"""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        episodes = request.args.get('episodes', 100, type=int)
        result = ml_models.run_reinforcement_learning(df, location, episodes)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/rule-based/<location>')
def ml_rule_based(location):
    """Rule-Based Expert System - Language of Logic"""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.run_rule_based_system(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/ensemble/<location>')
def ml_ensemble(location):
    """Ensemble Techniques - Voting, Bagging, Boosting"""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_ensemble_models(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/neural-network/<location>')
def ml_neural_network(location):
    """Neural Network - Multi-Layer Perceptron"""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_neural_network(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel deployment (comment out for local development)
if __name__ == '__main__':
    app.run(debug=True, port=5000)



