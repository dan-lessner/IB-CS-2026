def max_heapify_branch_only(arr, n, i):
    left = 2 * i + 1
    right = 2 * i + 2

    # Check left child
    if left < n and arr[left] > arr[i]:
        arr[i], arr[left] = arr[left], arr[i]
        max_heapify_branch_only(arr, n, left)

    # Check right child
    if right < n and arr[right] > arr[i]:
        arr[i], arr[right] = arr[right], arr[i]
        max_heapify_branch_only(arr, n, right)

def build_max_heap_branch_only(arr):
    n = len(arr)
    # Start from the last parent node and move upward
    for i in range(n // 2 - 1, -1, -1):
        max_heapify_branch_only(arr, n, i)

# Example usage
arr = [4, 10, 3, 5, 1, 2, 8]
build_max_heap_branch_only(arr)
print("Max Heap (branch-only):", arr)