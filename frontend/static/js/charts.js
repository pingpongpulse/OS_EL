/**
 * PhaseSentinel - Charts Integration
 * Chart.js integration for real-time metrics visualization
 */

// Global chart instances
let metricsChart = null;
let phaseChart = null;

/**
 * Initialize metrics timeline chart
 */
function initMetricsChart(canvasId, metricsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = metricsData.map((m, i) => (m.timestamp || i * 0.5).toFixed(1));
    const cpuData = metricsData.map(m => parseFloat(m.cpu_percent) || 0);
    const memoryData = metricsData.map(m => parseFloat(m.memory_percent) || 0);

    if (metricsChart) {
        metricsChart.destroy();
    }

    metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'CPU Usage (%)',
                    data: cpuData,
                    borderColor: '#64ffda',
                    backgroundColor: 'rgba(100, 255, 218, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 2,
                    pointBackgroundColor: '#64ffda',
                    pointBorderColor: '#64ffda'
                },
                {
                    label: 'Memory Usage (%)',
                    data: memoryData,
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 2,
                    pointBackgroundColor: '#ff6b6b',
                    pointBorderColor: '#ff6b6b'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12, weight: '500' },
                        padding: 15
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(30, 41, 59, 0.5)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(30, 41, 59, 0.5)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

/**
 * Initialize phase distribution chart
 */
function initPhaseChart(canvasId, phaseCounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (phaseChart) {
        phaseChart.destroy();
    }

    const colors = {
        'cpu_bound': '#64ffda',
        'io_bound': '#ff6b6b',
        'memory_bound': '#feca57',
        'idle': '#48dbfb',
        'mixed': '#a29bfe'
    };

    const labels = Object.keys(phaseCounts);
    const data = Object.values(phaseCounts);
    const backgroundColors = labels.map(l => colors[l] || '#64ffda');

    phaseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.replace('_', ' ')),
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderColor: '#0a192f',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12 },
                        padding: 15
                    }
                }
            }
        }
    });
}

/**
 * Fetch metrics from API
 */
async function fetchMetrics(resultId) {
    try {
        const response = await fetch(`/api/results/${resultId}`);
        if (response.ok) {
            return await response.json();
        }
    } catch (e) {
        console.error('Error fetching metrics:', e);
    }
    return null;
}

/**
 * Display metrics summary
 */
function displayMetricsSummary(metrics) {
    if (!metrics || !metrics.timeline) return;

    const cpus = metrics.timeline.map(m => m.cpu_percent);
    const mems = metrics.timeline.map(m => m.memory_percent);

    const avgCpu = cpus.reduce((a, b) => a + b, 0) / cpus.length;
    const maxCpu = Math.max(...cpus);
    const avgMem = mems.reduce((a, b) => a + b, 0) / mems.length;

    const summaryEl = document.getElementById('metrics-summary');
    if (summaryEl) {
        summaryEl.innerHTML = `
            <div class="metric-card">
                <div class="metric-label">Avg CPU</div>
                <div class="metric-value">${avgCpu.toFixed(1)}</div>
                <div class="metric-unit">%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Peak CPU</div>
                <div class="metric-value">${maxCpu.toFixed(1)}</div>
                <div class="metric-unit">%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Memory</div>
                <div class="metric-value">${avgMem.toFixed(1)}</div>
                <div class="metric-unit">%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Samples</div>
                <div class="metric-value">${metrics.timeline.length}</div>
                <div class="metric-unit">count</div>
            </div>
        `;
    }
}

/**
 * Display bottlenecks
 */
function displayBottlenecks(metrics) {
    if (!metrics || !metrics.bottlenecks) return;

    const containerEl = document.getElementById('bottlenecks-container');
    if (!containerEl) return;

    if (metrics.bottlenecks.length === 0) {
        containerEl.innerHTML = '<p class="text-muted">No bottlenecks detected</p>';
        return;
    }

    const bottlenecksHTML = metrics.bottlenecks.map(b => `
        <div class="bottleneck-item ${b.severity}">
            <div class="bottleneck-type">${b.type}</div>
            <div class="bottleneck-message">${b.message}</div>
            <div class="bottleneck-duration">Duration: ${(b.duration || 0).toFixed(1)}s</div>
        </div>
    `).join('');

    containerEl.innerHTML = bottlenecksHTML;
}

