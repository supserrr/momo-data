"""
Test cases for Data Structures and Algorithms implementation.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app
from dsa import SearchComparison, SortingComparison, DataStructuresDemo

client = TestClient(app)

class TestSearchAlgorithms:
    """Test cases for search algorithms."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_transactions = [
            {"id": 1, "amount": 100, "description": "Test 1"},
            {"id": 2, "amount": 200, "description": "Test 2"},
            {"id": 3, "amount": 300, "description": "Test 3"},
            {"id": 4, "amount": 400, "description": "Test 4"},
            {"id": 5, "amount": 500, "description": "Test 5"}
        ]
        self.search_comparison = SearchComparison()
        self.search_comparison.load_transaction_data(self.test_transactions, "amount")
    
    def test_linear_search_found(self):
        """Test linear search when element is found."""
        result = self.search_comparison.linear_search(300)
        assert result.found == True
        assert result.value["id"] == 3
        assert result.comparisons > 0
    
    def test_linear_search_not_found(self):
        """Test linear search when element is not found."""
        result = self.search_comparison.linear_search(600)
        assert result.found == False
        assert result.value is None
        assert result.comparisons == len(self.test_transactions)
    
    def test_binary_search_found(self):
        """Test binary search when element is found."""
        result = self.search_comparison.binary_search(300)
        assert result.found == True
        assert result.value["id"] == 3
        assert result.comparisons <= 3  # Should be O(log n)
    
    def test_binary_search_not_found(self):
        """Test binary search when element is not found."""
        result = self.search_comparison.binary_search(600)
        assert result.found == False
        assert result.value is None
        assert result.comparisons <= 3  # Should be O(log n)
    
    def test_hash_table_search_found(self):
        """Test hash table search when element is found."""
        result = self.search_comparison.hash_table_search(300)
        assert result.found == True
        assert result.value["id"] == 3
        assert result.comparisons == 1  # Should be O(1)
    
    def test_hash_table_search_not_found(self):
        """Test hash table search when element is not found."""
        result = self.search_comparison.hash_table_search(600)
        assert result.found == False
        assert result.value is None
        assert result.comparisons == 1  # Should be O(1)
    
    def test_search_comparison(self):
        """Test comparison of all search algorithms."""
        results = self.search_comparison.compare_search_algorithms(300)
        
        assert "linear_search" in results
        assert "binary_search" in results
        assert "hash_table_search" in results
        
        # All should find the same element
        for algorithm, result in results.items():
            assert result.found == True
            assert result.value["id"] == 3

