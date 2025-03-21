import LinkedList
def sorted(LList) :
    if LList.is_empty():
        return True
    current_item = LList.head
    while current_item.next:
        if current_item > current_item.next:
            return False
        current_item = current_item.next
    return True

# Example usage:
ll = LinkedList.LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.print_list()  # Output: 1 -> 2 -> 3 -> None
print(sorted(ll))  # Output: True

node_to_remove = ll.head.next  # Node with value 2
ll.remove_node(node_to_remove)
ll.print_list()  # Output: 1 -> 3 -> None