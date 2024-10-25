// Chart.js instance
let metricsChart = null;

async function analyzeTrack() {
    const spotifyUrl = document.getElementById('spotifyUrl').value;
    const loadingElement = document.getElementById('loading');
    const resultsElement = document.getElementById('results');
    const errorElement = document.getElementById('errorMessage');

    // Validate URL
    if (!isValidSpotifyUrl(spotifyUrl)) {
        showError('Please enter a valid Spotify track URL');
        return;
    }

    try {
        // Show loading state
        errorElement.style.display = 'none';
        loadingElement.style.display = 'block';
        resultsElement.style.display = 'none';

        // Make API request
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ spotify_url: spotifyUrl })
        });

        // Check if response is OK
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Parse response
        const data = await response.json();

        // Check for API error
        if (!data.success) {
            throw new Error(data.error || 'Analysis failed');
        }

        // Display results
        displayResults(data.results);
        resultsElement.style.display = 'block';

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    } finally {
        loadingElement.style.display = 'none';
    }
}

function displayResults(results) {
    // Display track information
    displayTrackInfo(results.track_data);
    
    // Display artist metrics
    displayArtistMetrics(results.artist_metrics);
    
    // Display prediction and recommendation
    displayPrediction(results.prediction);
    
    // Update visualization
    updateMetricsChart(results);
}

function displayTrackInfo(trackData) {
    const trackInfoElement = document.getElementById('trackInfo');
    
    trackInfoElement.innerHTML = `
        <div class="result-section">
            <h3>Track Information</h3>
            <div class="metric-grid">
                <div class="metric-item">
                    <span class="metric-label">Track Name:</span>
                    <span class="metric-value">${trackData.track_name}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Artist:</span>
                    <span class="metric-value">${trackData.artist_name}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Popularity:</span>
                    <span class="metric-value">${trackData.popularity}/100</span>
                </div>
            </div>
        </div>
    `;
}

function displayArtistMetrics(metrics) {
    const artistMetricsElement = document.getElementById('artistMetrics');
    
    artistMetricsElement.innerHTML = `
        <div class="result-section">
            <h3>Artist Metrics</h3>
            <div class="metric-grid">
                <div class="metric-item">
                    <span class="metric-label">Growth Rate:</span>
                    <span class="metric-value">${(metrics.growth_metrics.growth_rate * 100).toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Engagement Rate:</span>
                    <span class="metric-value">${(metrics.social_metrics.engagement_rate * 100).toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Sentiment Score:</span>
                    <span class="metric-value">${(metrics.sentiment_score * 100).toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Followers:</span>
                    <span class="metric-value">${formatNumber(metrics.social_metrics.followers)}</span>
                </div>
            </div>
        </div>
    `;
}

function displayPrediction(prediction) {
    const predictionElement = document.getElementById('prediction');
    
    const recommendationClass = getRecommendationClass(prediction.investment_score);
    
    predictionElement.innerHTML = `
        <div class="result-section">
            <h3>Investment Analysis</h3>
            <div class="metric-grid">
                <div class="metric-item">
                    <span class="metric-label">Success Probability:</span>
                    <span class="metric-value">${(prediction.success_probability * 100).toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Investment Score:</span>
                    <span class="metric-value">${(prediction.investment_score * 100).toFixed(1)}%</span>
                </div>
            </div>
            <div class="recommendation ${recommendationClass}">
                <h4>${prediction.recommendation.decision}</h4>
                <div class="confidence">Confidence: ${prediction.recommendation.confidence}</div>
                <div class="rationale">${prediction.recommendation.rationale}</div>
            </div>
        </div>
    `;
}

function updateMetricsChart(results) {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (metricsChart) {
        metricsChart.destroy();
    }

    // Create new chart
    metricsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Success Probability',
                'Growth Rate',
                'Engagement',
                'Sentiment',
                'Popularity'
            ],
            datasets: [{
                label: 'Track Metrics',
                data: [
                    results.prediction.success_probability * 100,
                    results.artist_metrics.growth_metrics.growth_rate * 100,
                    results.artist_metrics.social_metrics.engagement_rate * 100,
                    results.artist_metrics.sentiment_score * 100,
                    results.track_data.popularity
                ],
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(37, 99, 235, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Utility Functions
function isValidSpotifyUrl(url) {
    const regex = /^https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]+(\?|$)/;
    return regex.test(url) || url.includes('spotify:track:');
}

function getRecommendationClass(score) {
    if (score >= 0.8) return 'strong-invest';
    if (score >= 0.6) return 'consider-investment';
    return 'hold';
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

function clearResults() {
    // Clear input
    document.getElementById('spotifyUrl').value = '';
    
    // Hide results and error messages
    document.getElementById('results').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
    
    // Destroy chart if it exists
    if (metricsChart) {
        metricsChart.destroy();
        metricsChart = null;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key handler for the input field
    document.getElementById('spotifyUrl').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeTrack();
        }
    });
});