/**
 * Display recommendations
 */
function displayRecommendations(metrics) {
    if (!metrics || !metrics.recommendations) return;

    const containerEl = document.getElementById('recommendations-container');
    if (!containerEl) return;

    if (metrics.recommendations.length === 0) {
        containerEl.innerHTML = '<p class="text-muted">No recommendations available</p>';
        return;
    }

    const recsHTML = metrics.recommendations.map(r => `
        <div class="recommendation-card">
            <div class="rec-header">
                <span class="rec-type">${r.bottleneck_type || r.phase_type}</span>
                <span class="rec-speedup">${(r.predicted_speedup || 1.0).toFixed(1)}x speedup</span>
            </div>
            <div class="rec-suggestions">
                ${(r.suggestions || []).map(s => `<li>${s}</li>`).join('') || '<li>No specific suggestions</li>'}
            </div>
        </div>
    `).join('');

    containerEl.innerHTML = recsHTML;
}

/**
 * Initialize dashboard on page load
 */
function initDashboard() {
    const resultId = extractResultId();
    if (!resultId) return;

    fetchMetrics(resultId).then(metrics => {
        if (!metrics) return;

        displayMetricsSummary(metrics);
        displayBottlenecks(metrics);
        displayRecommendations(metrics);

        if (metrics.timeline && metrics.timeline.length > 0) {
            initMetricsChart('metricsChart', metrics.timeline);
        }

        if (metrics.phases && metrics.phases.length > 0) {
            const phaseCounts = {};
            metrics.phases.forEach(p => {
                phaseCounts[p.type] = (phaseCounts[p.type] || 0) + 1;
            });
            initPhaseChart('phaseChart', phaseCounts);
        }
    });
}

/**
 * Extract result ID from URL
 */
function extractResultId() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 1];
}

/**
 * Export results as JSON
 */
function exportResults(metrics) {
    const dataStr = JSON.stringify(metrics, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `phasesnoel-${Date.now()}.json`;
    link.click();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'System Metrics Over Time'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time (seconds)'
                    }
                }
            }
        }
    });

    return metricsChart;
}

/**
 * Initialize phase distribution chart
 */
function initPhaseChart(canvasId, metricsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Count phases
    const phaseCounts = {};
    metricsData.forEach(m => {
        const phase = m.phase || 'unknown';
        phaseCounts[phase] = (phaseCounts[phase] || 0) + 1;
    });

    const phases = Object.keys(phaseCounts);
    const counts = phases.map(p => phaseCounts[p]);
    const colors = phases.map(p => getPhaseColor(p));

    if (phaseChart) {
        phaseChart.destroy();
    }

    phaseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: phases.map(p => p.replace('_', ' ').toUpperCase()),
            datasets: [{
                data: counts,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Phase Distribution'
                },
                legend: {
                    display: true,
                    position: 'right'
                }
            }
        }
    });

    return phaseChart;
}

/**
 * Initialize bottleneck classification chart
 */
function initBottleneckChart(canvasId, bottleneckData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = bottleneckData.map(b => b.type || 'Unknown');
    const severity = bottleneckData.map(b => b.severity || 0);
    const colors = bottleneckData.map(b => getSeverityColor(b.severity));

    if (bottleneckChart) {
        bottleneckChart.destroy();
    }

    bottleneckChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Severity Score',
                data: severity,
                backgroundColor: colors,
                borderColor: colors.map(c => darkenColor(c, 20)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Bottleneck Classification'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Severity (0-10)'
                    }
                }
            }
        }
    });

    return bottleneckChart;
}

/**
 * Get color for phase type
 */
function getPhaseColor(phase) {
    const colors = {
        'idle': '#e9ecef',
        'cpu_bound': '#ffc107',
        'io_bound': '#17a2b8',
        'memory_bound': '#dc3545',
        'mixed': '#6f42c1',
        'unknown': '#6c757d'
    };
    return colors[phase] || colors['unknown'];
}

