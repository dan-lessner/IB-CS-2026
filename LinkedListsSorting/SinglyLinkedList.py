class LNode:
    """
    Class representing a linked list node.
    """
    def __init__(self, data):
        self.data = data  # Value stored in the node
        self.next = None  # Reference to the next node

    def __eq__(self, other):
        """Checks if two nodes have the same data value."""
        if isinstance(other, LNode):
            return self.data == other.data
        return False

    def __lt__(self, other):
        """Checks if this node's data is less than another node's data."""
        if isinstance(other, LNode):
            return self.data < other.data
        return False

    def __gt__(self, other):
        """Checks if this node's data is greater than another node's data."""
        if isinstance(other, LNode):
            return self.data > other.data
        return False

    def is_last(self):
        """Checks if the node is the last in the list."""
        return self.next is None

class LinkedList():
    """
    Class representing a linked list
    """
    def __init__(self):
        self.head = None  # First element of the list

    def append(self, data):
        """Adds a new element to the end of the list."""
        new_node = LNode(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next: 
            last = last.next
        last.next = new_node

    def reverse(self):
        prev, curr = None, self.head
        while curr:
            next = curr.next
            curr.next = prev
            prev = curr
            curr = next
        self.head = prev
        

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
            current.next = node.next   # Bypassing the node

    def print_list(self):
        """Prints the elements of the list."""
        current = self.head
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")
    def len(self):
        count = 0
        current = self.head
        while current:
            count+=1
            current = current.next
        return count
    def is_empty(self):
        if self.head == None:
            return True
        else:
            return False
    def by_index(self, index):
        curr_index = 0
        current = self.head
        while current:
            if curr_index == index:
                return current.data
            curr_index +=1
            current = current.next
    def concatenate(list1, list2):
        if not list1.head:  
            return list2
        if not list2.head:  
            return list1

        # Find the last node of the first list
        last_node = list1.head
        while last_node.next:
            last_node = last_node.next

    # Link the last node of the first list to the head of the second list
        last_node.next = list2.head
        return list1

# When imported, does not run the example usage so it doesnt create a mess
if __name__ == "__main__":
    # Example usage:
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.print_list()  # Output: 1 -> 2 -> 3 -> None

    node_to_remove = ll.head.next  # Node with value 2
    ll.remove_node(node_to_remove)
    ll.print_list()  # Output: 1 -> 3 -> None
