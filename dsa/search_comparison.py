"""
Search Algorithms Comparison Module
Implements and compares different search algorithms for transaction data.
"""

import time
import random
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Result of a search operation."""
    found: bool
    index: Optional[int]
    value: Any
    comparisons: int
    execution_time: float


class SearchComparison:
    """
    Comparison class for different search algorithms.
    Implements linear search, binary search, and hash table lookup.
    """
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.sorted_data: List[Dict[str, Any]] = []
        self.hash_table: Dict[str, Dict[str, Any]] = {}
        self.sort_key = 'amount'
    
    def load_transaction_data(self, transactions: List[Dict[str, Any]], sort_key: str = 'amount'):
        """
        Load transaction data for search operations.
        
        Args:
            transactions: List of transaction dictionaries
            sort_key: Key to sort by for binary search
        """
        self.data = transactions.copy()
        self.sort_key = sort_key
        
        # Create sorted copy for binary search
        self.sorted_data = sorted(transactions, key=lambda x: x.get(sort_key, 0))
        
        # Create hash table for O(1) lookup
        self.hash_table = {}
        for i, transaction in enumerate(transactions):
            key = str(transaction.get(sort_key, ''))
            if key not in self.hash_table:
                self.hash_table[key] = []
            self.hash_table[key].append({'index': i, 'transaction': transaction})
    
    def linear_search(self, target_value: Any) -> SearchResult:
        """
        Perform linear search on unsorted data.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        start_time = time.time()
        comparisons = 0
        
        for i, transaction in enumerate(self.data):
            comparisons += 1
            if str(transaction.get(self.sort_key, '')) == str(target_value):
                execution_time = time.time() - start_time
                return SearchResult(
                    found=True,
                    index=i,
                    value=transaction,
                    comparisons=comparisons,
                    execution_time=execution_time
                )
        
        execution_time = time.time() - start_time
        return SearchResult(
            found=False,
            index=None,
            value=None,
            comparisons=comparisons,
            execution_time=execution_time
        )
    
    def binary_search(self, target_value: Any) -> SearchResult:
        """
        Perform binary search on sorted data.
        Time Complexity: O(log n)
        Space Complexity: O(1)
        """
        start_time = time.time()
        comparisons = 0
        left, right = 0, len(self.sorted_data) - 1
        
        while left <= right:
            comparisons += 1
            mid = (left + right) // 2
            mid_value = self.sorted_data[mid].get(self.sort_key)
            
            if str(mid_value) == str(target_value):
                # Find the original index in unsorted data
                original_index = self.data.index(self.sorted_data[mid])
                execution_time = time.time() - start_time
                return SearchResult(
                    found=True,
                    index=original_index,
                    value=self.sorted_data[mid],
                    comparisons=comparisons,
                    execution_time=execution_time
                )
            elif float(mid_value or 0) < float(target_value or 0):
                left = mid + 1
            else:
                right = mid - 1
        
        execution_time = time.time() - start_time
        return SearchResult(
            found=False,
            index=None,
            value=None,
            comparisons=comparisons,
            execution_time=execution_time
        )
    
    def hash_table_search(self, target_value: Any) -> SearchResult:
        """
        Perform hash table lookup.
        Time Complexity: O(1) average case, O(n) worst case
        Space Complexity: O(n)
        """
        start_time = time.time()
        comparisons = 1  # Hash table lookup is typically O(1)
        
        key = str(target_value)
        if key in self.hash_table:
            # Return the first match
            match = self.hash_table[key][0]
            execution_time = time.time() - start_time
            return SearchResult(
                found=True,
                index=match['index'],
                value=match['transaction'],
                comparisons=comparisons,
                execution_time=execution_time
            )
        
        execution_time = time.time() - start_time
        return SearchResult(
            found=False,
            index=None,
            value=None,
            comparisons=comparisons,
            execution_time=execution_time
        )
    
    def compare_search_algorithms(self, target_value: Any) -> Dict[str, SearchResult]:
        """
        Compare all search algorithms on the same target value.
        
        Args:
            target_value: Value to search for
            
        Returns:
            Dictionary with results from each algorithm
        """
        results = {
            'linear_search': self.linear_search(target_value),
            'binary_search': self.binary_search(target_value),
            'hash_table_search': self.hash_table_search(target_value)
        }
        
        return results
    
    def benchmark_search_algorithms(self, num_tests: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Benchmark search algorithms with multiple random searches.
        
        Args:
            num_tests: Number of random searches to perform
            
        Returns:
            Dictionary with average performance metrics
        """
        if not self.data:
            return {}
        
        # Generate random target values
        possible_values = [transaction.get(self.sort_key) for transaction in self.data]
        test_values = random.choices(possible_values, k=num_tests)
        
        # Initialize metrics
        metrics = {
            'linear_search': {'total_time': 0, 'total_comparisons': 0, 'success_rate': 0},
            'binary_search': {'total_time': 0, 'total_comparisons': 0, 'success_rate': 0},
            'hash_table_search': {'total_time': 0, 'total_comparisons': 0, 'success_rate': 0}
        }
        
        # Run tests
        for target_value in test_values:
            results = self.compare_search_algorithms(target_value)
            
            for algorithm, result in results.items():
                metrics[algorithm]['total_time'] += result.execution_time
                metrics[algorithm]['total_comparisons'] += result.comparisons
                if result.found:
                    metrics[algorithm]['success_rate'] += 1
        
        # Calculate averages
        for algorithm in metrics:
            metrics[algorithm]['avg_time'] = metrics[algorithm]['total_time'] / num_tests
            metrics[algorithm]['avg_comparisons'] = metrics[algorithm]['total_comparisons'] / num_tests
            metrics[algorithm]['success_rate'] = (metrics[algorithm]['success_rate'] / num_tests) * 100
        
        return metrics
    
    def get_algorithm_analysis(self) -> Dict[str, Any]:
        """
        Get detailed analysis of each search algorithm.
        
        Returns:
            Dictionary with algorithm characteristics and use cases
        """
        return {
            'linear_search': {
                'time_complexity': 'O(n)',
                'space_complexity': 'O(1)',
                'best_case': 'O(1) - element at first position',
                'worst_case': 'O(n) - element at last position or not found',
                'average_case': 'O(n/2)',
                'use_cases': [
                    'Unsorted data',
                    'Small datasets',
                    'When data changes frequently',
                    'When memory is limited'
                ],
                'advantages': [
                    'Simple to implement',
                    'Works on unsorted data',
                    'No additional memory required',
                    'Stable (maintains relative order)'
                ],
                'disadvantages': [
                    'Slow for large datasets',
                    'Inefficient for frequent searches'
                ]
            },
            'binary_search': {
                'time_complexity': 'O(log n)',
                'space_complexity': 'O(1)',
                'best_case': 'O(1) - element at middle',
                'worst_case': 'O(log n) - element at leaf or not found',
                'average_case': 'O(log n)',
                'use_cases': [
                    'Sorted data',
                    'Large datasets',
                    'Frequent searches',
                    'Range queries'
                ],
                'advantages': [
                    'Very fast for large datasets',
                    'Efficient memory usage',
                    'Predictable performance'
                ],
                'disadvantages': [
                    'Requires sorted data',
                    'Complex to implement',
                    'Not suitable for unsorted data'
                ]
            },
            'hash_table_search': {
                'time_complexity': 'O(1) average, O(n) worst case',
                'space_complexity': 'O(n)',
                'best_case': 'O(1) - no collisions',
                'worst_case': 'O(n) - all elements hash to same bucket',
                'average_case': 'O(1)',
                'use_cases': [
                    'Frequent lookups',
                    'Key-value storage',
                    'Caching',
                    'Database indexing'
                ],
                'advantages': [
                    'Fastest average case',
                    'Direct access',
                    'Good for frequent searches'
                ],
                'disadvantages': [
                    'High memory usage',
                    'Hash collisions can degrade performance',
                    'Not suitable for range queries'
                ]
            }
        }
