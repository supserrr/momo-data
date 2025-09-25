"""
Data Structures Implementation Module
Implements various data structures for transaction data management.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json


@dataclass
class TransactionNode:
    """Node for linked list and tree structures."""
    data: Dict[str, Any]
    next: Optional['TransactionNode'] = None
    prev: Optional['TransactionNode'] = None
    left: Optional['TransactionNode'] = None
    right: Optional['TransactionNode'] = None


class TransactionLinkedList:
    """
    Doubly linked list implementation for transaction data.
    """
    
    def __init__(self):
        self.head: Optional[TransactionNode] = None
        self.tail: Optional[TransactionNode] = None
        self.size = 0
    
    def append(self, transaction: Dict[str, Any]) -> None:
        """Add transaction to the end of the list."""
        new_node = TransactionNode(transaction)
        
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
    
    def prepend(self, transaction: Dict[str, Any]) -> None:
        """Add transaction to the beginning of the list."""
        new_node = TransactionNode(transaction)
        
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        
        self.size += 1
    
    def insert_at(self, index: int, transaction: Dict[str, Any]) -> bool:
        """Insert transaction at specific index."""
        if index < 0 or index > self.size:
            return False
        
        if index == 0:
            self.prepend(transaction)
            return True
        elif index == self.size:
            self.append(transaction)
            return True
        
        new_node = TransactionNode(transaction)
        current = self.head
        
        for _ in range(index):
            current = current.next
        
        new_node.prev = current.prev
        new_node.next = current
        current.prev.next = new_node
        current.prev = new_node
        
        self.size += 1
        return True
    
    def remove(self, transaction_id: str) -> bool:
        """Remove transaction by ID."""
        current = self.head
        
        while current:
            if current.data.get('id') == transaction_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self.size -= 1
                return True
            
            current = current.next
        
        return False
    
    def find(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Find transaction by ID."""
        current = self.head
        
        while current:
            if current.data.get('id') == transaction_id:
                return current.data
            current = current.next
        
        return None
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert linked list to Python list."""
        result = []
        current = self.head
        
        while current:
            result.append(current.data)
            current = current.next
        
        return result
    
    def clear(self) -> None:
        """Clear all transactions."""
        self.head = self.tail = None
        self.size = 0


class TransactionStack:
    """
    Stack implementation using linked list for transaction data.
    """
    
    def __init__(self):
        self._list = TransactionLinkedList()
    
    def push(self, transaction: Dict[str, Any]) -> None:
        """Push transaction onto stack."""
        self._list.prepend(transaction)
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """Pop transaction from stack."""
        if self._list.head:
            transaction = self._list.head.data
            self._list.head = self._list.head.next
            if self._list.head:
                self._list.head.prev = None
            else:
                self._list.tail = None
            self._list.size -= 1
            return transaction
        return None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at top transaction without removing."""
        return self._list.head.data if self._list.head else None
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return self._list.size == 0
    
    def size(self) -> int:
        """Get stack size."""
        return self._list.size


