// MoMo Dashboard - Chart Handler with NeoBrutalism Style
// Handles data fetching and Chart.js visualization

// Enhanced Brutalist Color Palette
const COLORS = {
    yellow: '#ffc947',
    pink: '#ff90e8',
    mint: '#90ffdc',
    purple: '#b690ff',
    blue: '#90b3ff',
    orange: '#ffa500',
    green: '#90ff90',
    black: '#000000',
    white: '#ffffff',
    gray: '#f5f5f5',
    darkGray: '#333333'
};

// Brutalist Chart Configuration
const BRUTALIST_CONFIG = {
    borderWidth: 4,
    borderRadius: 0,
    fontFamily: "'Lexend Mega', sans-serif",
    fontWeight: 700,
    textTransform: 'uppercase'
};

// Enhanced Chart.js Configuration for Brutalist Design
Chart.defaults.font.family = "'Public Sans', sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.font.weight = 700;
Chart.defaults.color = COLORS.black;
Chart.defaults.borderColor = COLORS.black;
Chart.defaults.borderWidth = BRUTALIST_CONFIG.borderWidth;
Chart.defaults.plugins.legend.labels.boxWidth = 24;
Chart.defaults.plugins.legend.labels.boxHeight = 24;
Chart.defaults.plugins.legend.labels.padding = 20;
Chart.defaults.plugins.legend.labels.font = {
    family: BRUTALIST_CONFIG.fontFamily,
    weight: BRUTALIST_CONFIG.fontWeight,
    size: 14
};
Chart.defaults.plugins.legend.labels.textTransform = BRUTALIST_CONFIG.textTransform;

// Global chart instances
let charts = {};
let allTransactions = [];
let currentPage = 1;
let pageSize = 10; // Default page size
let totalPages = 1;

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Add load more button event listener
    // Pagination event listeners
    const pageSizeSelect = document.getElementById('pageSize');
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', handlePageSizeChange);
    }
    
    const firstPageBtn = document.getElementById('firstPageBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const lastPageBtn = document.getElementById('lastPageBtn');
    
    if (firstPageBtn) firstPageBtn.addEventListener('click', () => goToPage(1));
    if (prevPageBtn) prevPageBtn.addEventListener('click', () => goToPage(currentPage - 1));
    if (nextPageBtn) nextPageBtn.addEventListener('click', () => goToPage(currentPage + 1));
    if (lastPageBtn) lastPageBtn.addEventListener('click', () => goToPage(totalPages));
    
    // Auto-refresh disabled - data loads on page load only
    // setInterval(loadDashboardData, 30000);
});

// Load dashboard data from API - unified approach
async function loadDashboardData() {
    try {
        console.log('Loading unified dashboard data...');
        
        // Load ALL transactions first - this is our single source of truth
        const allTransactionsData = await loadAllTransactions();
        console.log('Loaded transactions:', allTransactionsData.length);
        
        if (allTransactionsData.length === 0) {
            throw new Error('No transaction data available');
        }
        
        // Generate all other data from the transactions
        const unifiedData = generateUnifiedDataFromTransactions(allTransactionsData);
        
        // Store all transactions for pagination
        allTransactions = allTransactionsData;
    currentPage = 1;
        totalPages = Math.ceil(allTransactions.length / pageSize);
        
        // Update all sections with the same unified data
        updateKeyMetrics(unifiedData);
        updateCharts(unifiedData);
        updateTransactionsTable(unifiedData);
        
        console.log('Dashboard data loaded successfully with unified approach');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show error message instead of sample data
        showErrorMessage('Unable to load data from API. Please check your connection and try again.');
        
        // Clear all sections
        updateKeyMetrics({
            summary: {
                total_transactions: 0,
                total_amount: 0,
                success_rate: 0
            }
        });
        updateCharts({
            charts: {
                monthly_stats: [],
                category_distribution: [],
                hourly_pattern: [],
                amount_distribution: []
            }
        });
        updateTransactionsTable({
            summary: { total_transactions: 0 }
        });
    }
}

