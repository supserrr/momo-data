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

// Load dashboard data from API
async function loadDashboardData() {
    try {
        // Load dashboard data for metrics and charts
        const response = await fetch('http://localhost:8000/api/dashboard-data');
        if (!response.ok) throw new Error('Failed to load dashboard data');

        const data = await response.json();
        console.log('Dashboard data from API:', data);
        
        // Load monthly transaction data
        const monthlyResponse = await fetch('http://localhost:8000/api/monthly-transactions');
        if (!monthlyResponse.ok) throw new Error('Failed to load monthly data');
        
        const monthlyData = await monthlyResponse.json();
        console.log('Monthly data from API:', monthlyData);
        
        // Load ALL transactions for the table using pagination (API limit is 100)
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
        
        console.log('All transactions from API:', allTransactionsData.length);
        
        // Transform API data to match expected format
        const transformedData = transformAPIData(data, monthlyData, allTransactionsData);
        
        // Store all transactions for pagination (use the full transaction list)
        allTransactions = allTransactionsData || [];
        currentPage = 1;
        totalPages = Math.ceil(allTransactions.length / pageSize);
        
        updateKeyMetrics(transformedData);
        updateCharts(transformedData);
        updateTransactionsTable(transformedData);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Load sample data as fallback
        loadSampleData();
    }
}

