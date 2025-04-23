import SinglyLinkedList

class DLNode(SinglyLinkedList.LNode):
    """
    Class representing a doubly linked list node.
    """
    def __init__(self, data):
        super().__init__(data)
        self.prev = None
        
    def is_first(self):
        """Checks if the node is the first in the list."""
        return self.prev is None

class DoublyLinkedList(SinglyLinkedList.LinkedList):
    """
    Class representing a linked list
    """

    def append(self, data):
        """Adds a new element to the end of the list."""
        new_node = DLNode(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next: 
            last = last.next
        last.next, new_node.prev = new_node, last

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
            current.next, node.next.prev = node.next, current  # Bypassing the node

    def print_list(self):
        """Prints the elements of the list."""
        current = self.head
        while current:
            print(current.data, end=" <--> ")
            current = current.next
        print("None")

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
        last_node.next, list2.head.prev = list2.head, last_node
        return list1

    def swap(self, node1Index, node2Index):
        # find nodes based on Index
        node1 = self.head
        for x in range(node1Index):
            node1 = node1.next
        node2 = self.head
        for x in range(node2Index):
            node2 = node2.next

        # temporary definitions
        prev, next = node1.prev, node2.next

        # if first node is first, point second node nowhere and make it self.head
        if not node1.is_first(): 
            prev.next, node2.prev = node2, prev
        else:
            node2.prev, self.head = None, node2

        # if second node is last, point first node nowhere
        if not node2.is_last(): 
            next.prev, node1.next = node1, next
        else:
            node1.next = None

        # swap inner pointers
        node1.prev, node2.next = node2, node1

# When imported, does not run the example usage so it doesnt create a mess
if __name__ == "__main__":
    # Example usage:
    ll = DoublyLinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.append(4)
    ll.append(5)
    ll.print_list()  # Output: 1 -> 2 -> 3 -> None

    node_to_remove = ll.head.next  # Node with value 2
    ll.remove_node(node_to_remove)
    ll.print_list()  # Output: 1 -> 3 -> None
