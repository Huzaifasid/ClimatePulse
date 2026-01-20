document.addEventListener('DOMContentLoaded', function() {
    let annualChart = null;
    let monthlyChart = null;
    let tempChart = null;

    // Screen elements
    const dataSourceScreen = document.getElementById('dataSourceScreen');
    const dashboardContainer = document.getElementById('dashboardContainer');
    
    // Data source selection elements
    const useDefaultBtn = document.getElementById('useDefaultBtn');
    const uploadCsvBtn = document.getElementById('uploadCsvBtn');
    const csvFileInput = document.getElementById('csvFileInput');
    const uploadStatus = document.getElementById('uploadStatus');
    const changeSourceBtn = document.getElementById('changeSourceBtn');
    const dataSourceIndicator = document.getElementById('dataSourceIndicator');
    
    // Dashboard elements
    const sidebar = document.querySelector('.sidebar');
    const mobileToggle = document.getElementById('mobileToggle');
    const locationSelect = document.getElementById('locationSelect');
    const yearSelect = document.getElementById('yearSelect');
    const currentLocationLabel = document.getElementById('currentLocation');
    const selectedYearLabel = document.getElementById('selectedYearLabel');
    const selectedYearLabel2 = document.getElementById('selectedYearLabel2');

    // Stats elements
    const totalRainfallEl = document.getElementById('totalRainfall');
    const avgTempEl = document.getElementById('avgTemp');
    const avgHumidityEl = document.getElementById('avgHumidity');
    const avgWindEl = document.getElementById('avgWind');

    // ========== DATA SOURCE SELECTION SCREEN ==========
    
    // Use Default Data button
    useDefaultBtn.addEventListener('click', async () => {
        useDefaultBtn.disabled = true;
        useDefaultBtn.textContent = 'Loading...';
        
        try {
            // Reset to default if there was custom data
            await fetch('/api/reset-data', { method: 'POST' });
            
            // Show dashboard
            showDashboard();
            initializeDashboard();
        } catch (err) {
            showUploadStatus('Failed to load default data: ' + err.message, 'error');
            useDefaultBtn.disabled = false;
            useDefaultBtn.textContent = 'Use Default Data';
        }
    });
    
    // Upload CSV button
    uploadCsvBtn.addEventListener('click', () => {
        csvFileInput.click();
    });
    
    // File selected for upload
    csvFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.name.endsWith('.csv')) {
            showUploadStatus('Please select a CSV file', 'error');
            return;
        }
        
        uploadCsvBtn.disabled = true;
        uploadCsvBtn.textContent = 'Uploading...';
        showUploadStatus('Uploading and validating...', 'loading');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showUploadStatus(`✅ ${data.message}`, 'success');
                
                // Update data source indicator in sidebar
                updateDataSourceUI({
                    type: 'custom',
                    filename: file.name,
                    record_count: data.record_count,
                    is_climate_data: data.is_climate_data
                });
                
                // Short delay then show dashboard
                setTimeout(() => {
                    showDashboard();
                    refreshLocations(data.locations);
                }, 1000);
            } else {
                showUploadStatus(`❌ ${data.message}`, 'error');
                uploadCsvBtn.disabled = false;
                uploadCsvBtn.textContent = 'Choose CSV File';
            }
        } catch (err) {
            showUploadStatus('Upload failed: ' + err.message, 'error');
            uploadCsvBtn.disabled = false;
            uploadCsvBtn.textContent = 'Choose CSV File';
        } finally {
            csvFileInput.value = ''; // Reset file input
        }
    });
    
    // Change data source button (in sidebar)
    changeSourceBtn.addEventListener('click', () => {
        showDataSourceScreen();
    });
    
    function showDashboard() {
        dataSourceScreen.classList.add('hidden');
        dashboardContainer.classList.remove('hidden');
    }
    
    function showDataSourceScreen() {
        dashboardContainer.classList.add('hidden');
        dataSourceScreen.classList.remove('hidden');
        // Reset buttons
        useDefaultBtn.disabled = false;
        useDefaultBtn.textContent = 'Use Default Data';
        uploadCsvBtn.disabled = false;
        uploadCsvBtn.textContent = 'Choose CSV File';
        uploadStatus.classList.remove('show');
    }
    
    // Mobile Sidebar Toggle
    if (mobileToggle) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== mobileToggle) {
            sidebar.classList.remove('active');
        }
    });

    // ========== FILE UPLOAD FUNCTIONALITY ==========
    
    function checkDataSource() {
        fetch('/api/data-source')
            .then(res => res.json())
            .then(data => {
                updateDataSourceUI(data);
            })
            .catch(err => console.error('Failed to check data source:', err));
    }
    
    function updateDataSourceUI(data) {
        if (!dataSourceIndicator) return;
        
        // Toggle climate features
        toggleClimateFeatures(data.is_climate_data);
        
        if (data.type === 'custom') {
            dataSourceIndicator.innerHTML = `
                <span class="source-badge custom">📁 ${data.filename}</span>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    ${data.record_count.toLocaleString()} records
                </div>
            `;
        } else {
            dataSourceIndicator.innerHTML = `
                <span class="source-badge default">📊 ${data.filename}</span>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    ${data.record_count.toLocaleString()} records (Default)
                </div>
            `;
        }
    }

    function toggleClimateFeatures(isClimate) {
        const climateElements = document.querySelectorAll('.climate-only');
        climateElements.forEach(el => {
            if (isClimate) {
                el.style.display = '';
            } else {
                el.style.display = 'none';
            }
        });

        // Update main metric label if not climate
        const rainfallLabel = document.querySelector('.stat-card:first-child h3');
        if (rainfallLabel) {
            rainfallLabel.textContent = isClimate ? 'Total Rainfall' : 'Total Records/Value';
        }
        
        const annualChartTitle = document.querySelector('.chart-container.large h3');
        if (annualChartTitle) {
            annualChartTitle.textContent = isClimate ? 'Annual Rainfall & Temperature Trends' : 'Annual Trends';
        }
    }
    
    function showUploadStatus(message, type, warnings = []) {
        if (!uploadStatus) return;
        
        uploadStatus.className = 'upload-status show ' + type;
        
        if (type === 'loading') {
            uploadStatus.innerHTML = `<div class="mini-spinner"></div>${message}`;
        } else {
            let html = message;
            if (warnings.length > 0) {
                html += '<ul class="upload-warnings">';
                warnings.forEach(w => html += `<li>⚠️ ${w}</li>`);
                html += '</ul>';
            }
            uploadStatus.innerHTML = html;
        }
    }
    
    function populateDataTable() {
        fetch('/api/data-table')
            .then(res => res.json())
            .then(data => {
                const header = document.getElementById('tableHeader');
                const body = document.getElementById('tableBody');
                if (!header || !body || data.length === 0) return;

                // Set headers
                const cols = Object.keys(data[0]);
                header.innerHTML = cols.map(c => `<th>${c}</th>`).join('');

                // Set body
                body.innerHTML = data.map(row => {
                    return `<tr>${cols.map(c => `<td>${row[c]}</td>`).join('')}</tr>`;
                }).join('');
            })
            .catch(err => console.error('Failed to load data table:', err));
    }

    function refreshLocations(locations) {
        // Clear and repopulate locations
        locationSelect.innerHTML = '<option value="" disabled>Select Location</option>';
        
        locations.forEach(loc => {
            const option = document.createElement('option');
            option.value = loc;
            option.textContent = loc;
            locationSelect.appendChild(option);
        });
        
        // Select first location and update dashboard
        if (locations.length > 0) {
            locationSelect.value = locations[0];
            updateDashboard(locations[0]);
        }
        
        // Clear ML results
        const mlResults = document.getElementById('mlResults');
        if (mlResults) {
            mlResults.innerHTML = '<p class="placeholder">Select a location and click "Train All Models" to see ML predictions</p>';
        }

        populateDataTable();
    }
    
    function initializeDashboard() {
        // Update data source indicator first to set overall mode
        checkDataSource();
        
        fetch('/api/locations')
            .then(response => response.json())
            .then(locations => {
                refreshLocations(locations);
            })
            .catch(err => console.error('Failed to load locations:', err));
    }
    
    function checkDataSource() {
        return fetch('/api/data-source')
            .then(res => res.json())
            .then(data => {
                updateDataSourceUI(data);
                return data;
            })
            .catch(err => {
                console.error('Failed to check data source:', err);
                return null;
            });
    }

    locationSelect.addEventListener('change', () => {
        updateDashboard(locationSelect.value);
    });

    yearSelect.addEventListener('change', () => {
        updateMonthlyData(locationSelect.value, yearSelect.value);
    });

    function updateDashboard(location) {
        currentLocationLabel.textContent = location;
        
        // Update Stats
        fetch(`/api/summary/${location}`)
            .then(res => res.json())
            .then(data => {
                const statsGrid = document.querySelector('.stats-grid');
                if (data.is_climate) {
                    // Update existing cards for climate data
                    statsGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-icon rainfall"></div>
                            <div class="stat-info">
                                <h3>Total Rainfall</h3>
                                <p id="totalRainfall">${(data.total_rainfall || 0).toLocaleString()}</p>
                                <span>mm</span>
                            </div>
                        </div>
                        <div class="stat-card climate-only">
                            <div class="stat-icon temp"></div>
                            <div class="stat-info">
                                <h3>Avg Temperature</h3>
                                <p id="avgTemp">${data.avg_temp || 0}</p>
                                <span>°C</span>
                            </div>
                        </div>
                        <div class="stat-card climate-only">
                            <div class="stat-icon humidity"></div>
                            <div class="stat-info">
                                <h3>Avg Humidity</h3>
                                <p id="avgHumidity">${data.avg_humidity || 0}</p>
                                <span>%</span>
                            </div>
                        </div>
                        <div class="stat-card climate-only">
                            <div class="stat-icon wind"></div>
                            <div class="stat-info">
                                <h3>Avg Wind Speed</h3>
                                <p id="avgWind">${data.avg_wind_speed || 0}</p>
                                <span>m/s</span>
                            </div>
                        </div>
                    `;
                } else {
                    // Rebuild stats grid for general data
                    let html = '';
                    if (data.metrics && data.metrics.length > 0) {
                        data.metrics.forEach((m, idx) => {
                            const iconClass = idx === 0 ? 'rainfall' : idx === 1 ? 'temp' : idx === 2 ? 'humidity' : 'wind';
                            const mLabel = m.label || `Metric ${idx + 1}`;
                            const mTotal = m.total !== undefined ? m.total : 0;
                            const mAvg = m.avg !== undefined ? m.avg : 0;
                            
                            html += `
                                <div class="stat-card">
                                    <div class="stat-icon ${iconClass}"></div>
                                    <div class="stat-info">
                                        <h3>${mLabel}</h3>
                                        <p>${mTotal.toLocaleString()}</p>
                                        <span>Total (Avg: ${mAvg})</span>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    // Always show record count
                    const recordCount = data.record_count !== undefined ? data.record_count : 0;
                    html += `
                        <div class="stat-card">
                            <div class="stat-icon rainfall"></div>
                            <div class="stat-info">
                                <h3>Total Records</h3>
                                <p>${recordCount.toLocaleString()}</p>
                                <span>Records for ${location}</span>
                            </div>
                        </div>
                    `;
                    statsGrid.innerHTML = html;
                }

                // Important: Re-sync visibility state
                toggleClimateFeatures(data.is_climate);
            });

        // Update Annual Trends
        fetch(`/api/trends/${location}`)
            .then(res => res.json())
            .then(data => {
                renderAnnualChart(data);
                
                // Populate Year Select
                yearSelect.innerHTML = '';
                // Clone years to avoid double-reverse issues if any
                const years = [...data.years].reverse();
                years.forEach(year => {
                    const option = document.createElement('option');
                    option.value = year;
                    option.textContent = year;
                    yearSelect.appendChild(option);
                });
                
                if (data.years.length > 0) {
                    yearSelect.value = years[0]; // Latest year
                    updateMonthlyData(location, yearSelect.value);
                }
            });
    }

    function updateMonthlyData(location, year) {
        selectedYearLabel.textContent = year;
        selectedYearLabel2.textContent = year;
        
        fetch(`/api/monthly/${location}/${year}`)
            .then(res => res.json())
            .then(data => {
                renderMonthlyChart(data);
                if (data.labels && data.labels.primary === 'Rainfall (mm)') {
                    renderTempRangeChart(data);
                }
            });
    }

    function renderAnnualChart(data) {
        if (annualChart) annualChart.destroy();
        
        const ctx = document.getElementById('annualTrendChart').getContext('2d');
        const datasets = [];
        
        if (data.primary_data) {
            datasets.push({
                label: data.labels.primary,
                data: [...data.primary_data], // Ensure it's in chronological order now (years are in order)
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                yAxisID: 'y',
                tension: 0.4
            });
        }
        
        if (data.secondary_data && data.labels.secondary) {
            datasets.push({
                label: data.labels.secondary,
                data: [...data.secondary_data],
                borderColor: '#f43f5e',
                borderDash: [5, 5],
                yAxisID: 'y1',
                tension: 0.4
            });
        }
        
        annualChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.years,
                datasets: datasets
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(255,255,255,0.05)' } },
                    y1: { type: 'linear', display: !!(data.secondary_data && data.labels.secondary), position: 'right', grid: { drawOnChartArea: false } },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                }
            }
        });
    }

    function renderMonthlyChart(data) {
        if (monthlyChart) monthlyChart.destroy();
        
        const ctx = document.getElementById('monthlyChart').getContext('2d');
        const datasets = [];
        
        if (data.primary_data && data.primary_data.length > 0) {
            datasets.push({
                label: data.labels.primary,
                data: data.primary_data,
                backgroundColor: '#38bdf8',
                borderRadius: 4
            });
        }
        
        if (data.secondary_data && data.labels.secondary && data.secondary_data.length > 0) {
            datasets.push({
                label: data.labels.secondary,
                data: data.secondary_data,
                backgroundColor: '#818cf8',
                borderRadius: 4
            });
        }
        
        monthlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.months.length > 0 ? data.months : ['No Day/Month Data'],
                datasets: datasets.length > 0 ? datasets : [{label: 'No Data', data: [0]}]
            },
            options: {
                responsive: true,
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderTempRangeChart(data) {
        if (tempChart) tempChart.destroy();
        
        const ctx = document.getElementById('tempRangeChart').getContext('2d');
        tempChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'Avg Temperature',
                        data: data.temp,
                        borderColor: '#fbbf24',
                        backgroundColor: 'rgba(251, 191, 36, 0.2)',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Humidity %',
                        data: data.humidity,
                        borderColor: '#10b981',
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
});
