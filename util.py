import chess,os,random
import chess.pgn
import chess.engine
import heapq  # For sorting moves by evaluation
import time

def save_game_pgn(board, opponent_color):
    """
    Save the completed chess game in PGN format with a Unix timestamp.

    Args:
        board (chess.Board): The chess board containing the game history.
        opponent_color (str): 'w' if the opponent played as White, 'b' if Black.
    """
    # Create PGN game object
    game = chess.pgn.Game()
    game.headers["White"] = "Me" if opponent_color == 'b' else "Opponent"
    game.headers["Black"] = "Opponent" if opponent_color == 'b' else "Me"
    node = game

    # Add all moves from the board to the PGN game
    for move in board.move_stack:
        node = node.add_variation(move)

    # Ensure the games directory exists
    if not os.path.exists("games"):
        os.makedirs("games")

    # Generate filename using Unix timestamp
    unix_time = int(time.time())
    file_name = f"games/game_{unix_time}.pgn"

    # Save the game to the file
    with open(file_name, "w") as pgn_file:
        exporter = chess.pgn.FileExporter(pgn_file)
        game.accept(exporter)

    print(f"\n🏁 Game Over! Saved as '{file_name}'")

def make_blunder(board, engine, blunder_chance=0.1):
    """Force the engine to make a blunder with a probability."""
    if random.random() > blunder_chance:
        return None  # No blunder, return control to normal move

    legal_moves = list(board.legal_moves)
    move_evals = []

    # Analyze all legal moves and store their evaluations
    for move in legal_moves:
        board.push(move)
        analysis = engine.analyse(board, chess.engine.Limit(time=0.5), info=chess.engine.INFO_SCORE)
        score = analysis["score"].relative.score(mate_score=10000) or 0
        board.pop()
        move_evals.append((score, move))

    # Sort moves by evaluation (from best to worst)
    worst_moves = heapq.nsmallest(3, move_evals, key=lambda x: x[0])  # Get the 3 worst moves

    # Randomly pick from the worst 3 moves to add unpredictability
    chosen_blunder = random.choice(worst_moves)
    blunder_move = chosen_blunder[1]
    blunder_eval = chosen_blunder[0]

    # Display blunder details
    blunder_move_algebraic = board.san(blunder_move)
    print(f"\n🤡 Blundering move: {blunder_move_algebraic} (Eval: {blunder_eval} cp)\n")
    return blunder_move

def detect_tactics(board, color):
    tactics = {
        "pins": [],
        "skewers": [],
        "forks": [],
        "discovered_attacks": [],
        "discovered_checks": [],
        "double_checks": [],
        "x_ray_attacks": [],
        "trapped_pieces": [],
        "back_rank_mate_threats": [],
        "stalemate_traps": [],
        "smothered_mate": [],
        "deflections": [],
        "decoys": [],
        "overloading": [],
        "interference": [],
        "zwischenzug": [],
        "underpromotion_trap": []
    }

    # Only consider high-value pieces (knight, bishop, rook, queen, king)
    high_value_pieces = {chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING}

    for square in chess.SQUARES:
        piece = board.piece_at(square)

        if piece and piece.color == color and piece.piece_type in high_value_pieces:
            # PIN DETECTION
            if board.is_pinned(color, square):
                tactics["pins"].append(chess.square_name(square))

            # FORK DETECTION
            attackers = board.attackers(color, square)
            if len(attackers) > 1:
                tactics["forks"].append(chess.square_name(square))

            # OVERLOADING DETECTION
            attackers = list(board.attackers(not color, square))
            defenders = list(board.attackers(color, square))
            if len(attackers) > 0 and len(defenders) == 1:
                tactics["overloading"].append(chess.square_name(square))

            # INTERFERENCE DETECTION (Simplified)
            for move in board.legal_moves:
                if move.from_square == square:
                    temp_board = board.copy()
                    temp_board.push(move)
                    if board.is_attacked_by(not color, move.to_square) and not temp_board.is_attacked_by(not color, move.to_square):
                        tactics["interference"].append(chess.square_name(move.to_square))

            # DECOY DETECTION
            for move in board.legal_moves:
                if move.from_square == square:
                    temp_board = board.copy()
                    temp_board.push(move)
                    if temp_board.is_check():
                        tactics["decoys"].append(chess.square_name(move.to_square))

            # SMOTHERED MATE CHECK
            if piece.piece_type == chess.KNIGHT:
                for move in board.legal_moves:
                    if move.from_square == square:
                        temp_board = board.copy()
                        temp_board.push(move)
                        if temp_board.is_checkmate():
                            king_square = temp_board.king(not color)
                            if all(temp_board.piece_at(sq) and temp_board.piece_at(sq).color != color
                                   for sq in chess.SQUARES if chess.square_distance(king_square, sq) == 1):
                                tactics["smothered_mate"].append(chess.square_name(king_square))

            # ZWISCHENZUG (In-Between Moves)
            if piece.piece_type != chess.KING:
                for move in board.legal_moves:
                    temp_board = board.copy()
                    temp_board.push(move)
                    if temp_board.is_check() and not board.is_check():
                        tactics["zwischenzug"].append(chess.square_name(move.to_square))

            # UNDERPROMOTION TRAP (Check if promoting to a piece other than queen gives better result)
            if piece.piece_type == chess.PAWN:
                if (color == chess.WHITE and chess.square_rank(square) == 6) or (color == chess.BLACK and chess.square_rank(square) == 1):
                    tactics["underpromotion_trap"].append(chess.square_name(square))

    return tactics 

