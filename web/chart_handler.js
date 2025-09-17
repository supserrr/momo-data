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
const TRANSACTIONS_PER_PAGE = 10;

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Add load more button event listener
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreTransactions);
    }
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Load dashboard data from XML SMS backup
async function loadDashboardData() {
    try {
        showRefreshIndicator();
        const response = await fetch('data/raw/modified_sms_v2.xml');
        if (!response.ok) throw new Error('Failed to load SMS data');

        const xmlText = await response.text();
        const data = parseSMSData(xmlText);
        console.log('Parsed SMS data:', data);
        console.log('Category distribution:', data.charts?.category_distribution);
        
        // Store all transactions for pagination
        allTransactions = data.transactions || [];
        currentPage = 1;
        
        updateKeyMetrics(data);
        updateCharts(data);
        updateTransactionsTable(data);
        hideRefreshIndicator();
    } catch (error) {
        console.error('Error loading SMS data:', error);
        // Load sample data as fallback
        loadSampleData();
        hideRefreshIndicator();
    }
}

// Parse SMS XML data and extract transaction information
function parseSMSData(xmlText) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
    const smsElements = xmlDoc.querySelectorAll('sms');
    
    const transactions = [];
    const transactionTypes = {};
    const dailyStats = {};
    const hourlyStats = {};
    const userStats = {};
    let totalAmount = 0;
    let successfulTransactions = 0;
    
    console.log(`Processing ${smsElements.length} SMS messages...`);
    
    smsElements.forEach(sms => {
        const body = sms.getAttribute('body') || '';
        const date = parseInt(sms.getAttribute('date'));
        const readableDate = sms.getAttribute('readable_date');
        
        // Parse different types of MTN Mobile Money messages
        const transaction = parseTransactionFromSMS(body, date, readableDate);
        
        if (transaction) {
            transactions.push(transaction);
            
            // Update statistics
            totalAmount += transaction.amount || 0;
            if (transaction.status === 'SUCCESS') {
                successfulTransactions++;
            }
            
            // Count transaction types
            const type = transaction.type || 'UNKNOWN';
            transactionTypes[type] = (transactionTypes[type] || 0) + 1;
            
            // Daily stats
            const day = new Date(date).toISOString().split('T')[0];
            dailyStats[day] = (dailyStats[day] || 0) + 1;
            
            // Hourly stats
            const hour = new Date(date).getHours();
            const hourKey = `${Math.floor(hour / 4) * 4}:00`;
            hourlyStats[hourKey] = (hourlyStats[hourKey] || 0) + 1;
            
            // User stats (from recipient names)
            if (transaction.recipient) {
                userStats[transaction.recipient] = (userStats[transaction.recipient] || 0) + 1;
            }
        }
    });
    
    // Sort transactions by date (newest first)
    transactions.sort((a, b) => b.date - a.date);
    
    // Calculate success rate
    const successRate = transactions.length > 0 ? (successfulTransactions / transactions.length) * 100 : 0;
    
    console.log(`Parsed ${transactions.length} transactions`);
    console.log('Transaction types found:', transactionTypes);
    
    // Remove top users analysis - no longer needed
    
    // Get daily stats for charts
    const dailyStatsArray = Object.entries(dailyStats)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, count]) => ({ date, count }));
    
    // Get detailed hourly stats for charts (24-hour analysis)
    const detailedHourlyStats = {};
    transactions.forEach(t => {
        const hour = new Date(t.date).getHours();
        if (!detailedHourlyStats[hour]) {
            detailedHourlyStats[hour] = { count: 0, volume: 0 };
        }
        detailedHourlyStats[hour].count++;
        detailedHourlyStats[hour].volume += t.amount || 0;
    });
    
    // Create hourly pattern with 4-hour intervals for better visualization
    const hourlyStatsArray = [
        { hour: '00:00-03:59', count: (detailedHourlyStats[0]?.count || 0) + (detailedHourlyStats[1]?.count || 0) + (detailedHourlyStats[2]?.count || 0) + (detailedHourlyStats[3]?.count || 0), volume: (detailedHourlyStats[0]?.volume || 0) + (detailedHourlyStats[1]?.volume || 0) + (detailedHourlyStats[2]?.volume || 0) + (detailedHourlyStats[3]?.volume || 0) },
        { hour: '04:00-07:59', count: (detailedHourlyStats[4]?.count || 0) + (detailedHourlyStats[5]?.count || 0) + (detailedHourlyStats[6]?.count || 0) + (detailedHourlyStats[7]?.count || 0), volume: (detailedHourlyStats[4]?.volume || 0) + (detailedHourlyStats[5]?.volume || 0) + (detailedHourlyStats[6]?.volume || 0) + (detailedHourlyStats[7]?.volume || 0) },
        { hour: '08:00-11:59', count: (detailedHourlyStats[8]?.count || 0) + (detailedHourlyStats[9]?.count || 0) + (detailedHourlyStats[10]?.count || 0) + (detailedHourlyStats[11]?.count || 0), volume: (detailedHourlyStats[8]?.volume || 0) + (detailedHourlyStats[9]?.volume || 0) + (detailedHourlyStats[10]?.volume || 0) + (detailedHourlyStats[11]?.volume || 0) },
        { hour: '12:00-15:59', count: (detailedHourlyStats[12]?.count || 0) + (detailedHourlyStats[13]?.count || 0) + (detailedHourlyStats[14]?.count || 0) + (detailedHourlyStats[15]?.count || 0), volume: (detailedHourlyStats[12]?.volume || 0) + (detailedHourlyStats[13]?.volume || 0) + (detailedHourlyStats[14]?.volume || 0) + (detailedHourlyStats[15]?.volume || 0) },
        { hour: '16:00-19:59', count: (detailedHourlyStats[16]?.count || 0) + (detailedHourlyStats[17]?.count || 0) + (detailedHourlyStats[18]?.count || 0) + (detailedHourlyStats[19]?.count || 0), volume: (detailedHourlyStats[16]?.volume || 0) + (detailedHourlyStats[17]?.volume || 0) + (detailedHourlyStats[18]?.volume || 0) + (detailedHourlyStats[19]?.volume || 0) },
        { hour: '20:00-23:59', count: (detailedHourlyStats[20]?.count || 0) + (detailedHourlyStats[21]?.count || 0) + (detailedHourlyStats[22]?.count || 0) + (detailedHourlyStats[23]?.count || 0), volume: (detailedHourlyStats[20]?.volume || 0) + (detailedHourlyStats[21]?.volume || 0) + (detailedHourlyStats[22]?.volume || 0) + (detailedHourlyStats[23]?.volume || 0) }
    ];
    
    return {
        summary: {
            total_transactions: transactions.length,
            total_amount: totalAmount,
            success_rate: successRate,
            successful_transactions: successfulTransactions,
            last_updated: new Date().toISOString()
        },
        transactions: transactions.slice(0, 50), // Show last 50 transactions
        statistics: {
            transactionTypes: transactionTypes
        },
        charts: {
            daily_stats: dailyStatsArray,
            category_distribution: Object.entries(transactionTypes).map(([type, count]) => ({
                category: type,
                count: count
            })),
            hourly_pattern: hourlyStatsArray
        }
    };
}

