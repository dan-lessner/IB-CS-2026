class Node:
    """
    Class representing a linked list node.
    """
    def __init__(self, data):
        self.data = data  # Value stored in the node
        self.next = None  # Reference to the next node

    def __eq__(self, other):
        """Checks if two nodes have the same data value."""
        if isinstance(other, Node):
            return self.data == other.data
        return False

    def __lt__(self, other):
        """Checks if this node's data is less than another node's data."""
        if isinstance(other, Node):
            return self.data < other.data
        return False

    def __gt__(self, other):
        """Checks if this node's data is greater than another node's data."""
        if isinstance(other, Node):
            return self.data > other.data
        return False

    def is_last(self):
        """Checks if the node is the last in the list."""
        return self.next is None

class LinkedList:
    """
    Class representing a linked list
    """
    def __init__(self):
        self.head = None  # First element of the list

    def append(self, data):
        """Adds a new element to the end of the list."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def remove_node(self, node):
        """Removes the given node from the list."""
        if not self.head or not node:
            return
        if self.head == node:
            self.head = node.next  # Removing head
            return
        current = self.head
        while current.next and current.next != node:
            current = current.next
        if current.next == node:
            current.next = node.next  # Bypassing the node

    def print_list(self):
        """Prints the elements of the list."""
        current = self.head
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")

# Example usage:
ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.print_list()  # Output: 1 -> 2 -> 3 -> None

node_to_remove = ll.head.next  # Node with value 2
ll.remove_node(node_to_remove)
ll.print_list()  # Output: 1 -> 3 -> None
