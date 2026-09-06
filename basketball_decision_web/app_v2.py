from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for, flash, abort
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate

from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./basketball.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024 #500 MB limit
ALLOWED_EXTENSIONS = {"mp4", "mov"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin,db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="player")
    coach_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    videos = db.relationship("Video", backref="user", lazy=True)
    coach = db.relationship("User", remote_side="User.id", backref="players")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PlayerProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)

    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    selected_answer = db.Column(db.String(120))
    is_correct = db.Column(db.Boolean)
    decision_point_index = db.Column(db.Integer)
    time_taken = db.Column(db.Float)
    attempt_number = db.Column(db.Integer)

    user = db.relationship("User", backref="progress")
    video = db.relationship("Video", backref="progress")


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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


# Tells Flask‑Login how to load a user from the database when they have a session cookie.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---- ROLE DECORATORS GO HERE ----
def coach_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "coach":
            return "Forbidden", 403
        return f(*args, **kwargs)
    return wrapper

def player_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "player":
            return "Forbidden", 403
        return f(*args, **kwargs)
    return wrapper


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
        decision_points_data=decision_points_data,
        video_id=video.id
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        title="About | Think the Game"
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    coaches = User.query.filter_by(role="coach").all()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        coach_id = request.form.get("coach_id")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Email uniqueness
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered. Please log in.", "error")
            return render_template("register.html", coaches=coaches)

        # Password match
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return render_template("register.html", coaches=coaches)

        # Create user correctly
        if role == "player":
            new_user = User(
                username=username,
                email=email,
                role="player",
                coach_id=coach_id
            )
        else:
            new_user = User(
                username=username,
                email=email,
                role="coach",
                coach_id=None
            )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect("/")

    return render_template("register.html", title="Register | Think the Game", coaches=coaches)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        if not identifier or not password:
            flash("Please enter both username/email and password.", "error")
            return render_template("login.html")

        # Determine whether identifier is email or username
        if "@" in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()

        # Validate login
        if not user or not user.check_password(password):
            flash("Invalid username or password. Please try again.", "error")
            return render_template("login.html")

        # Success
        login_user(user)
        return redirect("/")

    return render_template("login.html", title="Login | Think the Game")


@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user, title="Account | Think the Game")


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user=current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    players = current_user.players

    progress = (PlayerProgress.query.join(User).filter(User.coach_id == current_user.id).all())

    return render_template(
        "dashboard.html",
        title="Dashboard | Think the Game",
        user=current_user,
        players=players,
        progress=progress
    )


@app.route("/coach/videos")
@login_required
@coach_required
def video_bank():
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "video_bank.html", 
        title = "Video Bank | Think the Game",
        videos=videos)

@app.route("/player/videos")
@login_required
@player_required
def player_video_bank():
    videos = Video.query.filter_by(user_id=current_user.coach_id).all()
    return render_template(
        "video_bank.html", 
        title="Video bank | Think the Game",
        videos=videos)


@app.route("/upload_video", methods=["GET", "POST"])
@login_required
@coach_required
def upload_video():
    if request.method == "POST":
        file = request.files.get("video_file")
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")
        print(request.files)

        # Validate file
        if not file or file.filename == "":
            return "No file selected", 400

        if not allowed_file(file.filename):
            return "Invalid file type. Only MP4 and MOV files are allowed.", 400

        # Secure filename
        filename = secure_filename(file.filename)

        # Save file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Create Video entry
        new_video = Video(
            title=title,
            description=description,
            category=category,
            video_file=filename,
            user_id=current_user.id
        )

        # Save video to database
        db.session.add(new_video)
        db.session.commit()

        # Redirect to decision point editor
        return redirect(url_for("edit_video", video_id=new_video.id))

    return render_template(
        "upload_video.html",
        title="Video Upload | Think the Game")


@app.route("/edit_video/<int:video_id>", methods=["GET", "POST"])
@login_required
@coach_required
def edit_video(video_id):
    video = db.get_or_404(Video, video_id)

    if request.method == "POST":
        pause_time = float(request.form.get("pause_time"))
        reveal_time = float(request.form.get("reveal_time"))
        question = request.form.get("question")
        explanation = request.form.get("explanation")

        # Collect choices ;)
        choices = []
        for i in range(1, 6):
            text = request.form.get(f"choice{i}")
            if text and text.strip() != "":
                choices.append(text.strip())
        correct_choice_index = int(request.form.get("correct_choice"))

        # Create DecisionPoint
        dp = DecisionPoint(
            video_id = video.id,
            pause_time=pause_time,
            reveal_time=reveal_time,
            question=question,
            explanation=explanation
        )

        db.session.add(dp)
        db.session.flush() # get dp.id before adding choices

        # Add AnswerChoice rows
        for position, text in enumerate(choices, start=1):
            ac = AnswerChoice(
                decision_point_id=dp.id,
                text=text,
                position=position,
                is_correct=(position == correct_choice_index)
            )
            db.session.add(ac)

        db.session.commit()

    decision_points = DecisionPoint.query.filter_by(video_id=video.id).all()

    return render_template(
        "edit_video.html",
        video=video,
        decision_points=decision_points
    )

