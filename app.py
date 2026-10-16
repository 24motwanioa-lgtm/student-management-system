from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from collections import deque
import heapq, json, os

app = Flask(__name__)
app.secret_key = "student-management-system-local"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, "students.json")
undo_stack = []


def load_students():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, encoding="utf-8") as file:
            records = json.load(file)
        return {int(student["roll"]): student for student in records}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {}


students = load_students()


def save_students():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(list(students.values()), file, indent=2, ensure_ascii=False)


def validate_student(form):
    roll = int(form.get("roll", ""))
    name = form.get("name", "").strip()
    branch = form.get("branch", "").strip()
    semester = int(form.get("semester", ""))
    cgpa = float(form.get("cgpa", ""))
    attendance = float(form.get("attendance", ""))
    if roll < 1 or not name or not branch:
        raise ValueError("Enter a valid roll number, name, and branch.")
    if not 1 <= semester <= 12:
        raise ValueError("Semester must be between 1 and 12.")
    if not 0 <= cgpa <= 10:
        raise ValueError("CGPA must be between 0 and 10.")
    if not 0 <= attendance <= 100:
        raise ValueError("Attendance must be between 0 and 100.")
    return {"roll": roll, "name": name, "branch": branch,
            "semester": semester, "cgpa": cgpa, "attendance": attendance}


@app.get("/")
def index():
    query = request.args.get("q", "").strip().lower()
    records = sorted(students.values(), key=lambda item: item["roll"])
    if query:
        records = [s for s in records if query in str(s["roll"]).lower()
                   or query in s["name"].lower() or query in s["branch"].lower()]
    average = round(sum(s["cgpa"] for s in students.values()) / len(students), 2) if students else 0
    return render_template("index.html", students=records, total=len(students), avg=average, q=query)


@app.post("/add")
def add_student():
    try:
        student = validate_student(request.form)
        if student["roll"] in students:
            raise ValueError("A student with this roll number already exists.")
        undo_stack.append(("add", student["roll"], None))
        students[student["roll"]] = student
        save_students()
        flash("Student added successfully.", "success")
    except (ValueError, TypeError):
        flash("Unable to add the student. Check all entered values.", "error")
    return redirect(url_for("index"))


@app.post("/update/<int:roll>")
def update_student(roll):
    try:
        if roll not in students:
            raise ValueError("Student not found.")
        updated = validate_student(request.form)
        if updated["roll"] != roll and updated["roll"] in students:
            raise ValueError("The new roll number already exists.")
        old = students[roll].copy()
        undo_stack.append(("update", updated["roll"], old))
        del students[roll]
        students[updated["roll"]] = updated
        save_students()
        flash("Student record updated successfully.", "success")
    except (ValueError, TypeError):
        flash("Unable to update the student. Check all entered values.", "error")
    return redirect(url_for("index"))


@app.post("/delete/<int:roll>")
def delete_student(roll):
    if roll in students:
        old = students.pop(roll)
        undo_stack.append(("delete", roll, old))
        save_students()
        flash("Student deleted successfully.", "success")
    return redirect(url_for("index"))


@app.post("/undo")
def undo():
    if not undo_stack:
        flash("There is no record operation to undo in this session.", "error")
        return redirect(url_for("index"))
    action, roll, old = undo_stack.pop()
    if action == "add":
        students.pop(roll, None)
    elif action == "delete" and old:
        students[roll] = old
    elif action == "update" and old:
        students.pop(roll, None)
        students[old["roll"]] = old
    save_students()
    flash("The last student record operation was undone.", "success")
    return redirect(url_for("index"))


class AVLNode:
    def __init__(self, key):
        self.key, self.left, self.right, self.height = key, None, None, 1


def node_height(node):
    return node.height if node else 0


def refresh_height(node):
    node.height = 1 + max(node_height(node.left), node_height(node.right))


def rotate_right(y):
    x, subtree = y.left, y.left.right
    x.right, y.left = y, subtree
    refresh_height(y); refresh_height(x)
    return x