// Load all transactions from API with pagination
async function loadAllTransactions() {
        const allTransactionsData = [];
        let offset = 0;
    const limit = 100; // Use larger chunks for better performance
        let hasMore = true;
        let consecutiveErrors = 0;
        
        while (hasMore && consecutiveErrors < 3) {
            try {
                const transactionsResponse = await fetch(`http://localhost:8000/api/transactions?limit=${limit}&offset=${offset}`);
                if (!transactionsResponse.ok) {
                    console.warn(`API error at offset ${offset}, stopping pagination`);
                    break;
                }
                
                const batch = await transactionsResponse.json();
                
            // Check if we got an error response
                if (batch.success === false) {
                    console.warn(`API returned error at offset ${offset}, stopping pagination`);
                    break;
                }
                
                allTransactionsData.push(...batch);
            
            // If we got fewer than the limit, we've reached the end
                hasMore = batch.length === limit;
                offset += limit;
            consecutiveErrors = 0; // Reset error counter on success
                
                // Safety check to prevent infinite loops
                if (offset > 10000) break;
                
            } catch (error) {
                console.warn(`Error fetching transactions at offset ${offset}:`, error);
                consecutiveErrors++;
            offset += limit; // Try next batch
        }
    }
    
    return allTransactionsData;
}

// Generate unified data from transactions - single source of truth
function generateUnifiedDataFromTransactions(transactions) {
    if (!transactions || transactions.length === 0) {
        return {
            summary: {
                total_transactions: 0,
                total_amount: 0,
                success_rate: 0,
                active_users: 0
            },
            charts: {
                monthly_stats: [],
                category_distribution: [],
                hourly_pattern: [],
                amount_distribution: []
            }
        };
    }
    
    // Calculate summary statistics
    const totalAmount = transactions.reduce((sum, tx) => sum + (tx.amount || 0), 0);
    const successfulTransactions = transactions.filter(tx => tx.status === 'SUCCESS').length;
    const successRate = transactions.length > 0 ? (successfulTransactions / transactions.length) * 100 : 0;
    const uniquePhones = new Set(transactions.map(tx => tx.phone).filter(phone => phone)).size;
    
    // Generate category distribution from transactions
    const categoryStats = {};
    transactions.forEach(tx => {
        let category = tx.category || tx.type || 'UNKNOWN';
        
        // Normalize category names for display
        if (category === 'DATA_BUNDLE') category = 'Data Bundle';
        else if (category === 'AIRTIME') category = 'Airtime';
        else if (category === 'DEPOSIT') category = 'Deposit';
        else if (category === 'WITHDRAWAL') category = 'Withdrawal';
        else if (category === 'PAYMENT') category = 'Payment';
        else if (category === 'TRANSFER') category = 'Transfer';
        else if (category === 'QUERY') category = 'Query';
        else if (category === 'OTHER') category = 'Other';
        else if (category === 'UNKNOWN') category = 'Unknown';
        else if (category === 'PURCHASE') category = 'Purchase';
        else if (category === 'SEND') category = 'Send';
        else if (category === 'RECEIVE') category = 'Receive';
        else if (category === 'CASH_OUT') category = 'Cash Out';
        
        if (!categoryStats[category]) {
            categoryStats[category] = { count: 0, total_amount: 0, amounts: [] };
        }
        categoryStats[category].count++;
        categoryStats[category].total_amount += tx.amount || 0;
        categoryStats[category].amounts.push(tx.amount || 0);
    });
    
    const categoryDistribution = Object.entries(categoryStats).map(([category, stats]) => ({
        category,
            count: stats.count,
        total_amount: stats.total_amount,
        avg_amount: stats.total_amount / stats.count,
        min_amount: Math.min(...stats.amounts),
        max_amount: Math.max(...stats.amounts)
        }));
    
    // Generate monthly stats from transactions
        const monthlyStats = {};
    transactions.forEach(tx => {
            const date = new Date(tx.date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            if (!monthlyStats[monthKey]) {
                monthlyStats[monthKey] = { count: 0, volume: 0 };
            }
            monthlyStats[monthKey].count++;
        monthlyStats[monthKey].volume += tx.amount || 0;
        });
        
    const monthlyStatsArray = Object.entries(monthlyStats)
            .sort(([a], [b]) => a.localeCompare(b))
        .map(([month, data]) => ({ month, ...data }));
    
    // Generate hourly pattern from transactions
    const hourlyPattern = Array.from({length: 24}, (_, i) => ({
        hour: i,
        count: 0,
        volume: 0
    }));
    
    transactions.forEach(tx => {
            const hour = new Date(tx.date).getHours();
            hourlyPattern[hour].count++;
        hourlyPattern[hour].volume += tx.amount || 0;
        });
    
    // Generate amount distribution
    const amountRanges = [
        { range: '0-1,000', min: 0, max: 1000, count: 0 },
        { range: '1,000-5,000', min: 1000, max: 5000, count: 0 },
        { range: '5,000-10,000', min: 5000, max: 10000, count: 0 },
        { range: '10,000-25,000', min: 10000, max: 25000, count: 0 },
        { range: '25,000-50,000', min: 25000, max: 50000, count: 0 },
        { range: '50,000+', min: 50000, max: Infinity, count: 0 }
    ];
    
    transactions.forEach(tx => {
        const amount = tx.amount || 0;
        for (let range of amountRanges) {
            if (amount >= range.min && amount < range.max) {
                range.count++;
                break;
            }
        }
    });
    
    return {
        summary: {
            total_transactions: transactions.length,
            total_amount: totalAmount,
            success_rate: successRate,
            active_users: uniquePhones,
            successful_transactions: successfulTransactions,
            failed_transactions: transactions.length - successfulTransactions,
            last_updated: new Date().toISOString()
        },
        charts: {
            monthly_stats: monthlyStatsArray,
            category_distribution: categoryDistribution,
            hourly_pattern: hourlyPattern,
            amount_distribution: amountRanges
        }
    };
}


// SMS parsing functions removed - now using API data exclusively

// This function is no longer needed - we use generateUnifiedDataFromTransactions instead

// Sample data function removed - system now only uses real API data

// Update key metrics cards
function updateKeyMetrics(data) {
    const metrics = {
        totalTransactions: data.summary?.total_transactions || 0,
        totalAmount: data.summary?.total_amount || 0,
        successRate: data.summary?.success_rate || 0
    };
    
    // Animate number updates
    Object.entries(metrics).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element) {
            const formattedValue = formatMetricValue(key, value);
            element.innerHTML = `<span class="formatted-number animate-slide-in" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: clamp(1.2rem, 3vw, 1.8rem); display: flex; align-items: center; justify-content: center; height: 100%;">${formattedValue}</span>`;
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
            return value.toLocaleString();
        default:
            return value;
    }
}

