import chess,os
import chess.pgn

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
