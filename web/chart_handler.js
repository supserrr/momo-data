// MoMo Dashboard - Chart Handler with NeoBrutalism Style
// Handles data fetching and Chart.js visualization

// Enhanced Brutalist Color Palette with more colors for sub-categories
const COLORS = {
    yellow: '#ffc947',
    pink: '#ff90e8',
    mint: '#90ffdc',
    purple: '#b690ff',
    blue: '#90b3ff',
    orange: '#ffa500',
    green: '#90ff90',
    red: '#ff6b6b',
    cyan: '#4ecdc4',
    indigo: '#6c5ce7',
    teal: '#00b894',
    coral: '#fd79a8',
    lime: '#a4b0be',
    amber: '#fdcb6e',
    emerald: '#00cec9',
    rose: '#e84393',
    violet: '#a29bfe',
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
let filteredTransactions = [];
let currentPage = 1;
let pageSize = 10; // Default page size
let totalPages = 1;
let currentFilters = {};

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    initializeFilters();
    
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

// Load dashboard data from API - efficient approach with dedicated endpoints
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data from dedicated API endpoints...');
        
        // Load all data in parallel from dedicated endpoints
        const [
            summaryData,
            monthlyStats,
            categoryDistribution,
            transactionTypesData,
            hourlyPattern,
            amountDistribution,
            transactionsData
        ] = await Promise.all([
            loadSummaryData(),
            loadMonthlyStats(),
            loadCategoryDistribution(),
            loadTransactionTypesByAmount(),
            loadHourlyPattern(),
            loadAmountDistribution(),
            loadTransactionsForTable()
        ]);
        
        console.log('All data loaded successfully:', {
            summary: summaryData,
            monthlyStats: monthlyStats.length,
            categories: categoryDistribution.length,
            transactionTypes: transactionTypesData.length,
            hourlyPattern: hourlyPattern.length,
            amountDistribution: amountDistribution.length,
            transactions: transactionsData.length
        });
        
        // Store transactions for pagination and filtering
        allTransactions = transactionsData;
        filteredTransactions = [...transactionsData];
        currentPage = 1;
        totalPages = Math.ceil(allTransactions.length / pageSize);
        
        // Create unified data structure
        const unifiedData = {
            summary: summaryData,
            charts: {
                monthly_stats: monthlyStats,
                category_distribution: categoryDistribution,
                transaction_types_by_amount: transactionTypesData,
                hourly_pattern: hourlyPattern,
                amount_distribution: amountDistribution
            }
        };
        
        // Update all sections with the data
        updateKeyMetrics(unifiedData);
        updateCharts(unifiedData);
        updateTransactionsTable(unifiedData);
        
        console.log('Dashboard data loaded successfully with dedicated endpoints approach');
        
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
                transaction_types_by_amount: [],
                hourly_pattern: [],
                amount_distribution: []
            }
        });
        updateTransactionsTable({
            summary: { total_transactions: 0 }
        });
    }
}

// Load summary data for key metrics
async function loadSummaryData() {
    try {
        console.log('Fetching summary data...');
        const response = await fetch('http://localhost:8001/api/dashboard-data');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        return data.summary || { total_transactions: 0, total_amount: 0, success_rate: 0 };
    } catch (error) {
        console.warn('Error fetching summary data:', error);
        return { total_transactions: 0, total_amount: 0, success_rate: 0 };
    }
}

// Load monthly stats for volume chart
async function loadMonthlyStats() {
    try {
        console.log('Fetching monthly stats...');
        const response = await fetch('http://localhost:8001/api/monthly-stats');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Error fetching monthly stats:', error);
        return [];
    }
}

// Load category distribution for doughnut chart
async function loadCategoryDistribution() {
    try {
        console.log('Fetching category distribution...');
        const response = await fetch('http://localhost:8001/api/category-distribution');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Error fetching category distribution:', error);
        return [];
    }
}

// Load hourly pattern for line chart
async function loadHourlyPattern() {
    try {
        console.log('Fetching hourly pattern...');
        const response = await fetch('http://localhost:8001/api/hourly-pattern');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Error fetching hourly pattern:', error);
        return [];
    }
}

