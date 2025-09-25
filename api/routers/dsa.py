"""
DSA (Data Structures and Algorithms) Router
Provides endpoints for demonstrating and comparing data structures and algorithms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..db import MySQLDatabaseManager
from ..auth import get_current_user
from dsa import SearchComparison, SortingComparison, DataStructuresDemo

router = APIRouter(prefix="/dsa", tags=["dsa"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/search/comparison")
async def compare_search_algorithms(
    target_value: Any = Query(..., description="Value to search for"),
    sort_key: str = Query("amount", description="Field to search by"),
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to load"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Compare different search algorithms on transaction data."""
    try:
        # Get transaction data
        transactions = db.get_transactions(limit=limit)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Initialize search comparison
        search_comparison = SearchComparison()
        search_comparison.load_transaction_data(transactions, sort_key)
        
        # Perform comparison
        results = search_comparison.compare_search_algorithms(target_value)
        
        return {
            "target_value": target_value,
            "sort_key": sort_key,
            "data_size": len(transactions),
            "results": {
                algorithm: {
                    "found": result.found,
                    "index": result.index,
                    "comparisons": result.comparisons,
                    "execution_time_ms": round(result.execution_time * 1000, 4)
                }
                for algorithm, result in results.items()
            },
            "algorithm_analysis": search_comparison.get_algorithm_analysis()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/benchmark")
async def benchmark_search_algorithms(
    sort_key: str = Query("amount", description="Field to search by"),
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to load"),
    num_tests: int = Query(100, ge=10, le=1000, description="Number of test searches"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Benchmark search algorithms with multiple random searches."""
    try:
        # Get transaction data
        transactions = db.get_transactions(limit=limit)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Initialize search comparison
        search_comparison = SearchComparison()
        search_comparison.load_transaction_data(transactions, sort_key)
        
        # Run benchmark
        metrics = search_comparison.benchmark_search_algorithms(num_tests)
        
        return {
            "sort_key": sort_key,
            "data_size": len(transactions),
            "num_tests": num_tests,
            "benchmark_results": {
                algorithm: {
                    "avg_time_ms": round(metrics[algorithm]['avg_time'] * 1000, 4),
                    "avg_comparisons": round(metrics[algorithm]['avg_comparisons'], 2),
                    "success_rate_percent": round(metrics[algorithm]['success_rate'], 2)
                }
                for algorithm in metrics
            },
            "algorithm_analysis": search_comparison.get_algorithm_analysis()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sorting/comparison")
async def compare_sorting_algorithms(
    sort_key: str = Query("amount", description="Field to sort by"),
    limit: int = Query(50, ge=1, le=500, description="Number of transactions to sort"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Compare different sorting algorithms on transaction data."""
    try:
        # Get transaction data
        transactions = db.get_transactions(limit=limit)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Initialize sorting comparison
        sorting_comparison = SortingComparison()
        sorting_comparison.load_transaction_data(transactions, sort_key)
        
        # Perform comparison
        results = sorting_comparison.compare_sorting_algorithms()
        
        return {
            "sort_key": sort_key,
            "data_size": len(transactions),
            "results": {
                algorithm: {
                    "execution_time_ms": round(result.execution_time * 1000, 4),
                    "comparisons": result.comparisons,
                    "swaps": result.swaps,
                    "algorithm": result.algorithm
                }
                for algorithm, result in results.items()
            },
            "algorithm_analysis": sorting_comparison.get_algorithm_analysis()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sorting/benchmark")
async def benchmark_sorting_algorithms(
    sort_key: str = Query("amount", description="Field to sort by"),
    limit: int = Query(50, ge=1, le=500, description="Number of transactions to sort"),
    num_tests: int = Query(10, ge=5, le=50, description="Number of test runs"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Benchmark sorting algorithms with multiple random datasets."""
    try:
        # Get transaction data
        transactions = db.get_transactions(limit=limit)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Initialize sorting comparison
        sorting_comparison = SortingComparison()
        sorting_comparison.load_transaction_data(transactions, sort_key)
        
        # Run benchmark
        metrics = sorting_comparison.benchmark_sorting_algorithms(num_tests)
        
        return {
            "sort_key": sort_key,
            "data_size": len(transactions),
            "num_tests": num_tests,
            "benchmark_results": {
                algorithm: {
                    "avg_time_ms": round(metrics[algorithm]['avg_time'] * 1000, 4),
                    "avg_comparisons": round(metrics[algorithm]['avg_comparisons'], 2),
                    "avg_swaps": round(metrics[algorithm]['avg_swaps'], 2)
                }
                for algorithm in metrics
            },
            "algorithm_analysis": sorting_comparison.get_algorithm_analysis()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-structures/demo")
async def demonstrate_data_structures(
    limit: int = Query(20, ge=1, le=100, description="Number of transactions to demonstrate with"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Demonstrate various data structures with transaction data."""
    try:
        # Get transaction data
        transactions = db.get_transactions(limit=limit)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Initialize data structures demo
        demo = DataStructuresDemo()
        demo.load_sample_data(transactions)
        
        # Get demonstrations
        demonstrations = demo.get_all_demonstrations()
        
        return {
            "data_size": len(transactions),
            "demonstrations": demonstrations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-structures/performance")
async def get_data_structures_performance(
    current_user: str = Depends(get_current_user)
):
    """Get performance characteristics of different data structures."""
    try:
        demo = DataStructuresDemo()
        performance_comparison = demo.get_performance_comparison()
        
        return {
            "performance_characteristics": performance_comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/algorithms/summary")
async def get_algorithms_summary(
    current_user: str = Depends(get_current_user)
):
    """Get summary of all implemented algorithms and data structures."""
    try:
        return {
            "search_algorithms": {
                "linear_search": {
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "description": "Sequential search through unsorted data"
                },
                "binary_search": {
                    "time_complexity": "O(log n)",
                    "space_complexity": "O(1)",
                    "description": "Divide and conquer search on sorted data"
                },
                "hash_table_search": {
                    "time_complexity": "O(1) average",
                    "space_complexity": "O(n)",
                    "description": "Direct access using hash function"
                }
            },
            "sorting_algorithms": {
                "bubble_sort": {
                    "time_complexity": "O(n²)",
                    "space_complexity": "O(1)",
                    "description": "Simple comparison-based sorting"
                },
                "selection_sort": {
                    "time_complexity": "O(n²)",
                    "space_complexity": "O(1)",
                    "description": "Find minimum and swap to position"
                },
                "insertion_sort": {
                    "time_complexity": "O(n²) worst, O(n) best",
                    "space_complexity": "O(1)",
                    "description": "Insert elements in correct position"
                },
                "merge_sort": {
                    "time_complexity": "O(n log n)",
                    "space_complexity": "O(n)",
                    "description": "Divide and conquer with merging"
                },
                "quick_sort": {
                    "time_complexity": "O(n log n) average, O(n²) worst",
                    "space_complexity": "O(log n)",
                    "description": "Divide and conquer with partitioning"
                }
            },
            "data_structures": {
                "linked_list": {
                    "description": "Linear collection with dynamic size",
                    "operations": ["insert", "delete", "search", "traverse"]
                },
                "stack": {
                    "description": "LIFO (Last In, First Out) structure",
                    "operations": ["push", "pop", "peek"]
                },
                "queue": {
                    "description": "FIFO (First In, First Out) structure",
                    "operations": ["enqueue", "dequeue", "front"]
                },
                "binary_search_tree": {
                    "description": "Hierarchical structure with ordering",
                    "operations": ["insert", "search", "delete", "traverse"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