class TransactionQueue:
    """
    Queue implementation using linked list for transaction data.
    """
    
    def __init__(self):
        self._list = TransactionLinkedList()
    
    def enqueue(self, transaction: Dict[str, Any]) -> None:
        """Add transaction to queue."""
        self._list.append(transaction)
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Remove transaction from queue."""
        if self._list.head:
            transaction = self._list.head.data
            self._list.head = self._list.head.next
            if self._list.head:
                self._list.head.prev = None
            else:
                self._list.tail = None
            self._list.size -= 1
            return transaction
        return None
    
    def front(self) -> Optional[Dict[str, Any]]:
        """Get front transaction without removing."""
        return self._list.head.data if self._list.head else None
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._list.size == 0
    
    def size(self) -> int:
        """Get queue size."""
        return self._list.size


class TransactionBinarySearchTree:
    """
    Binary Search Tree implementation for transaction data.
    """
    
    def __init__(self, key_field: str = 'amount'):
        self.root: Optional[TransactionNode] = None
        self.key_field = key_field
        self.size = 0
    
    def insert(self, transaction: Dict[str, Any]) -> None:
        """Insert transaction into BST."""
        self.root = self._insert_recursive(self.root, transaction)
        self.size += 1
    
    def _insert_recursive(self, node: Optional[TransactionNode], transaction: Dict[str, Any]) -> TransactionNode:
        """Recursive helper for insertion."""
        if not node:
            return TransactionNode(transaction)
        
        if float(transaction.get(self.key_field, 0) or 0) < float(node.data.get(self.key_field, 0) or 0):
            node.left = self._insert_recursive(node.left, transaction)
        else:
            node.right = self._insert_recursive(node.right, transaction)
        
        return node
    
    def search(self, key_value: Any) -> Optional[Dict[str, Any]]:
        """Search for transaction by key value."""
        return self._search_recursive(self.root, key_value)
    
    def _search_recursive(self, node: Optional[TransactionNode], key_value: Any) -> Optional[Dict[str, Any]]:
        """Recursive helper for search."""
        if not node:
            return None
        
        if str(key_value) == str(node.data.get(self.key_field)):
            return node.data
        elif float(key_value or 0) < float(node.data.get(self.key_field, 0) or 0):
            return self._search_recursive(node.left, key_value)
        else:
            return self._search_recursive(node.right, key_value)
    
    def inorder_traversal(self) -> List[Dict[str, Any]]:
        """Get transactions in sorted order."""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[TransactionNode], result: List[Dict[str, Any]]) -> None:
        """Recursive helper for inorder traversal."""
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)
    
    def preorder_traversal(self) -> List[Dict[str, Any]]:
        """Get transactions in preorder."""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node: Optional[TransactionNode], result: List[Dict[str, Any]]) -> None:
        """Recursive helper for preorder traversal."""
        if node:
            result.append(node.data)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)
    
    def postorder_traversal(self) -> List[Dict[str, Any]]:
        """Get transactions in postorder."""
        result = []
        self._postorder_recursive(self.root, result)
        return result
    
    def _postorder_recursive(self, node: Optional[TransactionNode], result: List[Dict[str, Any]]) -> None:
        """Recursive helper for postorder traversal."""
        if node:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append(node.data)
    
    def find_min(self) -> Optional[Dict[str, Any]]:
        """Find transaction with minimum key value."""
        if not self.root:
            return None
        
        current = self.root
        while current.left:
            current = current.left
        
        return current.data
    
    def find_max(self) -> Optional[Dict[str, Any]]:
        """Find transaction with maximum key value."""
        if not self.root:
            return None
        
        current = self.root
        while current.right:
            current = current.right
        
        return current.data
    
    def height(self) -> int:
        """Get height of the tree."""
        return self._height_recursive(self.root)
    
    def _height_recursive(self, node: Optional[TransactionNode]) -> int:
        """Recursive helper for height calculation."""
        if not node:
            return -1
        
        left_height = self._height_recursive(node.left)
        right_height = self._height_recursive(node.right)
        
        return 1 + max(left_height, right_height)


class DataStructuresDemo:
    """
    Demonstration class for all data structures.
    """
    
    def __init__(self):
        self.linked_list = TransactionLinkedList()
        self.stack = TransactionStack()
        self.queue = TransactionQueue()
        self.bst = TransactionBinarySearchTree()
    
    def load_sample_data(self, transactions: List[Dict[str, Any]]) -> None:
        """Load sample transaction data into all data structures."""
        for transaction in transactions:
            self.linked_list.append(transaction)
            self.stack.push(transaction)
            self.queue.enqueue(transaction)
            self.bst.insert(transaction)
    
    def demonstrate_linked_list(self) -> Dict[str, Any]:
        """Demonstrate linked list operations."""
        return {
            'size': self.linked_list.size,
            'first_transaction': self.linked_list.head.data if self.linked_list.head else None,
            'last_transaction': self.linked_list.tail.data if self.linked_list.tail else None,
            'all_transactions': self.linked_list.to_list()
        }
    
    def demonstrate_stack(self) -> Dict[str, Any]:
        """Demonstrate stack operations."""
        return {
            'size': self.stack.size(),
            'top_transaction': self.stack.peek(),
            'is_empty': self.stack.is_empty()
        }
    
    def demonstrate_queue(self) -> Dict[str, Any]:
        """Demonstrate queue operations."""
        return {
            'size': self.queue.size(),
            'front_transaction': self.queue.front(),
            'is_empty': self.queue.is_empty()
        }
    
    def demonstrate_bst(self) -> Dict[str, Any]:
        """Demonstrate BST operations."""
        return {
            'size': self.bst.size,
            'height': self.bst.height(),
            'min_transaction': self.bst.find_min(),
            'max_transaction': self.bst.find_max(),
            'inorder_traversal': self.bst.inorder_traversal(),
            'preorder_traversal': self.bst.preorder_traversal(),
            'postorder_traversal': self.bst.postorder_traversal()
        }
    
    def get_performance_comparison(self) -> Dict[str, Any]:
        """Get performance characteristics of each data structure."""
        return {
            'linked_list': {
                'insertion': 'O(1) at head/tail, O(n) at position',
                'deletion': 'O(1) at head/tail, O(n) at position',
                'search': 'O(n)',
                'access': 'O(n)',
                'space_complexity': 'O(n)',
                'use_cases': [
                    'Dynamic size requirements',
                    'Frequent insertions/deletions',
                    'Implementation of other data structures'
                ]
            },
            'stack': {
                'push': 'O(1)',
                'pop': 'O(1)',
                'peek': 'O(1)',
                'search': 'O(n)',
                'space_complexity': 'O(n)',
                'use_cases': [
                    'Function call management',
                    'Expression evaluation',
                    'Undo operations',
                    'Backtracking algorithms'
                ]
            },
            'queue': {
                'enqueue': 'O(1)',
                'dequeue': 'O(1)',
                'front': 'O(1)',
                'search': 'O(n)',
                'space_complexity': 'O(n)',
                'use_cases': [
                    'BFS algorithms',
                    'Task scheduling',
                    'Buffer management',
                    'Print job management'
                ]
            },
            'binary_search_tree': {
                'insertion': 'O(log n) average, O(n) worst case',
                'search': 'O(log n) average, O(n) worst case',
                'deletion': 'O(log n) average, O(n) worst case',
                'traversal': 'O(n)',
                'space_complexity': 'O(n)',
                'use_cases': [
                    'Sorted data storage',
                    'Range queries',
                    'Database indexing',
                    'Expression trees'
                ]
            }
        }
    
    def get_all_demonstrations(self) -> Dict[str, Any]:
        """Get demonstrations for all data structures."""
        return {
            'linked_list': self.demonstrate_linked_list(),
            'stack': self.demonstrate_stack(),
            'queue': self.demonstrate_queue(),
            'binary_search_tree': self.demonstrate_bst(),
            'performance_comparison': self.get_performance_comparison()
        }
