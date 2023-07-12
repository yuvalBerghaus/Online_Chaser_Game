import sys
import socket
import selectors
import types
import random

sel = selectors.DefaultSelector()

class Game:
    def __init__(self):
        self.players = {}
        self.chaser_stage = 0
        self.questions = {
            'A': [],
            'B': [],
            'C': [],
            'C+': []
        }
        
    def add_player(self, player_id, connection):
        self.players[player_id] = {
            'stage': 'A',
            'money': 0,
            'answered_count' : 0,
            'lifeline': True,
            'connection': connection,
            'correct_answers' : 0
        }
    
    def remove_player(self, player_id):
        del self.players[player_id]
    
    def generate_questions(self):
        level_a_questions = [
            {
                'question': 'Who painted the Mona Lisa?',
                'options': ['Leonardo da Vinci', 'Vincent van Gogh', 'Pablo Picasso', 'Michelangelo'],
                'correct': 'A'
            },
            {
                'question': 'Which planet is known as the "Red Planet"?',
                'options': ['Mars', 'Jupiter', 'Venus', 'Saturn'],
                'correct': 'A'
            },
            {
                'question' : 'Who is the author of the famous novel "To Kill a Mockingbird"?',
                'options': ['J.D. Salinger', 'Harper Lee', 'F. Scott Fitzgerald', 'Ernest Hemingway'],
                'correct': 'B'
            }
        ]
        self.questions['A'] = random.sample(level_a_questions, 3)

        
        # Level B questions
        level_b_questions = [
            {
                'question': 'What is the capital city of Australia?',
                'options': ['Sydney', 'Canberra', 'Melbourne', 'Perth'],
                'correct': 'B'
            },
            {
                'question': 'Which country is famous for the Taj Mahal?',
                'options': ['India', 'China', 'Egypt', 'Italy'],
                'correct': 'A'
            }
        ]
        self.questions['B'] = random.sample(level_b_questions, 2)
        
        # Level C questions
        level_c_questions = [
            {
                'question': 'Who wrote the play "Romeo and Juliet"?',
                'options': ['William Shakespeare', 'Charles Dickens', 'Jane Austen', 'F. Scott Fitzgerald'],
                'correct': 'A'
            },
            {
                'question': 'Which animal is the largest living mammal?',
                'options': ['Blue whale', 'African elephant', 'Giraffe', 'Hippopotamus'],
                'correct': 'A'
            }
        ]
        self.questions['C'] = random.sample(level_c_questions, 2)
        
        # Level C+ questions
        level_c_plus_questions = [
            {
                'question': 'What is the chemical symbol for gold?',
                'options': ['Au', 'Ag', 'Fe', 'Hg'],
                'correct': 'A'
            },
            {
                'question': 'Who discovered penicillin?',
                'options': ['Alexander Fleming', 'Marie Curie', 'Albert Einstein', 'Isaac Newton'],
                'correct': 'A'
            }
        ]
        self.questions['C+'] = random.sample(level_c_plus_questions, 2)
    #this function handles the answer and updates a new question!
    def process_answer(self, player_id, answer):
        player = self.players[player_id]
        current_stage = player['stage']
        current_money = player['money']
        correct_answer = self.get_current_question(player_id)['correct']
        answer = answer.upper()
        if answer == correct_answer:
            # Correct answer TODO fix here counter phases logic change - counter = amount of answered questions
            if current_stage == 'A':
                # Level A
                if player['money'] == 0:
                    player['money'] = 5000
                else:
                    player['money'] *= 2
            elif current_stage == 'B':
                # Level B
                player['money'] = current_money * 2
            elif current_stage == 'C':
                # Level C
                player['stage'] = 'C+'
            # Handle other stages
            player['correct_answers'] += 1
        
        else:
            # Incorrect answer
            if current_stage == 'A':
                # Level A
                player['money'] = 0
                player['stage'] = 'A'
            elif current_stage == 'B':
                # Level B
                player['money'] = current_money // 2
        # Handle other stages TODO
        player['answered_count'] += 1
        print('answered_count = ',player['answered_count'] )
        if player['answered_count'] == 3:
            if player['correct_answers'] > 0:
                self.move_player_forward(player_id)
            else:
                player['stage'] = 'A'


        # Update board for player
        self.send_board_info(player_id)
    #TODO - fix move_player_forward only after 3 phases ended
    def move_player_forward(self, player_id):
        player = self.players[player_id]
        current_stage = player['stage']
        current_position = self.get_stage_position(current_stage) # TODO - finished stage A!!!!
        next_stage = self.get_next_stage(current_stage)
        next_position = self.get_stage_position(next_stage)
        
        # Update player's stage and position
        player['stage'] = next_stage
        
        # Move player towards bank
        if next_position > current_position:
            self.chaser_stage = max(self.chaser_stage, next_position)
        
        # Move chaser towards bank
        self.move_chaser()
    
    def move_chaser(self):
        chaser_position = self.get_stage_position('chaser')
        self.chaser_stage = min(self.chaser_stage + 1, chaser_position)
    
    def send_board_info(self, player_id):
        player = self.players[player_id]
        current_stage = player['stage']
        current_money = player['money']
        lifeline = player['lifeline']
        
        # Prepare board info message
        board_info = f"Money: {current_money} | Stage: {current_stage} | Chaser: {self.chaser_stage} | Lifeline: {lifeline}"
        
        # Send board info to the player
        conn = player['connection']
        conn.sendall(board_info.encode())
    
    def get_stage_position(self, stage, answered_count):
        pass
        # if stage == 'A':
        #     return 1
        # elif stage == 'B':
        #     return 4
        # elif stage == 'C':
        #     return 5
        # elif stage == 'C+':
        #     return 6
        # elif stage == 'chaser':
        #     return 3
        # elif stage == 'bank':
        #     return 7

    
    def get_next_stage(self, current_stage):
        if current_stage == 'A':
            return 'B'
        elif current_stage == 'B':
            return 'C'
        elif current_stage == 'C':
            return 'C+'
        # Handle other stages
    #TODO - fix here! need to change the question to the next one
    def get_current_question(self, player_id):
        player = self.players[player_id]
        current_stage = player['stage']
        # current_question_index = self.get_stage_position(current_stage, player['answered_count']) - 1
        current_question_index = player['answered_count']
        if len(self.questions[current_stage]) > current_question_index:
            return self.questions[current_stage][current_question_index]
        else:
            return None