// Manual refresh function for the refresh button
async function refreshDashboardData() {
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = 'Refreshing...';
        refreshBtn.style.opacity = '0.7';
    }
    
    try {
        await loadDashboardData();
        
        // Show success feedback
        if (refreshBtn) {
            refreshBtn.innerHTML = 'Refreshed!';
            setTimeout(() => {
                refreshBtn.innerHTML = 'Refresh Data';
                refreshBtn.disabled = false;
                refreshBtn.style.opacity = '1';
            }, 2000);
        }
    } catch (error) {
        console.error('Error refreshing data:', error);
        
        // Show error feedback
        if (refreshBtn) {
            refreshBtn.innerHTML = 'Error';
            setTimeout(() => {
                refreshBtn.innerHTML = 'Refresh Data';
                refreshBtn.disabled = false;
                refreshBtn.style.opacity = '1';
            }, 2000);
        }
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

// Transform API data to match expected frontend format
function transformAPIData(apiData, monthlyData = null, allTransactionsData = null) {
    const { summary, categories, amount_distribution, recent_transactions } = apiData;
    
    // Use all transactions data if available, otherwise fall back to recent_transactions
    const transactionsToUse = allTransactionsData || recent_transactions;
    
    // Transform categories to match expected format with additional data
    const categoryDistribution = categories.map(cat => ({
        category: cat.category,
        count: cat.count,
        total_amount: cat.total_amount || 0,
        avg_amount: cat.avg_amount || 0,
        min_amount: cat.min_amount || 0,
        max_amount: cat.max_amount || 0
    }));
    
    // Use monthly data from API if available, otherwise fallback to recent transactions
    let monthlyStatsArray = [];
    if (monthlyData && monthlyData.monthly_stats) {
        monthlyStatsArray = monthlyData.monthly_stats.map(stats => ({
            month: stats.month,
            count: stats.count,
            volume: stats.volume
        }));
    } else {
        // Fallback: create monthly stats from transactions
        const monthlyStats = {};
        transactionsToUse.forEach(tx => {
            const date = new Date(tx.date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            if (!monthlyStats[monthKey]) {
                monthlyStats[monthKey] = { count: 0, volume: 0 };
            }
            monthlyStats[monthKey].count++;
            monthlyStats[monthKey].volume += tx.amount;
        });
        
        monthlyStatsArray = Object.entries(monthlyStats)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([month, data]) => ({ 
                month, 
                count: data.count,
                volume: data.volume
            }));
    }
    
    // Use hourly data from API if available, otherwise fallback to recent transactions
    let hourlyPattern = Array.from({length: 24}, (_, i) => ({
        hour: i,
        count: 0,
        volume: 0
    }));
    
    if (monthlyData && monthlyData.hourly_pattern) {
        // Reset the pattern and populate with API data
        hourlyPattern.forEach(slot => { slot.count = 0; slot.volume = 0; });
        monthlyData.hourly_pattern.forEach(hour_data => {
            const hour = parseInt(hour_data.hour);
            if (hour >= 0 && hour < 24) {
                hourlyPattern[hour] = {
                    hour: hour,
                    count: hour_data.count,
                    volume: hour_data.volume
                };
            }
        });
    } else {
        // Fallback: distribute transactions across hours
        transactionsToUse.forEach(tx => {
            const hour = new Date(tx.date).getHours();
            hourlyPattern[hour].count++;
            hourlyPattern[hour].volume += tx.amount;
        });
    }
    
    // Create amount distribution data
    const amountRanges = [
        { range: '0-1,000', min: 0, max: 1000, count: 0 },
        { range: '1,000-5,000', min: 1000, max: 5000, count: 0 },
        { range: '5,000-10,000', min: 5000, max: 10000, count: 0 },
        { range: '10,000-25,000', min: 10000, max: 25000, count: 0 },
        { range: '25,000-50,000', min: 25000, max: 50000, count: 0 },
        { range: '50,000+', min: 50000, max: Infinity, count: 0 }
    ];
    
    transactionsToUse.forEach(tx => {
        const amount = tx.amount;
        for (let range of amountRanges) {
            if (amount >= range.min && amount < range.max) {
                range.count++;
                break;
            }
        }
    });
    
    return {
        summary: {
            total_transactions: summary.total_transactions,
            total_amount: summary.total_amount,
            average_transaction_amount: summary.average_transaction_amount,
            success_rate: summary.success_rate,
            successful_transactions: summary.successful_transactions,
            failed_transactions: summary.failed_transactions,
            pending_transactions: summary.pending_transactions,
            last_updated: summary.last_updated
        },
        transactions: transactionsToUse.map(tx => ({
            id: tx.id,
            date: tx.date,
            amount: tx.amount,
            type: tx.type,
            status: tx.status,
            phone: tx.phone,
            category: tx.category,
            reference: tx.reference,
            original_data: tx.original_data,
            raw_data: tx.raw_data,
            xml_tag: tx.xml_tag,
            xml_attributes: tx.xml_attributes,
            cleaned_at: tx.cleaned_at,
            categorized_at: tx.categorized_at,
            loaded_at: tx.loaded_at
        })),
        statistics: {
            transactionTypes: categoryDistribution.reduce((acc, cat) => {
                acc[cat.category] = cat.count;
                return acc;
            }, {})
        },
        charts: {
            monthly_stats: monthlyStatsArray,
            category_distribution: categoryDistribution,
            hourly_pattern: hourlyPattern,
            amount_distribution: amountRanges
        }
    };
}

// Load sample data for demonstration
function loadSampleData() {
    const sampleTransactions = [
            {
                id: 1,
                date: '2024-01-15T10:30:00Z',
                type: 'Transfer',
                category: 'Transfer',
                amount: 25000,
                phone: '+250788123456',
                reference: 'TXN001',
                status: 'Success',
                raw_data: 'You transferred 25000 RWF to John Doe. New balance: 50000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705312200000' }
            },
            {
                id: 2,
                date: '2024-01-15T09:45:00Z',
                type: 'Payment',
                category: 'Payment',
                amount: 15000,
                phone: '+250788234567',
                reference: 'TXN002',
                status: 'Success',
                raw_data: 'Payment of 15000 RWF to Shop ABC. New balance: 35000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705309500000' }
            },
            {
                id: 3,
                date: '2024-01-15T09:15:00Z',
                type: 'Withdrawal',
                category: 'Withdrawal',
                amount: 50000,
                phone: '+250788345678',
                reference: 'TXN003',
                status: 'Pending',
                raw_data: 'Withdrawal of 50000 RWF requested. Processing...',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705307700000' }
            },
            {
                id: 4,
                date: '2024-01-15T08:30:00Z',
                type: 'Transfer',
                category: 'Transfer',
                amount: 75000,
                phone: '+250788456789',
                reference: 'TXN004',
                status: 'Success',
                raw_data: 'You transferred 75000 RWF to Jane Smith. New balance: 125000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705305000000' }
            },
            {
                id: 5,
                date: '2024-01-15T08:00:00Z',
                type: 'Payment',
                category: 'Payment',
                amount: 12000,
                phone: '+250788567890',
                reference: 'TXN005',
                status: 'Failed',
                raw_data: 'Payment failed. Insufficient balance.',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705304400000' }
            },
            {
                id: 6,
                date: '2024-01-15T07:45:00Z',
                type: 'Deposit',
                category: 'Deposit',
                amount: 100000,
                phone: '+250788678901',
                reference: 'TXN006',
                status: 'Success',
                raw_data: 'You received 100000 RWF from Bank Deposit. New balance: 200000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705303500000' }
            },
            {
                id: 7,
                date: '2024-01-15T07:20:00Z',
                type: 'Transfer',
                category: 'Transfer',
                amount: 30000,
                phone: '+250788789012',
                reference: 'TXN007',
                status: 'Success',
                raw_data: 'You transferred 30000 RWF to Mike Johnson. New balance: 100000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705302000000' }
            },
            {
                id: 8,
                date: '2024-01-15T06:55:00Z',
                type: 'Payment',
                category: 'Payment',
                amount: 8500,
                phone: '+250788890123',
                reference: 'TXN008',
                status: 'Success',
                raw_data: 'Payment of 8500 RWF to Restaurant XYZ. New balance: 130000 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705300500000' }
            },
            {
                id: 9,
                date: '2024-01-15T06:30:00Z',
                type: 'Withdrawal',
                category: 'Withdrawal',
                amount: 45000,
                phone: '+250788901234',
                reference: 'TXN009',
                status: 'Pending',
                raw_data: 'Withdrawal of 45000 RWF requested. Processing...',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705299000000' }
            },
            {
                id: 10,
                date: '2024-01-15T06:00:00Z',
                type: 'Transfer',
                category: 'Transfer',
                amount: 18000,
                phone: '+250788012345',
                reference: 'TXN010',
                status: 'Success',
                raw_data: 'You transferred 18000 RWF to Sarah Wilson. New balance: 138500 RWF',
                xml_tag: 'sms',
                xml_attributes: { address: 'M-Money', date: '1705297200000' }
            }
        ];
    
    const sampleData = {
        summary: {
            total_transactions: 1247,
            total_amount: 15678900,
            success_rate: 94.2,
            active_users: 89
        },
        categories: [
            { category: 'Transfer', count: 45, total_amount: 500000, avg_amount: 11111, min_amount: 1000, max_amount: 100000 },
            { category: 'Payment', count: 30, total_amount: 300000, avg_amount: 10000, min_amount: 500, max_amount: 50000 },
            { category: 'Withdrawal', count: 15, total_amount: 200000, avg_amount: 13333, min_amount: 2000, max_amount: 100000 },
            { category: 'Deposit', count: 10, total_amount: 100000, avg_amount: 10000, min_amount: 1000, max_amount: 50000 }
        ],
        amount_distribution: [
            { range: '0-1,000', count: 5 },
            { range: '1,000-5,000', count: 15 },
            { range: '5,000-10,000', count: 25 },
            { range: '10,000-25,000', count: 30 },
            { range: '25,000-50,000', count: 20 },
            { range: '50,000+', count: 5 }
        ],
        recent_transactions: sampleTransactions,
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
    allTransactions = sampleTransactions;
    currentPage = 1;
    totalPages = Math.ceil(allTransactions.length / pageSize);
    
    // Create sample monthly data
    const sampleMonthlyData = {
        monthly_stats: [
            { month: '2024-01', count: 150, volume: 2500000 },
            { month: '2024-02', count: 180, volume: 3000000 },
            { month: '2024-03', count: 200, volume: 3500000 },
            { month: '2024-04', count: 220, volume: 4000000 },
            { month: '2024-05', count: 250, volume: 4500000 },
            { month: '2024-06', count: 280, volume: 5000000 }
        ],
        hourly_pattern: [
            { hour: 0, count: 2, volume: 50000 },
            { hour: 1, count: 1, volume: 25000 },
            { hour: 2, count: 0, volume: 0 },
            { hour: 3, count: 1, volume: 30000 },
            { hour: 4, count: 2, volume: 40000 },
            { hour: 5, count: 3, volume: 60000 },
            { hour: 6, count: 5, volume: 100000 },
            { hour: 7, count: 8, volume: 150000 },
            { hour: 8, count: 12, volume: 200000 },
            { hour: 9, count: 15, volume: 250000 },
            { hour: 10, count: 18, volume: 300000 },
            { hour: 11, count: 20, volume: 350000 },
            { hour: 12, count: 22, volume: 400000 },
            { hour: 13, count: 25, volume: 450000 },
            { hour: 14, count: 28, volume: 500000 },
            { hour: 15, count: 30, volume: 550000 },
            { hour: 16, count: 32, volume: 600000 },
            { hour: 17, count: 35, volume: 650000 },
            { hour: 18, count: 38, volume: 700000 },
            { hour: 19, count: 40, volume: 750000 },
            { hour: 20, count: 35, volume: 650000 },
            { hour: 21, count: 30, volume: 550000 },
            { hour: 22, count: 25, volume: 450000 },
            { hour: 23, count: 20, volume: 350000 }
        ]
    };
    
    // Transform sample data to match expected format
    const transformedData = transformAPIData(sampleData, sampleMonthlyData, sampleTransactions);
    
    updateKeyMetrics(transformedData);
    updateCharts(transformedData);
    updateTransactionsTable(transformedData);
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
    updateVolumeChart(data.charts?.monthly_stats || []);
    updateCategoryChart(data.charts?.category_distribution || []);
    updateAmountChart(data.charts?.amount_distribution || []);
    updateHourlyChart(data.charts?.hourly_pattern || []);
}

