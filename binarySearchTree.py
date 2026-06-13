class TreeNode:
    def __init__(self, value=0, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def insert(root, value):
    if root is None:
        return TreeNode(value)
    
    if value < root.value:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)
    
    return root

def max_depth(root):
    if root is None:
        return 0
    else:
        left_depth = max_depth(root.left)
        right_depth = max_depth(root.right)
        return max(left_depth, right_depth) + 1
    
def in_order_traversal(root, result=[]):
    if root is not None:
        in_order_traversal(root.left, result)
        result.append(root.value)
        in_order_traversal(root.right, result)
    return result

def find_low(root):
    current = root
    while current.left is not None:
        current = current.left
    return current.value

def find_max(root):
    current = root
    while current.right is not None:
        current = current.right
    return current.value

def find_mid(root):
    sorted_values = in_order_traversal(root, result=[])
    n = len(sorted_values)

    if n%2 == 1:
        return sorted_values[n//2]
    else:
        return (sorted_values[n//2-1]+sorted_values[n//2])/2

if __name__ == "__main__":
    root = None
    values = [8, 3, 10, 1, 6, 14, 4, 7, 13, 2, 15, 5, 9]
    for value in values:
        root = insert(root, value)
        
    
    depth = max_depth(root)
    smallest = find_low(root)
    largest = find_max(root)
    median = find_mid(root)

    print(f"The maximum depth of the Binary Search Tree is: {depth}")
    print(f"The smallest value in the Binary Search Tree is: {smallest}")
    print(f"The largest value in the Binary Search Tree is: {largest}")
    print(f"The median value in the Binary Search Tree is: {median}")
