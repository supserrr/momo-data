// MoMo Dashboard - Chart Handler with NeoBrutalism Style
// Handles data fetching and Chart.js visualization

// NeoBrutalism Color Palette
const COLORS = {
    yellow: '#ffc947',
    pink: '#ff90e8',
    mint: '#90ffdc',
    purple: '#b690ff',
    blue: '#90b3ff',
    orange: '#ffa500',
    green: '#90ff90',
    black: '#000000',
    white: '#ffffff'
};

// Chart.js Default Configuration for NeoBrutalism
Chart.defaults.font.family = "'Public Sans', sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.font.weight = 600;
Chart.defaults.color = COLORS.black;
Chart.defaults.borderColor = COLORS.black;
Chart.defaults.plugins.legend.labels.boxWidth = 20;
Chart.defaults.plugins.legend.labels.boxHeight = 20;
Chart.defaults.plugins.legend.labels.padding = 15;

// Global chart instances
let charts = {};

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Load dashboard data from JSON
async function loadDashboardData() {
    try {
        showRefreshIndicator();
        const response = await fetch('/data/processed/dashboard.json');
        if (!response.ok) throw new Error('Failed to load dashboard data');
        
        const data = await response.json();
        updateKeyMetrics(data);
        updateCharts(data);
        updateTransactionsTable(data);
        hideRefreshIndicator();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Failed to load dashboard data. Please refresh the page.');
        hideRefreshIndicator();
    }
}

// Update key metrics cards
function updateKeyMetrics(data) {
    const metrics = {
        totalTransactions: data.summary?.total_transactions || 0,
        totalAmount: data.summary?.total_amount || 0,
        successRate: data.summary?.success_rate || 0,
        activeUsers: data.summary?.unique_users || 0
    };
    
    // Animate number updates
    Object.entries(metrics).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element) {
            const formattedValue = formatMetricValue(key, value);
            element.innerHTML = `<span class="formatted-number animate-slide-in">${formattedValue}</span>`;
        }
    });
}

// Format metric values based on type
function formatMetricValue(key, value) {
    switch(key) {
        case 'totalAmount':
            return formatCurrency(value);
        case 'successRate':
            return `${value.toFixed(1)}%`;
        case 'totalTransactions':
        case 'activeUsers':
            return value.toLocaleString();
        default:
            return value;
    }
}

// Update all charts
function updateCharts(data) {
    updateVolumeChart(data.daily_stats || []);
    updateCategoryChart(data.category_distribution || []);
    updateUsersChart(data.top_users || []);
    updateHourlyChart(data.hourly_pattern || []);
}

// Volume by Date Chart
function updateVolumeChart(dailyStats) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
    const chartData = {
        labels: dailyStats.map(d => formatDate(d.date)),
        datasets: [{
            label: 'Transaction Count',
            data: dailyStats.map(d => d.count),
            backgroundColor: COLORS.yellow,
            borderColor: COLORS.black,
            borderWidth: 3,
            barThickness: 30,
            borderSkipped: false
        }]
    };
    
    if (charts.volume) charts.volume.destroy();
    
    charts.volume = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: getBarChartOptions('Transaction Volume by Date', false)
    });
}

// Category Distribution Chart
function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    const chartData = {
        labels: categories.map(c => c.category),
        datasets: [{
            label: 'Transactions',
            data: categories.map(c => c.count),
            backgroundColor: [
                COLORS.yellow,
                COLORS.pink,
                COLORS.mint,
                COLORS.purple,
                COLORS.blue,
                COLORS.orange
            ],
            borderColor: COLORS.black,
            borderWidth: 3,
            offset: 5
        }]
    };
    
    if (charts.category) charts.category.destroy();
    
    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '50%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 14,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: COLORS.white,
                    titleColor: COLORS.black,
                    bodyColor: COLORS.black,
                    borderColor: COLORS.black,
                    borderWidth: 3,
                    titleFont: {
                        size: 16,
                        weight: 700
                    },
                    bodyFont: {
                        size: 14,
                        weight: 600
                    },
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Top Users Chart
function updateUsersChart(topUsers) {
    const ctx = document.getElementById('usersChart');
    if (!ctx) return;
    
    const chartData = {
        labels: topUsers.map(u => u.phone || 'Unknown'),
        datasets: [{
            label: 'Transaction Volume',
            data: topUsers.map(u => u.total_amount),
            backgroundColor: COLORS.mint,
            borderColor: COLORS.black,
            borderWidth: 3,
            borderSkipped: false
        }]
    };
    
    if (charts.users) charts.users.destroy();
    
    charts.users = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: getBarChartOptions('Top Users by Volume (RWF)', true)
    });
}

