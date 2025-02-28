import cloudscraper
import chess
import chess.engine

USERNAME = ""  # Your Chess.com username
ENGINE_PATH = "/data/data/com.termux/files/usr/bin/stockfish"

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_games(username):
    scraper = cloudscraper.create_scraper()
    url = f"https://api.chess.com/pub/player/{username}/games"
    response = scraper.get(url)

    if response.status_code != 200:
        print(RED + "Failed to fetch games." + RESET)
        return []

    return response.json().get("games", [])

def get_best_move(fen):
    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(time=2))
    return board.san(result.move)

# Fetch games
# Fetch games
games = get_games(USERNAME)
if not games:
    print(RED + "No ongoing games found." + RESET)
    exit()

moves_to_make = []  # Store all games where it's your turn

for game in games:
    is_black = game["black"].endswith(USERNAME)
    turn = (game["turn"] == "black" and is_black) or (game["turn"] == "white" and not is_black)

    if turn:
        opponent_name = game["white"].split("/")[-1] if is_black else game["black"].split("/")[-1]
        fen = game["fen"]
        best_move = get_best_move(fen)
        
        moves_to_make.append((opponent_name, fen, best_move))

# Display all moves instead of exiting early
if moves_to_make:
    print(f"\n{BOLD}{CYAN}Your Moves:{RESET}")
    for i, (opponent_name, fen, best_move) in enumerate(moves_to_make, 1):
        print(f"{BOLD}{i}. Opponent: {CYAN}{opponent_name}{RESET}")
        print(f"   FEN: {fen}")
        print(f"   {BOLD}Best Move: {GREEN}{best_move}{RESET}\n")
else:
    print(CYAN + "\nNo games where it's your turn found. Here are all ongoing games:" + RESET)
    for i, game in enumerate(games, 1):
        is_black = game["black"].endswith(USERNAME)
        opponent_name = game["white"].split("/")[-1] if is_black else game["black"].split("/")[-1]
        turn = (game["turn"] == "black" and is_black) or (game["turn"] == "white" and not is_black)
        print(f"{BOLD}{i}. {CYAN}{opponent_name}{RESET} (Your turn: {GREEN if turn else RED}{turn}{RESET})")

    print("\n" + RED + "No moves to make. Wait for your opponent." + RESET)