// Load amount distribution for bar chart
async function loadAmountDistribution() {
    try {
        console.log('Fetching amount distribution...');
        const response = await fetch('http://localhost:8001/api/amount-distribution');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Error fetching amount distribution:', error);
        return [];
    }
}

// Load transactions for table (limited for performance)
async function loadTransactionsForTable() {
    try {
        console.log('Fetching transactions for table...');
        const response = await fetch('http://localhost:8001/api/transactions?limit=1000&offset=0');
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Error fetching transactions for table:', error);
        return [];
    }
}

// Load all transactions from API with pagination (legacy function, kept for compatibility)
async function loadAllTransactions() {
        const allTransactionsData = [];
        let offset = 0;
    const limit = 100; // Use larger chunks for better performance
        let hasMore = true;
        let consecutiveErrors = 0;
        
        while (hasMore && consecutiveErrors < 3) {
            try {
                console.log(`Fetching transactions: offset=${offset}, limit=${limit}`);
                const transactionsResponse = await fetch(`http://localhost:8001/api/transactions?limit=${limit}&offset=${offset}`);
                console.log(`Response status: ${transactionsResponse.status}`);
                if (!transactionsResponse.ok) {
                    console.warn(`API error at offset ${offset}, stopping pagination`);
                    break;
                }
                
                const batch = await transactionsResponse.json();
                console.log(`Received ${batch.length} transactions in batch`);
                
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

// Load transaction types by amount data from API
async function loadTransactionTypesByAmount() {
    try {
        console.log('Fetching transaction types by amount...');
        const response = await fetch('http://localhost:8001/api/transaction-types-by-amount');
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            console.warn('API error for transaction types by amount');
            return [];
        }
        
        const data = await response.json();
        console.log('Received transaction types data:', data);
        
        // Check if we got an error response
        if (data.success === false) {
            console.warn('API returned error for transaction types by amount');
            return [];
        }
        
        return data;
    } catch (error) {
        console.warn('Error fetching transaction types by amount:', error);
        return [];
    }
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
        // Use transaction type instead of category to show main transaction types
        let transactionType = tx.type || tx.transaction_type || 'UNKNOWN';
        
        // Clean up the type name for better display
        const displayType = transactionType.replace(/_/g, ' ').toUpperCase();
        
        if (!categoryStats[displayType]) {
            categoryStats[displayType] = { count: 0, total_amount: 0, amounts: [] };
        }
        categoryStats[displayType].count++;
        categoryStats[displayType].total_amount += tx.amount || 0;
        categoryStats[displayType].amounts.push(tx.amount || 0);
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
            if (isNaN(date.getTime())) {
                console.warn('Invalid date for transaction:', tx.date, tx);
                return;
            }
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
    
    console.log('Generated monthly stats:', monthlyStatsArray);
    
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
    updateTransactionTypesChart(data.charts?.transaction_types_by_amount || []);
    updateAmountChart(data.charts?.amount_distribution || []);
    updateHourlyChart(data.charts?.hourly_pattern || []);
}

// This function is no longer needed - we use generateUnifiedDataFromTransactions instead


// Volume by Month Chart with Brutalist Styling
function updateVolumeChart(monthlyStats) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
    console.log('updateVolumeChart called with:', monthlyStats);
    
    // Handle empty data
    if (!monthlyStats || monthlyStats.length === 0) {
        console.log('No monthly stats data, destroying chart');
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

// Group categories into simplified, meaningful groups
function groupCategories(categories) {
    const groups = {
        'Deposits': {
            groupName: 'Deposits',
            count: 0,
            total_amount: 0,
            subCategories: []
        },
        'Transfers': {
            groupName: 'Transfers',
            count: 0,
            total_amount: 0,
            subCategories: []
        },
        'Payments': {
            groupName: 'Payments',
            count: 0,
            total_amount: 0,
            subCategories: []
        },
        'Mobile Services': {
            groupName: 'Mobile Services',
            count: 0,
            total_amount: 0,
            subCategories: []
        },
        'Other': {
            groupName: 'Other',
            count: 0,
            total_amount: 0,
            subCategories: []
        }
    };
    
    // Group categories based on their names
    categories.forEach(category => {
        const categoryName = category.category;
        const count = parseInt(category.count) || 0;
        const totalAmount = parseFloat(category.total_amount) || 0;
        
        if (categoryName.includes('DEPOSIT') || categoryName.includes('Deposit')) {
            groups['Deposits'].count += count;
            groups['Deposits'].total_amount += totalAmount;
            groups['Deposits'].subCategories.push(categoryName);
        } else if (categoryName.includes('TRANSFER') || categoryName.includes('Transfer')) {
            groups['Transfers'].count += count;
            groups['Transfers'].total_amount += totalAmount;
            groups['Transfers'].subCategories.push(categoryName);
        } else if (categoryName.includes('PAYMENT') || categoryName.includes('Payment')) {
            groups['Payments'].count += count;
            groups['Payments'].total_amount += totalAmount;
            groups['Payments'].subCategories.push(categoryName);
        } else if (categoryName.includes('AIRTIME') || categoryName.includes('Airtime') || 
                   categoryName.includes('DATA') || categoryName.includes('Data')) {
            groups['Mobile Services'].count += count;
            groups['Mobile Services'].total_amount += totalAmount;
            groups['Mobile Services'].subCategories.push(categoryName);
        } else {
            groups['Other'].count += count;
            groups['Other'].total_amount += totalAmount;
            groups['Other'].subCategories.push(categoryName);
        }
    });
    
    // Calculate averages and filter out empty groups
    const result = Object.values(groups)
        .filter(group => group.count > 0)
        .map(group => ({
            ...group,
            avg_amount: group.count > 0 ? group.total_amount / group.count : 0
        }));
    
    return result;
}

// Category Distribution Chart with Brutalist Styling - Simplified Groups
function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    console.log('Category chart data:', categories);
    
    // Handle empty data
    if (!categories || categories.length === 0) {
        if (charts.category) charts.category.destroy();
        return;
    }
    
    // Group categories into simplified groups
    const groupedCategories = groupCategories(categories);
    console.log('Grouped categories:', groupedCategories);
    
    // Create dynamic color assignment for simplified groups
    const colorKeys = Object.keys(COLORS).filter(key => 
        !['black', 'white', 'gray', 'darkGray'].includes(key)
    );
    
    const chartData = {
        labels: groupedCategories.map(c => c.groupName.toUpperCase()),
            datasets: [{
            label: 'Transaction Count',
            data: groupedCategories.map(c => c.count),
            backgroundColor: groupedCategories.map((_, index) => {
                const colorKey = colorKeys[index % colorKeys.length];
                return COLORS[colorKey];
            }),
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
                                    const group = groupedCategories[i];
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
                            const group = groupedCategories[context.dataIndex];
                            return [
                                `Category Group: ${label}`,
                                `Transactions: ${value} (${percentage}%)`,
                                `Total Amount: ${formatCurrency(group.total_amount || 0)}`,
                                `Avg Amount: ${formatCurrency(group.avg_amount || 0)}`,
                                `Includes: ${group.subCategories.join(', ')}`
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
    
    // Generate colors for all ranges dynamically
    const colorKeys = Object.keys(COLORS).filter(key => 
        !['black', 'white', 'gray', 'darkGray'].includes(key)
    );
    const backgroundColors = amountData.map((_, index) => 
        COLORS[colorKeys[index % colorKeys.length]]
    );
    
    const chartData = {
        labels: amountData.map(a => a.amount_range),
            datasets: [{
            label: 'Transaction Count',
            data: amountData.map(a => a.count),
            backgroundColor: backgroundColors,
                borderColor: COLORS.black,
                borderWidth: BRUTALIST_CONFIG.borderWidth,
            barThickness: 30, // Reduced thickness to fit more bars
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


// Transaction Types by Amount Donut Chart with Brutalist Styling
function updateTransactionTypesChart(transactionTypesData) {
    const ctx = document.getElementById('transactionTypesChart');
    if (!ctx) return;
    
    console.log('Transaction types chart data:', transactionTypesData);
    
    // Handle empty data
    if (!transactionTypesData || transactionTypesData.length === 0) {
        if (charts.transactionTypes) charts.transactionTypes.destroy();
        return;
    }
    
    // Filter to only show the specific transaction types requested
    const requestedTypes = ['DEPOSIT', 'TRANSFER', 'PAYMENT', 'RECEIVE', 'AIRTIME', 'DATA_BUNDLE', 'PURCHASE'];
    const filteredData = transactionTypesData.filter(item => 
        requestedTypes.includes(item.transaction_type)
    );
    
    // Check for missing transaction types
    const availableTypes = transactionTypesData.map(item => item.transaction_type);
    const missingTypes = requestedTypes.filter(type => !availableTypes.includes(type));
    
    // If no data matches, show all available types
    const dataToShow = filteredData.length > 0 ? filteredData : transactionTypesData;
    
    // Log missing types for debugging
    if (missingTypes.length > 0) {
        console.log('Missing transaction types in database:', missingTypes);
        console.log('Available transaction types:', availableTypes);
    }
    
    // Create dynamic color assignment
    const colorKeys = Object.keys(COLORS).filter(key => 
        !['black', 'white', 'gray', 'darkGray'].includes(key)
    );
    
    const chartData = {
        labels: dataToShow.map(t => t.transaction_type.toUpperCase()),
        datasets: [{
            label: 'Total Amount (RWF)',
            data: dataToShow.map(t => t.total_amount),
            backgroundColor: dataToShow.map((item, index) => {
                const colorKey = colorKeys[index % colorKeys.length];
                // Make small values slightly more vibrant for visibility
                const isSmallValue = item.total_amount < 50000;
                return isSmallValue ? COLORS[colorKey] : COLORS[colorKey];
            }),
            borderColor: dataToShow.map((item, index) => {
                // Add thicker border for small values to make them more visible
                const isSmallValue = item.total_amount < 50000;
                return isSmallValue ? COLORS.black : COLORS.black;
            }),
            borderWidth: dataToShow.map(item => item.total_amount < 50000 ? 3 : 2),
            borderRadius: 4, // Slightly rounded corners for elegance
            borderSkipped: false
        }]
    };
    
    if (charts.transactionTypes) charts.transactionTypes.destroy();
    
    charts.transactionTypes = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Horizontal bar chart
            layout: {
                padding: {
                    left: 20,
                    right: 20,
                    top: 20,
                    bottom: 20
                }
            },
            plugins: {
                legend: {
                    display: false // Hide legend since values are on the bars
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label.toUpperCase();
                        },
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed.x; // x-axis for horizontal bars
                            const typeData = dataToShow[context.dataIndex];
                            const total = dataToShow.reduce((sum, t) => sum + t.total_amount, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            
                            return [
                                `Transaction Type: ${label}`,
                                `Total Amount: ${formatCurrency(value)} (${percentage}%)`,
                                `Transaction Count: ${typeData.count}`,
                                `Average Amount: ${formatCurrency(typeData.avg_amount)}`
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
            },
            scales: {
                x: {
                    beginAtZero: true,
                    suggestedMin: 0,
                    suggestedMax: undefined, // Let Chart.js auto-scale
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
                        callback: function(value) {
                            return formatCurrency(value);
                        },
                        maxTicksLimit: 8 // Limit number of ticks for cleaner look
                    }
                },
                y: {
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
                    categoryPercentage: 0.6, // More spacing between bars
                    barPercentage: 0.7, // Thinner bars for less chunkiness
                    minBarLength: 20 // Ensure minimum bar length for visibility
                }
            }
        }
    });
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
    
    // Use filtered data if available, otherwise use allTransactions
    const sourceData = data || filteredTransactions.length > 0 ? filteredTransactions : allTransactions;
    
    // Calculate pagination
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = Math.min(startIndex + pageSize, sourceData.length);
    const transactionsToShow = sourceData.slice(startIndex, endIndex);
    
    if (sourceData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="nb-text-center">
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
            <td><span class="type-badge type-${(t.transaction_type || t.type || 'unknown').toLowerCase()}">${t.transaction_type || t.type || 'Unknown'}</span></td>
            <td class="formatted-number">${formatCurrency(t.amount)}</td>
            <td><span class="direction-badge direction-${(t.direction || 'unknown').toLowerCase()}">${t.direction || 'Unknown'}</span></td>
            <td><span class="status-badge status-${(t.status || 'unknown').toLowerCase()}">${t.status || 'Unknown'}</span></td>
            <td><button class="view-btn" onclick="viewTransactionDetails('${t.id || (startIndex + index)}')">VIEW</button></td>
        `;
        tbody.appendChild(row);
    });

    // Update table info
    const startItem = sourceData.length > 0 ? startIndex + 1 : 0;
    const endItem = endIndex;
    tableInfo.innerHTML = `<span>Showing ${startItem}-${endItem} of ${sourceData.length} total transactions</span>`;
    
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
        const sourceData = filteredTransactions.length > 0 ? filteredTransactions : allTransactions;
        totalPages = Math.ceil(sourceData.length / pageSize);
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
    
    // Calculate total pages based on current data source
    const sourceData = filteredTransactions.length > 0 ? filteredTransactions : allTransactions;
    totalPages = Math.ceil(sourceData.length / pageSize);
    
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

function formatCategory(category) {
    if (!category) return 'Unknown';
    
    // Convert category codes to readable names
    const categoryMap = {
        'TRANSFER_INCOMING': 'Transfer In',
        'TRANSFER_OUTGOING': 'Transfer Out',
        'PAYMENT_PERSONAL': 'Payment Personal',
        'PAYMENT_BUSINESS': 'Payment Business',
        'DEPOSIT_AGENT': 'Deposit Agent',
        'DEPOSIT_CASH': 'Deposit Cash',
        'DEPOSIT_BANK_TRANSFER': 'Deposit Bank',
        'DEPOSIT_OTHER': 'Deposit Other',
        'AIRTIME': 'Airtime',
        'DATA_BUNDLE': 'Data Bundle',
        'DEPOSIT': 'Deposit',
        'WITHDRAWAL': 'Withdrawal',
        'TRANSFER': 'Transfer',
        'PAYMENT': 'Payment',
        'QUERY': 'Query',
        'OTHER': 'Other',
        'UNKNOWN': 'Unknown'
    };
    
    return categoryMap[category] || category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
    
    // If it starts with +250, keep as Rwanda format
    if (normalizedPhone.startsWith('+250')) {
        // Already in correct format
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

// View transaction details - optimized to only show relevant information
async function viewTransactionDetails(transactionId) {
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
    
    // Fetch comprehensive transaction details from the API
    try {
        console.log('Fetching detailed transaction data for ID:', transaction.id);
        const response = await fetch(`http://localhost:8001/api/transactions/${transaction.id}/details`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const detailedTransaction = await response.json();
        console.log('Detailed transaction data:', detailedTransaction);
        
        // Use the detailed transaction data
        transaction = detailedTransaction;
    } catch (error) {
        console.warn('Error fetching detailed transaction data:', error);
        // Fall back to the basic transaction data
    }
    
    // Determine transaction type and create appropriate view
    const transactionType = (transaction.transaction_type || transaction.type || 'unknown').toUpperCase();
    const category = transaction.category || 'unknown';
    
    // Use categorized fields if available
    const financial = transaction.categorized_fields?.financial || {};
    const identifiers = transaction.categorized_fields?.identifiers || {};
    const parties = transaction.categorized_fields?.parties || {};
    const metadata = transaction.categorized_fields?.metadata || {};
    const rawData = transaction.categorized_fields?.raw_data || {};
    
    // Create modal with consistent NeoBrutalism styling
    const modal = document.createElement('div');
    modal.className = 'transaction-modal';
    
    // Build content dynamically based on available data
    let content = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${getTransactionIcon(transactionType)} ${getTransactionTitle(transactionType)}</h3>
                <button class="close-btn" onclick="this.closest('.transaction-modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="detail-grid">
                    <!-- Transaction Type & Category -->
                    <div class="detail-item full-width highlight">
                        <label>Transaction Type:</label>
                        <span class="category-badge category-${category.toLowerCase().replace('_', '-')}">${formatCategory(category)}</span>
                    </div>
                    
                    <!-- Amount (always shown) -->
                    <div class="detail-item">
                        <label>Amount:</label>
                        <span class="formatted-number large-amount ${transactionType === 'RECEIVE' ? 'positive' : ''}">${formatCurrency(financial.amount || transaction.amount)}</span>
                    </div>`;
    
    // Only show fee if it exists and is greater than 0
    const fee = financial.fee || transaction.fee;
    if (fee && fee > 0) {
        content += `
                    <div class="detail-item">
                        <label>Fee:</label>
                        <span class="formatted-number">${formatCurrency(fee)}</span>
                    </div>`;
    }
    
    // Only show new balance if available
    const newBalance = financial.new_balance || transaction.new_balance;
    if (newBalance) {
        content += `
                    <div class="detail-item">
                        <label>New Balance:</label>
                        <span class="formatted-number">${formatCurrency(newBalance)}</span>
                    </div>`;
    }
    
    // Show relevant party information based on transaction type
    if (transactionType === 'DEPOSIT') {
        // For deposits, show agent info if available
        const agentMomoNumber = parties.agent_momo_number || transaction.agent_momo_number;
        if (agentMomoNumber) {
            content += `
                    <div class="detail-item">
                        <label>Agent Momo Number:</label>
                        <span>${formatPhone(agentMomoNumber)}</span>
                    </div>`;
        }
    } else if (transactionType === 'TRANSFER' || transactionType === 'RECEIVE') {
        // For transfers, show sender/recipient info
        const senderName = parties.sender_name || transaction.sender_name;
        const senderPhone = parties.sender_phone || transaction.sender_phone;
        const recipientName = parties.recipient_name || transaction.recipient_name;
        const recipientPhone = parties.recipient_phone || transaction.recipient_phone;
        const momoCode = parties.momo_code || transaction.momo_code;
        
        if (senderName) {
            content += `
                    <div class="detail-item">
                        <label>Sender Name:</label>
                        <span class="sender-name">${senderName}</span>
                    </div>`;
        }
        if (senderPhone) {
            content += `
                    <div class="detail-item">
                        <label>Sender Phone:</label>
                        <span>${formatPhone(senderPhone)}</span>
                    </div>`;
        }
        if (recipientName) {
            content += `
                    <div class="detail-item">
                        <label>Recipient Name:</label>
                        <span>${recipientName}</span>
                    </div>`;
        }
        if (recipientPhone) {
            content += `
                    <div class="detail-item">
                        <label>Recipient Phone:</label>
                        <span>${formatPhone(recipientPhone)}</span>
                    </div>`;
        }
        if (momoCode) {
            content += `
                    <div class="detail-item">
                        <label>Momo Code:</label>
                        <span>${momoCode}</span>
                    </div>`;
        }
    } else if (transactionType === 'PAYMENT') {
        // For payments, show business info if available
        const businessName = parties.business_name || transaction.business_name;
        const recipientName = parties.recipient_name || transaction.recipient_name;
        const momoCode = parties.momo_code || transaction.momo_code;
        
        if (businessName) {
            content += `
                    <div class="detail-item full-width">
                        <label>Business Name:</label>
                        <span class="business-name">${businessName}</span>
                    </div>`;
        }
        if (recipientName) {
            content += `
                    <div class="detail-item">
                        <label>Recipient Name:</label>
                        <span>${recipientName}</span>
                    </div>`;
        }
        if (momoCode) {
            content += `
                    <div class="detail-item">
                        <label>Momo Code:</label>
                        <span>${momoCode}</span>
                    </div>`;
        }
    }
    
    // Show transaction IDs based on transaction type and available data
    const ids = [];
    const seenValues = new Set();
    
    // Use categorized identifiers if available
    const txId = identifiers.transaction_id || transaction.transaction_id;
    const externalTransactionId = identifiers.external_transaction_id || transaction.external_transaction_id;
    const financialTransactionId = identifiers.financial_transaction_id || transaction.financial_transaction_id;
    const reference = identifiers.reference || transaction.reference;
    
    // For payment transactions, show the appropriate ID based on what's available
    if (transactionType === 'PAYMENT') {
        // For payments, prioritize the actual transaction ID from the message
        if (txId) {
            ids.push({ label: 'Transaction ID', value: txId });
            seenValues.add(txId);
        }
        if (financialTransactionId && !seenValues.has(financialTransactionId)) {
            ids.push({ label: 'Financial ID', value: financialTransactionId });
            seenValues.add(financialTransactionId);
        }
        if (externalTransactionId && !seenValues.has(externalTransactionId)) {
            ids.push({ label: 'External ID', value: externalTransactionId });
            seenValues.add(externalTransactionId);
        }
    } else {
        // For other transaction types, show all available IDs
        if (transaction.id) ids.push({ label: 'Database ID', value: transaction.id });
        if (txId) ids.push({ label: 'Transaction ID', value: txId });
        if (externalTransactionId) ids.push({ label: 'External ID', value: externalTransactionId });
        if (financialTransactionId) ids.push({ label: 'Financial ID', value: financialTransactionId });
        
        // Remove duplicates
        const uniqueIds = [];
        for (const id of ids) {
            if (!seenValues.has(id.value)) {
                uniqueIds.push(id);
                seenValues.add(id.value);
            }
        }
        ids.length = 0;
        ids.push(...uniqueIds);
    }
    
    // Display IDs
    for (const id of ids) {
        content += `
                    <div class="detail-item">
                        <label>${id.label}:</label>
                        <span>${id.value}</span>
                    </div>`;
    }
    
    // Always show date
    const date = metadata.date || transaction.date;
    content += `
                    <div class="detail-item">
                        <label>Date:</label>
                        <span>${formatDate(date)}</span>
                    </div>`;
    
    // Only show status if available
    const status = metadata.status || transaction.status;
    if (status) {
        content += `
                    <div class="detail-item">
                        <label>Status:</label>
                        <span class="status-badge status-${status.toLowerCase()}">${status}</span>
                    </div>`;
    }
    
    // Only show confidence score if available
    const confidenceScore = metadata.confidence_score || transaction.confidence_score;
    if (confidenceScore) {
        content += `
                    <div class="detail-item">
                        <label>Confidence Score:</label>
                        <span>${(confidenceScore * 100).toFixed(1)}%</span>
                    </div>`;
    }
    
    // Only show reference if available and not duplicate of an ID
    // For payment transactions, reference is usually the same as transaction_id, so skip it
    if (reference && !seenValues.has(reference) && transactionType !== 'PAYMENT') {
        content += `
                    <div class="detail-item">
                        <label>Reference:</label>
                        <span>${reference}</span>
                    </div>`;
    }
    
    // Always show original message if available (check multiple possible field names)
    // Handle empty strings, null, undefined, and "null" string values properly
    const getValidMessage = (field) => {
        if (!field || field === 'null' || field === null || field === undefined) return null;
        const trimmed = field.trim();
        return trimmed.length > 0 ? trimmed : null;
    };
    
    const originalMessage = getValidMessage(rawData.original_message) || 
                           getValidMessage(transaction.original_message) || 
                           getValidMessage(transaction.original_data) || 
                           getValidMessage(transaction.raw_data) || 
                           getValidMessage(transaction.raw_sms_data);
    
    // Debug: Log available fields for troubleshooting
    console.log('Transaction fields for original message:', {
        original_message: transaction.original_message,
        original_data: transaction.original_data,
        raw_data: transaction.raw_data,
        raw_sms_data: transaction.raw_sms_data,
        original_message_length: transaction.original_message ? transaction.original_message.length : 0,
        original_data_length: transaction.original_data ? transaction.original_data.length : 0,
        raw_data_length: transaction.raw_data ? transaction.raw_data.length : 0,
        found: !!originalMessage
    });
    
    if (originalMessage) {
        content += `
                    <div class="detail-item full-width">
                        <label>Original Message:</label>
                        <textarea readonly class="original-message">${originalMessage}</textarea>
                    </div>`;
    } else {
        // Show debug info if no original message found
        content += `
                    <div class="detail-item full-width">
                        <label>Debug Info:</label>
                        <span style="font-size: 0.8rem; color: #666;">
                            No original message found. Field values:<br/>
                            original_message: "${transaction.original_message}" (type: ${typeof transaction.original_message})<br/>
                            original_data: "${transaction.original_data}" (type: ${typeof transaction.original_data})<br/>
                            raw_data: "${transaction.raw_data}" (type: ${typeof transaction.raw_data})<br/>
                            raw_sms_data: "${transaction.raw_sms_data}" (type: ${typeof transaction.raw_sms_data})
                        </span>
                    </div>`;
    }
    
    content += `
                </div>
            </div>
        </div>
    `;
    
    modal.innerHTML = content;
    document.body.appendChild(modal);
}

// Helper functions for transaction display
function getTransactionIcon(type) {
    const icons = {
        'DEPOSIT': '💰',
        'TRANSFER': '🔄',
        'PAYMENT': '💳',
        'RECEIVE': '📥',
        'AIRTIME': '📱',
        'DATA_BUNDLE': '📶',
        'PURCHASE': '🛒'
    };
    return icons[type] || '📋';
}

function getTransactionTitle(type) {
    const titles = {
        'DEPOSIT': 'Deposit Transaction',
        'TRANSFER': 'Transfer Transaction',
        'PAYMENT': 'Payment Transaction',
        'RECEIVE': 'Money Received',
        'AIRTIME': 'Airtime Purchase',
        'DATA_BUNDLE': 'Data Bundle Purchase',
        'PURCHASE': 'Purchase Transaction'
    };
    return titles[type] || 'Transaction Details';
}

// ========================================
// FILTER FUNCTIONALITY
// ========================================

function initializeFilters() {
    // Initialize filtered transactions with all transactions
    filteredTransactions = [...allTransactions];
    
    // Add event listeners for minimal filters
    document.getElementById('clearFilters').addEventListener('click', clearFilters);
    document.getElementById('searchFilter').addEventListener('input', debounce(applyFilters, 300));
    document.getElementById('typeFilter').addEventListener('change', applyFilters);
}

function applyFilters() {
    const typeFilter = document.getElementById('typeFilter').value;
    const searchFilter = document.getElementById('searchFilter').value.toLowerCase();
    
    // Filter transactions
    filteredTransactions = allTransactions.filter(transaction => {
        // Type filter
        if (typeFilter && transaction.transaction_type !== typeFilter && transaction.type !== typeFilter) {
            return false;
        }
        
        // Search filter
        if (searchFilter) {
            const searchableText = [
                transaction.transaction_type || transaction.type || '',
                transaction.category || '',
                transaction.sender_name || '',
                transaction.recipient_name || '',
                transaction.sender_phone || '',
                transaction.recipient_phone || '',
                transaction.reference || '',
                transaction.status || ''
            ].join(' ').toLowerCase();
            
            if (!searchableText.includes(searchFilter)) {
                return false;
            }
        }
        
        return true;
    });
    
    // Reset to first page
    currentPage = 1;
    
    // Update table
    updateTransactionsTable(filteredTransactions);
}

function clearFilters() {
    // Clear filter inputs
    document.getElementById('typeFilter').value = '';
    document.getElementById('searchFilter').value = '';
    
    // Reset filters
    filteredTransactions = [...allTransactions];
    currentPage = 1;
    
    // Update table
    updateTransactionsTable(filteredTransactions);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