// Hourly Pattern Chart
function updateHourlyChart(hourlyData) {
    const ctx = document.getElementById('hourlyChart');
    if (!ctx) return;
    
    // Generate 24-hour labels
    const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
    const data = Array(24).fill(0);
    
    // Fill in actual data
    hourlyData.forEach(h => {
        if (h.hour >= 0 && h.hour < 24) {
            data[h.hour] = h.count;
        }
    });
    
    const chartData = {
        labels: hours,
        datasets: [{
            label: 'Transactions',
            data: data,
            backgroundColor: COLORS.purple,
            borderColor: COLORS.black,
            borderWidth: 3,
            fill: true,
            tension: 0,
            pointRadius: 6,
            pointBackgroundColor: COLORS.white,
            pointBorderColor: COLORS.black,
            pointBorderWidth: 3,
            pointHoverRadius: 8
        }]
    };
    
    if (charts.hourly) charts.hourly.destroy();
    
    charts.hourly = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        lineWidth: 2
                    },
                    ticks: {
                        font: {
                            weight: 600
                        },
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        lineWidth: 2
                    },
                    ticks: {
                        font: {
                            weight: 600
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: getTooltipConfig()
            }
        }
    });
}

// Get standard bar chart options
function getBarChartOptions(title, horizontal = false) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: horizontal ? 'y' : 'x',
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        weight: 600
                    }
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0,0,0,0.1)',
                    lineWidth: 2
                },
                ticks: {
                    font: {
                        weight: 600
                    },
                    callback: function(value) {
                        if (horizontal) return value.toLocaleString();
                        return value;
                    }
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: getTooltipConfig()
        }
    };
}

// Get tooltip configuration
function getTooltipConfig() {
    return {
        backgroundColor: COLORS.white,
        titleColor: COLORS.black,
        bodyColor: COLORS.black,
        borderColor: COLORS.black,
        borderWidth: 3,
        titleFont: {
            size: 16,
            weight: 700,
            family: "'Lexend Mega', sans-serif"
        },
        bodyFont: {
            size: 14,
            weight: 600
        },
        padding: 12,
        displayColors: false,
        callbacks: {
            label: function(context) {
                let label = context.dataset.label || '';
                if (label) label += ': ';
                
                if (context.parsed.y !== null) {
                    label += formatNumber(context.parsed.y);
                } else if (context.parsed !== null) {
                    label += formatNumber(context.parsed);
                }
                
                return label;
            }
        }
    };
}

// Update transactions table
function updateTransactionsTable(data) {
    const tbody = document.getElementById('transactionsBody');
    const footer = document.getElementById('tableFooter');
    
    if (!tbody || !data.recent_transactions) return;
    
    const transactions = data.recent_transactions.slice(0, 10);
    
    if (transactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="nb-text-center">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No transactions found</p>
                    </div>
                </td>
            </tr>
        `;
        footer.innerHTML = '<span>No transactions to display</span>';
        return;
    }
    
    tbody.innerHTML = transactions.map(t => `
        <tr class="animate-slide-in">
            <td>${formatDate(t.date)}</td>
            <td>${t.category || 'Unknown'}</td>
            <td class="formatted-number">${formatCurrency(t.amount)}</td>
            <td>${formatPhone(t.sender_phone)}</td>
            <td>${formatPhone(t.receiver_phone)}</td>
            <td><span class="status-badge status-${t.status.toLowerCase()}">${t.status}</span></td>
        </tr>
    `).join('');
    
    footer.innerHTML = `<span>Showing ${transactions.length} of ${data.summary?.total_transactions || 0} total transactions</span>`;
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-RW', {
        style: 'currency',
        currency: 'RWF',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount || 0);
}

function formatNumber(num) {
    return (num || 0).toLocaleString();
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-RW', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function formatPhone(phone) {
    if (!phone) return 'Unknown';
    if (phone.length > 8) {
        return phone.slice(0, -4) + '****';
    }
    return phone;
}

// UI Helper Functions
function showRefreshIndicator() {
    let indicator = document.querySelector('.refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'refresh-indicator';
        indicator.innerHTML = '🔄 Refreshing data...';
        document.body.appendChild(indicator);
    }
    indicator.classList.add('show');
}

function hideRefreshIndicator() {
    const indicator = document.querySelector('.refresh-indicator');
    if (indicator) {
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 500);
    }
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message animate-slide-in';
    errorDiv.innerHTML = `⚠️ ${message}`;
    
    const container = document.querySelector('.main-container');
    if (container) {
        container.insertBefore(errorDiv, container.firstChild);
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatCurrency,
        formatDate,
        formatPhone,
        formatNumber,
        formatMetricValue
    };
}