// Update all charts
function updateCharts(data) {
    // Use chart data from parsed SMS data
    updateVolumeChart(data.charts?.monthly_stats || []);
    updateCategoryChart(data.charts?.category_distribution || []);
    updateAmountChart(data.charts?.amount_distribution || []);
    updateHourlyChart(data.charts?.hourly_pattern || []);
}

// This function is no longer needed - we use generateUnifiedDataFromTransactions instead

// Volume by Month Chart with Brutalist Styling
function updateVolumeChart(monthlyStats) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
    // Handle empty data
    if (!monthlyStats || monthlyStats.length === 0) {
        if (charts.volume) charts.volume.destroy();
        return;
    }
    
    const chartData = {
        labels: monthlyStats.map(d => formatMonth(d.month)),
            datasets: [{
            label: 'Transaction Count',
            data: monthlyStats.map(d => d.count),
            backgroundColor: COLORS.blue,
            borderColor: COLORS.blue,
            borderWidth: 4,
            fill: false,
            tension: 0,
            pointRadius: 8,
            pointBackgroundColor: COLORS.white,
            pointBorderColor: COLORS.blue,
            pointBorderWidth: 3,
            pointHoverRadius: 12,
            pointStyle: 'rect',
            borderJoinStyle: 'miter',
            borderCapStyle: 'square',
            yAxisID: 'y'
        }, {
            label: 'Volume (RWF)',
            data: monthlyStats.map(d => d.volume || 0),
            backgroundColor: COLORS.orange,
            borderColor: COLORS.orange,
            borderWidth: 4,
            fill: false,
            tension: 0,
            pointRadius: 6,
            pointBackgroundColor: COLORS.white,
            pointBorderColor: COLORS.orange,
            pointBorderWidth: 3,
            pointHoverRadius: 10,
            pointStyle: 'circle',
            borderJoinStyle: 'miter',
            borderCapStyle: 'square',
            yAxisID: 'y1'
        }]
    };
    
    if (charts.volume) charts.volume.destroy();
    
    charts.volume = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                    font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            size: 14,
                            weight: BRUTALIST_CONFIG.fontWeight
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                        color: COLORS.black,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            if (label.includes('Volume')) {
                                return `${label}: ${formatCurrency(value)}`;
                            }
                            return `${label}: ${value}`;
                        }
                    },
                    backgroundColor: COLORS.white,
                    titleColor: COLORS.black,
                    bodyColor: COLORS.black,
                    borderColor: COLORS.black,
                    borderWidth: 2,
                    titleFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 14
                    },
                    bodyFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    grid: {
                        color: COLORS.gray,
                        lineWidth: 1,
                        drawBorder: true,
                        borderColor: COLORS.black,
                        borderWidth: 2
                    },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                    color: COLORS.black
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    suggestedMin: 0,
                    suggestedMax: undefined,
                    grid: {
                        color: COLORS.gray,
                        lineWidth: 1,
                        drawBorder: true,
                        borderColor: COLORS.black,
                        borderWidth: 2
                    },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                        color: COLORS.black,
                        stepSize: undefined,
                        precision: 0
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    suggestedMin: 0,
                    suggestedMax: undefined,
                    grid: {
                        drawOnChartArea: false,
                        drawBorder: true,
                        borderColor: COLORS.black,
                        borderWidth: 2
                    },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                        color: COLORS.black,
                        stepSize: undefined,
                        precision: 0,
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// Category Distribution Chart with Brutalist Styling
function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    console.log('Category chart data:', categories);
    
    // Handle empty data
    if (!categories || categories.length === 0) {
        if (charts.category) charts.category.destroy();
        return;
    }
    
    const chartData = {
        labels: categories.map(c => c.category.toUpperCase()),
            datasets: [{
            label: 'Transaction Count',
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
                borderWidth: BRUTALIST_CONFIG.borderWidth,
            offset: 8,
            borderRadius: 0
        }]
    };
    
    if (charts.category) charts.category.destroy();
    
    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '40%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            size: 14,
                            weight: BRUTALIST_CONFIG.fontWeight
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                        color: COLORS.black,
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'rect',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const dataset = data.datasets[0];
                                    const value = dataset.data[i];
                                    const total = dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: dataset.backgroundColor[i],
                                        strokeStyle: dataset.borderColor,
                                        lineWidth: dataset.borderWidth,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            const category = categories[context.dataIndex];
                            return [
                                `${label}: ${value} transactions (${percentage}%)`,
                                `Total Amount: ${formatCurrency(category.total_amount || 0)}`,
                                `Avg Amount: ${formatCurrency(category.avg_amount || 0)}`,
                                `Min: ${formatCurrency(category.min_amount || 0)}`,
                                `Max: ${formatCurrency(category.max_amount || 0)}`
                            ];
                        }
                    },
                    backgroundColor: COLORS.white,
                    titleColor: COLORS.black,
                    bodyColor: COLORS.black,
                    borderColor: COLORS.black,
                    borderWidth: 2,
                    titleFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 14
                    },
                    bodyFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 12
                    }
                }
            }
        }
    });
}

