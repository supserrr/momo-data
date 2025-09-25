"""
Sorting Algorithms Comparison Module
Implements and compares different sorting algorithms for transaction data.
"""

import time
import random
from typing import List, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class SortResult:
    """Result of a sorting operation."""
    sorted_data: List[Dict[str, Any]]
    comparisons: int
    swaps: int
    execution_time: float
    algorithm: str


class SortingComparison:
    """
    Comparison class for different sorting algorithms.
    Implements bubble sort, selection sort, insertion sort, merge sort, and quick sort.
    """
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.sort_key = 'amount'
    
    def load_transaction_data(self, transactions: List[Dict[str, Any]], sort_key: str = 'amount'):
        """
        Load transaction data for sorting operations.
        
        Args:
            transactions: List of transaction dictionaries
            sort_key: Key to sort by
        """
        self.data = transactions.copy()
        self.sort_key = sort_key
    
    def bubble_sort(self) -> SortResult:
        """
        Perform bubble sort on transaction data.
        Time Complexity: O(n²)
        Space Complexity: O(1)
        """
        start_time = time.time()
        data = [transaction.copy() for transaction in self.data]
        n = len(data)
        comparisons = 0
        swaps = 0
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                comparisons += 1
                if float(data[j].get(self.sort_key, 0) or 0) > float(data[j + 1].get(self.sort_key, 0) or 0):
                    data[j], data[j + 1] = data[j + 1], data[j]
                    swaps += 1
                    swapped = True
            
            if not swapped:
                break
        
        execution_time = time.time() - start_time
        return SortResult(
            sorted_data=data,
            comparisons=comparisons,
            swaps=swaps,
            execution_time=execution_time,
            algorithm="Bubble Sort"
        )
    
    def selection_sort(self) -> SortResult:
        """
        Perform selection sort on transaction data.
        Time Complexity: O(n²)
        Space Complexity: O(1)
        """
        start_time = time.time()
        data = [transaction.copy() for transaction in self.data]
        n = len(data)
        comparisons = 0
        swaps = 0
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                comparisons += 1
                if float(data[j].get(self.sort_key, 0) or 0) < float(data[min_idx].get(self.sort_key, 0) or 0):
                    min_idx = j
            
            if min_idx != i:
                data[i], data[min_idx] = data[min_idx], data[i]
                swaps += 1
        
        execution_time = time.time() - start_time
        return SortResult(
            sorted_data=data,
            comparisons=comparisons,
            swaps=swaps,
            execution_time=execution_time,
            algorithm="Selection Sort"
        )
    
    def insertion_sort(self) -> SortResult:
        """
        Perform insertion sort on transaction data.
        Time Complexity: O(n²) worst case, O(n) best case
        Space Complexity: O(1)
        """
        start_time = time.time()
        data = [transaction.copy() for transaction in self.data]
        n = len(data)
        comparisons = 0
        swaps = 0
        
        for i in range(1, n):
            key = data[i]
            j = i - 1
            
            while j >= 0:
                comparisons += 1
                if float(data[j].get(self.sort_key, 0) or 0) > float(key.get(self.sort_key, 0) or 0):
                    data[j + 1] = data[j]
                    swaps += 1
                    j -= 1
                else:
                    break
            
            data[j + 1] = key
        
        execution_time = time.time() - start_time
        return SortResult(
            sorted_data=data,
            comparisons=comparisons,
            swaps=swaps,
            execution_time=execution_time,
            algorithm="Insertion Sort"
        )
    
    def merge_sort(self) -> SortResult:
        """
        Perform merge sort on transaction data.
        Time Complexity: O(n log n)
        Space Complexity: O(n)
        """
        start_time = time.time()
        data = [transaction.copy() for transaction in self.data]
        comparisons = 0
        swaps = 0
        
        def merge_sort_helper(arr):
            nonlocal comparisons, swaps
            
            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = merge_sort_helper(arr[:mid])
            right = merge_sort_helper(arr[mid:])
            
            return merge(left, right)
        
        def merge(left, right):
            nonlocal comparisons, swaps
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                comparisons += 1
                if float(left[i].get(self.sort_key, 0) or 0) <= float(right[j].get(self.sort_key, 0) or 0):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
                    swaps += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        sorted_data = merge_sort_helper(data)
        execution_time = time.time() - start_time
        
        return SortResult(
            sorted_data=sorted_data,
            comparisons=comparisons,
            swaps=swaps,
            execution_time=execution_time,
            algorithm="Merge Sort"
        )
    
    def quick_sort(self) -> SortResult:
        """
        Perform quick sort on transaction data.
        Time Complexity: O(n log n) average case, O(n²) worst case
        Space Complexity: O(log n)
        """
        start_time = time.time()
        data = [transaction.copy() for transaction in self.data]
        comparisons = 0
        swaps = 0
        
        def quick_sort_helper(arr, low, high):
            nonlocal comparisons, swaps
            
            if low < high:
                pi = partition(arr, low, high)
                quick_sort_helper(arr, low, pi - 1)
                quick_sort_helper(arr, pi + 1, high)
        
        def partition(arr, low, high):
            nonlocal comparisons, swaps
            
            pivot = arr[high].get(self.sort_key, 0)
            i = low - 1
            
            for j in range(low, high):
                comparisons += 1
                if arr[j].get(self.sort_key, 0) <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            swaps += 1
            return i + 1
        
        quick_sort_helper(data, 0, len(data) - 1)
        execution_time = time.time() - start_time
        
        return SortResult(
            sorted_data=data,
            comparisons=comparisons,
            swaps=swaps,
            execution_time=execution_time,
            algorithm="Quick Sort"
        )
    
    def compare_sorting_algorithms(self) -> Dict[str, SortResult]:
        """
        Compare all sorting algorithms on the same dataset.
        
        Returns:
            Dictionary with results from each algorithm
        """
        results = {
            'bubble_sort': self.bubble_sort(),
            'selection_sort': self.selection_sort(),
            'insertion_sort': self.insertion_sort(),
            'merge_sort': self.merge_sort(),
            'quick_sort': self.quick_sort()
        }
        
        return results
    
    def benchmark_sorting_algorithms(self, num_tests: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Benchmark sorting algorithms with multiple random datasets.
        
        Args:
            num_tests: Number of random datasets to test
            
        Returns:
            Dictionary with average performance metrics
        """
        if not self.data:
            return {}
        
        # Initialize metrics
        metrics = {
            'bubble_sort': {'total_time': 0, 'total_comparisons': 0, 'total_swaps': 0},
            'selection_sort': {'total_time': 0, 'total_comparisons': 0, 'total_swaps': 0},
            'insertion_sort': {'total_time': 0, 'total_comparisons': 0, 'total_swaps': 0},
            'merge_sort': {'total_time': 0, 'total_comparisons': 0, 'total_swaps': 0},
            'quick_sort': {'total_time': 0, 'total_comparisons': 0, 'total_swaps': 0}
        }
        
        # Run tests
        for _ in range(num_tests):
            # Shuffle data for each test
            random.shuffle(self.data)
            results = self.compare_sorting_algorithms()
            
            for algorithm, result in results.items():
                metrics[algorithm]['total_time'] += result.execution_time
                metrics[algorithm]['total_comparisons'] += result.comparisons
                metrics[algorithm]['total_swaps'] += result.swaps
        
        # Calculate averages
        for algorithm in metrics:
            metrics[algorithm]['avg_time'] = metrics[algorithm]['total_time'] / num_tests
            metrics[algorithm]['avg_comparisons'] = metrics[algorithm]['total_comparisons'] / num_tests
            metrics[algorithm]['avg_swaps'] = metrics[algorithm]['total_swaps'] / num_tests
        
        return metrics
    
    def get_algorithm_analysis(self) -> Dict[str, Any]:
        """
        Get detailed analysis of each sorting algorithm.
        
        Returns:
            Dictionary with algorithm characteristics and use cases
        """
        return {
            'bubble_sort': {
                'time_complexity': 'O(n²)',
                'space_complexity': 'O(1)',
                'best_case': 'O(n) - already sorted',
                'worst_case': 'O(n²) - reverse sorted',
                'average_case': 'O(n²)',
                'stable': True,
                'in_place': True,
                'use_cases': [
                    'Educational purposes',
                    'Small datasets',
                    'When simplicity is important'
                ],
                'advantages': [
                    'Simple to implement',
                    'Stable sorting',
                    'In-place sorting',
                    'Good for nearly sorted data'
                ],
                'disadvantages': [
                    'Very slow for large datasets',
                    'Poor performance on average'
                ]
            },
            'selection_sort': {
                'time_complexity': 'O(n²)',
                'space_complexity': 'O(1)',
                'best_case': 'O(n²)',
                'worst_case': 'O(n²)',
                'average_case': 'O(n²)',
                'stable': False,
                'in_place': True,
                'use_cases': [
                    'When memory writes are costly',
                    'Small datasets',
                    'When minimum swaps are required'
                ],
                'advantages': [
                    'Minimum number of swaps',
                    'In-place sorting',
                    'Simple to implement'
                ],
                'disadvantages': [
                    'Always O(n²) time complexity',
                    'Not stable',
                    'Poor performance'
                ]
            },
            'insertion_sort': {
                'time_complexity': 'O(n²) worst case, O(n) best case',
                'space_complexity': 'O(1)',
                'best_case': 'O(n) - already sorted',
                'worst_case': 'O(n²) - reverse sorted',
                'average_case': 'O(n²)',
                'stable': True,
                'in_place': True,
                'use_cases': [
                    'Small datasets',
                    'Nearly sorted data',
                    'Online sorting',
                    'Hybrid sorting algorithms'
                ],
                'advantages': [
                    'Efficient for small datasets',
                    'Stable sorting',
                    'In-place sorting',
                    'Good for nearly sorted data'
                ],
                'disadvantages': [
                    'Poor performance for large datasets',
                    'O(n²) average case'
                ]
            },
            'merge_sort': {
                'time_complexity': 'O(n log n)',
                'space_complexity': 'O(n)',
                'best_case': 'O(n log n)',
                'worst_case': 'O(n log n)',
                'average_case': 'O(n log n)',
                'stable': True,
                'in_place': False,
                'use_cases': [
                    'Large datasets',
                    'When stability is required',
                    'External sorting',
                    'Parallel sorting'
                ],
                'advantages': [
                    'Consistent O(n log n) performance',
                    'Stable sorting',
                    'Good for large datasets',
                    'Predictable performance'
                ],
                'disadvantages': [
                    'Requires O(n) extra space',
                    'Not in-place',
                    'Slower than quick sort in practice'
                ]
            },
            'quick_sort': {
                'time_complexity': 'O(n log n) average, O(n²) worst case',
                'space_complexity': 'O(log n)',
                'best_case': 'O(n log n) - good pivot selection',
                'worst_case': 'O(n²) - bad pivot selection',
                'average_case': 'O(n log n)',
                'stable': False,
                'in_place': True,
                'use_cases': [
                    'General-purpose sorting',
                    'Large datasets',
                    'When average performance matters',
                    'In-memory sorting'
                ],
                'advantages': [
                    'Fast average case performance',
                    'In-place sorting',
                    'Cache-friendly',
                    'Widely used in practice'
                ],
                'disadvantages': [
                    'Worst case O(n²) performance',
                    'Not stable',
                    'Performance depends on pivot selection'
                ]
            }
        }
