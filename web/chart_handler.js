// MoMo Data Dashboard - Chart Handler and Data Management

class MomoDashboard {
    constructor() {
        this.data = null;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderDashboard();
    }

    async loadData() {
        try {
            const response = await fetch('/api/dashboard-data');
            if (response.ok) {
                this.data = await response.json();
            } else {
                // Fallback to local data file
                const fallbackResponse = await fetch('data/processed/dashboard.json');
                if (fallbackResponse.ok) {
                    this.data = await fallbackResponse.json();
                } else {
                    this.data = this.getMockData();
                }
            }
        } catch (error) {
            console.warn('Failed to load data from API, using mock data:', error);
            this.data = this.getMockData();
        }
    }

    getMockData() {
        return {
            summary: {
                totalTransactions: 1250,
                totalAmount: 2450000,
                successRate: 94.5,
                lastUpdated: new Date().toISOString()
            },
            transactions: [
                { date: '2025-01-15', amount: 50000, type: 'Deposit', status: 'Success', phone: '+256700123456' },
                { date: '2025-01-15', amount: 25000, type: 'Withdrawal', status: 'Success', phone: '+256700123457' },
                { date: '2025-01-15', amount: 100000, type: 'Transfer', status: 'Success', phone: '+256700123458' },
                { date: '2025-01-15', amount: 15000, type: 'Payment', status: 'Failed', phone: '+256700123459' },
                { date: '2025-01-15', amount: 75000, type: 'Deposit', status: 'Success', phone: '+256700123460' }
            ],
            analytics: {
                amountDistribution: {
                    '0-10000': 45,
                    '10000-50000': 30,
                    '50000-100000': 20,
                    '100000+': 5
                },
                transactionTypes: {
                    'Deposit': 40,
                    'Withdrawal': 25,
                    'Transfer': 20,
                    'Payment': 15
                }
            }
        };
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                this.scrollToSection(targetId);
            });
        });

        // Report controls
        document.getElementById('export-json')?.addEventListener('click', () => this.exportData());
        document.getElementById('refresh-data')?.addEventListener('click', () => this.refreshData());
        document.getElementById('run-etl')?.addEventListener('click', () => this.runETL());
    }

    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
        }
    }

    renderDashboard() {
        this.renderSummary();
        this.renderTransactionChart();
        this.renderTransactionTable();
        this.renderAnalyticsCharts();
    }

    renderSummary() {
        const summary = this.data.summary;
        
        document.getElementById('total-transactions').textContent = summary.total_transactions.toLocaleString();
        document.getElementById('total-amount').textContent = `RWF ${summary.total_amount.toLocaleString()}`;
        document.getElementById('success-rate').textContent = `${summary.success_rate}%`;
        document.getElementById('last-updated').textContent = new Date(summary.last_updated).toLocaleString();
    }

    renderTransactionChart() {
        const transactions = this.data.transactions;
        const dates = [...new Set(transactions.map(t => t.date))].sort();
        const amounts = dates.map(date => 
            transactions.filter(t => t.date === date).reduce((sum, t) => sum + t.amount, 0)
        );

        const trace = {
            x: dates,
            y: amounts,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Daily Transaction Amount',
            line: { color: '#8B4513', width: 4 },
            marker: { size: 10, color: '#CD853F' }
        };

        const layout = {
            title: 'Daily Transaction Amounts',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Amount (RWF)' },
            margin: { t: 50, r: 50, b: 50, l: 50 }
        };

        Plotly.newPlot('transaction-chart', [trace], layout, {responsive: true});
    }

    renderTransactionTable() {
        const tbody = document.getElementById('transaction-tbody');
        tbody.innerHTML = '';

        this.data.transactions.slice(0, 10).forEach((transaction) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(transaction.date).toLocaleDateString()}</td>
                <td>RWF ${transaction.amount.toLocaleString()}</td>
                <td>${transaction.type}</td>
                <td><span class="status ${transaction.status.toLowerCase()}">${transaction.status}</span></td>
                <td>${transaction.phone}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    renderAnalyticsCharts() {
        this.renderAmountDistributionChart();
        this.renderTransactionTypesChart();
    }

    renderAmountDistributionChart() {
        const distribution = this.data.analytics.amountDistribution;
        
        const trace = {
            labels: Object.keys(distribution),
            values: Object.values(distribution),
            type: 'pie',
            marker: {
                colors: ['#8B4513', '#CD853F', '#D2691E', '#DEB887']
            }
        };

        const layout = {
            title: 'Transaction Amount Distribution',
            margin: { t: 50, r: 50, b: 50, l: 50 }
        };

        Plotly.newPlot('amount-distribution-chart', [trace], layout, {responsive: true});
    }

    renderTransactionTypesChart() {
        const types = this.data.analytics.transactionTypes;
        
        const trace = {
            x: Object.keys(types),
            y: Object.values(types),
            type: 'bar',
            marker: { color: '#8B4513' }
        };

        const layout = {
            title: 'Transaction Types Distribution',
            xaxis: { title: 'Transaction Type' },
            yaxis: { title: 'Count' },
            margin: { t: 50, r: 50, b: 50, l: 50 }
        };

        Plotly.newPlot('transaction-types-chart', [trace], layout, {responsive: true});
    }

    async exportData() {
        try {
            this.showStatus('Exporting data...', 'info');
            
            const response = await fetch('/api/export-json');
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `momo-data-${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showStatus('Data exported successfully!', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showStatus('Export failed. Please try again.', 'error');
        }
    }

    async refreshData() {
        try {
            this.showStatus('Refreshing data...', 'info');
            await this.loadData();
            this.renderDashboard();
            this.showStatus('Data refreshed successfully!', 'success');
        } catch (error) {
            console.error('Refresh error:', error);
            this.showStatus('Failed to refresh data.', 'error');
        }
    }

    async runETL() {
        try {
            this.showStatus('Running ETL process...', 'info');
            
            const response = await fetch('/api/run-etl', { method: 'POST' });
            if (response.ok) {
                const result = await response.json();
                this.showStatus(`ETL completed: ${result.message}`, 'success');
                // Refresh data after ETL
                setTimeout(() => this.refreshData(), 2000);
            } else {
                throw new Error('ETL process failed');
            }
        } catch (error) {
            console.error('ETL error:', error);
            this.showStatus('ETL process failed. Please check logs.', 'error');
        }
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('report-status');
        statusEl.textContent = message;
        statusEl.className = `status-message ${type}`;
        statusEl.style.display = 'block';
        
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MomoDashboard();
});

// Add CSS for status indicators
const style = document.createElement('style');
style.textContent = `
    .status {
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status.success {
        background-color: #d4edda;
        color: #155724;
    }
    .status.failed {
        background-color: #f8d7da;
        color: #721c24;
    }
`;
document.head.appendChild(style);