class TestSortingAlgorithms:
    """Test cases for sorting algorithms."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_transactions = [
            {"id": 1, "amount": 500, "description": "Test 1"},
            {"id": 2, "amount": 200, "description": "Test 2"},
            {"id": 3, "amount": 100, "description": "Test 3"},
            {"id": 4, "amount": 400, "description": "Test 4"},
            {"id": 5, "amount": 300, "description": "Test 5"}
        ]
        self.sorting_comparison = SortingComparison()
        self.sorting_comparison.load_transaction_data(self.test_transactions, "amount")
    
    def test_bubble_sort(self):
        """Test bubble sort algorithm."""
        result = self.sorting_comparison.bubble_sort()
        
        assert result.algorithm == "Bubble Sort"
        assert len(result.sorted_data) == len(self.test_transactions)
        
        # Check if sorted
        amounts = [t["amount"] for t in result.sorted_data]
        assert amounts == sorted(amounts)
    
    def test_selection_sort(self):
        """Test selection sort algorithm."""
        result = self.sorting_comparison.selection_sort()
        
        assert result.algorithm == "Selection Sort"
        assert len(result.sorted_data) == len(self.test_transactions)
        
        # Check if sorted
        amounts = [t["amount"] for t in result.sorted_data]
        assert amounts == sorted(amounts)
    
    def test_insertion_sort(self):
        """Test insertion sort algorithm."""
        result = self.sorting_comparison.insertion_sort()
        
        assert result.algorithm == "Insertion Sort"
        assert len(result.sorted_data) == len(self.test_transactions)
        
        # Check if sorted
        amounts = [t["amount"] for t in result.sorted_data]
        assert amounts == sorted(amounts)
    
    def test_merge_sort(self):
        """Test merge sort algorithm."""
        result = self.sorting_comparison.merge_sort()
        
        assert result.algorithm == "Merge Sort"
        assert len(result.sorted_data) == len(self.test_transactions)
        
        # Check if sorted
        amounts = [t["amount"] for t in result.sorted_data]
        assert amounts == sorted(amounts)
    
    def test_quick_sort(self):
        """Test quick sort algorithm."""
        result = self.sorting_comparison.quick_sort()
        
        assert result.algorithm == "Quick Sort"
        assert len(result.sorted_data) == len(self.test_transactions)
        
        # Check if sorted
        amounts = [t["amount"] for t in result.sorted_data]
        assert amounts == sorted(amounts)
    
    def test_sorting_comparison(self):
        """Test comparison of all sorting algorithms."""
        results = self.sorting_comparison.compare_sorting_algorithms()
        
        assert "bubble_sort" in results
        assert "selection_sort" in results
        assert "insertion_sort" in results
        assert "merge_sort" in results
        assert "quick_sort" in results
        
        # All should produce sorted data
        for algorithm, result in results.items():
            amounts = [t["amount"] for t in result.sorted_data]
            assert amounts == sorted(amounts)

class TestDataStructures:
    """Test cases for data structures."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_transactions = [
            {"id": 1, "amount": 100, "description": "Test 1"},
            {"id": 2, "amount": 200, "description": "Test 2"},
            {"id": 3, "amount": 300, "description": "Test 3"}
        ]
        self.demo = DataStructuresDemo()
        self.demo.load_sample_data(self.test_transactions)
    
    def test_linked_list(self):
        """Test linked list operations."""
        demo = self.demo.demonstrate_linked_list()
        
        assert demo["size"] == len(self.test_transactions)
        assert demo["first_transaction"] is not None
        assert demo["last_transaction"] is not None
        assert len(demo["all_transactions"]) == len(self.test_transactions)
    
    def test_stack(self):
        """Test stack operations."""
        demo = self.demo.demonstrate_stack()
        
        assert demo["size"] == len(self.test_transactions)
        assert demo["top_transaction"] is not None
        assert demo["is_empty"] == False
    
    def test_queue(self):
        """Test queue operations."""
        demo = self.demo.demonstrate_queue()
        
        assert demo["size"] == len(self.test_transactions)
        assert demo["front_transaction"] is not None
        assert demo["is_empty"] == False
    
    def test_binary_search_tree(self):
        """Test binary search tree operations."""
        demo = self.demo.demonstrate_bst()
        
        assert demo["size"] == len(self.test_transactions)
        assert demo["height"] >= 0
        assert demo["min_transaction"] is not None
        assert demo["max_transaction"] is not None
        assert len(demo["inorder_traversal"]) == len(self.test_transactions)

class TestDSAAPI:
    """Test cases for DSA API endpoints."""
    
    def test_algorithms_summary_endpoint(self):
        """Test algorithms summary endpoint."""
        response = client.get("/api/dsa/algorithms/summary", auth=("admin", "password"))
        assert response.status_code == 200
        
        data = response.json()
        assert "search_algorithms" in data
        assert "sorting_algorithms" in data
        assert "data_structures" in data
    
    def test_data_structures_performance_endpoint(self):
        """Test data structures performance endpoint."""
        response = client.get("/api/dsa/data-structures/performance", auth=("admin", "password"))
        assert response.status_code == 200
        
        data = response.json()
        assert "performance_characteristics" in data
    
    def test_search_comparison_endpoint(self):
        """Test search comparison endpoint."""
        response = client.get(
            "/api/dsa/search/comparison?target_value=100&sort_key=amount&limit=10",
            auth=("admin", "password")
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "target_value" in data
        assert "results" in data
        assert "algorithm_analysis" in data
    
    def test_sorting_comparison_endpoint(self):
        """Test sorting comparison endpoint."""
        response = client.get(
            "/api/dsa/sorting/comparison?sort_key=amount&limit=10",
            auth=("admin", "password")
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "sort_key" in data
        assert "results" in data
        assert "algorithm_analysis" in data
    
    def test_data_structures_demo_endpoint(self):
        """Test data structures demo endpoint."""
        response = client.get(
            "/api/dsa/data-structures/demo?limit=10",
            auth=("admin", "password")
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data_size" in data
        assert "demonstrations" in data
