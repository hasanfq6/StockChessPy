import chess

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