// Create chart data from real data structure
function createChartDataFromRealData(data) {
    const chartData = {
        monthly_stats: [],
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
    
    // Create monthly stats from transactions
    if (data.transactions && data.transactions.length > 0) {
        const monthlyStats = {};
        data.transactions.forEach(tx => {
            const date = new Date(tx.date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            if (!monthlyStats[monthKey]) {
                monthlyStats[monthKey] = { count: 0, volume: 0 };
            }
            monthlyStats[monthKey].count++;
            monthlyStats[monthKey].volume += tx.amount;
        });
        
        chartData.monthly_stats = Object.entries(monthlyStats)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([month, data]) => ({
                month: month,
                count: data.count,
                volume: data.volume
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

// Volume by Month Chart with Brutalist Styling
function updateVolumeChart(monthlyStats) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
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
                <td colspan="8" class="nb-text-center">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No transactions found</p>
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
            <td><span class="category-badge category-${(t.category || 'unknown').toLowerCase()}">${t.category || 'Unknown'}</span></td>
            <td class="formatted-number">${formatCurrency(t.amount)}</td>
            <td class="nb-hidden nb-block-md">${t.phone || 'N/A'}</td>
            <td class="nb-hidden nb-block-md">${t.reference || 'N/A'}</td>
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
    if (!phone) return 'Unknown';
    if (phone.length > 8) {
        return phone.slice(0, -4) + '****';
    }
    return phone;
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
                        <label>Category:</label>
                        <span class="category-badge category-${(transaction.category || 'unknown').toLowerCase()}">${transaction.category || 'Unknown'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Amount:</label>
                        <span class="formatted-number">${formatCurrency(transaction.amount)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Phone:</label>
                        <span>${transaction.phone || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Reference:</label>
                        <span>${transaction.reference || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Status:</label>
                        <span class="status-badge status-${(transaction.status || 'unknown').toLowerCase()}">${transaction.status || 'Unknown'}</span>
                    </div>
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