def detect_game_phase(board):
    """Detect the current phase of the game based on move count and remaining pieces."""
    total_moves = board.fullmove_number
    piece_count = len(board.piece_map())

    if total_moves <= 10:
        return "Opening"
    elif piece_count <= 10:
        return "Endgame"
    else:
        return "Middlegame"

def is_position_complex(board, engine):
    """Detect if the position is complex based on the evaluation spread of legal moves."""
    evaluations = []
    for move in board.legal_moves:
        board.push(move)
        analysis = engine.analyse(board, chess.engine.Limit(time=0.5), info=chess.engine.INFO_SCORE)
        score = analysis["score"].relative.score(mate_score=10000)
        if score is not None:
            evaluations.append(score)
        board.pop()

    if not evaluations:
        return False

    eval_range = max(evaluations) - min(evaluations)
    return eval_range > 150  # Complex if evaluation range is wide

def adjust_adaptive_mode(board, engine, args):
    """Enhanced adaptive logic that adjusts based on game phase, complexity, and evaluation."""
    phase = detect_game_phase(board)
    analysis = engine.analyse(board, chess.engine.Limit(time=1), info=chess.engine.INFO_SCORE)
    score = analysis["score"].relative.score(mate_score=10000)  

    complex_position = is_position_complex(board, engine)

    # Adjust based on game phase
    if phase == "Opening":
        print("\n🟦 Opening Phase: Playing safe and developing pieces.")
        args.skill = 15
        args.nodestime = 5000

    elif phase == "Middlegame":
        if score > 300:
            print("\n🟢 Middlegame: Playing aggressively (Winning)")
            args.skill = 20
            args.nodestime = 10000
        elif score < -300:
            print("\n🔴 Middlegame: Playing defensively (Losing)")
            args.skill = 15
            args.nodestime = 8000
        else:
            if complex_position:
                print("\n🟡 Middlegame: Cautious play (Complex Position)")
                args.skill = 16
                args.nodestime = 8000
            else:
                print("\n🟡 Middlegame: Balanced strategy (Equal Position)")
                args.skill = 18
                args.nodestime = 10000

    elif phase == "Endgame":
        print("\n⚪ Endgame: Precision-focused strategy")
        args.skill = 20
        args.nodestime = 12000

    # Apply updated settings to Stockfish
    engine.configure({
        "Skill Level": args.skill,
        "nodestime": args.nodestime
    })


# Ensure games directory exists
os.makedirs("games", exist_ok=True)

def save_game(board, filename):
    """Save the current game to a PGN file."""
    game = chess.pgn.Game().from_board(board)
    filepath = f"games/{filename}.pgn"
    with open(filepath, "w") as file:
        file.write(str(game))
    print(f"💾 Game saved as '{filepath}'")


def list_saved_games():
    """List available saved games in the 'games' directory."""
    files = [f for f in os.listdir("games") if f.endswith(".pgn")]
    return files