// Amount Distribution Chart with Brutalist Styling
function updateAmountChart(amountData) {
    const ctx = document.getElementById('amountChart');
    if (!ctx) return;
    
    console.log('Amount chart data:', amountData);
    
    // Handle empty data
    if (!amountData || amountData.length === 0) {
        if (charts.amount) charts.amount.destroy();
        return;
    }
    
    const chartData = {
        labels: amountData.map(a => a.range),
            datasets: [{
            label: 'Transaction Count',
            data: amountData.map(a => a.count),
            backgroundColor: [
                COLORS.yellow,
                COLORS.pink,
                COLORS.mint,
                COLORS.purple,
                COLORS.blue,
                COLORS.orange
            ],
                borderColor: COLORS.black,
                borderWidth: BRUTALIST_CONFIG.borderWidth,
            barThickness: 40,
            borderSkipped: false,
            borderRadius: 0,
            borderJoinStyle: 'miter'
        }]
    };
    
    if (charts.amount) charts.amount.destroy();
    
    charts.amount = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                    font: {
                        family: BRUTALIST_CONFIG.fontFamily,
                            size: 14,
                            weight: BRUTALIST_CONFIG.fontWeight
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform,
                        color: COLORS.black,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed.y;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} transactions (${percentage}%)`;
                        }
                    },
                    backgroundColor: COLORS.white,
                    titleColor: COLORS.black,
                    bodyColor: COLORS.black,
                    borderColor: COLORS.black,
                    borderWidth: 2,
                    titleFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 14
                    },
                    bodyFont: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform
                    }
                    },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: COLORS.black,
                        lineWidth: 2
                },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        textTransform: BRUTALIST_CONFIG.textTransform
                    }
                }
            }
        }
    });
}

// Hourly Pattern Chart with Brutalist Styling
function updateHourlyChart(hourlyData) {
    const ctx = document.getElementById('hourlyChart');
    if (!ctx) return;
    
    // Handle empty data
    if (!hourlyData || hourlyData.length === 0) {
        if (charts.hourly) charts.hourly.destroy();
        return;
    }
    
    // Use the 24-hour data from our enhanced parsing
    const labels = hourlyData.map(h => `${h.hour}:00`);
    const countData = hourlyData.map(h => h.count || 0);
    const volumeData = hourlyData.map(h => h.volume || 0);
    
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Transaction Count',
            data: countData,
            backgroundColor: COLORS.mint,
            borderColor: COLORS.mint,
            borderWidth: 4,
            fill: false,
            tension: 0,
            pointRadius: 8,
            pointBackgroundColor: COLORS.white,
            pointBorderColor: COLORS.mint,
            pointBorderWidth: 3,
            pointHoverRadius: 12,
            pointStyle: 'rect',
            borderJoinStyle: 'miter',
            borderCapStyle: 'square',
            yAxisID: 'y'
        }, {
            label: 'Transaction Volume (RWF)',
            data: volumeData,
            backgroundColor: COLORS.purple,
            borderColor: COLORS.purple,
            borderWidth: 4,
            fill: false,
            tension: 0,
            pointRadius: 6,
            pointBackgroundColor: COLORS.white,
            pointBorderColor: COLORS.purple,
            pointBorderWidth: 3,
            pointHoverRadius: 10,
            pointStyle: 'circle',
            borderJoinStyle: 'miter',
            borderCapStyle: 'square',
            yAxisID: 'y1'
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
                    type: 'category',
                    grid: {
                        color: COLORS.gray,
                        lineWidth: 1,
                        drawBorder: true,
                        borderColor: COLORS.black,
                        borderWidth: 2
                    },
                    ticks: {
                font: {
                    family: BRUTALIST_CONFIG.fontFamily,
                    weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        color: COLORS.black,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    type: 'linear',
                    beginAtZero: true,
                    suggestedMin: 0,
                    suggestedMax: undefined,
                    grid: {
                        color: COLORS.gray,
                        lineWidth: 1,
                        drawBorder: true,
                        borderColor: COLORS.black,
                        borderWidth: 2
                    },
                    ticks: {
                        font: {
                            family: BRUTALIST_CONFIG.fontFamily,
                            weight: BRUTALIST_CONFIG.fontWeight,
                            size: 12
                        },
                        color: COLORS.black,
                        stepSize: undefined,
                        precision: 0
                    }
                }
            },
            plugins: {
            legend: {
                display: false
            },
            tooltip: getBrutalistTooltipConfig()
            }
        }
    });
}

// Get brutalist bar chart options
function getBrutalistBarChartOptions(title, horizontal = false) {
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
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 12
                    },
                    color: COLORS.black,
                    textTransform: BRUTALIST_CONFIG.textTransform
                },
                border: {
                    display: true,
                    color: COLORS.black,
                    width: BRUTALIST_CONFIG.borderWidth
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: COLORS.black,
                    lineWidth: 2,
                    drawBorder: true,
                    borderColor: COLORS.black
                },
                ticks: {
                    font: {
                        family: BRUTALIST_CONFIG.fontFamily,
                        weight: BRUTALIST_CONFIG.fontWeight,
                        size: 12
                    },
                    color: COLORS.black,
                    callback: function(value) {
                        if (horizontal) return value.toLocaleString();
                        return value;
                    }
                },
                border: {
                    display: true,
                    color: COLORS.black,
                    width: BRUTALIST_CONFIG.borderWidth
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: getBrutalistTooltipConfig()
        }
    };
}

// Get standard bar chart options (legacy)
function getBarChartOptions(title, horizontal = false) {
    return getBrutalistBarChartOptions(title, horizontal);
}

// Get brutalist tooltip configuration
function getBrutalistTooltipConfig() {
    return {
        backgroundColor: COLORS.white,
        titleColor: COLORS.black,
        bodyColor: COLORS.black,
        borderColor: COLORS.black,
        borderWidth: BRUTALIST_CONFIG.borderWidth,
        titleFont: {
            size: 18,
            weight: BRUTALIST_CONFIG.fontWeight,
            family: BRUTALIST_CONFIG.fontFamily
        },
        bodyFont: {
            size: 14,
            weight: BRUTALIST_CONFIG.fontWeight,
            family: "'Public Sans', sans-serif"
        },
        padding: 16,
        displayColors: false,
        cornerRadius: 0,
        callbacks: {
            title: function(context) {
                return context[0].label.toUpperCase();
            },
            label: function(context) {
                let label = context.dataset.label || '';
                if (label) label += ': ';
                
                if (context.parsed.y !== null) {
                    label += formatNumber(context.parsed.y);
                } else if (context.parsed !== null) {
                    label += formatNumber(context.parsed);
                }
                
                return label.toUpperCase();
            }
        }
    };
}

// Get tooltip configuration (legacy)
function getTooltipConfig() {
    return getBrutalistTooltipConfig();
}

// Update transactions table with pagination
function updateTransactionsTable(data) {
    const tbody = document.getElementById('transactionsBody');
    const tableInfo = document.getElementById('tableInfo');
    const paginationControls = document.getElementById('paginationControls');

    if (!tbody) return;
    
    // Calculate pagination
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = Math.min(startIndex + pageSize, allTransactions.length);
    const transactionsToShow = allTransactions.slice(startIndex, endIndex);
    
    if (allTransactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="nb-text-center">
                    <div class="empty-state">
                        <div class="empty-state-icon">📊</div>
                        <p>No transaction data available</p>
                        <p style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">Data will appear here once transactions are processed from raw files</p>
                    </div>
                </td>
            </tr>
        `;
        tableInfo.innerHTML = '<span>No transactions to display</span>';
        paginationControls.style.display = 'none';
        return;
    }

    // Clear existing rows
    tbody.innerHTML = '';

    // Add transactions for current page
    transactionsToShow.forEach((t, index) => {
        const row = document.createElement('tr');
        row.className = 'animate-slide-in';
        row.style.animationDelay = `${index * 0.05}s`;
        row.innerHTML = `
            <td>${formatDate(t.date)}</td>
            <td><span class="type-badge type-${(t.type || 'unknown').toLowerCase()}">${t.type || 'Unknown'}</span></td>
            <td class="formatted-number">${formatCurrency(t.amount)}</td>
            <td>${formatPhone(t.phone)}</td>
            <td>${t.reference || 'N/A'}</td>
            <td>${t.recipient_name || 'N/A'}</td>
            <td>${t.personal_id || 'N/A'}</td>
            <td><span class="status-badge status-${(t.status || 'unknown').toLowerCase()}">${t.status || 'Unknown'}</span></td>
            <td><button class="view-btn" onclick="viewTransactionDetails('${t.id || (startIndex + index)}')">VIEW</button></td>
        `;
        tbody.appendChild(row);
    });

    // Update table info
    const startItem = allTransactions.length > 0 ? startIndex + 1 : 0;
    const endItem = endIndex;
    tableInfo.innerHTML = `<span>Showing ${startItem}-${endItem} of ${allTransactions.length} total transactions</span>`;
    
    // Update pagination controls
    updatePaginationControls();
}

