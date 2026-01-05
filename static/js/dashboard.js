document.addEventListener('DOMContentLoaded', function() {
    let annualChart = null;
    let monthlyChart = null;
    let tempChart = null;

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

    // Initialize Locations
    fetch('/api/locations')
        .then(response => response.json())
        .then(locations => {
            locations.forEach(loc => {
                const option = document.createElement('option');
                option.value = loc;
                option.textContent = loc;
                locationSelect.appendChild(option);
            });
            
            // Set default location
            if (locations.length > 0) {
                locationSelect.value = locations[0];
                updateDashboard(locations[0]);
            }
        });

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
                totalRainfallEl.textContent = data.total_rainfall.toLocaleString();
                avgTempEl.textContent = data.avg_temp;
                avgHumidityEl.textContent = data.avg_humidity;
                avgWindEl.textContent = data.avg_wind_speed;
            });

        // Update Annual Trends
        fetch(`/api/trends/${location}`)
            .then(res => res.json())
            .then(data => {
                renderAnnualChart(data);
                
                // Populate Year Select
                yearSelect.innerHTML = '';
                data.years.reverse().forEach(year => {
                    const option = document.createElement('option');
                    option.value = year;
                    option.textContent = year;
                    yearSelect.appendChild(option);
                });
                
                if (data.years.length > 0) {
                    yearSelect.value = data.years[0]; // Latest year
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
                renderTempRangeChart(data);
            });
    }

    function renderAnnualChart(data) {
        if (annualChart) annualChart.destroy();
        
        const ctx = document.getElementById('annualTrendChart').getContext('2d');
        annualChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.years.reverse(), // Put back in order
                datasets: [
                    {
                        label: 'Total Rainfall (mm)',
                        data: data.rainfall.reverse(),
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: true,
                        yAxisID: 'y',
                        tension: 0.4
                    },
                    {
                        label: 'Avg Temperature (°C)',
                        data: data.temp.reverse(),
                        borderColor: '#f43f5e',
                        borderDash: [5, 5],
                        yAxisID: 'y1',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(255,255,255,0.05)' } },
                    y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false } },
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
        monthlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'Rainfall',
                        data: data.rainfall,
                        backgroundColor: '#38bdf8',
                        borderRadius: 4
                    },
                    {
                        label: 'Wind Speed',
                        data: data.wind_speed,
                        backgroundColor: '#818cf8',
                        borderRadius: 4
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