def rotate_left(x):
    y, subtree = x.right, x.right.left
    y.left, x.right = x, subtree
    refresh_height(x); refresh_height(y)
    return y


def insert_avl(root, key):
    if not root:
        return AVLNode(key)
    if key < root.key:
        root.left = insert_avl(root.left, key)
    elif key > root.key:
        root.right = insert_avl(root.right, key)
    else:
        return root
    refresh_height(root)
    balance = node_height(root.left) - node_height(root.right)
    if balance > 1 and key < root.left.key:
        return rotate_right(root)                 # LL
    if balance < -1 and key > root.right.key:
        return rotate_left(root)                  # RR
    if balance > 1 and key > root.left.key:
        root.left = rotate_left(root.left)        # LR
        return rotate_right(root)
    if balance < -1 and key < root.right.key:
        root.right = rotate_right(root.right)     # RL
        return rotate_left(root)
    return root


def inorder_tree(root):
    return inorder_tree(root.left) + [root.key] + inorder_tree(root.right) if root else []


def tree_height(root):
    return node_height(root)


def build_bst(values):
    root = None
    def insert(node, key):
        if node is None:
            return {"key": key, "left": None, "right": None}
        if key < node["key"]:
            node["left"] = insert(node["left"], key)
        elif key > node["key"]:
            node["right"] = insert(node["right"], key)
        return node
    for value in values:
        root = insert(root, value)
    def walk(node):
        return walk(node["left"]) + [node["key"]] + walk(node["right"]) if node else []
    return root, walk(root)


def parse_values(data):
    raw = data.get("values", "10,20,30,40")
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except (ValueError, AttributeError):
        raise ValueError("Enter comma-separated integers, for example: 10, 20, 30, 40.")
    if not values:
        raise ValueError("Enter at least one integer.")
    if len(values) > 40:
        raise ValueError("Enter no more than 40 integers.")
    return values