// Pagination functions
function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    updateTransactionsTable();
    
    // Scroll to top of table
    const table = document.getElementById('transactionsTable');
    if (table) {
        table.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function handlePageSizeChange() {
    const pageSizeSelect = document.getElementById('pageSize');
    if (pageSizeSelect) {
        pageSize = parseInt(pageSizeSelect.value);
        currentPage = 1;
        totalPages = Math.ceil(allTransactions.length / pageSize);
        updateTransactionsTable();
    }
}

function updatePaginationControls() {
    const paginationControls = document.getElementById('paginationControls');
    const firstPageBtn = document.getElementById('firstPageBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const lastPageBtn = document.getElementById('lastPageBtn');
    const pageNumbers = document.getElementById('pageNumbers');
    
    if (!paginationControls) return;
    
    // Show pagination controls if there are multiple pages
    if (totalPages > 1) {
        paginationControls.style.display = 'flex';
    } else {
        paginationControls.style.display = 'none';
        return;
    }
    
    // Update navigation buttons
    if (firstPageBtn) {
        firstPageBtn.disabled = currentPage === 1;
    }
    if (prevPageBtn) {
        prevPageBtn.disabled = currentPage === 1;
    }
    if (nextPageBtn) {
        nextPageBtn.disabled = currentPage === totalPages;
    }
    if (lastPageBtn) {
        lastPageBtn.disabled = currentPage === totalPages;
    }
    
    // Generate page numbers
    if (pageNumbers) {
        pageNumbers.innerHTML = '';
        generatePageNumbers(pageNumbers);
    }
}

function generatePageNumbers(container) {
    const maxVisiblePages = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Adjust start page if we're near the end
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Add first page and ellipsis if needed
    if (startPage > 1) {
        addPageNumber(container, 1);
        if (startPage > 2) {
            addEllipsis(container);
        }
    }
    
    // Add page numbers
    for (let i = startPage; i <= endPage; i++) {
        addPageNumber(container, i);
    }
    
    // Add ellipsis and last page if needed
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            addEllipsis(container);
        }
        addPageNumber(container, totalPages);
    }
}

