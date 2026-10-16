# Student Management System

A local Flask web application for managing student records and working with data structures and algorithms. The interface is in English.

## Features
- Add, search, update, and delete student records
- Store student data in a local `students.json` file
- Track roll number, name, branch, semester, CGPA, and attendance
- Undo the most recent student-record change during the current server session
- Implementations for Stack, Queue, Priority Queue, Deque, Linked List operations, BST insertion and inorder traversal, AVL insertion with balancing rotations, Graph adjacency list, DFS, BFS, Kruskal MST, sparse matrix triplets, and polynomial evaluation

## Run on Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

## Run on WSL / Bash
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

The terminal prints the local URL: `http://127.0.0.1:5000`. Open it in your browser and keep the terminal running.

## Algorithm input notes
- Enter comma-separated integers. Graph edges connect consecutive distinct input vertices; edge weights are the absolute difference between endpoints (or 1 when equal). DFS and BFS start at the first vertex.
- The sparse-matrix operation constructs a diagonal matrix from the supplied values and displays non-zero entries as triplets.
- Polynomial coefficients are interpreted in ascending power order: the first number is the constant coefficient, the next is the coefficient of x, and so on.
