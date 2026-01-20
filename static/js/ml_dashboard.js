// ML Dashboard JavaScript
// Handles ML model training, predictions, and visualizations

let confusionChart = null;
let clusterChart = null;
let predictionChart = null;

// Get current location from main dashboard
function getCurrentLocation() {
    return document.getElementById('locationSelect').value;
}

// Train all models at once
async function trainAllModels() {
    const location = getCurrentLocation();
    if (!location) {
        alert('Please select a location first');
        return;
    }
    
    showMLLoading(true);
    
    try {
        const response = await fetch(`/api/ml/train-all/${location}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayAllModelResults(data);
    } catch (error) {
        console.error('Error training models:', error);
        document.getElementById('mlResults').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        showMLLoading(false);
    }
}

// Train individual model
async function trainModel(modelType) {
    const location = getCurrentLocation();
    if (!location) {
        alert('Please select a location first');
        return;
    }
    
    showMLLoading(true);
    
    const endpoints = {
        'linear_regression': 'linear-regression',
        'decision_tree': 'decision-tree',
        'random_forest': 'random-forest',
        'logistic_regression': 'logistic-regression',
        'knn': 'knn',
        'kmeans': 'kmeans',
        'reinforcement_learning': 'reinforcement-learning',
        'rule_based': 'rule-based',
        'ensemble': 'ensemble',
        'neural_network': 'neural-network'
    };
    
    try {
        const response = await fetch(`/api/ml/${endpoints[modelType]}/${location}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayModelResult(modelType, data);
    } catch (error) {
        console.error('Error training model:', error);
        document.getElementById('mlResults').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        showMLLoading(false);
    }
}

function showMLLoading(show) {
    const loader = document.getElementById('mlLoader');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}

function displayAllModelResults(data) {
    const resultsDiv = document.getElementById('mlResults');
    let html = `<div class="results-header">
        <h4>Analysis Results for ${data.location}</h4>
        <span class="badge-count">${Object.keys(data.models).length} Models Trained</span>
    </div>`;
    
    // Define Categories
    const categories = {
        'Future Prediction': ['linear_regression', 'decision_tree', 'random_forest'],
        'Rain Classification': ['logistic_regression', 'knn', 'neural_network'],
        'Advanced Analysis': ['ensemble', 'rule_based', 'reinforcement_learning'],
        'Pattern Recognition': ['kmeans']
    };
    
    for (const [categoryName, modelKeys] of Object.entries(categories)) {
        // Filter models that are present in the response
        const validModels = modelKeys.filter(key => data.models[key]);
        
        if (validModels.length > 0) {
            html += `<div class="category-section">
                <h5 class="category-title">${categoryName}</h5>
                <div class="models-grid">`;
                
            for (const key of validModels) {
                html += generateModelCard(key, data.models[key]);
            }
            
            html += `</div></div>`;
        }
    }
    
    resultsDiv.innerHTML = html;
    
    // Render charts for all models that need them
    // Classification
    ['logistic_regression', 'knn', 'neural_network', 'ensemble'].forEach(key => {
        if (data.models[key] && data.models[key].confusion_matrix) {
            // Slight delay for each to avoid UI freeze and ensure DOM is ready
            setTimeout(() => renderConfusionMatrix(key === 'logistic_regression' ? 'logistic' : key, data.models[key]), 100);
        }
    });
    
    // Clustering
    if (data.models.kmeans && data.models.kmeans.cluster_stats) {
        setTimeout(() => renderClusterChart(data.models.kmeans), 200);
    }
}

function displayModelResult(modelType, data) {
    const resultsDiv = document.getElementById('mlResults');
    resultsDiv.innerHTML = generateModelCard(modelType, data);
    
    if (data.confusion_matrix) {
        setTimeout(() => renderConfusionMatrix(modelType, data), 100);
    }
    if (data.cluster_stats) {
        setTimeout(() => renderClusterChart(data), 100);
    }
}

function generateModelCard(modelKey, result) {
    if (result.error) {
        return `<div class="ml-card error"><h5>${formatModelName(modelKey)}</h5><p>Error: ${result.error}</p></div>`;
    }
    
    let html = `<div class="ml-card ${getModelCategory(modelKey)}">`;
    html += `<h5>${result.model_type || formatModelName(modelKey)}</h5>`;
    
    // Regression metrics
    if (result.r2_score !== undefined) {
        html += `<div class="metric"><span>R² Score:</span> <strong>${(result.r2_score * 100).toFixed(2)}%</strong></div>`;
        html += `<div class="metric"><span>RMSE:</span> <strong>${result.rmse} mm</strong></div>`;
    }
    
    // Classification metrics
    if (result.accuracy !== undefined) {
        html += `<div class="metric"><span>Accuracy:</span> <strong>${(result.accuracy * 100).toFixed(2)}%</strong></div>`;
    }
    
    // KNN specific
    if (result.n_neighbors !== undefined) {
        html += `<div class="metric"><span>K Neighbors:</span> <strong>${result.n_neighbors}</strong></div>`;
    }
    
    // Clustering metrics
    if (result.silhouette_score !== undefined) {
        html += `<div class="metric"><span>Silhouette Score:</span> <strong>${result.silhouette_score.toFixed(4)}</strong></div>`;
        html += `<div class="metric"><span>Clusters:</span> <strong>${result.n_clusters}</strong></div>`;
    }
    
    // Reinforcement Learning
    if (result.algorithm === 'Q-Learning') {
        html += `<div class="metric"><span>Scenario:</span> <strong>${result.scenario}</strong></div>`;
        html += `<div class="metric"><span>Episodes:</span> <strong>${result.episodes}</strong></div>`;
        html += `<div class="metric"><span>Final Avg Reward:</span> <strong>${result.final_avg_reward}</strong></div>`;
        if (result.learning_progress) {
            html += `<div class="metric"><span>Improvement:</span> <strong>${result.learning_progress.improvement}</strong></div>`;
        }
        if (result.learned_policy) {
            html += `<div class="rl-policy"><h6>Learned Policy (Sample):</h6><ul>`;
            for (const p of result.learned_policy) {
                html += `<li><span class="state">${p.state}</span> → <span class="decision ${p.decision.includes('DON') ? 'no' : 'yes'}">${p.decision}</span></li>`;
            }
            html += `</ul></div>`;
        }
    }
    
    // Rule-Based Expert System
    if (result.rules) {
        html += `<div class="metric"><span>Total Rules:</span> <strong>${result.total_rules}</strong></div>`;
        html += `<div class="metric"><span>Inference Engine:</span> <strong>${result.inference_engine}</strong></div>`;
        html += `<div class="expert-rules"><h6>Expert Rules:</h6><ul>`;
        for (const r of result.rules) {
            html += `<li><strong>${r.id}:</strong> ${r.rule} <span class="fired">(fired ${r.times_fired}x)</span></li>`;
        }
        html += `</ul></div>`;
    }
    
    // Ensemble Techniques
    if (result.techniques) {
        html += `<div class="metric"><span>Best Technique:</span> <strong>${result.best_technique}</strong></div>`;
        html += `<div class="metric"><span>Best Accuracy:</span> <strong>${(result.best_accuracy * 100).toFixed(2)}%</strong></div>`;
        html += `<div class="ensemble-comparison"><h6>Ensemble Methods Comparison:</h6><table>`;
        html += `<tr><th>Method</th><th>Type</th><th>Accuracy</th></tr>`;
        for (const t of result.techniques) {
            const isBest = t.name === result.best_technique;
            html += `<tr class="${isBest ? 'best' : ''}">
                <td>${t.name}</td>
                <td>${t.type}</td>
                <td>${(t.accuracy * 100).toFixed(2)}%</td>
            </tr>`;
        }
        html += `</table></div>`;
    }
    
    // Neural Network Architecture
    if (result.architecture) {
        const arch = result.architecture;
        html += `<div class="metric"><span>Total Layers:</span> <strong>${result.total_layers}</strong></div>`;
        html += `<div class="metric"><span>Epochs Trained:</span> <strong>${result.epochs}</strong></div>`;
        html += `<div class="nn-architecture"><h6>Network Architecture:</h6>`;
        html += `<div class="layer-diagram">`;
        html += `<div class="layer input"><span>Input</span><span>${arch.input_layer}</span></div>`;
        for (const neurons of arch.hidden_layers) {
            html += `<div class="layer hidden"><span>Hidden</span><span>${neurons}</span></div>`;
        }
        html += `<div class="layer output"><span>Output</span><span>${arch.output_layer}</span></div>`;
        html += `</div>`;
        html += `<div class="nn-details">`;
        html += `<span>Activation: <strong>${arch.activation}</strong></span>`;
        html += `<span>Optimizer: <strong>${arch.optimizer}</strong></span>`;
        html += `</div></div>`;
    }
    
    // Feature importance
    if (result.feature_importance) {
        html += `<div class="feature-importance"><h6>Feature Importance:</h6><ul>`;
        for (const [feature, importance] of Object.entries(result.feature_importance)) {
            const barWidth = (importance * 100).toFixed(1);
            html += `<li><span>${feature}</span><div class="bar" style="width: ${barWidth}%"></div><span>${(importance * 100).toFixed(1)}%</span></li>`;
        }
        html += `</ul></div>`;
    }
    
    // Confusion matrix placeholder
    if (result.confusion_matrix) {
        html += `<div class="confusion-matrix-container"><canvas id="cm-${modelKey}"></canvas></div>`;
    }
    
    // Cluster chart placeholder
    if (result.cluster_stats) {
        html += `<div class="cluster-chart-container"><canvas id="cluster-chart"></canvas></div>`;
        html += `<div class="cluster-stats">`;
        for (const stat of result.cluster_stats) {
            html += `<div class="cluster-stat">
                <strong>Cluster ${stat.cluster}</strong>
                <span>${stat.count} days</span>
                <span>Avg Temp: ${stat.avg_temp}°C</span>
                <span>Avg Rain: ${stat.avg_rainfall}mm</span>
            </div>`;
        }
        html += `</div>`;
    }
    
    html += `</div>`;
    return html;
}

function formatModelName(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getModelCategory(key) {
    const categories = {
        'linear_regression': 'regression',
        'decision_tree': 'regression',
        'random_forest': 'regression',
        'logistic_regression': 'classification',
        'knn': 'classification',
        'kmeans': 'clustering',
        'reinforcement_learning': 'rl',
        'rule_based': 'logic',
        'ensemble': 'ensemble',
        'neural_network': 'neural'
    };
    return categories[key] || '';
}

function renderConfusionMatrix(modelKey, data) {
    const canvas = document.getElementById(`cm-${modelKey}`);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (confusionChart) confusionChart.destroy();
    
    const cm = data.confusion_matrix;
    const labels = data.labels || ['No Rain', 'Rain'];
    
    confusionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['True Negative', 'False Positive', 'False Negative', 'True Positive'],
            datasets: [{
                label: 'Confusion Matrix',
                data: [cm[0][0], cm[0][1], cm[1][0], cm[1][1]],
                backgroundColor: ['#10b981', '#f43f5e', '#f97316', '#38bdf8'],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Confusion Matrix',
                    color: '#94a3b8'
                },
                legend: { display: false }
            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderClusterChart(data) {
    const canvas = document.getElementById('cluster-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (clusterChart) clusterChart.destroy();
    
    const stats = data.cluster_stats;
    
    clusterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: stats.map((stat, i) => ({
                label: `Cluster ${stat.cluster}`,
                data: [{ x: stat.avg_temp, y: stat.avg_rainfall }],
                backgroundColor: ['#38bdf8', '#f43f5e', '#10b981', '#fbbf24', '#818cf8'][i],
                pointRadius: Math.sqrt(stat.count) / 2
            }))
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Cluster Distribution (Temp vs Rainfall)',
                    color: '#94a3b8'
                }
            },
            scales: {
                x: { title: { display: true, text: 'Avg Temperature (°C)' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { title: { display: true, text: 'Avg Rainfall (mm)' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

// Initialize ML Dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Track if models have been trained at least once
    let modelsTrainedOnce = false;
    
    // Train All button
    const trainAllBtn = document.getElementById('trainAllBtn');
    if (trainAllBtn) {
        trainAllBtn.addEventListener('click', () => {
            modelsTrainedOnce = true;
            trainAllModels();
        });
    }
    
    // Individual model buttons
    document.querySelectorAll('.model-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            modelsTrainedOnce = true;
            trainModel(btn.dataset.model);
        });
    });
    
    // Auto-refresh ML results when location changes
    const locationSelect = document.getElementById('locationSelect');
    if (locationSelect) {
        locationSelect.addEventListener('change', () => {
            if (modelsTrainedOnce) {
                // Show a quick notification that models are retraining
                const resultsDiv = document.getElementById('mlResults');
                if (resultsDiv && !resultsDiv.querySelector('.placeholder')) {
                    trainAllModels();
                }
            }
        });
    }
    
    // Auto-refresh ML results when year changes
    const yearSelect = document.getElementById('yearSelect');
    if (yearSelect) {
        yearSelect.addEventListener('change', () => {
            if (modelsTrainedOnce) {
                const resultsDiv = document.getElementById('mlResults');
                if (resultsDiv && !resultsDiv.querySelector('.placeholder')) {
                    trainAllModels();
                }
            }
        });
    }
});
