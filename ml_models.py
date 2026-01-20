"""
Machine Learning Models for Rainfall & Climate Analysis
Implements: KNN, Linear Regression, Logistic Regression, Decision Tree, Random Forest, K-Means
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import (
    mean_squared_error, r2_score, accuracy_score, 
    confusion_matrix, classification_report, silhouette_score
)
import os

# Feature columns for ML models
FEATURE_COLS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'RH2M', 'WS2M_MAX', 'QV2M']
TARGET_REGRESSION = 'PRECTOTCORR'  # Rainfall prediction
RAIN_THRESHOLD = 1.0  # mm - for classification (rain vs no rain)

# Store trained models in memory
trained_models = {}


def prepare_data(df, location):
    """Prepare and clean data for ML models"""
    data = df[df['Locations'] == location].copy()
    
    # Check if we have data for this location
    if len(data) == 0:
        raise ValueError(f"No data found for location: {location}")
    
    # Ensure all required columns exist, fill with defaults if missing
    defaults = {
        'T2M': 25.0, 'T2M_MAX': 30.0, 'T2M_MIN': 20.0,
        'RH2M': 50.0, 'WS2M_MAX': 5.0, 'QV2M': 10.0,
        'PRECTOTCORR': 0.0
    }
    
    for col, default_val in defaults.items():
        if col not in data.columns:
            data[col] = default_val
        else:
            # Fill NaN values with defaults
            data[col] = data[col].fillna(default_val)
    
    # Ensure numeric types
    for col in FEATURE_COLS + [TARGET_REGRESSION]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(defaults.get(col, 0))
    
    # Check minimum sample size (need at least 10 samples for train/test split)
    MIN_SAMPLES = 10
    if len(data) < MIN_SAMPLES:
        raise ValueError(f"Insufficient data for {location}: only {len(data)} samples found, need at least {MIN_SAMPLES}")
    
    X = data[FEATURE_COLS].values
    y_regression = data[TARGET_REGRESSION].values
    y_classification = (data[TARGET_REGRESSION] > RAIN_THRESHOLD).astype(int).values
    
    return X, y_regression, y_classification, data


def train_linear_regression(df, location):
    """Train Linear Regression for rainfall prediction"""
    X, y, _, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    trained_models[f'linear_regression_{location}'] = {'model': model, 'scaler': scaler}
    
    return {
        'model_type': 'Linear Regression',
        'r2_score': round(r2_score(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'coefficients': dict(zip(FEATURE_COLS, model.coef_.round(4).tolist())),
        'sample_predictions': y_pred[:10].round(2).tolist(),
        'sample_actual': y_test[:10].round(2).tolist()
    }


def train_decision_tree(df, location):
    """Train Decision Tree Regressor"""
    X, y, _, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = DecisionTreeRegressor(max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    trained_models[f'decision_tree_{location}'] = {'model': model, 'scaler': None}
    
    return {
        'model_type': 'Decision Tree',
        'r2_score': round(r2_score(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'feature_importance': dict(zip(FEATURE_COLS, model.feature_importances_.round(4).tolist())),
        'sample_predictions': y_pred[:10].round(2).tolist(),
        'sample_actual': y_test[:10].round(2).tolist()
    }


def train_random_forest(df, location):
    """Train Random Forest Regressor"""
    X, y, _, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    trained_models[f'random_forest_{location}'] = {'model': model, 'scaler': None}
    
    return {
        'model_type': 'Random Forest',
        'r2_score': round(r2_score(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'feature_importance': dict(zip(FEATURE_COLS, model.feature_importances_.round(4).tolist())),
        'n_estimators': 100,
        'sample_predictions': y_pred[:10].round(2).tolist(),
        'sample_actual': y_test[:10].round(2).tolist()
    }


def train_logistic_regression(df, location):
    """Train Logistic Regression for rain/no-rain classification"""
    X, _, y, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)
    
    trained_models[f'logistic_regression_{location}'] = {'model': model, 'scaler': scaler}
    
    return {
        'model_type': 'Logistic Regression',
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'confusion_matrix': cm.tolist(),
        'labels': ['No Rain', 'Rain'],
        'classification_report': classification_report(y_test, y_pred, target_names=['No Rain', 'Rain'], output_dict=True)
    }


def train_knn_classifier(df, location, n_neighbors=5):
    """Train KNN Classifier"""
    X, _, y, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)
    
    trained_models[f'knn_{location}'] = {'model': model, 'scaler': scaler}
    
    return {
        'model_type': 'K-Nearest Neighbors',
        'n_neighbors': n_neighbors,
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'confusion_matrix': cm.tolist(),
        'labels': ['No Rain', 'Rain'],
        'classification_report': classification_report(y_test, y_pred, target_names=['No Rain', 'Rain'], output_dict=True)
    }


def train_kmeans(df, location, n_clusters=4):
    """Train K-Means Clustering (Unsupervised)"""
    X, _, _, data = prepare_data(df, location)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)
    
    silhouette = silhouette_score(X_scaled, labels)
    
    # Get cluster statistics
    data_with_clusters = data.copy()
    data_with_clusters['Cluster'] = labels
    
    cluster_stats = []
    for i in range(n_clusters):
        cluster_data = data_with_clusters[data_with_clusters['Cluster'] == i]
        cluster_stats.append({
            'cluster': i,
            'count': len(cluster_data),
            'avg_temp': round(cluster_data['T2M'].mean(), 2),
            'avg_rainfall': round(cluster_data['PRECTOTCORR'].mean(), 2),
            'avg_humidity': round(cluster_data['RH2M'].mean(), 2)
        })
    
    trained_models[f'kmeans_{location}'] = {'model': model, 'scaler': scaler}
    
    return {
        'model_type': 'K-Means Clustering',
        'n_clusters': n_clusters,
        'silhouette_score': round(silhouette, 4),
        'cluster_centers': model.cluster_centers_.round(4).tolist(),
        'cluster_stats': cluster_stats,
        'feature_names': FEATURE_COLS
    }


def get_all_models_summary(df, location):
    """Train all models and return summary"""
    results = {
        'location': location,
        'models': {}
    }
    
    try:
        results['models']['linear_regression'] = train_linear_regression(df, location)
    except Exception as e:
        results['models']['linear_regression'] = {'error': str(e)}
    
    try:
        results['models']['decision_tree'] = train_decision_tree(df, location)
    except Exception as e:
        results['models']['decision_tree'] = {'error': str(e)}
    
    try:
        results['models']['random_forest'] = train_random_forest(df, location)
    except Exception as e:
        results['models']['random_forest'] = {'error': str(e)}
    
    try:
        results['models']['logistic_regression'] = train_logistic_regression(df, location)
    except Exception as e:
        results['models']['logistic_regression'] = {'error': str(e)}
    
    try:
        results['models']['knn'] = train_knn_classifier(df, location)
    except Exception as e:
        results['models']['knn'] = {'error': str(e)}
    
    try:
        results['models']['kmeans'] = train_kmeans(df, location)
    except Exception as e:
        results['models']['kmeans'] = {'error': str(e)}
    
    try:
        results['models']['reinforcement_learning'] = run_reinforcement_learning(df, location)
    except Exception as e:
        results['models']['reinforcement_learning'] = {'error': str(e)}
    
    try:
        results['models']['rule_based'] = run_rule_based_system(df, location)
    except Exception as e:
        results['models']['rule_based'] = {'error': str(e)}
    
    try:
        results['models']['ensemble'] = train_ensemble_models(df, location)
    except Exception as e:
        results['models']['ensemble'] = {'error': str(e)}
    
    try:
        results['models']['neural_network'] = train_neural_network(df, location)
    except Exception as e:
        results['models']['neural_network'] = {'error': str(e)}
    
    return results


# ========== NEURAL NETWORK (MLP) ==========
# Multi-Layer Perceptron for classification

def train_neural_network(df, location):
    """
    Neural Network: Multi-Layer Perceptron Classifier
    A deep learning approach for rain/no-rain classification
    """
    from sklearn.neural_network import MLPClassifier
    
    X, _, y, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define MLP architecture
    hidden_layers = (64, 32, 16)  # 3 hidden layers
    
    model = MLPClassifier(
        hidden_layer_sizes=hidden_layers,
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
    
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    trained_models[f'neural_network_{location}'] = {'model': model, 'scaler': scaler}
    
    return {
        'model_type': 'Neural Network (MLP)',
        'architecture': {
            'input_layer': len(FEATURE_COLS),
            'hidden_layers': list(hidden_layers),
            'output_layer': 2,
            'activation': 'ReLU',
            'optimizer': 'Adam'
        },
        'total_layers': len(hidden_layers) + 2,
        'epochs': model.n_iter_,
        'accuracy': round(acc, 4),
        'confusion_matrix': cm.tolist(),
        'labels': ['No Rain', 'Rain'],
        'loss_curve': model.loss_curve_[-10:] if hasattr(model, 'loss_curve_') else [],
        'description': 'Deep learning classifier with multiple hidden layers'
    }



# ========== ENSEMBLE TECHNIQUES ==========
# Voting, Bagging, and Boosting ensemble methods

def train_ensemble_models(df, location):
    """
    Ensemble Techniques: Combining multiple models for better predictions
    - Voting Classifier: Combines predictions from multiple classifiers
    - Bagging: Bootstrap Aggregating with Decision Trees
    - Gradient Boosting: Sequential ensemble with boosting
    """
    from sklearn.ensemble import (
        VotingClassifier, BaggingClassifier, GradientBoostingClassifier,
        AdaBoostClassifier, StackingClassifier
    )
    from sklearn.svm import SVC
    
    X, _, y, _ = prepare_data(df, location)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    ensemble_results = []
    
    # 1. Voting Classifier (Hard Voting)
    voting_clf = VotingClassifier(
        estimators=[
            ('lr', LogisticRegression(random_state=42, max_iter=1000)),
            ('dt', DecisionTreeClassifier(max_depth=10, random_state=42)),
            ('knn', KNeighborsClassifier(n_neighbors=5))
        ],
        voting='hard'
    )
    voting_clf.fit(X_train_scaled, y_train)
    voting_acc = accuracy_score(y_test, voting_clf.predict(X_test_scaled))
    ensemble_results.append({
        'name': 'Voting Classifier',
        'type': 'Hard Voting',
        'models': ['Logistic Regression', 'Decision Tree', 'KNN'],
        'accuracy': round(voting_acc, 4)
    })
    
    # 2. Bagging Classifier
    bagging_clf = BaggingClassifier(
        estimator=DecisionTreeClassifier(max_depth=10),
        n_estimators=50,
        random_state=42,
        n_jobs=-1
    )
    bagging_clf.fit(X_train_scaled, y_train)
    bagging_acc = accuracy_score(y_test, bagging_clf.predict(X_test_scaled))
    ensemble_results.append({
        'name': 'Bagging Classifier',
        'type': 'Bootstrap Aggregating',
        'base_model': 'Decision Tree',
        'n_estimators': 50,
        'accuracy': round(bagging_acc, 4)
    })
    
    # 3. AdaBoost Classifier
    ada_clf = AdaBoostClassifier(
        estimator=DecisionTreeClassifier(max_depth=3),
        n_estimators=50,
        random_state=42
    )
    ada_clf.fit(X_train_scaled, y_train)
    ada_acc = accuracy_score(y_test, ada_clf.predict(X_test_scaled))
    ensemble_results.append({
        'name': 'AdaBoost',
        'type': 'Adaptive Boosting',
        'base_model': 'Decision Tree (depth=3)',
        'n_estimators': 50,
        'accuracy': round(ada_acc, 4)
    })
    
    # 4. Gradient Boosting Classifier
    gb_clf = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    gb_clf.fit(X_train_scaled, y_train)
    gb_acc = accuracy_score(y_test, gb_clf.predict(X_test_scaled))
    gb_cm = confusion_matrix(y_test, gb_clf.predict(X_test_scaled))
    ensemble_results.append({
        'name': 'Gradient Boosting',
        'type': 'Sequential Boosting',
        'n_estimators': 100,
        'accuracy': round(gb_acc, 4)
    })
    
    # Find best ensemble
    best_ensemble = max(ensemble_results, key=lambda x: x['accuracy'])
    
    return {
        'model_type': 'Ensemble Techniques',
        'description': 'Combining multiple models for improved predictions',
        'techniques': ensemble_results,
        'best_technique': best_ensemble['name'],
        'best_accuracy': best_ensemble['accuracy'],
        'confusion_matrix': gb_cm.tolist(),
        'labels': ['No Rain', 'Rain'],
        'feature_importance': dict(zip(FEATURE_COLS, gb_clf.feature_importances_.round(4).tolist()))
    }



# ========== REINFORCEMENT LEARNING ==========
# Simulated Irrigation Policy Optimization using Q-Learning

def run_reinforcement_learning(df, location, episodes=100):
    """
    Reinforcement Learning Demo: Irrigation Policy Optimization
    
    The agent learns when to irrigate based on weather conditions.
    - States: Weather conditions (temp, humidity, recent rainfall)
    - Actions: Irrigate (1) or Don't Irrigate (0)
    - Rewards: +10 for correct decision, -5 for wrong decision
    """
    X, y_rainfall, _, data = prepare_data(df, location)
    
    # Discretize states for Q-learning
    # State = (temp_level, humidity_level, recent_rain)
    # temp_level: 0=cold(<20), 1=mild(20-30), 2=hot(>30)
    # humidity_level: 0=dry(<50), 1=moderate(50-70), 2=humid(>70)
    # recent_rain: 0=no, 1=yes
    
    def get_state(temp, humidity, rainfall):
        t = 0 if temp < 20 else (1 if temp < 30 else 2)
        h = 0 if humidity < 50 else (1 if humidity < 70 else 2)
        r = 1 if rainfall > 1 else 0
        return t * 6 + h * 2 + r  # 18 possible states
    
    def get_reward(action, actual_rainfall, humidity):
        """
        Reward logic:
        - If no rain and dry conditions: irrigating is good (+10), not irrigating is bad (-5)
        - If rain or humid: not irrigating is good (+10), irrigating wastes water (-5)
        """
        needs_water = actual_rainfall < 1 and humidity < 60
        if needs_water:
            return 10 if action == 1 else -5
        else:
            return 10 if action == 0 else -5
    
    # Q-Learning parameters
    n_states = 18
    n_actions = 2
    Q = np.zeros((n_states, n_actions))
    alpha = 0.1  # Learning rate
    gamma = 0.9  # Discount factor
    epsilon = 0.3  # Exploration rate
    
    # Training history
    rewards_per_episode = []
    
    # Sample data for training
    sample_size = min(1000, len(data))
    sample_indices = np.random.choice(len(data), sample_size, replace=False)
    
    for episode in range(episodes):
        total_reward = 0
        
        for idx in sample_indices[:100]:  # Use subset per episode
            row = data.iloc[idx]
            state = get_state(row['T2M'], row['RH2M'], row['PRECTOTCORR'])
            
            # Epsilon-greedy action selection
            if np.random.random() < epsilon:
                action = np.random.randint(n_actions)
            else:
                action = np.argmax(Q[state])
            
            # Get reward
            reward = get_reward(action, row['PRECTOTCORR'], row['RH2M'])
            total_reward += reward
            
            # Q-learning update (simplified - no next state in this demo)
            Q[state, action] += alpha * (reward - Q[state, action])
        
        rewards_per_episode.append(total_reward)
        epsilon = max(0.1, epsilon * 0.99)  # Decay exploration
    
    # Generate policy
    policy = []
    state_names = []
    for t in range(3):
        for h in range(3):
            for r in range(2):
                state = t * 6 + h * 2 + r
                action = np.argmax(Q[state])
                temp_label = ['Cold (<20°C)', 'Mild (20-30°C)', 'Hot (>30°C)'][t]
                humidity_label = ['Dry (<50%)', 'Moderate (50-70%)', 'Humid (>70%)'][h]
                rain_label = 'Recent Rain' if r else 'No Recent Rain'
                decision = 'IRRIGATE' if action == 1 else 'DON\'T IRRIGATE'
                policy.append({
                    'state': f"{temp_label}, {humidity_label}, {rain_label}",
                    'decision': decision,
                    'q_value': round(Q[state, action], 2)
                })
    
    return {
        'model_type': 'Reinforcement Learning (Q-Learning)',
        'algorithm': 'Q-Learning',
        'scenario': 'Irrigation Policy Optimization',
        'episodes': episodes,
        'final_avg_reward': round(np.mean(rewards_per_episode[-10:]), 2),
        'learning_progress': {
            'initial_reward': round(rewards_per_episode[0], 2),
            'final_reward': round(rewards_per_episode[-1], 2),
            'improvement': round(rewards_per_episode[-1] - rewards_per_episode[0], 2)
        },
        'learned_policy': policy[:6],  # Sample policies
        'q_table_shape': list(Q.shape),
        'description': 'Agent learned when to irrigate based on temperature, humidity, and recent rainfall'
    }


# ========== RULE-BASED EXPERT SYSTEM (Language of Logic) ==========

def run_rule_based_system(df, location):
    """
    Rule-Based Expert System for Weather Prediction
    Uses IF-THEN rules based on domain knowledge (Language of Logic)
    """
    X, y_rainfall, _, data = prepare_data(df, location)
    
    # Define expert rules
    rules = [
        {
            'id': 'R1',
            'name': 'High Humidity Rain Rule',
            'condition': 'IF humidity > 80% AND temp > 25°C',
            'conclusion': 'THEN rain is LIKELY',
            'logic': lambda row: row['RH2M'] > 80 and row['T2M'] > 25,
            'prediction': 1
        },
        {
            'id': 'R2',
            'name': 'Low Humidity Dry Rule',
            'condition': 'IF humidity < 40%',
            'conclusion': 'THEN rain is UNLIKELY',
            'logic': lambda row: row['RH2M'] < 40,
            'prediction': 0
        },
        {
            'id': 'R3',
            'name': 'Cold Dry Rule',
            'condition': 'IF temp < 15°C AND humidity < 60%',
            'conclusion': 'THEN rain is UNLIKELY',
            'logic': lambda row: row['T2M'] < 15 and row['RH2M'] < 60,
            'prediction': 0
        },
        {
            'id': 'R4',
            'name': 'Monsoon Indicator',
            'condition': 'IF humidity > 70% AND wind > 5 m/s AND temp > 28°C',
            'conclusion': 'THEN rain is VERY LIKELY',
            'logic': lambda row: row['RH2M'] > 70 and row['WS2M_MAX'] > 5 and row['T2M'] > 28,
            'prediction': 1
        },
        {
            'id': 'R5',
            'name': 'Moderate Conditions',
            'condition': 'IF 50% < humidity < 70% AND 20°C < temp < 30°C',
            'conclusion': 'THEN rain is POSSIBLE',
            'logic': lambda row: 50 < row['RH2M'] < 70 and 20 < row['T2M'] < 30,
            'prediction': 0.5  # Uncertain
        },
        {
            'id': 'R6',
            'name': 'Hot Dry Rule',
            'condition': 'IF temp > 35°C AND humidity < 50%',
            'conclusion': 'THEN rain is VERY UNLIKELY',
            'logic': lambda row: row['T2M'] > 35 and row['RH2M'] < 50,
            'prediction': 0
        }
    ]
    
    # Apply rules to test data
    sample_size = min(500, len(data))
    test_data = data.sample(sample_size, random_state=42)
    actual_rain = (test_data['PRECTOTCORR'] > 1).astype(int).values
    
    predictions = []
    rules_fired = {r['id']: 0 for r in rules}
    
    for idx, row in test_data.iterrows():
        pred = None
        fired_rule = None
        
        # Check rules in priority order
        for rule in rules:
            if rule['logic'](row):
                pred = rule['prediction']
                fired_rule = rule['id']
                rules_fired[rule['id']] += 1
                break
        
        if pred is None:
            pred = 0  # Default: no rain
            
        predictions.append(1 if pred >= 0.5 else 0)
    
    predictions = np.array(predictions)
    
    # Calculate accuracy
    accuracy = accuracy_score(actual_rain, predictions)
    cm = confusion_matrix(actual_rain, predictions)
    
    # Format rules for display
    rules_display = []
    for r in rules:
        rules_display.append({
            'id': r['id'],
            'name': r['name'],
            'rule': f"{r['condition']} {r['conclusion']}",
            'times_fired': rules_fired[r['id']]
        })
    
    return {
        'model_type': 'Rule-Based Expert System',
        'approach': 'Language of Logic (IF-THEN Rules)',
        'total_rules': len(rules),
        'accuracy': round(accuracy, 4),
        'confusion_matrix': cm.tolist(),
        'labels': ['No Rain', 'Rain'],
        'rules': rules_display,
        'inference_engine': 'Forward Chaining',
        'description': 'Expert system using propositional logic rules for weather prediction'
    }

