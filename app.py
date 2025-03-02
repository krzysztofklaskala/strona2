from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Usunięto zbędny folder database/
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Model użytkownika
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)  # Wydłużona kolumna dla hashowanych haseł

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Strona główna
@app.route('/')
def home():
    return render_template("index.html")

# Strona logowania
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):  # Sprawdzanie hasha
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash("Nieprawidłowa nazwa użytkownika lub hasło!", "danger")
    
    return render_template("login.html")

# Strona rejestracji
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Użytkownik już istnieje!", "danger")
        else:
            hashed_password = generate_password_hash(password)  # Hashowanie hasła
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Konto utworzone! Możesz się zalogować.", "success")
            return redirect(url_for('login'))
    
    return render_template("register.html")

# Panel użytkownika
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Witaj, {current_user.username}! <br><a href='/logout'>Wyloguj</a>"

# Wylogowanie
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Tworzy bazę danych tylko raz przy starcie aplikacji
    app.run(debug=True)
