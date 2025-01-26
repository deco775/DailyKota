from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,logout_user, login_required, current_user
import stripe
#from werkzeug.security import generate_security_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "Pitsorate.100%"
#app.config['SESSION_TYPE'] = 'filesystem'
#app.config['SESSION_PERMANENT'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config["SQLALCHEMY_TRACE_MODIFICATION"] = False
stripe.api_key = "sk_test_51QlY0cDh32MrkoNopytVxPsn2Rt0y4akRcKvPW1VkyD5LettOZWGjhftKNAvwD7fG4jgE679aJawBybSyrPrdAeg00yvMXtzjd"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods = ['GET', 'POST'] )
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        #hashed_password = generate_password_hash(password)

        user = User(username=username, email=email, password= password)
        db.session.add(user)
        db.session.commit()

        #return render_template ('login.html')

        return redirect(url_for("login"))
    else:
        return render_template('register.html')

@app.route('/')
@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
    return render_template ('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username']=username

        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            login_user(user)
            #return redirect(url_for('dashboard', username=username))
            flash('Log in Successfully')
            return render_template("dashboard.html", username = username)
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/store1')
def store1():
    return render_template('store1.html')

@app.route('/store_1')
@login_required
def store_1():
    return render_template('store_1.html')

@app.route('/database')
def database():
    users = User.query.all()
    return render_template('viewdb.html', users = users)

@app.route('/dashboard')
@login_required
def dashboard():
    #username = request.args.get('username')
    return redirect(url_for('payment'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/pay', methods=['GET','POST'])
def process_payment():
    try:
        # Retrieve payment details from the form
        token = request.form.get('stripeToken')  # Payment token (e.g., Stripe token)
        items = [
            {"name": "Item1", "price": 20},
            {"name": "Item2", "price": 30},
            {"name": "Item3", "price": 50},
        ]

        if not token:
            #flash("Invalid payment details.", "error")
            return redirect(url_for('dashboard'))

        # Calculate total amount
        total_amount = sum(item['price'] for item in items) * 100  # Convert to cents

        # Create a charge
        stripe.Charge.create(
            amount=int(total_amount),
            currency="usd",
            source=token,
            description="Payment for items",
        )

        flash("Payment successful!", "success")
        return redirect(url_for('dashboard'))

    except stripe.error.StripeError as e:
        flash(f"Payment failed: {str(e)}", "error")
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))


@app.route('/payment')
def payment():
    total = request.args.get('total', type=float)
    return render_template('payment.html', total=total)

@app.route('/pay', methods=['POST'])
def pay():
    payment_amount = float(request.form['payment_amount'])
    total_amount = float(request.form['total_amount'])

    if payment_amount >= total_amount:
        flash("Payment successful! Thank you for your purchase.")
    else:
        flash("Insufficient funds. Please try again.")

    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
