/**
 * Chart.js scripts for PhaseProfiler dashboard
 * Handles phase timeline, bottleneck visualization, and metrics charts
 */

// Global chart instances
let metricsChart = null;
let phaseChart = null;
let bottleneckChart = null;

/**
 * Initialize metrics timeline chart
 */
function initMetricsChart(canvasId, metricsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = metricsData.map(m => m.timestamp || m.sample_id);
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
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Memory Usage (%)',
                    data: memoryData,
                    borderColor: 'rgb(118, 75, 162)',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
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