function addPageNumber(container, pageNum) {
    const pageBtn = document.createElement('button');
    pageBtn.className = 'page-number';
    if (pageNum === currentPage) {
        pageBtn.classList.add('active');
    }
    pageBtn.textContent = pageNum;
    pageBtn.addEventListener('click', () => goToPage(pageNum));
    container.appendChild(pageBtn);
}

function addEllipsis(container) {
    const ellipsis = document.createElement('span');
    ellipsis.className = 'page-number ellipsis';
    ellipsis.textContent = '...';
    container.appendChild(ellipsis);
}

// Smooth scroll function for navigation
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
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

function formatMonth(monthStr) {
    if (!monthStr) return 'N/A';
    const [year, month] = monthStr.split('-');
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short'
    });
}

function formatPhone(phone) {
    if (!phone) return 'N/A';
    
    // Normalize phone number to Rwanda format (+250)
    let normalizedPhone = phone;
    
    // If it starts with +256, convert to +250 (Rwanda)
    if (normalizedPhone.startsWith('+256')) {
        normalizedPhone = '+250' + normalizedPhone.substring(4);
    }
    // If it starts with 256, add +250
    else if (normalizedPhone.startsWith('256')) {
        normalizedPhone = '+250' + normalizedPhone.substring(3);
    }
    // If it starts with 250, add +
    else if (normalizedPhone.startsWith('250')) {
        normalizedPhone = '+' + normalizedPhone;
    }
    // If it doesn't start with +, add +250
    else if (!normalizedPhone.startsWith('+')) {
        normalizedPhone = '+250' + normalizedPhone;
    }
    
    // Mask the last 4 digits for privacy
    if (normalizedPhone.length > 8) {
        return normalizedPhone.slice(0, -4) + '****';
    }
    
    return normalizedPhone;
}

