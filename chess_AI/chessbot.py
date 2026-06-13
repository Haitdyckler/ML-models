import copy
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple, Optional
import threading

class ChessBot:
    def __init__(self):
        self.board = self.init_board()
        self.current_turn = 'white'
        
        # Piece values for evaluation
        self.piece_values = {
            'pawn': 100,
            'knight': 320,
            'bishop': 330,
            'rook': 500,
            'queen': 900,
            'king': 20000
        }
        
        # Position bonus tables
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
    
    def init_board(self) -> List[List[Optional[dict]]]:
        """Initialize chess board with starting position"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Pawns
        for i in range(8):
            board[1][i] = {'type': 'pawn', 'color': 'black'}
            board[6][i] = {'type': 'pawn', 'color': 'white'}
        
        # Rooks
        board[0][0] = board[0][7] = {'type': 'rook', 'color': 'black'}
        board[7][0] = board[7][7] = {'type': 'rook', 'color': 'white'}
        
        # Knights
        board[0][1] = board[0][6] = {'type': 'knight', 'color': 'black'}
        board[7][1] = board[7][6] = {'type': 'knight', 'color': 'white'}
        
        # Bishops
        board[0][2] = board[0][5] = {'type': 'bishop', 'color': 'black'}
        board[7][2] = board[7][5] = {'type': 'bishop', 'color': 'white'}
        
        # Queens
        board[0][3] = {'type': 'queen', 'color': 'black'}
        board[7][3] = {'type': 'queen', 'color': 'white'}
        
        # Kings
        board[0][4] = {'type': 'king', 'color': 'black'}
        board[7][4] = {'type': 'king', 'color': 'white'}
        
        return board
    
    def get_legal_moves(self, row: int, col: int, board: List[List]) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece at given position"""
        piece = board[row][col]
        if not piece:
            return []
        
        moves = []
        piece_type = piece['type']
        color = piece['color']
        direction = -1 if color == 'white' else 1
        
        if piece_type == 'pawn':
            # Forward move
            if 0 <= row + direction < 8 and board[row + direction][col] is None:
                moves.append((row + direction, col))
                # Double move from starting position
                start_row = 6 if color == 'white' else 1
                if row == start_row and board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
            
            # Captures
            for dc in [-1, 1]:
                new_row, new_col = row + direction, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board[new_row][new_col] and board[new_row][new_col]['color'] != color:
                        moves.append((new_row, new_col))
        
        elif piece_type == 'knight':
            knight_moves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if not board[new_row][new_col] or board[new_row][new_col]['color'] != color:
                        moves.append((new_row, new_col))
        
        elif piece_type == 'bishop':
            for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self._get_sliding_moves(row, col, dr, dc, board, color))
        
        elif piece_type == 'rook':
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                moves.extend(self._get_sliding_moves(row, col, dr, dc, board, color))
        
        elif piece_type == 'queen':
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self._get_sliding_moves(row, col, dr, dc, board, color))
        
        elif piece_type == 'king':
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if not board[new_row][new_col] or board[new_row][new_col]['color'] != color:
                        moves.append((new_row, new_col))
        
        return moves
    
    def _get_sliding_moves(self, row: int, col: int, dr: int, dc: int, 
                          board: List[List], color: str) -> List[Tuple[int, int]]:
        """Get moves for sliding pieces (bishop, rook, queen)"""
        moves = []
        new_row, new_col = row + dr, col + dc
        
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            if board[new_row][new_col] is None:
                moves.append((new_row, new_col))
            elif board[new_row][new_col]['color'] != color:
                moves.append((new_row, new_col))
                break
            else:
                break
            new_row += dr
            new_col += dc
        
        return moves
    
    def is_king_in_check(self, board: List[List], color: str) -> bool:
        """Check if the king of given color is in check"""
        # Find king position
        king_pos = None
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c]['type'] == 'king' and board[r][c]['color'] == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c]['color'] == opponent_color:
                    moves = self.get_legal_moves(r, c, board)
                    if king_pos in moves:
                        return True
        
        return False
    
    def get_all_legal_moves(self, board: List[List], color: str) -> List[dict]:
        """Get all legal moves for a color that don't leave king in check"""
        moves = []
        
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c]['color'] == color:
                    piece_moves = self.get_legal_moves(r, c, board)
                    
                    for new_r, new_c in piece_moves:
                        # Simulate move
                        new_board = copy.deepcopy(board)
                        new_board[new_r][new_c] = new_board[r][c]
                        new_board[r][c] = None
                        
                        # Check if move leaves king in check
                        if not self.is_king_in_check(new_board, color):
                            moves.append({
                                'from': (r, c),
                                'to': (new_r, new_c),
                                'piece': board[r][c]['type']
                            })
        
        return moves
    
    def evaluate_board(self, board: List[List]) -> int:
        """Evaluate board position (positive = good for white, negative = good for black)"""
        score = 0
        
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    value = self.piece_values[piece['type']]
                    
                    # Add positional bonus
                    if piece['type'] == 'pawn':
                        pos_bonus = self.pawn_table[r][c] if piece['color'] == 'white' else self.pawn_table[7-r][c]
                        value += pos_bonus
                    elif piece['type'] == 'knight':
                        pos_bonus = self.knight_table[r][c] if piece['color'] == 'white' else self.knight_table[7-r][c]
                        value += pos_bonus
                    
                    # Add mobility bonus
                    mobility = len(self.get_legal_moves(r, c, board))
                    value += mobility * 10
                    
                    if piece['color'] == 'white':
                        score += value
                    else:
                        score -= value
        
        return score
    
    def minimax(self, board: List[List], depth: int, alpha: float, beta: float, 
                maximizing: bool) -> Tuple[int, Optional[dict]]:
        """Minimax algorithm with alpha-beta pruning"""
        color = 'white' if maximizing else 'black'
        moves = self.get_all_legal_moves(board, color)
        
        # Base case: depth 0 or no legal moves
        if depth == 0 or not moves:
            return self.evaluate_board(board), None
        
        best_move = None
        
        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                # Make move
                new_board = copy.deepcopy(board)
                new_board[move['to'][0]][move['to'][1]] = new_board[move['from'][0]][move['from'][1]]
                new_board[move['from'][0]][move['from'][1]] = None
                
                # Recursive call
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                # Make move
                new_board = copy.deepcopy(board)
                new_board[move['to'][0]][move['to'][1]] = new_board[move['from'][0]][move['from'][1]]
                new_board[move['from'][0]][move['from'][1]] = None
                
                # Recursive call
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval, best_move
    
    def get_best_move(self, depth: int = 4) -> Optional[dict]:
        """Get best move for current player using minimax"""
        maximizing = self.current_turn == 'white'
        _, best_move = self.minimax(self.board, depth, float('-inf'), float('inf'), maximizing)
        return best_move
    
    def make_move(self, move: dict) -> bool:
        """Make a move on the board"""
        if not move:
            return False
        
        from_r, from_c = move['from']
        to_r, to_c = move['to']
        
        self.board[to_r][to_c] = self.board[from_r][from_c]
        self.board[from_r][from_c] = None
        
        # Switch turn
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        return True
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if game is over and return winner"""
        white_moves = self.get_all_legal_moves(self.board, 'white')
        black_moves = self.get_all_legal_moves(self.board, 'black')
        
        if not white_moves:
            if self.is_king_in_check(self.board, 'white'):
                return True, 'black'
            return True, 'draw'
        
        if not black_moves:
            if self.is_king_in_check(self.board, 'black'):
                return True, 'white'
            return True, 'draw'
        
        return False, None


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Bot - Play vs AI")
        self.bot = ChessBot()
        self.selected_square = None
        self.valid_moves = []
        self.square_size = 70
        self.player_color = 'white'
        self.ai_thinking = False
        
        # Load piece images
        self.piece_images = {}
        self.load_piece_images()
        
        self.setup_ui()
        self.draw_board()
    
    def load_piece_images(self):
        """Load all piece images from the images folder"""
        try:
            from PIL import Image, ImageTk
            
            # Mapping of piece types to image filenames
            # First letter: w = white, b = black
            # Second letter: P = pawn, R = rook, N = knight, B = bishop, Q = queen, K = king
            piece_files = {
                ('white', 'pawn'): 'wP.png',
                ('white', 'rook'): 'wR.png',
                ('white', 'knight'): 'wN.png',
                ('white', 'bishop'): 'wB.png',
                ('white', 'queen'): 'wQ.png',
                ('white', 'king'): 'wK.png',
                ('black', 'pawn'): 'bP.png',
                ('black', 'rook'): 'bR.png',
                ('black', 'knight'): 'bN.png',
                ('black', 'bishop'): 'bB.png',
                ('black', 'queen'): 'bQ.png',
                ('black', 'king'): 'bK.png',
            }
            
            for (color, piece_type), filename in piece_files.items():
                try:
                    # Load image from images folder
                    img_path = f'images/{filename}'
                    img = Image.open(img_path)
                    
                    # Resize to fit square (leave some padding)
                    img = img.resize((int(self.square_size * 0.8), int(self.square_size * 0.8)), Image.LANCZOS)
                    
                    # Convert to PhotoImage for tkinter
                    self.piece_images[(color, piece_type)] = ImageTk.PhotoImage(img)
                except FileNotFoundError:
                    print(f"Warning: Could not find image file: {img_path}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            
            if not self.piece_images:
                raise Exception("No piece images loaded")
                
        except ImportError:
            print("PIL (Pillow) not found. Please install it with: pip install Pillow")
            print("Falling back to Unicode symbols...")
            # Fallback to unicode symbols
            self.piece_images = None
            self.piece_symbols = {
                'white': {
                    'pawn': '♙', 'rook': '♖', 'knight': '♘',
                    'bishop': '♗', 'queen': '♕', 'king': '♔'
                },
                'black': {
                    'pawn': '♟', 'rook': '♜', 'knight': '♞',
                    'bishop': '♝', 'queen': '♛', 'king': '♚'
                }
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            print("Falling back to Unicode symbols...")
            self.piece_images = None
            self.piece_symbols = {
                'white': {
                    'pawn': '♙', 'rook': '♖', 'knight': '♘',
                    'bishop': '♗', 'queen': '♕', 'king': '♔'
                },
                'black': {
                    'pawn': '♟', 'rook': '♜', 'knight': '♞',
                    'bishop': '♝', 'queen': '♛', 'king': '♚'
                }
            }
    
    def setup_ui(self):
        """Setup the user interface"""
        # Top frame for info and controls
        top_frame = tk.Frame(self.root, bg='#2c3e50')
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(
            top_frame, 
            text="Your Turn (White)", 
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Difficulty selection
        difficulty_frame = tk.Frame(top_frame, bg='#2c3e50')
        difficulty_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(difficulty_frame, text="AI Difficulty:", bg='#2c3e50', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.difficulty_var = tk.StringVar(value="Medium")
        difficulties = ["Easy (Depth 2)", "Medium (Depth 3)", "Hard (Depth 4)"]
        self.difficulty_menu = tk.OptionMenu(difficulty_frame, self.difficulty_var, *difficulties)
        self.difficulty_menu.config(bg='#34495e', fg='white', font=('Arial', 10))
        self.difficulty_menu.pack(side=tk.LEFT, padx=5)
        
        # Color selection
        color_frame = tk.Frame(top_frame, bg='#2c3e50')
        color_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(color_frame, text="Play as:", bg='#2c3e50', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.color_var = tk.StringVar(value="White")
        colors = ["White", "Black"]
        self.color_menu = tk.OptionMenu(color_frame, self.color_var, *colors, command=self.change_color)
        self.color_menu.config(bg='#34495e', fg='white', font=('Arial', 10))
        self.color_menu.pack(side=tk.LEFT, padx=5)
        
        # New game button
        new_game_btn = tk.Button(
            top_frame,
            text="New Game",
            command=self.new_game,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5,
            relief=tk.RAISED,
            cursor='hand2'
        )
        new_game_btn.pack(side=tk.RIGHT, padx=10)
        
        # Canvas for chess board
        self.canvas = tk.Canvas(
            self.root,
            width=self.square_size * 8,
            height=self.square_size * 8,
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind('<Button-1>', self.on_square_click)
    
    def get_ai_depth(self):
        """Get AI depth based on difficulty selection"""
        difficulty = self.difficulty_var.get()
        if "Easy" in difficulty:
            return 2
        elif "Medium" in difficulty:
            return 3
        else:
            return 4
    
    def draw_board(self):
        """Draw the chess board and pieces"""
        self.canvas.delete('all')
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                # Flip board if player is black
                display_row = row if self.player_color == 'white' else 7 - row
                display_col = col if self.player_color == 'white' else 7 - col
                
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Determine square color
                is_light = (display_row + display_col) % 2 == 0
                color = '#f0d9b5' if is_light else '#b58863'
                
                # Highlight selected square
                if self.selected_square == (display_row, display_col):
                    color = '#7fc97f'
                
                # Highlight valid moves
                elif (display_row, display_col) in self.valid_moves:
                    color = '#bedb7f'
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
                
                # Draw coordinate labels
                if col == 0:
                    label_num = str(8 - display_row) if self.player_color == 'white' else str(display_row + 1)
                    self.canvas.create_text(
                        x1 + 5, y1 + 5,
                        text=label_num,
                        font=('Arial', 10, 'bold'),
                        fill='#769656' if is_light else '#eeeed2'
                    )
                if row == 7:
                    label_letter = chr(97 + display_col) if self.player_color == 'white' else chr(104 - display_col)
                    self.canvas.create_text(
                        x2 - 5, y2 - 5,
                        text=label_letter,
                        font=('Arial', 10, 'bold'),
                        fill='#769656' if not is_light else '#eeeed2'
                    )
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                # Flip board if player is black
                display_row = row if self.player_color == 'white' else 7 - row
                display_col = col if self.player_color == 'white' else 7 - col
                
                piece = self.bot.board[display_row][display_col]
                if piece:
                    x = col * self.square_size + self.square_size // 2
                    y = row * self.square_size + self.square_size // 2
                    
                    # Use images if available, otherwise use unicode symbols
                    if self.piece_images:
                        img = self.piece_images.get((piece['color'], piece['type']))
                        if img:
                            self.canvas.create_image(x, y, image=img)
                    else:
                        symbol = self.piece_symbols[piece['color']][piece['type']]
                        self.canvas.create_text(
                            x, y,
                            text=symbol,
                            font=('Arial', 48),
                            fill='white' if piece['color'] == 'white' else 'black'
                        )
    
    def on_square_click(self, event):
        """Handle square click events"""
        if self.ai_thinking or self.bot.current_turn != self.player_color:
            return
        
        col = event.x // self.square_size
        row = event.y // self.square_size
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        # Convert display coordinates to board coordinates
        if self.player_color == 'black':
            row = 7 - row
            col = 7 - col
        
        # If a square is already selected
        if self.selected_square:
            # Try to make a move
            if (row, col) in self.valid_moves:
                move = {
                    'from': self.selected_square,
                    'to': (row, col),
                    'piece': self.bot.board[self.selected_square[0]][self.selected_square[1]]['type']
                }
                self.make_player_move(move)
            # Select a different piece
            elif self.bot.board[row][col] and self.bot.board[row][col]['color'] == self.player_color:
                self.select_square(row, col)
            # Deselect
            else:
                self.selected_square = None
                self.valid_moves = []
                self.draw_board()
        else:
            # Select a square if it has a player piece
            if self.bot.board[row][col] and self.bot.board[row][col]['color'] == self.player_color:
                self.select_square(row, col)
    
    def select_square(self, row, col):
        """Select a square and highlight valid moves"""
        self.selected_square = (row, col)
        
        # Get valid moves for this piece
        all_moves = self.bot.get_legal_moves(row, col, self.bot.board)
        
        # Filter out moves that leave king in check
        self.valid_moves = []
        for move_row, move_col in all_moves:
            test_board = copy.deepcopy(self.bot.board)
            test_board[move_row][move_col] = test_board[row][col]
            test_board[row][col] = None
            
            if not self.bot.is_king_in_check(test_board, self.player_color):
                self.valid_moves.append((move_row, move_col))
        
        self.draw_board()
    
    def make_player_move(self, move):
        """Make a player move and trigger AI response"""
        self.bot.make_move(move)
        self.selected_square = None
        self.valid_moves = []
        self.draw_board()
        
        # Check if game is over
        game_over, winner = self.bot.is_game_over()
        if game_over:
            self.handle_game_over(winner)
            return
        
        # AI's turn
        self.status_label.config(text="AI is thinking...")
        self.ai_thinking = True
        self.root.update()
        
        # Run AI move in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.make_ai_move)
        thread.start()
    
    def make_ai_move(self):
        """Make AI move (runs in separate thread)"""
        depth = self.get_ai_depth()
        best_move = self.bot.get_best_move(depth=depth)
        
        if best_move:
            self.bot.make_move(best_move)
        
        # Update UI in main thread
        self.root.after(0, self.after_ai_move)
    
    def after_ai_move(self):
        """Called after AI makes a move"""
        self.ai_thinking = False
        self.draw_board()
        
        # Check if game is over
        game_over, winner = self.bot.is_game_over()
        if game_over:
            self.handle_game_over(winner)
        else:
            color_name = "White" if self.player_color == 'white' else "Black"
            self.status_label.config(text=f"Your Turn ({color_name})")
    
    def handle_game_over(self, winner):
        """Handle game over"""
        if winner == 'draw':
            message = "Game Over - Draw (Stalemate)"
            self.status_label.config(text="Draw!")
        elif winner == self.player_color:
            message = "Congratulations! You won!"
            self.status_label.config(text="You Win!")
        else:
            message = "Game Over - AI wins!"
            self.status_label.config(text="AI Wins!")
        
        messagebox.showinfo("Game Over", message)
    
    def new_game(self):
        """Start a new game"""
        self.bot = ChessBot()
        self.selected_square = None
        self.valid_moves = []
        self.ai_thinking = False
        
        # Update player color based on selection
        self.player_color = self.color_var.get().lower()
        
        # Update status
        if self.player_color == 'white':
            self.status_label.config(text="Your Turn (White)")
        else:
            self.status_label.config(text="Your Turn (Black)")
        
        self.draw_board()
        
        # If player chose black, AI makes first move
        if self.player_color == 'black':
            self.status_label.config(text="AI is thinking...")
            self.ai_thinking = True
            self.root.update()
            thread = threading.Thread(target=self.make_ai_move)
            thread.start()
    
    def change_color(self, selection):
        """Handle color change during game"""
        new_color = selection.lower()
        if new_color != self.player_color and not self.ai_thinking:
            # Ask user to start new game with new color
            if messagebox.askyesno("Change Color", "Start a new game to play as " + selection + "?"):
                self.new_game()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#2c3e50')
    root.resizable(False, False)
    app = ChessGUI(root)
    root.mainloop()