// Parse individual transaction from SMS message
function parseTransactionFromSMS(body, timestamp, readableDate) {
    if (!body || !body.includes('RWF')) return null;
    
    let transaction = {
        date: new Date(timestamp).toISOString(),
        amount: 0,
        type: 'UNKNOWN',
        status: 'SUCCESS',
        recipient: null,
        sender: null,
        fee: 0,
        balance: 0
    };
    
    console.log('Parsing SMS:', body.substring(0, 100) + '...');
    
    // Extract amount (look for patterns like "2000 RWF", "1,000 RWF", etc.)
    const amountMatch = body.match(/(\d{1,3}(?:,\d{3})*)\s*RWF/);
    if (amountMatch) {
        transaction.amount = parseInt(amountMatch[1].replace(/,/g, ''));
    }
    
    // Determine transaction type based on message content
    if (body.includes('received') && body.includes('from')) {
        transaction.type = 'DEPOSIT';
        transaction.status = 'SUCCESS';
        // Extract sender name
        const senderMatch = body.match(/from\s+([^(]+)\s*\(/);
        if (senderMatch) {
            transaction.sender = senderMatch[1].trim();
        }
    } else if (body.includes('bank deposit')) {
        transaction.type = 'DEPOSIT';
        transaction.status = 'SUCCESS';
    } else if (body.includes('transferred to')) {
        transaction.type = 'TRANSFER';
        transaction.status = 'SUCCESS';
        // Extract recipient name
        const recipientMatch = body.match(/transferred to\s+([^(]+)\s*\(/);
        if (recipientMatch) {
            transaction.recipient = recipientMatch[1].trim();
        }
    } else if (body.includes('payment of') && body.includes('to')) {
        // Check if it's airtime first
        if (body.includes('Airtime')) {
            transaction.type = 'AIRTIME';
        } else {
            transaction.type = 'PAYMENT';
        }
        transaction.status = 'SUCCESS';
        // Extract recipient name
        const recipientMatch = body.match(/to\s+([^(]+)\s*\d+/);
        if (recipientMatch) {
            transaction.recipient = recipientMatch[1].trim();
        }
    } else if (body.includes('withdrawal') || body.includes('withdraw')) {
        transaction.type = 'WITHDRAWAL';
        transaction.status = 'SUCCESS';
    }
    
    // Extract fee
    const feeMatch = body.match(/Fee was[:\s]*(\d+)\s*RWF/);
    if (feeMatch) {
        transaction.fee = parseInt(feeMatch[1]);
    }
    
    // Extract balance
    const balanceMatch = body.match(/balance[:\s]*(\d{1,3}(?:,\d{3})*)\s*RWF/);
    if (balanceMatch) {
        transaction.balance = parseInt(balanceMatch[1].replace(/,/g, ''));
    }
    
    // Check for failed transactions
    if (body.includes('failed') || body.includes('error') || body.includes('unsuccessful')) {
        transaction.status = 'FAILED';
    }
    
    console.log('Parsed transaction:', transaction.type, transaction.amount);
    
    return transaction.amount > 0 ? transaction : null;
}

// Load sample data for demonstration
function loadSampleData() {
    const sampleData = {
        summary: {
            total_transactions: 1247,
            total_amount: 15678900,
            success_rate: 94.2,
            active_users: 89
        },
        recent_transactions: [
            {
                date: '2024-01-15T10:30:00Z',
                category: 'Transfer',
                amount: 25000,
                sender_phone: '+250788123456',
                receiver_phone: '+250789654321',
                status: 'Success'
            },
            {
                date: '2024-01-15T09:45:00Z',
                category: 'Payment',
                amount: 15000,
                sender_phone: '+250788234567',
                receiver_phone: '+250789765432',
                status: 'Success'
            },
            {
                date: '2024-01-15T09:15:00Z',
                category: 'Withdrawal',
                amount: 50000,
                sender_phone: '+250788345678',
                receiver_phone: '+250789876543',
                status: 'Pending'
            },
            {
                date: '2024-01-15T08:30:00Z',
                category: 'Transfer',
                amount: 75000,
                sender_phone: '+250788456789',
                receiver_phone: '+250789987654',
                status: 'Success'
            },
            {
                date: '2024-01-15T08:00:00Z',
                category: 'Payment',
                amount: 12000,
                sender_phone: '+250788567890',
                receiver_phone: '+250789098765',
                status: 'Failed'
            },
            {
                date: '2024-01-15T07:45:00Z',
                category: 'Deposit',
                amount: 100000,
                sender_phone: '+250788678901',
                receiver_phone: '+250789109876',
                status: 'Success'
            },
            {
                date: '2024-01-15T07:20:00Z',
                category: 'Transfer',
                amount: 30000,
                sender_phone: '+250788789012',
                receiver_phone: '+250789210987',
                status: 'Success'
            },
            {
                date: '2024-01-15T06:55:00Z',
                category: 'Payment',
                amount: 8500,
                sender_phone: '+250788890123',
                receiver_phone: '+250789321098',
                status: 'Success'
            },
            {
                date: '2024-01-15T06:30:00Z',
                category: 'Withdrawal',
                amount: 45000,
                sender_phone: '+250788901234',
                receiver_phone: '+250789432109',
                status: 'Pending'
            },
            {
                date: '2024-01-15T06:00:00Z',
                category: 'Transfer',
                amount: 18000,
                sender_phone: '+250788012345',
                receiver_phone: '+250789543210',
                status: 'Success'
            }
        ],
                    charts: {
                        volume_by_date: {
                            labels: ['2024-01-09', '2024-01-10', '2024-01-11', '2024-01-12', '2024-01-13', '2024-01-14', '2024-01-15'],
                            data: [45, 52, 38, 67, 89, 76, 94]
                        },
                        category_distribution: [
                            { category: 'Transfer', count: 45 },
                            { category: 'Payment', count: 30 },
                            { category: 'Withdrawal', count: 15 },
                            { category: 'Deposit', count: 10 }
                        ],
                        hourly_pattern: {
                            labels: ['00:00-03:59', '04:00-07:59', '08:00-11:59', '12:00-15:59', '16:00-19:59', '20:00-23:59'],
                            data: [5, 8, 25, 35, 28, 15]
                        }
                    }
    };
    
    // Store sample transactions for pagination
    allTransactions = sampleData.recent_transactions || [];
    currentPage = 1;
    
    updateKeyMetrics(sampleData);
    updateCharts(sampleData);
    updateTransactionsTable(sampleData);
}

// Update key metrics cards
function updateKeyMetrics(data) {
    const metrics = {
        totalTransactions: data.summary?.total_transactions || 0,
        totalAmount: data.summary?.total_amount || 0,
        successRate: data.summary?.success_rate || 0,
        activeUsers: data.summary?.unique_users || data.summary?.successful_transactions || 0
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
    // Use chart data from parsed SMS data
    updateVolumeChart(data.charts?.daily_stats || []);
    updateCategoryChart(data.charts?.category_distribution || []);
    updateHourlyChart(data.charts?.hourly_pattern || []);
}

// Create chart data from real data structure
function createChartDataFromRealData(data) {
    const chartData = {
        daily_stats: [],
        category_distribution: [],
        hourly_pattern: []
    };
    
    // Create category distribution from transaction types
    if (data.statistics?.transactionTypes) {
        chartData.category_distribution = Object.entries(data.statistics.transactionTypes).map(([type, count]) => ({
            category: type,
            count: count
        }));
    }
    
    // Create sample daily stats (since real data doesn't have this)
    if (data.transactions && data.transactions.length > 0) {
        const dates = [...new Set(data.transactions.map(t => t.date.split('T')[0]))].sort();
        chartData.daily_stats = dates.map(date => ({
            date: date,
            count: data.transactions.filter(t => t.date.startsWith(date)).length
        }));
    }
    
    // Create sample hourly pattern (since real data doesn't have this)
    chartData.hourly_pattern = [
        { hour: '00:00', count: 0 },
        { hour: '04:00', count: 1 },
        { hour: '08:00', count: 2 },
        { hour: '12:00', count: 3 },
        { hour: '16:00', count: 2 },
        { hour: '20:00', count: 1 }
    ];
    
    // Top users analysis removed - no longer needed
    
    return chartData;
}

// Volume by Date Chart with Brutalist Styling
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
            borderWidth: BRUTALIST_CONFIG.borderWidth,
            barThickness: 40,
            borderSkipped: false,
            borderRadius: 0,
            borderJoinStyle: 'miter'
        }]
    };
    
    if (charts.volume) charts.volume.destroy();
    
    charts.volume = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: getBrutalistBarChartOptions('Transaction Volume by Date', false)
    });
}

