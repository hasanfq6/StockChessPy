import os,sys
import argparse
import chess
import chess.engine

# Stockfish path for Termux
engine_path = "/data/data/com.termux/files/usr/bin/stockfish"

# Check if Stockfish is installed
if not os.path.exists(engine_path):
    print("❌ Stockfish engine not found. Install it. Refer https://github.com/Kamanati/StockChessPy")
    exit(1)

# Argument Parser
import argparse

parser = argparse.ArgumentParser(description="Stockfish Chess Engine with Custom Modes")

# Modes Group
modes_group = parser.add_argument_group("Modes", "Predefined playstyles")
modes_group.add_argument("-A", "--aggressive", action="store_true", help="Enable maximum strength mode (Default Mode)")
modes_group.add_argument("-I", "--intermediate", action="store_true", help="Enable moderate strength mode")
modes_group.add_argument("-C", "--club", action="store_true", help="Enable normal player mode (Human-like play)")
modes_group.add_argument("-K", "--classical", action="store_true", help="Enable deep calculation mode (Slow & Strategic)")
modes_group.add_argument("-D", "--defensive", action="store_true", help="Enable defensive playstyle (Avoids blunders)")
modes_group.add_argument("-G", "--gambit", action="store_true", help="Enable aggressive and risky plays (Sacrifices material)")
modes_group.add_argument("-X", "--adaptive", action="store_true", help="Enable dynamic playstyle (Adjusts strategy during the game)")

# Custom Configuration Group
custom_group = parser.add_argument_group("Custom", "Fine-tune engine settings")
custom_group.add_argument("-s", "--skill", type=int, default=20, help="Stockfish skill level (0-20)")
custom_group.add_argument("-e", "--elo", type=int, default=3190, help="Stockfish UCI Elo rating (1390 - 3190)")
custom_group.add_argument("-t", "--threads", type=int, default=3, help="Number of CPU threads for Stockfish (Higher = Faster)")
custom_group.add_argument("-m", "--hash", type=int, default=512, help="Hash table size (MB) (Higher = Lower chance of crash)")
custom_group.add_argument("-o", "--move-overhead", type=int, default=30, help="Move overhead in milliseconds (Higher = More time for move)")
custom_group.add_argument("-n", "--nodestime", type=int, default=10000, help="Minimum nodes per move (Higher = Best move)")
custom_group.add_argument("-z", "--syzygy-depth", type=int, default=10, help="Syzygy tablebase probe depth (Endgame table)")

# Parse arguments
args = parser.parse_args()

slected_mode = None

# Apply predefined configurations based on mode
if args.aggressive:
    args.skill = 20
    args.elo = 3190
    args.threads = 4
    args.hash = 700
    args.move_overhead = 10
    args.nodestime = 10000
    slected_mode = "Aggressive"

elif args.intermediate:
    args.skill = 15
    args.elo = 2500
    args.threads = 2
    args.hash = 512
    args.move_overhead = 25
    args.nodestime = 8000
    slected_mode = "Intermediate"

elif args.club:
    args.skill = 10
    args.elo = 1800
    args.threads = 2
    args.hash = 256
    args.move_overhead = 50
    args.nodestime = 5000
    slected_mode = "Club"

elif args.classical:
    args.skill = 20
    args.elo = 3190
    args.threads = 4
    args.hash = 700
    args.move_overhead = 50
    args.nodestime = 10000
    slected_mode = "Classical"

elif args.defensive:
    args.skill = 15
    args.elo = 2400
    args.threads = 2
    args.hash = 512
    args.move_overhead = 40
    args.nodestime = 10000
    slected_mode = "Defensive"

elif args.gambit:
    args.skill = 17
    args.elo = 2700
    args.threads = 3
    args.hash = 256
    args.move_overhead = 15
    args.nodestime = 10000
    slected_mode = "Gambit"

elif args.adaptive:
    args.skill = 18  # Start with a balanced level
    args.elo = 2800
    args.threads = 3
    args.hash = 768
    args.move_overhead = 20
    args.nodestime = 10000
    slected_mode = "Adaptive"