// UI Helper Functions

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

// View transaction details
function viewTransactionDetails(transactionId) {
    let transaction;
    
    // Try to find by ID first
    if (transactionId) {
        transaction = allTransactions.find(t => t.id === transactionId || t.id === parseInt(transactionId));
    }
    
    // If not found by ID, try to find by index
    if (!transaction && !isNaN(transactionId)) {
        const index = parseInt(transactionId);
        if (index >= 0 && index < allTransactions.length) {
            transaction = allTransactions[index];
        }
    }
    
    if (!transaction) {
        console.error('Transaction not found:', transactionId);
        return;
    }
    
    // Create modal or detailed view
    const modal = document.createElement('div');
    modal.className = 'transaction-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Transaction Details</h3>
                <button class="close-btn" onclick="this.closest('.transaction-modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>ID:</label>
                        <span>${transaction.id || 'N/A'}</span>
                </div>
                    <div class="detail-item">
                        <label>Date:</label>
                        <span>${formatDate(transaction.date)}</span>
                </div>
                    <div class="detail-item">
                        <label>Type:</label>
                        <span class="type-badge type-${(transaction.type || 'unknown').toLowerCase()}">${transaction.type || 'Unknown'}</span>
                </div>
                    <div class="detail-item">
                        <label>Amount:</label>
                        <span class="formatted-number">${formatCurrency(transaction.amount)}</span>
                </div>
                    <div class="detail-item">
                        <label>Phone:</label>
                        <span>${formatPhone(transaction.phone)}</span>
                </div>
                    <div class="detail-item">
                        <label>Reference:</label>
                        <span>${transaction.reference || 'N/A'}</span>
                </div>
                    <div class="detail-item">
                        <label>Recipient Name:</label>
                        <span>${transaction.recipient_name || (['DEPOSIT', 'WITHDRAWAL', 'Purchase', 'Airtime', 'Cash Out'].includes(transaction.type) ? 'Self' : 'N/A')}</span>
                </div>
                    <div class="detail-item">
                        <label>Personal ID:</label>
                        <span>${transaction.personal_id || (['DEPOSIT', 'WITHDRAWAL', 'Purchase', 'Airtime', 'Cash Out'].includes(transaction.type) ? 'Self' : 'N/A')}</span>
                </div>
                    <div class="detail-item">
                        <label>Status:</label>
                        <span class="status-badge status-${(transaction.status || 'unknown').toLowerCase()}">${transaction.status || 'Unknown'}</span>
                </div>
                    ${transaction.type === 'DEPOSIT' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Money deposited into your account by Self</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'WITHDRAWAL' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Money withdrawn from your account by Self</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'PAYMENT' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Payment sent to ${transaction.recipient_name || 'recipient'}</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'Purchase' && transaction.category === 'Data Bundle' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Data bundle purchase for internet access</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'Airtime' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Airtime purchase for ${transaction.phone || 'phone number'}</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'Send' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Money sent to ${transaction.recipient_name || 'recipient'}</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'Receive' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Money received from ${transaction.recipient_name || 'sender'}</span>
                    </div>
                    ` : ''}
                    ${transaction.type === 'Cash Out' ? `
                    <div class="detail-item full-width">
                        <label>Transaction Description:</label>
                        <span>Cash withdrawn from account</span>
                    </div>
                    ` : ''}
                    ${transaction.raw_data ? `
                    <div class="detail-item full-width">
                        <label>Original SMS Data:</label>
                        <textarea readonly>${transaction.raw_data}</textarea>
                </div>
                    ` : ''}
                    ${transaction.xml_attributes ? `
                    <div class="detail-item full-width">
                        <label>XML Attributes:</label>
                        <textarea readonly>${JSON.stringify(transaction.xml_attributes, null, 2)}</textarea>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .transaction-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border: 6px solid black;
            border-radius: 0;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 12px 12px 0 rgba(0,0,0,1);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border-bottom: 6px solid black;
            background: var(--brutal-yellow);
            font-family: 'Lexend Mega', sans-serif;
        }
        .modal-header h3 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--brutal-black);
        }
        .modal-body {
            padding: 1.5rem;
        }
        .detail-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .detail-item.full-width {
            grid-column: 1 / -1;
        }
        .detail-item label {
            font-weight: 700;
            text-transform: uppercase;
            color: var(--brutal-black);
            font-family: 'Lexend Mega', sans-serif;
            display: block;
            margin-bottom: 0.5rem;
        }
        .detail-item span {
            display: block;
            padding: 0.5rem;
            background: var(--brutal-gray);
            border: 2px solid var(--brutal-black);
            font-weight: 600;
        }
        .detail-item textarea {
            width: 100%;
            height: 120px;
            border: 3px solid var(--brutal-black);
            padding: 0.75rem;
            font-family: monospace;
            font-size: 0.8rem;
            background: var(--brutal-white);
            resize: vertical;
        }
        .close-btn {
            background: var(--brutal-pink);
            color: var(--brutal-white);
            border: 3px solid var(--brutal-black);
            font-size: 1.5rem;
            font-weight: 700;
            cursor: pointer;
            padding: 0.5rem 0.75rem;
            box-shadow: 4px 4px 0 rgba(0,0,0,1);
            transition: all 0.2s ease;
        }
        .close-btn:hover {
            transform: translateY(-2px);
            box-shadow: 6px 6px 0 rgba(0,0,0,1);
        }
        .close-btn:active {
            transform: translateY(0);
            box-shadow: 2px 2px 0 rgba(0,0,0,1);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
}
