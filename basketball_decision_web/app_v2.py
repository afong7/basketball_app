from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///basketball.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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


@app.route("/")
def index():
    videos = Video.query.order_by(Video.created_at.desc()).all()

    return render_template(
        "index.html",
        title="Basketball Decision Making",
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_data()

    app.run(debug=True)