@app.route("/delete_decision_point/<int:dp_id>", methods=["POST"])
@coach_required
def delete_decision_point(dp_id):
    dp = db.get_or_404(DecisionPoint, dp_id)
    video_id = dp.video_id
    db.session.delete(dp)
    db.session.commit()
    return redirect(url_for("edit_video", video_id=video_id))

@app.route("/edit_decision_point/<int:dp_id>", methods=["GET", "POST"])
@coach_required
def edit_decision_point(dp_id):
    dp = db.get_or_404(DecisionPoint, dp_id)
    vid = dp.video

    if request.method == "POST":
        dp.pause_time = float(request.form.get("pause_time"))
        dp.reveal_time = float(request.form.get("reveal_time"))
        dp.question = request.form.get("question")
        dp.explanation = request.form.get("explanation")

        # Update choices
        correct_choice = int(request.form.get("correct_choice"))
        for choice in dp.answer_choices:
            new_text = request.form.get(f"choice{choice.position}")
            if new_text:
                choice.text = new_text.strip()

            choice.is_correct = (choice.position == correct_choice)

        db.session.commit()
        return redirect(url_for("edit_video", video_id=dp.video_id))

    return render_template("edit_dp.html", title="Edit Decision Point | Think the Game", dp=dp, vid=vid)


@app.route("/coach/dashboard")
@login_required
@coach_required
def coach_dashboard():
    players = current_user.players
    progress = (
        PlayerProgress.query
        .join(User)
        .filter(User.coach_id == current_user.id)
        .all()
    )

    return render_template(
        "coach_dashboard.html",
        players=players,
        progress=progress
    )


@app.route("/player_progress")
@player_required
def player_progress():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    # Get all progress entries for this player
    progress_entries = (
        PlayerProgress.query
        .filter_by(user_id=current_user.id)
        .join(Video)
        .filter(Video.user_id == current_user.coach_id)
        .all()
    )

    return render_template(
        "player_progress.html",
        progress_entries=progress_entries,
        user=current_user
    )


@app.route("/save_progress", methods=["POST"])
@login_required
def save_progress():
    data = request.get_json()

    video_id = data.get("video_id")
    correct = data.get("correct_answers")
    total = data.get("total_questions")

    progress = PlayerProgress(
        user_id=current_user.id,
        video_id=video_id,
        correct_answers=correct,
        total_questions=total,
        selected_answer=data.get("selected_answer"),
        is_correct=data.get("is_correct"),
        decision_point_index=data.get("decision_point_index"),
        time_taken=data.get("time_taken"),
        attempt_number=data.get("attempt_number")
    )

    db.session.add(progress)
    db.session.commit()
    return {"status": "ok"}


@app.route("/coach/analytics")
@login_required
@coach_required
def analytics():
    # All progress entries for this coach's players
    progress_entries = (PlayerProgress.query.join(User).filter(User.coach_id == current_user.id).all())

    # Group by player
    from collections import defaultdict
    player_stats = defaultdict(list)
    video_stats = defaultdict(list)

    for entry in progress_entries:
        accuracy = entry. correct_answers / entry.total_questions if entry.total_questions else 0
        player_stats[entry.user.username].append(accuracy)
        video_stats[entry.video.title].append(accuracy)

    # Compute analytics
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0

    avg_accuracy = avg([acc for lst in player_stats.values() for acc in lst])

    most_active_player = max(player_stats.items(), key=lambda x: len(x[1]), default=(None, []))[0]
    most_improved_player = max(player_stats.items(), key=lambda x: (x[1][-1] - x[1][0]) if len(x[1]) > 1 else -999, default=(None, []))[0]

    hardest_video = min(video_stats.items(), key=lambda x: avg(x[1]), default=(None, []))[0]

    return render_template(
        "analytics.html",
        title="Player Analytics | Think the Game",
        avg_accuracy=avg_accuracy,
        player_stats=player_stats,
        video_stats=video_stats,
        most_active_player=most_active_player,
        most_improved_player=most_improved_player,
        hardest_video=hardest_video
    )

# Allows us to actually see the app in action when we run the script + upload/update the database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)