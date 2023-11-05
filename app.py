from flask import *
from flask_wtf import FlaskForm
from sql import add_user, is_username_taken, check_user, get_by_id
from wtforms import StringField, PasswordField, SubmitField, FileField
from flask_wtf.file import FileSize
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
from flask_debugtoolbar import DebugToolbarExtension
import logging
import time

app = Flask(__name__)


#setting up thr Toolbar in debug mode
app.debug = True
app.secret_key = 'upasana12345'

toolbar = DebugToolbarExtension(app)

#logger function
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('performance_logger')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators= [DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                     EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(form, field):
        if is_username_taken(field.data):
            print("error")
            raise ValidationError('Username already taken')

class loginForm(FlaskForm):
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

class tweetCreation(FlaskForm):
    tweet = StringField('tweet', validators=[DataRequired()])
    media = FileField('image',validators=[FileSize(max_size=16777216, min_size=0 )] )
    submit = SubmitField(' Post ')

class User(UserMixin):
    def __init__(self, id, username, email, password):
         self.id = id
         self.username = username
         self.email = email
         self.password = password
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id   

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    data = get_by_id(user_id)
    return User(data[0], data[1], data[2], data[3])

class Game:
    win_cases = [[[0,0],[0,1],[0,2]],[[1,0],[1,1],[1,2]],[[2,0],[2,1],[2,2]],  # horizontal lines
             [[0,0],[1,0],[2,0]], [[0,1],[1,1],[2,1]],                     # diagonals
             [[0,2],[1,2],[2,2]], [[0,0],[1,1],[2,2]], [[0,2],[1,1],[2,0]]] #vertical
    
    corners = [[0,0],[2,0], [0,2], [2,2]]
    edgeVertical = [[1,0],[1,2]]
    edgeHorizontal1 = [[0,1]] #on the top
    edgeHorizontal2 = [[2,1]]
    diagonal = [[1,1]]
    previous_moves= []
    ai_moves = []
    Player2_moves = []

    def __init__(self, Player1, Player2, environment):
        self.player1 = Player1
        #if player2 exists it will be 1 else 0. same for the environment
        self.Player2 = Player2
        self.environment = environment
        # splace because neither of the player has taken this position
        self.board = [['','',''], 
                      ['','',''], 
                      ['','','']]
        self.previous_move = None

        self.movenumber = 0
        
    def algorithm(self):
        if self.movenumber == 0:
            if self.previous_move in Game.corners:
                return [1,1]
            if self.previous_move in Game.edgeVertical:
                return [self.previous_move[0]+1, self.previous_move[1]]
            if self.previous_move in Game.edgeHorizontal1:
                return [self.previous_move[0]+ 2, self.previous_move[1]]
            if self.previous_move in Game.edgeHorizontal2:
                return [self.previous_move[0], self.previous_move[1] + 1]
            if self.previous_move in Game.diagonal:
                return [2,2 ]
        else:
            win_case = None
            block_case = None
            win_build = None

            for i in Game.win_cases:
           
                value_win = [value for value in i if value not in Game.ai_moves] #it gives us a odd value out
                value_block = [value for value in i if value not in Game.previous_moves] 
                if len(value_win) == 1 and self.board[value_win[0][0]][value_win[0][1]] == '':
                    
                    win_case =  value_win[0]
                if len(value_block) == 1 and self.board[value_block[0][0]][value_block[0][1]] == '':
                  
                    block_case = value_block[0]
                if len(value_win) == 2:
                    if value_win[0] in Game.diagonal and self.board[value_win[0][0]][value_win[0][1]] == '' :
                        win_build =  value_win[0]
                    elif self.board[value_win[1][0]][value_win[1][1]] == '':
                        win_build = value_win[1]
                else:
                    #return a random empty cell
                    empty_cells = [[i, j] for i in range(3) for j in range(3) if self.board[i][j] == '']
                    random_choice =  random.choice(empty_cells) if empty_cells else None

            if win_case:
                print('win case')
                return win_case
            if block_case:
                print('block case')
                return block_case
            if win_build:
                print('win build')
                return win_build
            else:
                return random_choice

        
    def reset(self):
        Game.ai_moves = []
        Game.previous_moves = []
        Game.Player2_moves = []
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.previous_move = None
        self.movenumber = 0

    def update_board(self, move, player):
        #name the empty cell with the player that occupied it
       
        self.board[move[0]][move[1]] = player
        self.previous_move = move
    

    def player1Move(self, move):
        Game.previous_moves.append(move)
        self.update_board(move, self.player1)

        if self.environment == 1:
            return self.aiMove()

    def Player2Move(self, move):
        self.update_board(move, self.Player2)
    def empty_cell(self):
        return [[i, j] for i in range(3) for j in range(3) if self.board[i][j] == '']

    def aiMove(self):
        move = self.algorithm()
        if move is None:
            return self.won()
        Game.ai_moves.append(move)
        self.movenumber +=1
        self.update_board(move, self.environment)
        return move
        
    def won(self):
        for i in Game.win_cases: 
            player1 = 0
            player2 = 0
            ai = 0
            for j in i:
                if self.board[j[0]][j[1]] == self.player1:
                    player1 += 1
                    if player1 == 3:
                        return ['Player 1', i]
                if self.board[j[0]][j[1]] == self.Player2:
                    player2 += 1
                    if player2 == 3:
                        return ['Player 2', i]
                if j in self.ai_moves:  # Check if the current cell is in ai_moves
                    ai += 1 
                    if ai == 3:
                        return  ['Environment', i]

        # Check for a draw condition if no winning condition is met
        if not any('' in row for row in self.board):
            self.reset()
            return 'Draw'
        


@app.route('/', methods= ['GET','POST'])
def homepage():
    return render_template('homepage.html')

@app.route('/restart-server', methods=['GET'])
def restart_game():
    if tictactoe is not None:
        tictactoe.reset()
    else:
        pass
    return "Game restarted successfully"

        

@app.route('/register', methods= ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        add_user(username, email, password)
        return redirect('/login')
    return render_template('register.html', form= form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = loginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(email)
        user = check_user(email)
        Us = load_user(user[0]) 
        print(Us.email, Us.password)
        if email == Us.email and password == Us.password:
            login_user(Us)
            flash("successfully logged in")
            return redirect(url_for('website'))
        else:
            flash('Login Failed. Invalid Credentials')
    return render_template('login.html', form=form)

  
@app.route('/aimatch', methods=['POST'])
def aimatch():
    #Performance Debug Tool 
    #Calculating Performace with time 

    start_time = time.time()


    global tictactoe  # Access the global tictactoe object
    if tictactoe is None:
        tictactoe = Game('X', 0, 1)
    row_col = str(request.form.get('row_col'))
   
    row = int(row_col[0])
    column = int(row_col[1])
 
    if [row, column] in tictactoe.ai_moves or [row, column] in tictactoe.previous_moves:
        #end time 
        end_time = time.time()
        elapsed_time = start_time - end_time
        #Log Performance Tracker
        logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
        return jsonify({'status': 'error', 'message': 'Invalid move'})
    else:
        next_move = tictactoe.player1Move([row, column])
        outcome = tictactoe.won()
        print(outcome)
        if outcome == 'Draw' or next_move == 'Draw':
            tictactoe.reset()
            end_time = time.time()
            elapsed_time = start_time - end_time
            logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
            return jsonify({'status': 'draw', 'message': 'Game is a draw', 'next_move': next_move})
        
        elif outcome:
            tictactoe.reset()
            end_time = time.time()
            elapsed_time = start_time - end_time
            logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
            return jsonify({'status': 'win', 'message': f'Player {outcome[0]} wins', 'next_move': next_move})
        end_time = time.time()
        elapsed_time = start_time - end_time
        return jsonify({'status': 'next_move', 'message': 'Next move', 'next_move': next_move})

@app.route('/inplayerVsplayer', methods =['POST'])
@login_required
def In_PlayerVsPlayer():
    global tictactoe
    #game has been initialized
    if tictactoe is None:
        tictactoe = Game('X', 1, 0)
    return 'INITIALIZED PVP'

@app.route('/player1', methods = ['POST'])
@login_required
def Player1_moves():
    print('Player 1')
    start_time = time.time()
    global tictactoe  # Access the global tictactoe object
    if tictactoe is None:
        tictactoe = Game('X', 1,0)
    row_col = str(request.form.get('row_col'))
    row = int(row_col[0])
    column = int(row_col[1])
    if [row, column] in tictactoe.Player2_moves or [row, column] in tictactoe.previous_moves:
        end_time = time.time()
        elapsed_time = start_time - end_time
        logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
        return jsonify({'status': 'error', 'message': 'Invalid move'})
    else:
        tictactoe.player1Move([row, column])
        outcome = tictactoe.won()
        print(outcome)
        if outcome == 'Draw':
            tictactoe.reset()
            end_time = time.time()
            elapsed_time = start_time - end_time
            logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
            return jsonify({'status': 'draw', 'message': 'Game is a draw', 'next_move': outcome})
            
        elif outcome:
            tictactoe.reset()
            end_time = time.time()
            elapsed_time = start_time - end_time
            logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
            return jsonify({'status': 'win', 'message': '{outcome[0]} has won', 'next_move': outcome})
        end_time = time.time()
        elapsed_time = start_time - end_time
        logger.info(f"Route : / -Time taken : {elapsed_time : .6f} seconds")
        return jsonify({'status': 'next_move', 'message': 'Next move', 'next_move':'Player2'})
        #no return just save it into the server for the moment
            
@app.route('/player2', methods = ['POST'])
@login_required
def Player2_moves():
    row_col = str(request.form.get('row_col'))
    row = int(row_col[0])
    column = int(row_col[1])
    if [row, column] in tictactoe.Player2_moves or [row, column] in tictactoe.previous_moves:
        return jsonify({'status': 'error', 'message': 'Invalid move'})
    else:
        tictactoe.Player2Move([row, column])
        outcome = tictactoe.won()
        if outcome == 'Draw':
            tictactoe.reset()
            return jsonify({'status': 'draw', 'message': 'Game is a draw', 'next_move': outcome})
            
        elif outcome:
            tictactoe.reset()
            return jsonify({'status': 'win', 'message': 'Game is a draw', 'next_move': outcome})
        
        return jsonify({'status': 'next_move', 'message': 'Next move', 'next_move':'Player1'})
            


@app.route('/website', methods=['GET', 'POST'])
@login_required
def website():
    return render_template('website.html')



@app.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    return render_template('leaderboard.html')
#finish leaderboard, player vs player, update profile, 

# @app.route('/get_media/<media_id>')
# def get_media(media_id):
#     media = fs.get(ObjectId(media_id))
#     return send_file(BytesIO(media.read()), mimetype='image/jpeg')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.teardown_appcontext
def close_connection(exception): 
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)

