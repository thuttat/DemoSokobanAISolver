# 🧠 Sokoban AI

## 📘 Introduction
Hi~ 
**Sokoban AI** is a project that my friends and I did for the AI subject at the University. This project simulates the classic **Sokoban puzzle game**, where the player (or an AI agent) pushes boxes onto target locations inside a maze.  
The goal of this project is to develop an **AI-based solver** that can automatically find the optimal solution using various search algorithms.
Our goal when doing this is to compare the algorithms of Path-finding.

---

## 🧩 Project Structure
```
SOKOBANAI/
│
├── algorithms/           # AI algorithms (BFS, DFS, A*, etc.)
├── assets/               # Game assets (images, sounds, etc.)
├── maps/                 # Sokoban level maps
│
├── dataset.txt           # Level dataset
├── experiment_results.csv# Algorithm performance results
├── game.log              # Log file
├── main.py               # Main entry point
├── menu.py               # Menu and game launcher
├── sokoban.py            # Core Sokoban game logic
├── txt_to_tmx.py         # Convert text maps to TMX format
└── requirements.txt      # Python dependencies
```

---

## ⚙️ How to Run

### 1️⃣ Install Dependencies
```bash
git clone https://github.com/thuttat/DemoSokobanAISolver.git
cd SokobanAI
pip install -r requirements.txt
```

### 2️⃣ Run the Program
```bash
python main.py
```

You can use the menu to choose maps and algorithms.

---

## 🤖 Features
- Sokoban game simulation  
- Multiple AI search algorithms (BFS, DFS, UCS, A*)  
- Experiment logging and result comparison  
- Map conversion tool (`txt_to_tmx.py`)  

---

## 👨‍💻 Author
- **Name:**
Trịnh Thị Anh Thư
Lê Hoàng Bảo Trân
Nguyễn Triệu Duy
- **GitHub:**
https://github.com/thuttat
https://github.com/TranLe05
https://github.com/duynguyenntd