# Initialize board and Stockfish engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

# Configure Stockfish based on arguments
engine.configure({
    "Skill Level": args.skill,
    "UCI_Elo": args.elo,
    "UCI_LimitStrength": False,
    "Threads": args.threads,
    "Hash": args.hash,
    "Move Overhead": args.move_overhead,
    "nodestime": args.nodestime,
    "SyzygyProbeDepth": args.syzygy_depth,
    "UCI_ShowWDL": True
})

# Display Configurations in an Attractive Way
print("\n🔧 Stockfish Configuration 🔧")
if slected_mode is not None:
      print(f"🎮 Mode        : {slected_mode} ")
elif len(sys.argv) == 1:
     print(f"🎮 Mode        : Aggresive (Default)")
else:
      print(f"🎮 Mode        : Custom ")
print(f"🧠 Skill Level     : {args.skill}")
print(f"🎖️  Elo Rating     : {args.elo}")
print(f"🖥️  CPU Threads    : {args.threads}")
print(f"💾 Hash Size       : {args.hash} MB")
print(f"⏳ Move Overhead   : {args.move_overhead} ms")
print(f"🔍 Nodes per Move  : {args.nodestime}")
print(f"📚 Syzygy Depth    : {args.syzygy_depth}\n")

if len(sys.argv) == 1:
     print("StockChessPy starts as Aggresive for costomize use `python main.py -h`\n")

# Ask for opponent's color
while True:
    opponent_color = input("Is your opponent playing as White or Black? (w/b): ").strip().lower()
    if opponent_color in ['w', 'b']:
        break
    print("Invalid choice. Enter 'w' for White or 'b' for Black.")

# If opponent is Black, suggest the best opening move
if opponent_color == 'b':
    best_move = engine.play(board, chess.engine.Limit(time=2))
    best_move_algebraic = board.san(best_move.move)
    print(f"\n🔥 Suggested first move: {best_move_algebraic} 🔥")
    board.push(best_move.move)

print("\nChess Assistant Started. Enter opponent's moves in algebraic notation (e.g., e4, Nc6)")

while not board.is_game_over():
    move = input("\nEnter opponent's move (or 'board' to view board, 'quit' to exit): ").strip()

    if move.lower() == "quit":
        break
    elif move.lower() == "board":
        print(board)
        continue

    try:
        board.push_san(move)
    except ValueError:
        print("❌ Invalid move, try again.")
        continue

    if board.is_game_over():
        break

    # Adaptive Mode Adjustments
    if args.adaptive:
        analysis = engine.analyse(board, chess.engine.Limit(time=1), info=chess.engine.INFO_SCORE)
        score = analysis["score"].relative.score(mate_score=10000)  # Score in centipawns

        if score > 300:  # Winning
            print("\n🟢 Adaptive Mode: Playing Aggressive (Winning)")
            args.skill = 20
            args.nodestime = 10000

        elif score < -300:  # Losing
            print("\n🔴 Adaptive Mode: Playing Defensive (Losing)")
            args.skill = 15
            args.nodestime = 8000

        elif -100 < score < 100:  # Equal
            print("\n🟡 Adaptive Mode: Playing Classical (Equal Position)")
            args.skill = 18
            args.nodestime = 10000

        engine.configure({"Skill Level": args.skill, "nodestime": args.nodestime})

    analysis = engine.analyse(board, chess.engine.Limit(time=2), info=chess.engine.INFO_SCORE)
    mate_in = analysis["score"].relative.mate()
    if mate_in is not None:
        print(f"\n⚠️ CHECKMATE IN {mate_in} MOVES! ⚠️")

    # Get best move
    best_move = engine.play(board, chess.engine.Limit(time=3))
    best_move_algebraic = board.san(best_move.move)
    print(f"\n✅ Best move for you: {best_move_algebraic}")
    board.push(best_move.move)

print("\n🏁 Game Over!")
engine.quit() 