@app.post("/api/dsa")
def dsa_operation():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "stack")
    try:
        values = parse_values(data)
    except ValueError as error:
        return jsonify(error=str(error)), 400

    unique = list(dict.fromkeys(values))
    steps, structure, title = [], [], ""
    operation = ""

    if topic == "stack":
        stack = []
        for value in values:
            stack.append(value)
            steps.append(f"Push {value} onto the stack.")
        removed = stack.pop()
        title, structure = "Stack", stack[::-1]
        operation = f"Pop removed {removed}. Stack uses Last In, First Out (LIFO)."
    elif topic == "queue":
        queue = deque()
        for value in values:
            queue.append(value)
            steps.append(f"Enqueue {value} at the rear.")
        removed = queue.popleft()
        title, structure = "Queue", list(queue)
        operation = f"Dequeue removed {removed}. Queue uses First In, First Out (FIFO)."
    elif topic == "priority":
        heap = []
        for value in values:
            heapq.heappush(heap, value)
            steps.append(f"Insert {value} into the min-priority queue.")
        order = [heapq.heappop(heap) for _ in range(len(heap))]
        title, structure = "Priority Queue", order
        operation = f"Elements were removed in priority order (smallest first): {order}."
    elif topic == "deque":
        dq = deque(values)
        front_removed = dq.popleft()
        rear_removed = dq.pop() if dq else None
        title, structure = "Deque", list(dq)
        operation = f"Removed front element {front_removed} and rear element {rear_removed}. A deque supports insertion and deletion at both ends."
        steps = ["Initialized deque from the supplied values.", "Removed one element from the front and one from the rear."]
    elif topic == "linked":
        linked = values[:]
        removed = linked.pop(0) if linked else None
        title, structure = "Singly Linked List", linked
        operation = f"Head deletion removed {removed}. Remaining list: " + (" → ".join(map(str, linked)) if linked else "empty") + "."
        steps = [f"Node {i + 1} stores {value}." for i, value in enumerate(values)]
    elif topic == "bst":
        _, inorder = build_bst(values)
        title, structure = "Binary Search Tree", inorder
        operation = "Inorder traversal returns the unique keys in sorted order."
        steps = [f"Insert key {value} into the binary search tree." for value in values]
    elif topic == "avl":
        root = None
        for value in values:
            root = insert_avl(root, value)
            steps.append(f"Insert {value}; rebalance the tree if needed.")
        title, structure = "AVL Tree", inorder_tree(root)
        operation = f"Balanced AVL tree built successfully. Tree height: {tree_height(root)}. Rotations are applied when required."
    elif topic in ("graph", "dfs", "bfs", "mst"):
        vertices = unique
        adjacency = {v: [] for v in vertices}
        edges = []
        for i in range(len(vertices) - 1):
            a, b = vertices[i], vertices[i + 1]
            weight = abs(a - b) or 1
            adjacency[a].append(b); adjacency[b].append(a)
            edges.append((weight, a, b))
        if topic == "graph":
            title, structure = "Undirected Graph — Adjacency List", [[v, adjacency[v]] for v in vertices]
            operation = f"Created an undirected graph with {len(vertices)} vertices and {len(edges)} edges. Consecutive input vertices are connected."
            steps = [f"Add edge {a} — {b} with weight {w}." for w, a, b in edges]
        elif topic in ("dfs", "bfs"):
            visited, order = set(), []
            if vertices:
                pending = [vertices[0]] if topic == "dfs" else deque([vertices[0]])
                while pending:
                    current = pending.pop() if topic == "dfs" else pending.popleft()
                    if current in visited:
                        continue
                    visited.add(current); order.append(current)
                    neighbours = adjacency[current]
                    if topic == "dfs":
                        pending.extend(reversed(neighbours))
                    else:
                        pending.extend(n for n in neighbours if n not in visited)
            title = "Depth-First Search" if topic == "dfs" else "Breadth-First Search"
            structure = order
            operation = f"Traversal starts at {vertices[0]} and visits the graph in {('depth-first' if topic == 'dfs' else 'breadth-first')} order."
            steps = [f"Visit vertex {v}." for v in order]
        else:
            # Kruskal's algorithm on the graph formed by the consecutive input vertices.
            parent = {v: v for v in vertices}
            rank = {v: 0 for v in vertices}
            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            def union(a, b):
                ra, rb = find(a), find(b)
                if ra == rb: return False
                if rank[ra] < rank[rb]: ra, rb = rb, ra
                parent[rb] = ra
                if rank[ra] == rank[rb]: rank[ra] += 1
                return True
            chosen, total = [], 0
            for weight, a, b in sorted(edges):
                if union(a, b):
                    chosen.append([a, b, weight]); total += weight
            title, structure = "Minimum Spanning Tree (Kruskal)", chosen
            operation = f"Total MST weight: {total}. Selected {len(chosen)} edge(s) from the supplied graph."
            steps = [f"Select edge {a} — {b}, weight {w}." for a, b, w in chosen]
    elif topic == "sparse":
        # Build a square diagonal matrix from values and convert it to triplet form.
        triplets = [[i, i, value] for i, value in enumerate(values) if value != 0]
        title, structure = "Sparse Matrix — Triplet Representation", triplets
        operation = f"A {len(values)} × {len(values)} diagonal matrix is represented using {len(triplets)} non-zero triplet(s). Rows and columns are zero-indexed."
        steps = [f"Row {row}, column {column}, value {value}." for row, column, value in triplets]
    elif topic == "polynomial":
        x = float(data.get("x", "2"))
        result = sum(coefficient * (x ** power) for power, coefficient in enumerate(values))
        title, structure = "Polynomial Evaluation", values
        expression = " + ".join(f"({coefficient})x^{power}" for power, coefficient in enumerate(values))
        operation = f"Using coefficients in ascending power order, P(x) = {expression}; P({x:g}) = {result:g}."
        steps = [f"Coefficient for x^{power}: {coefficient}." for power, coefficient in enumerate(values)]
    else:
        return jsonify(error="Please select a valid data structure or algorithm."), 400

    return jsonify(title=title, structure=structure, operation=operation, steps=steps)


if __name__ == "__main__":
    print("\nStudent Management System")
    print("Open in your browser: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