/**
 * Get color for severity level
 */
function getSeverityColor(severity) {
    if (severity >= 7) return '#dc3545'; // Red - severe
    if (severity >= 4) return '#ffc107'; // Yellow - moderate
    return '#28a745'; // Green - mild
}

/**
 * Darken a color (hex)
 */
function darkenColor(color, percent) {
    // Simple darkening - in production, use a color library
    return color;
}

/**
 * Render phase timeline as HTML blocks
 */
function renderPhaseTimeline(containerId, metricsData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    metricsData.forEach((metric, index) => {
        const phase = metric.phase || 'unknown';
        const block = document.createElement('div');
        block.className = `phase-block phase-${phase.replace('_', '-')}`;
        block.textContent = phase.replace('_', ' ').toUpperCase();
        block.title = `Sample ${index + 1}: ${phase}`;
        container.appendChild(block);
    });
}

/**
 * Update metrics display cards
 */
function updateMetricsCards(metricsData) {
    if (!metricsData || metricsData.length === 0) return;

    const latest = metricsData[metricsData.length - 1];
    const avgCpu = metricsData.reduce((sum, m) => sum + parseFloat(m.cpu_percent || 0), 0) / metricsData.length;
    const avgMemory = metricsData.reduce((sum, m) => sum + parseFloat(m.memory_percent || 0), 0) / metricsData.length;

    // Update CPU metric
    const cpuElement = document.getElementById('metric-cpu');
    if (cpuElement) {
        cpuElement.textContent = avgCpu.toFixed(1);
    }

    // Update Memory metric
    const memoryElement = document.getElementById('metric-memory');
    if (memoryElement) {
        memoryElement.textContent = avgMemory.toFixed(1);
    }

    // Update I/O metric
    const ioElement = document.getElementById('metric-io');
    if (ioElement) {
        const avgIo = metricsData.reduce((sum, m) => 
            sum + parseFloat(m.disk_read_mb || 0) + parseFloat(m.disk_write_mb || 0), 0) / metricsData.length;
        ioElement.textContent = avgIo.toFixed(2);
    }
}

/**
 * Render bottleneck list
 */
function renderBottleneckList(containerId, bottlenecks) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (!bottlenecks || bottlenecks.length === 0) {
        container.innerHTML = '<p>No bottlenecks detected.</p>';
        return;
    }

    bottlenecks.forEach(bottleneck => {
        const item = document.createElement('div');
        item.className = `bottleneck-item ${getSeverityClass(bottleneck.severity)}`;
        
        item.innerHTML = `
            <h4>${bottleneck.type || 'Unknown Bottleneck'}</h4>
            <p>${bottleneck.description || 'No description available.'}</p>
            <p><strong>Severity:</strong> ${bottleneck.severity || 'N/A'}/10</p>
            ${bottleneck.recommendation ? `<p><strong>Recommendation:</strong> ${bottleneck.recommendation}</p>` : ''}
        `;

        container.appendChild(item);
    });
}

/**
 * Get CSS class for severity
 */
function getSeverityClass(severity) {
    if (severity >= 7) return 'severe';
    if (severity >= 4) return 'moderate';
    return 'mild';
}

/**
 * Fetch metrics and update all charts
 */
async function refreshMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();

        if (data.status === 'success' && data.metrics) {
            const metrics = data.metrics;

            // Update charts
            initMetricsChart('metricsChart', metrics);
            initPhaseChart('phaseChart', metrics);
            renderPhaseTimeline('phaseTimeline', metrics);
            updateMetricsCards(metrics);

            return metrics;
        }
    } catch (error) {
        console.error('Error fetching metrics:', error);
    }
}

/**
 * Initialize dashboard charts on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the dashboard page
    if (document.getElementById('metricsChart')) {
        // Initial load
        refreshMetrics();

        // Auto-refresh every 5 seconds
        setInterval(refreshMetrics, 5000);
    }
});

