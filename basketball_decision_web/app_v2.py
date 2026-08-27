from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///basketball.db"
# real database = basketball_decision_web/instance/basketball.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin,db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    video_file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    decision_points = db.relationship(
        "DecisionPoint",
        backref="video",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="DecisionPoint.pause_time"
    )


class DecisionPoint(db.Model):
    __tablename__ = "decision_points"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(
        db.Integer,
        db.ForeignKey("videos.id"),
        nullable=False
    )
    pause_time = db.Column(db.Float, nullable=False)
    reveal_time = db.Column(db.Float, nullable=False)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    answer_choices = db.relationship(
        "AnswerChoice",
        backref="decision_point",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="AnswerChoice.position"
    )


class AnswerChoice(db.Model):
    __tablename__ = "answer_choices"

    id = db.Column(db.Integer, primary_key=True)
    decision_point_id = db.Column(
        db.Integer,
        db.ForeignKey("decision_points.id"),
        nullable=False
    )
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    position = db.Column(db.Integer, nullable=False)


def create_data():
    sample_title = "Start of the game"

    existing_video = Video.query.filter_by(title=sample_title).first()

    if existing_video:
        return

    new_video = Video(
        title=sample_title,
        description=(
            "Watch this opening possession and make the best decision "
            "at each pause."
        ),
        category="Jump ball",
        video_file="clip1.mp4"
    )

    decision1 = DecisionPoint(
        video=new_video,
        pause_time=14.9,
        reveal_time=16.3,
        question="Where should the centre tip it to?",
        explanation="There is no defense behind. It's the safest option."
    )

    answer_choice1 = AnswerChoice(
        decision_point=decision1,
        text="Behind",
        is_correct=True,
        position=1
    )

    answer_choice2 = AnswerChoice(
        decision_point=decision1,
        text="In front",
        is_correct=False,
        position=2
    )

    answer_choice3 = AnswerChoice(
        decision_point=decision1,
        text="To the side",
        is_correct=False,
        position=3
    )

    decision2 = DecisionPoint(
        video=new_video,
        pause_time=16.8,
        reveal_time=19.4,
        question="What is the best next decision?",
        explanation=(
            "The player who caught the jump ball is a 4 and defense has "
            "gotten up. Unless she's Wemby (she's not), find a ball handler."
        )
    )

    answer_choice4 = AnswerChoice(
        decision_point=decision2,
        text="Dribble across half",
        is_correct=False,
        position=1
    )

    answer_choice5 = AnswerChoice(
        decision_point=decision2,
        text="Find a ball handler",
        is_correct=True,
        position=2
    )

    answer_choice6 = AnswerChoice(
        decision_point=decision2,
        text="Throw the ball out of bounds",
        is_correct=False,
        position=3
    )

    db.session.add_all([
        new_video,
        decision1,
        decision2,
        answer_choice1,
        answer_choice2,
        answer_choice3,
        answer_choice4,
        answer_choice5,
        answer_choice6
    ])

    db.session.commit()

# Tells Flask‑Login how to load a user from the database when they have a session cookie.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def index():
    videos = Video.query.order_by(Video.created_at.desc()).all()

    return render_template(
        "index.html",
        title="Homepage | Think the Game",
        videos=videos
    )


@app.route("/videos/<int:video_id>")
def video(video_id):
    video = db.get_or_404(Video, video_id)

    decision_points_data = []

    for decision_point in video.decision_points:
        ordered_choices = sorted(
            decision_point.answer_choices,
            key=lambda choice: choice.position
        )

        correct_choice = next(
            (
                choice
                for choice in ordered_choices
                if choice.is_correct
            ),
            None
        )

        decision_points_data.append({
            "pause_time": decision_point.pause_time,
            "reveal_time": decision_point.reveal_time,
            "question": decision_point.question,
            "choices": [choice.text for choice in ordered_choices],
            "correct_answer": (
                correct_choice.text if correct_choice else ""
            ),
            "explanation": decision_point.explanation
        })

    return render_template(
        "video.html",
        title=video.title,
        video=video,
        decision_points_data=decision_points_data
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        title="About | Think the Game"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return "Email already registered. Please log in.", 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect("/")

    return render_template(
        "register.html",
        title="Register | Think the Game"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")
        if not identifier or not password:
            return "Please enter both username/email and password", 400

        if "@" in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = user = User.query.filter_by(username=identifier).first()    

        if user and user.check_password(password):
            login_user(user)
            return redirect("/")
        else:
            return "Invalid email or password.", 400

    return render_template(
        "login.html",
        title="Login | Think the Game"
    )

@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user, title="Account | Think the Game")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        title="Dashboard | Think the Game",
        user=current_user
    )

@app.route("/upload_video")
@login_required
def upload_video():
    return "Upload page coming soon!"

# Allows us to actually see the app in action when we run the script + upload/update the database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_data()

    app.run(debug=True)