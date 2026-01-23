import os
import random

REPO_OWNER = "sukantsondhi"
REPO_NAME = "sukantsondhi"

def load_game_state():
    """Load game state from file or return empty board."""
    try:
        with open("game_state.txt", "r") as f:
            board = list(f.read().strip())
            if len(board) != 9:
                return list("---------")
            return board
    except FileNotFoundError:
        return list("---------")

def save_game_state(board):
    """Save game state to file."""
    with open("game_state.txt", "w") as f:
        f.write("".join(board))

def check_winner(board):
    """Check if there's a winner. Returns 'X', 'O', 'draw', or None."""
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    
    for line in lines:
        if board[line[0]] == board[line[1]] == board[line[2]] != '-':
            return board[line[0]]
    
    if '-' not in board:
        return 'draw'
    
    return None

def get_computer_move(board):
    """Get computer's move using simple AI."""
    # Check if computer can win
    for i in range(9):
        if board[i] == '-':
            board[i] = 'O'
            if check_winner(board) == 'O':
                board[i] = '-'
                return i
            board[i] = '-'
    
    # Block player's winning move
    for i in range(9):
        if board[i] == '-':
            board[i] = 'X'
            if check_winner(board) == 'X':
                board[i] = '-'
                return i
            board[i] = '-'
    
    # Take center if available
    if board[4] == '-':
        return 4
    
    # Take a corner
    corners = [0, 2, 6, 8]
    random.shuffle(corners)
    for corner in corners:
        if board[corner] == '-':
            return corner
    
    # Take any available edge
    edges = [1, 3, 5, 7]
    random.shuffle(edges)
    for edge in edges:
        if board[edge] == '-':
            return edge
    
    return None

def generate_board_markdown(board, game_message=""):
    """Generate the markdown for the game board."""
    
    def cell(index):
        if board[index] == 'X':
            return "❌"
        elif board[index] == 'O':
            return "⭕"
        else:
            # Clickable cell - creates an issue
            return f"[▪️](https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new?title=tictactoe%7Cmove%7C{index}&body=Just+click+submit!)"
    
    winner = check_winner(board)
    if winner:
        # Game over - show non-clickable board
        def static_cell(index):
            if board[index] == 'X':
                return "❌"
            elif board[index] == 'O':
                return "⭕"
            else:
                return "▪️"
        
        if winner == 'X':
            game_message = "🎉 **You won!** Click 'New Game' to play again!"
        elif winner == 'O':
            game_message = "🤖 **Computer wins!** Click 'New Game' to play again!"
        else:
            game_message = "🤝 **It's a draw!** Click 'New Game' to play again!"
        
        board_md = f"""
|   |   |   |
|:-:|:-:|:-:|
| {static_cell(0)} | {static_cell(1)} | {static_cell(2)} |
| {static_cell(3)} | {static_cell(4)} | {static_cell(5)} |
| {static_cell(6)} | {static_cell(7)} | {static_cell(8)} |

{game_message}

[🔄 New Game](https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new?title=tictactoe%7Creset&body=Starting+a+new+game!)
"""
    else:
        if not game_message:
            game_message = "⬆️ **Click a cell, then submit the issue to play!**"
        
        board_md = f"""
|   |   |   |
|:-:|:-:|:-:|
| {cell(0)} | {cell(1)} | {cell(2)} |
| {cell(3)} | {cell(4)} | {cell(5)} |
| {cell(6)} | {cell(7)} | {cell(8)} |

{game_message}

[🔄 New Game](https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new?title=tictactoe%7Creset&body=Click+Submit+to+reset!)
"""
    
    return board_md

def update_readme(board, game_message=""):
    """Update the README with the current game state."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    board_md = generate_board_markdown(board, game_message)
    
    start_marker = "<!-- TICTACTOE:START -->"
    end_marker = "<!-- TICTACTOE:END -->"
    
    if start_marker in content and end_marker in content:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        new_content = before + start_marker + "\n" + board_md + "\n" + end_marker + after
    else:
        # Markers not found - this shouldn't happen if README is set up correctly
        new_content = content
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    issue_title = os.environ.get("ISSUE_TITLE", "")
    
    if not issue_title.startswith("tictactoe|"):
        return
    
    parts = issue_title.split("|")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "reset":
        # Reset the game
        board = list("---------")
        save_game_state(board)
        update_readme(board)
        return
    
    if action == "move" and len(parts) > 2:
        try:
            position = int(parts[2])
        except ValueError:
            return
        
        if position < 0 or position > 8:
            return
        
        board = load_game_state()
        
        # Check if game is already over
        if check_winner(board):
            return
        
        # Check if cell is empty
        if board[position] != '-':
            return
        
        # Player's move
        board[position] = 'X'
        
        # Check if player won
        if check_winner(board) == 'X':
            save_game_state(board)
            update_readme(board)
            return
        
        # Check for draw
        if check_winner(board) == 'draw':
            save_game_state(board)
            update_readme(board)
            return
        
        # Computer's move
        computer_move = get_computer_move(board)
        if computer_move is not None:
            board[computer_move] = 'O'
        
        save_game_state(board)
        update_readme(board)

if __name__ == "__main__":
    main()