def accept_wrapper(sock, game):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    player_id = addr[1]  # Assuming unique port numbers as player IDs
    game.add_player(player_id, conn)
    send_instructions(conn)
    # game.generate_questions()
    # send_question(conn, game.get_current_question(player_id))
    
def send_instructions(conn):
    instructions = "Welcome to The Chase game!\n"
    instructions += "Answer the questions correctly to win money!\n"
    instructions += "Enter your answer as a single letter (A, B, C, or D).\n"
    instructions += "Get ready to play!"
    conn.sendall(instructions.encode())

def send_question(conn, question):
    if question is None:
        send_game_summary(conn)
    else:
        question_text = question['question']
        options = question['options']
        random.shuffle(options)
        question_text += "\n"
        for i, option in enumerate(options):
            question_text += f"{chr(ord('A')+i)}) {option}\n"
        conn.sendall(question_text.encode())


def service_connection(key, mask, game):
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            message = recv_data.decode().strip()
            player_id = data.addr[1]
            
            if player_id in game.players:
                if message == "yes":
                    print(message)
                    handle_initial_response(sock, game, player_id, message)
                elif game.players[player_id]['stage'] == 'C+':
                    handle_game_over_response(sock, game, player_id, message)
                elif game.players[player_id]['stage'] == 'C':
                    handle_question_response(sock, game, player_id, message)
                    #TODO - put all phases
                else:
                    handle_question_response(sock, game, player_id, message)
            
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            player_id = data.addr[1]
            game.remove_player(player_id)
    
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

def handle_initial_response(sock, game, player_id, response):
    if response.lower() == 'yes':
        # Player wants to play, generate questions and send Level A question
        game.generate_questions()
        send_question(sock, game.get_current_question(player_id))
    else:
        # Player does not want to play, end the connection
        sock.sendall("Thank you for playing!".encode())
        sel.unregister(sock)
        sock.close()
        game.remove_player(player_id)

def handle_question_response(sock, game, player_id, response):

    current_stage = game.players[player_id]['stage']
    current_question = game.get_current_question(player_id)
    if response.lower() == current_question['correct'].lower():
        sock.sendall("Correct answer!\n".encode())
    game.process_answer(player_id, response.lower())
    next_question = game.get_current_question(player_id)
    if next_question:
        send_question(sock, next_question)
    else:
        print("GAME OVER")
    #     sock.sendall("Correct answer!\n".encode())
    #     game.process_answer(player_id, response.lower())
    #     next_question = game.get_current_question(player_id)
    #     if next_question:
    #         send_question(sock, next_question)
    #     else:
    #         # Player has reached the bank, game is over
    #         send_game_summary(sock)
    #         sel.unregister(sock)
    #         sock.close()
    #         game.remove_player(player_id)
    # else:
    #     sock.sendall("Incorrect answer!\n".encode())
    #     send_question(sock, current_question)

def send_game_summary(sock):
    summary = "Game over!\n"
    summary += "Thank you for playing!"
    sock.sendall(summary.encode())

# Server setup
host, port = "127.0.0.1", 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

game = Game()

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj, game)
            else:
                service_connection(key, mask, game)

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
