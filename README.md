# StockChessPy

StockChessPy is a simple chess assistant powered by [Stockfish](https://stockfishchess.org/) that runs in **Termux**. It allows you to play against an opponent while suggesting optimal moves using Stockfish’s powerful analysis.

## 🔗 Repository
[GitHub - Kamanati/StockChessPy](https://github.com/Kamanati/StockChessPy)

---

## 🚀 Features
- **Stockfish Engine Integration** – Provides best move recommendations.
- **Customizable Play Style** – Adjusts difficulty, strength, and analysis depth.
- **Algebraic Notation Input** – Enter moves in standard chess notation.
- **Board Visualization** – View the current board state at any time.
- **Checkmate Alerts** – Notifies when a forced checkmate is available.
- **Optimized for Termux** – Runs smoothly on mobile devices.

---

## 📦 Installation

### 1️⃣ Install **Termux** (if not already installed)
Download and install Termux from [F-Droid](https://f-droid.org/packages/com.termux/) or the [Google Play Store](https://play.google.com/store/apps/details?id=com.termux).

### 2️⃣ Install Stockfish  
Run the following command in Termux:

```sh
wget https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-android-armv8.tar 
tar -xvf stockfish-android-armv8.tar
cd stockfish
cp stockfish-android-armv8 /data/data/com.termux/files/usr/bin/stockfish

```
### Install on *Linux* and *Windows*:

Go [here](https://stockfishchess.org/download/) and check for installation
`Make sure to change the path of stockfish inside the main.py`

```python
engine_path = "/data/data/com.termux/files/usr/bin/stockfish"
# Change to Stockfish orginal path in your system

```

### 3️⃣ Clone this repository  

```sh
git clone https://github.com/Kamanati/StockChessPy.git
cd StockChessPy
```

### 4️⃣ Run the script  

```sh
python main.py
```

---

## 🕹️ How to Play
1. Choose whether your opponent plays as **White (w) or Black (b)**.
2. If the opponent is Black, Stockfish suggests an opening move.
3. Enter the opponent’s moves in **Algebraic Notation** (e.g., `e4`, `Nc6`).
4. Stockfish will recommend the best possible move for you.
5. Type `board` to display the current game position.
6. Type `quit` to exit the game.

---

## ⚙️ Custom Stockfish Configuration
The script uses the following Stockfish settings:

- **Skill Level:** 20 (Max difficulty)
- **UCI Elo:** 3190 (Grandmaster level)
- **Threads:** 3 (Optimized for mobile)
- **Hash Memory:** 512 MB
- **Move Overhead:** 30ms (Faster responses)
- **Tablebases:** Used only in deep endgames

These settings can be adjusted inside the script if needed.

---

## 🏆 Example Gameplay
```
Is your opponent playing as White or Black? (w/b): w
Enter opponent's move (or 'board' to view board, 'quit' to exit): e4
✅ Best move for you: c5
Enter opponent's move: Nf3
✅ Best move for you: d6
...
⚠️ CHECKMATE IN 2 MOVES! FORCING MATE ⚠️
✅ Best move for you: Qh5#
🏁 Game Over!
```

---

## ❌ Troubleshooting

### Stockfish not found?
Make sure Stockfish is installed by running:

```sh
which stockfish
```
See Installation Option 

### Script not running?
Ensure you have Python installed:

```sh
pkg install python
```

Then, run the script again.

---

## 📜 License
This project is open-source under the **MIT License**.

---

## 📬 Contact
For issues, suggestions, or contributions, visit [GitHub Issues](https://github.com/Kamanati/StockChessPy/issues).

---

Happy Chess Playing! ♟️🔥
