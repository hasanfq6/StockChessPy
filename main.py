import os
import chess
import chess.engine

# Stockfish path for Termux
engine_path = "/data/data/com.termux/files/usr/bin/stockfish"


# Check if Stockfish is installed
if not os.path.exists(engine_path):
    print("❌ Stockfish engine not found. Install it Refer https://github.com/Kamanati/StockChessPy")
    exit(1)

# Initialize board and Stockfish engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

# Configure Stockfish for custom play style
engine.configure({
    "Skill Level": 20,       # Max difficulty (0-20)
    "UCI_Elo": 3190,         # Max strength (if UCI_LimitStrength=True)
    "UCI_LimitStrength": False,  # Use full engine strength
    "Threads": 3,            # Use 4 CPU cores
    "Hash": 512,             # Allocate memory for deeper analysis
    "Move Overhead": 30,     # Less time wasted, more aggressive
    "nodestime": 10000,        # Forces more nodes per move (deeper calc)
    "SyzygyProbeDepth": 10,   # Use tablebases only at deep endgames
    "UCI_ShowWDL": True      # Show win/draw/loss probabilities
})

# Ask for opponent's color
while True:
    opponent_color = input("Is your opponent playing as White or Black? (w/b): ").strip().lower()
    if opponent_color in ['w', 'b']:
        break
    print("Invalid choice. Enter 'w' for White or 'b' for Black.")

# If opponent is Black, suggest the best opening move
if opponent_color == 'b':
    best_move = engine.play(board, chess.engine.Limit(time=2))  # 2s per move
    best_move_algebraic = board.san(best_move.move)  # Convert to standard notation
    print(f"\n🔥 Suggested first move: {best_move_algebraic} 🔥")
    board.push(best_move.move)

print("\nChess Assistant Started. Enter opponent's moves in algebraic notation (e.g., e4, Nc6)")

while not board.is_game_over():
    # Get opponent's move
    move = input("\nEnter opponent's move (or 'board' to view board, 'quit' to exit): ").strip()

    if move.lower() == "quit":
        break
    elif move.lower() == "board":
        print(board)
        continue

    try:
        board.push_san(move)  # Convert from algebraic notation and apply
    except ValueError:
        print("❌ Invalid move, try again.")
        continue

    if board.is_game_over():
        break

    # Check for forced checkmate
    analysis = engine.analyse(board, chess.engine.Limit(time=2), info=chess.engine.INFO_SCORE)
    mate_in = analysis["score"].relative.mate()
    if mate_in is not None:
        print(f"\n⚠️ CHECKMATE IN {mate_in} MOVES! FORCING MATE ⚠️")

    # Get best move (forcing checkmate if possible)
    best_move = engine.play(board, chess.engine.Limit(time=3))
    best_move_algebraic = board.san(best_move.move)  # Convert to standard notation
    print(f"\n✅ Best move for you: {best_move_algebraic}")
    board.push(best_move.move)  # Play best move

print("\n🏁 Game Over!")
engine.quit()
