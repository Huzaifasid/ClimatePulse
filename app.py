from flask import Flask, render_template, jsonify, request, session
import data_utils
import ml_models
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'climate-pulse-secret-key-2026')

# Store uploaded dataframes in memory (keyed by session ID)
uploaded_data_store = {}

# Load default data once at startup
try:
    default_df = data_utils.load_data()
    print("Default data loaded successfully.")
except Exception as e:
    print(f"Error loading default data: {e}")
    default_df = None

def get_current_df():
    """Get the dataframe for current session (uploaded or default)"""
    session_id = session.get('data_session_id')
    if session_id and session_id in uploaded_data_store:
        return uploaded_data_store[session_id]['data']
    return default_df

def get_data_source_info():
    """Get info about current data source"""
    session_id = session.get('data_session_id')
    if session_id and session_id in uploaded_data_store:
        info = uploaded_data_store[session_id]
        return {
            'type': 'custom',
            'filename': info.get('filename', 'Unknown'),
            'record_count': len(info['data']),
            'warnings': info.get('warnings', []),
            'is_climate_data': info.get('is_climate_data', False)
        }
    return {
        'type': 'default',
        'filename': 'lac_data.csv',
        'record_count': len(default_df) if default_df is not None else 0,
        'warnings': [],
        'is_climate_data': True
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    locations = data_utils.get_locations(df)
    return jsonify(locations)

@app.route('/api/summary/<location>')
def get_summary(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    summary = data_utils.get_stats_summary(df, location)
    return jsonify(summary)

@app.route('/api/trends/<location>')
def get_trends(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    trends = data_utils.get_annual_trends(df, location)
    return jsonify(trends)

@app.route('/api/monthly/<location>/<int:year>')
def get_monthly(location, year):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    monthly = data_utils.get_monthly_averages(df, location, year)
    return jsonify(monthly)

# ========== ML MODEL ENDPOINTS ==========

@app.route('/api/ml/train-all/<location>')
def train_all_models(location):
    """Train all ML models for a location and return summary"""
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        results = ml_models.get_all_models_summary(df, location)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/linear-regression/<location>')
def ml_linear_regression(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_linear_regression(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/decision-tree/<location>')
def ml_decision_tree(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_decision_tree(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/random-forest/<location>')
def ml_random_forest(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_random_forest(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/logistic-regression/<location>')
def ml_logistic_regression(location):
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_logistic_regression(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/knn/<location>')
def ml_knn(location):
    df = get_current_df()
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
    df = get_current_df()
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
    df = get_current_df()
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
    df = get_current_df()
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
    df = get_current_df()
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
    df = get_current_df()
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    try:
        result = ml_models.train_neural_network(df, location)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== FILE UPLOAD ENDPOINTS ==========

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Only CSV files are allowed'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        
        # Process the upload
        result = data_utils.load_data_from_upload(file_content, file.filename)
        
        if result['success']:
            # Generate session ID if not exists
            if 'data_session_id' not in session:
                session['data_session_id'] = str(uuid.uuid4())
            
            session_id = session['data_session_id']
            
            # Store the dataframe in memory
            uploaded_data_store[session_id] = {
                'data': result['data'],
                'filename': file.filename,
                'warnings': result['validation'].get('warnings', []),
                'is_climate_data': result['validation'].get('is_climate_data', False)
            }
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'warnings': result['validation'].get('warnings', []),
                'record_count': len(result['data']),
                'locations': data_utils.get_locations(result['data']),
                'is_climate_data': result['validation'].get('is_climate_data', False)
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'errors': result['validation'].get('errors', [])
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/data-source')
def get_data_source():
    """Get current data source information"""
    return jsonify(get_data_source_info())

@app.route('/api/reset-data', methods=['POST'])
def reset_data():
    """Reset to default data source"""
    session_id = session.get('data_session_id')
    
    if session_id and session_id in uploaded_data_store:
        del uploaded_data_store[session_id]
    
    if 'data_session_id' in session:
        del session['data_session_id']
    
    return jsonify({
        'success': True,
        'message': 'Reset to default data source',
        'data_source': get_data_source_info()
    })

@app.route('/api/data-table')
def get_data_table():
    """Get a preview of the current data in table format"""
    df = get_current_df()
    if df is None:
        return jsonify([])
    
    # Return first 50 rows as list of dicts
    return jsonify(df.head(50).fillna('').to_dict(orient='records'))

@app.route('/api/required-columns')
def get_required_columns():
    """Get list of required columns for CSV upload"""
    return jsonify(data_utils.get_required_columns())

# Required for Vercel deployment (comment out for local development)
if __name__ == '__main__':
    app.run(debug=True, port=5000)



