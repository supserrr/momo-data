/**
 * MoMo Dashboard Chart Handler
 * Team 11 - Enterprise Web Development
 */

class MoMoChartHandler {
    constructor() {
        this.charts = {};
        this.data = null;
        this.isLoading = false;
    }

    /**
     * Initialize all charts and setup the dashboard
     */
    async initialize() {
        console.log('Initializing MoMo Chart Handler...');
        
        try {
            // Load data from API or JSON file
            await this.loadData();
            
            // Create all chart visualizations
            this.createTransactionChart();
            this.createCategoryChart();
            this.createAmountChart();
            
            // Setup user interactions
            this.setupEventListeners();
            
            console.log('Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
            this.showError('Failed to load chart data');
        }
    }

    /**
     * Load dashboard data
     */
    async loadData() {
        this.isLoading = true;
        
        try {
            // Try to load from API first
            const apiResponse = await fetch('/api/dashboard-data');
            if (apiResponse.ok) {
                this.data = await apiResponse.json();
                return;
            }
        } catch (error) {
            console.warn('API not available, trying JSON file...');
        }

        try {
            // Fallback to JSON file
            const jsonResponse = await fetch('/data/processed/dashboard.json');
            if (jsonResponse.ok) {
                this.data = await jsonResponse.json();
                return;
            }
        } catch (error) {
            console.warn('JSON file not available, using sample data...');
        }

        // Use sample data as fallback
        this.data = this.generateSampleData();
    }

    /**
     * Generate sample data for demonstration
     */
    generateSampleData() {
        return {
            summary: {
                total_transactions: 1247,
                total_amount: 2450000,
                success_rate: 98.7,
                active_users: 3421
            },
            transactions: [
                { id: 'TXN001', amount: 50000, type: 'Transfer', status: 'Success', phone: '+250791234567', date: '2024-05-16 10:30' },
                { id: 'TXN002', amount: 25000, type: 'Payment', status: 'Success', phone: '+250788765432', date: '2024-05-16 10:25' },
                { id: 'TXN003', amount: 100000, type: 'Deposit', status: 'Success', phone: '+250790123456', date: '2024-05-16 10:20' },
                { id: 'TXN004', amount: 15000, type: 'Withdrawal', status: 'Success', phone: '+250799876543', date: '2024-05-16 10:15' },
                { id: 'TXN005', amount: 75000, type: 'Transfer', status: 'Success', phone: '+250791111111', date: '2024-05-16 10:10' },
                { id: 'TXN006', amount: 30000, type: 'Payment', status: 'Success', phone: '+250792222222', date: '2024-05-16 10:05' },
                { id: 'TXN007', amount: 80000, type: 'Deposit', status: 'Success', phone: '+250793333333', date: '2024-05-16 10:00' },
                { id: 'TXN008', amount: 45000, type: 'Transfer', status: 'Success', phone: '+250794444444', date: '2024-05-16 09:55' },
                { id: 'TXN009', amount: 20000, type: 'Withdrawal', status: 'Success', phone: '+250795555555', date: '2024-05-16 09:50' },
                { id: 'TXN010', amount: 60000, type: 'Payment', status: 'Success', phone: '+250796666666', date: '2024-05-16 09:45' }
            ],
            analytics: {
                dailyData: [
                    { date: '2024-05-10', transactions: 1200, amount: 2100000 },
                    { date: '2024-05-11', transactions: 1350, amount: 2400000 },
                    { date: '2024-05-12', transactions: 1100, amount: 1900000 },
                    { date: '2024-05-13', transactions: 1400, amount: 2600000 },
                    { date: '2024-05-14', transactions: 1600, amount: 2800000 },
                    { date: '2024-05-15', transactions: 1800, amount: 3200000 },
                    { date: '2024-05-16', transactions: 1247, amount: 2450000 }
                ],
                categoryDistribution: [
                    { category: 'Transfer', count: 35, amount: 850000 },
                    { category: 'Payment', count: 25, amount: 600000 },
                    { category: 'Deposit', count: 20, amount: 500000 },
                    { category: 'Withdrawal', count: 15, amount: 400000 },
                    { category: 'Other', count: 5, amount: 100000 }
                ]
            }
        };
    }

    /**
     * Create transaction trends chart
     */
    createTransactionChart() {
        const chartElement = document.getElementById('transaction-chart');
        if (!chartElement) return;

        const dailyData = this.data.analytics.dailyData;

        const trace = {
            x: dailyData.map(d => d.date),
            y: dailyData.map(d => d.transactions),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Transactions',
            line: {
                color: '#FF6B35',
                width: 4
            },
            marker: {
                size: 8,
                color: '#FF6B35',
                line: {
                    color: '#2C3E50',
                    width: 2
                }
            },
            fill: 'tonexty',
            fillcolor: 'rgba(255, 107, 53, 0.1)'
        };

        const layout = {
            title: {
                text: 'Daily Transaction Volume',
                font: {
                    size: 18,
                    family: 'Lexend Mega',
                    color: '#2C3E50'
                }
            },
            xaxis: {
                title: {
                    text: 'Date',
                    font: {
                        family: 'Public Sans',
                        size: 14
                    }
                },
                gridcolor: '#e9ecef',
                gridwidth: 1
            },
            yaxis: {
                title: {
                    text: 'Number of Transactions',
                    font: {
                        family: 'Public Sans',
                        size: 14
                    }
                },
                gridcolor: '#e9ecef',
                gridwidth: 1
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: {
                family: 'Public Sans',
                size: 12
            },
            margin: {
                l: 60,
                r: 30,
                t: 60,
                b: 60
            },
            hovermode: 'closest'
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };

        Plotly.newPlot(chartElement, [trace], layout, config);
        this.charts.transaction = chartElement;
    }

    /**
     * Create category distribution chart
     */
    createCategoryChart() {
        const chartElement = document.getElementById('category-chart');
        if (!chartElement) return;

        const categoryData = this.data.analytics.categoryDistribution;
        
        const trace = {
            values: categoryData.map(c => c.count),
            labels: categoryData.map(c => c.category),
            type: 'pie',
            marker: {
                colors: ['#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
                line: {
                    color: '#2C3E50',
                    width: 2
                }
            },
            textinfo: 'label+percent',
            textfont: {
                family: 'Public Sans',
                size: 12
            },
            hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Transaction Categories',
                font: {
                    size: 18,
                    family: 'Lexend Mega',
                    color: '#2C3E50'
                }
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: {
                family: 'Public Sans',
                size: 12
            },
            margin: {
                l: 30,
                r: 30,
                t: 60,
                b: 30
            },
            showlegend: true,
            legend: {
                orientation: 'v',
                x: 1.05,
                y: 0.5
            }
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };

        Plotly.newPlot(chartElement, [trace], layout, config);
        this.charts.category = chartElement;
    }

    /**
     * Create amount trends chart
     */
    createAmountChart() {
        // This would create an additional chart if needed
        // For now, we'll use the existing charts
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('button[onclick="refreshData()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshCharts());
        }

        // Window resize handler
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * Refresh all charts
     */
    async refreshCharts() {
        console.log('Refreshing charts...');
        this.showLoading(true);
        
        try {
            await this.loadData();
            this.createTransactionChart();
            this.createCategoryChart();
            this.updateSummaryCards();
            this.updateTransactionsTable();
        } catch (error) {
            console.error('Error refreshing charts:', error);
            this.showError('Failed to refresh data');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Update summary cards
     */
    updateSummaryCards() {
        const summary = this.data.summary;
        
        // Update transaction count
        const totalTransactionsEl = document.getElementById('total-transactions');
        if (totalTransactionsEl) {
            totalTransactionsEl.textContent = this.formatNumber(summary.total_transactions);
        }

        // Update total amount
        const totalAmountEl = document.getElementById('total-amount');
        if (totalAmountEl) {
            totalAmountEl.textContent = this.formatNumber(summary.total_amount);
        }

        // Update success rate
        const successRateEl = document.getElementById('success-rate');
        if (successRateEl) {
            successRateEl.textContent = summary.success_rate.toFixed(1) + '%';
        }

        // Update active users
        const activeUsersEl = document.getElementById('active-users');
        if (activeUsersEl) {
            activeUsersEl.textContent = this.formatNumber(summary.active_users);
        }
    }

    /**
     * Update transactions table
     */
    updateTransactionsTable() {
        const tbody = document.getElementById('transactions-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        this.data.transactions.slice(0, 10).forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${tx.id}</td>
                <td>${this.formatNumber(tx.amount)} RWF</td>
                <td><span class="badge ${this.getTypeBadgeClass(tx.type)}"><div class="badge-inner"><p class="badge-text">${tx.type}</p></div></span></td>
                <td><span class="badge ${tx.status === 'Success' ? 'green' : 'orange'}"><div class="badge-inner"><p class="badge-text">${tx.status}</p></div></span></td>
                <td>${tx.phone}</td>
                <td>${tx.date}</td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * Get badge class for transaction type
     */
    getTypeBadgeClass(type) {
        const typeMap = {
            'Transfer': 'blue',
            'Payment': 'green',
            'Deposit': 'orange',
            'Withdrawal': 'default'
        };
        return typeMap[type] || 'default';
    }

    /**
     * Handle window resize
     */
    handleResize() {
        Object.values(this.charts).forEach(chart => {
            if (chart && Plotly) {
                Plotly.Plots.resize(chart);
            }
        });
    }

    /**
     * Show loading state
     */
    showLoading(show) {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            if (show) {
                spinner.classList.remove('nb-hidden');
            } else {
                spinner.classList.add('nb-hidden');
            }
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        // You could implement a toast notification here
        alert(message);
    }

    /**
     * Format number with commas
     */
    formatNumber(num) {
        return new Intl.NumberFormat('en-RW').format(num);
    }

    /**
     * Export chart data
     */
    exportData() {
        const dataStr = JSON.stringify(this.data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'momo-dashboard-data.json';
        link.click();
        
        URL.revokeObjectURL(url);
    }
}

// Initialize chart handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.momoChartHandler = new MoMoChartHandler();
    window.momoChartHandler.initialize();
});

// Global functions for HTML onclick handlers
function refreshData() {
    if (window.momoChartHandler) {
        window.momoChartHandler.refreshCharts();
    }
}

function exportData() {
    if (window.momoChartHandler) {
        window.momoChartHandler.exportData();
    }
}

function runETL() {
    console.log('Running ETL process...');
    // This would trigger the ETL process
    alert('ETL process started! Check the logs for progress.');
}

function loadMoreTransactions() {
    console.log('Loading more transactions...');
    // This would implement pagination
    alert('Loading more transactions...');
}