// Category Distribution Chart with Brutalist Styling
function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    console.log('Category chart data:', categories);
    
    const chartData = {
        labels: categories.map(c => c.category.toUpperCase()),
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
                        pointStyle: 'rect'
                    }
                },
                tooltip: getBrutalistTooltipConfig()
            }
        }
    });
}

// Top Users Chart removed - no longer needed

// Hourly Pattern Chart with Brutalist Styling
function updateHourlyChart(hourlyData) {
    const ctx = document.getElementById('hourlyChart');
    if (!ctx) return;
    
    // Use the 4-hour interval data from our enhanced parsing
    const labels = hourlyData.map(h => h.hour);
    const countData = hourlyData.map(h => h.count || 0);
    const volumeData = hourlyData.map(h => h.volume || 0);
    
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Transaction Count',
            data: countData,
            backgroundColor: COLORS.brutalPurple,
            borderColor: COLORS.brutalBlack,
            borderWidth: BRUTALIST_CONFIG.borderWidth,
            fill: true,
            tension: 0.1,
            pointRadius: 8,
            pointBackgroundColor: COLORS.brutalWhite,
            pointBorderColor: COLORS.brutalBlack,
            pointBorderWidth: BRUTALIST_CONFIG.borderWidth,
            pointHoverRadius: 12,
            pointStyle: 'rect',
            borderJoinStyle: 'miter',
            borderCapStyle: 'square',
            yAxisID: 'y'
        }, {
            label: 'Transaction Volume (RWF)',
            data: volumeData,
            backgroundColor: COLORS.brutalBlue,
            borderColor: COLORS.brutalBlack,
            borderWidth: BRUTALIST_CONFIG.borderWidth,
            fill: false,
            tension: 0.1,
            pointRadius: 6,
            pointBackgroundColor: COLORS.brutalWhite,
            pointBorderColor: COLORS.brutalBlack,
            pointBorderWidth: BRUTALIST_CONFIG.borderWidth,
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
                        maxRotation: 45,
                        minRotation: 45
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
                        color: COLORS.black
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
    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (!tbody) return;

    // Get transactions for current page
    const startIndex = (currentPage - 1) * TRANSACTIONS_PER_PAGE;
    const endIndex = startIndex + TRANSACTIONS_PER_PAGE;
    const transactionsToShow = allTransactions.slice(0, endIndex);
    const hasMore = endIndex < allTransactions.length;

    if (transactionsToShow.length === 0) {
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
        tableInfo.innerHTML = '<span>No transactions to display</span>';
        loadMoreBtn.style.display = 'none';
        return;
    }

    // Clear existing rows
    tbody.innerHTML = '';

    // Add transactions for current page
    const newTransactions = allTransactions.slice(startIndex, endIndex);
    newTransactions.forEach((t, index) => {
        const row = document.createElement('tr');
        row.className = 'animate-slide-in';
        row.style.animationDelay = `${index * 0.1}s`;
        row.innerHTML = `
            <td>${formatDate(t.date)}</td>
            <td>${t.type || t.category || 'Unknown'}</td>
            <td class="formatted-number">${formatCurrency(t.amount)}</td>
            <td>${t.sender || t.sender_phone || t.phone || 'N/A'}</td>
            <td>${t.recipient || t.receiver_phone || 'N/A'}</td>
            <td><span class="status-badge status-${t.status.toLowerCase()}">${t.status}</span></td>
        `;
        tbody.appendChild(row);
    });

    // Update table info and load more button
    tableInfo.innerHTML = `<span>Showing ${transactionsToShow.length} of ${allTransactions.length} total transactions</span>`;
    
    if (hasMore) {
        loadMoreBtn.style.display = 'block';
        loadMoreBtn.disabled = false;
    } else {
        loadMoreBtn.style.display = 'none';
    }
}

// Load more transactions
function loadMoreTransactions() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    if (loadMoreBtn) {
        loadMoreBtn.disabled = true;
        loadMoreBtn.textContent = 'Loading...';
    }
    
    // Simulate loading delay for better UX
    setTimeout(() => {
        currentPage++;
        updateTransactionsTable({});
        
        if (loadMoreBtn) {
            loadMoreBtn.disabled = false;
            loadMoreBtn.textContent = 'Load More Transactions';
        }
    }, 500);
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