def load_game():
    """Load a game from saved PGN files with user selection."""
    games = list_saved_games()
    if not games:
        print("❌ No saved games found.")
        return None

    print("\n📂 Select a saved game to load:")
    for i, game_file in enumerate(games, 1):
        print(f"{i}. {game_file}")

    while True:
        try:
            choice = int(input("Enter the number of the game to load: "))
            if 1 <= choice <= len(games):
                selected_game = games[choice - 1]
                with open(f"games/{selected_game}", "r") as file:
                    game = chess.pgn.read_game(file)
                print(f"✅ Loaded game: {selected_game}")

                # Apply all moves from the loaded PGN to set the board state correctly
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)

                return board
            else:
                print("⚠️ Invalid selection. Try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def evaluate_position(engine, board):
    """Evaluate the board position using Stockfish."""
    info = engine.analyse(board, chess.engine.Limit(time=0.5))
    score = info["score"].white()  # Always get evaluation from White's perspective
    return score.score(mate_score=100000)  # If mate detected, return a very high score

def remove_game_statistics(board, last_move, stats):
    """
    Removes the impact of the last move from the game statistics.
    
    Args:
        board: The current board state.
        last_move: The move object to remove.
        stats: Dictionary tracking stats for White and Black.
    """
    # Determine color from the move based on who just played
    color = "Black" if board.turn == chess.WHITE else "White"

    # Check the last recorded result and decrement it
    if stats[color]["blunders"] > 0:
        stats[color]["blunders"] -= 1
    elif stats[color]["mistakes"] > 0:
        stats[color]["mistakes"] -= 1
    elif stats[color]["inaccuracies"] > 0:
        stats[color]["inaccuracies"] -= 1

def update_game_statistics(engine, board, move, stats):
    """
    Detect and update inaccuracies, mistakes, and blunders.
    
    Args:
        engine: Stockfish engine instance.
        board: Current chess board state.
        move: The move just played.
        stats: Dictionary tracking stats for White and Black.
    """
    player = "White" if board.turn == chess.BLACK else "Black"  # Board turn is after making the move

    # Evaluate position before the move
    board.pop()  # Undo move temporarily
    eval_before = evaluate_position(engine, board)
    board.push(move)  # Redo the move

    # Evaluate after the move
    eval_after = evaluate_position(engine, board)

    # Calculate the drop in centipawn score (negative drop indicates worsening position)
    score_diff = eval_before - eval_after

    # Detect type of error
    if score_diff >= 300:
        stats[player]['blunders'] += 1
    elif score_diff >= 100:
        stats[player]['mistakes'] += 1
    elif score_diff >= 50:
        stats[player]['inaccuracies'] += 1

def initialize_game_stats():
    """Initialize the stats for both players."""
    return {
        "White": {"blunders": 0, "mistakes": 0, "inaccuracies": 0},
        "Black": {"blunders": 0, "mistakes": 0, "inaccuracies": 0}
    }

def game_statistics_summary(board, stats, total_moves):
    """Display the game statistics for both players."""
    result = ""
    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        result = f"🏆 Result: {winner} wins by checkmate!"
    elif board.is_stalemate():
        result = "🤝 Result: Draw by stalemate!"
    elif board.is_insufficient_material():
        result = "🤝 Result: Draw due to insufficient material!"
    elif board.is_seventyfive_moves():
        result = "🤝 Result: Draw by seventy-five move rule!"
    elif board.is_fivefold_repetition():
        result = "🤝 Result: Draw by fivefold repetition!"
    else:
        result = "🏁 Game ended without a decisive result."

    summary = f"""
🏁 Game Summary:
----------------------------
🔢 Total Moves Played : {total_moves // 2}
----------------------------
🔍 White:
❌ Blunders           : {stats['White']['blunders']}
⚠️ Mistakes           : {stats['White']['mistakes']}
❓ Inaccuracies       : {stats['White']['inaccuracies']}
----------------------------
🔍 Black:
❌ Blunders           : {stats['Black']['blunders']}
⚠️ Mistakes           : {stats['Black']['mistakes']}
❓ Inaccuracies       : {stats['Black']['inaccuracies']}
----------------------------
{result}
    """
    return summary
