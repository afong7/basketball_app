from flask import Flask, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#c) enable communication with a database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basketball.db' 
# - takes the location of the application’s database from the SQLALCHEMY_DATABASE_URI configuration variable we set

#d) set the SQLALCHEMY_TRACK_MODIFICATIONS configuration option to False to disable a feature of Flask-SQLAlchemy that signals 
# the application every time a change is about to be made in the database.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#e) create an SQLAlchemy object and bind it to our app
db = SQLAlchemy(app)

class Video(db.Model): #any CREATED model inherits from db.Model
    __tablename__ = "videos"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), index=True)
    video_file = db.Column(db.String(255), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    decision_points = db.relationship('DecisionPoint', backref='video', lazy=True, cascade="all, delete-orphan", order_by="DecisionPoint.pause_time")
    
#a) initialize a field with the .relationship() method. 
# In one-to-many relationships, the relationship field is used on the ‘one’ side of the relationship
class DecisionPoint(db.Model):
    __tablename__ = "decision_points"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    pause_time = db.Column(db.Float, nullable=False)
    reveal_time = db.Column(db.Float, nullable=False)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    answer_choices = db.relationship('AnswerChoices', backref='decision_point', lazy=True, cascade="all, delete-orphan")

class AnswerChoices(db.Model):
    __tablename__ = "answer_choices"
    id = db.Column(db.Integer, primary_key=True)
    decision_point_id = db.Column(db.Integer, db.ForeignKey('decision_points.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, nullable=False)

# drills = [
#     {
#         "id": "1",
#         "title": "Game clip",
#         "question": "What should the player do?",
#         "choices": [
#             "Pass to the corner",
#             "Pass to the top of the key",
#             "Attack the basket"
#         ],
#         "video_file": "clip1.mp4",
#         "pause_time": 15.1,
#         "correct_answer": "Attack the basket",
#         "explanation": (
#             "There is open space in front of the ball handler, "
#             "so driving creates the best scoring opportunity. "
#             "The player can either keep if nobody comes to them, or look for a kickout."
#         )
#     }
# ]

videos = [
    {
        "id": "1",
        "title": "Start of the game",
        "description": (
            "Watch this opening possession and make the best decision "
            "at each pause."
        ),
        "category": "Jump ball",
        "video_file": "clip1.mp4",
        "decision_points": [
            {
                "id": "1",
                "pause_time": 14.9,
                "reveal_time": 16.3,
                "question": "Where should the centre tip it to?",
                "choices": [
                    "Behind",
                    "In front",
                    "Other"
                ],
                "correct_answer": "Behind",
                "explanation": (
                    "There is no defense behind. It's the safest option."
                )
            },
            {
                "id": "2",
                "pause_time": 16.8,
                "reveal_time": 20.0,
                "question": "What is the best next decision?",
                "choices": [
                    "Dribble across half",
                    "Find a ball handler",
                    "Throw the ball out of bounds"
                ],
                "correct_answer": "Find a ball handler",
                "explanation": (
                    "The player who caught the jump ball is a 4 and defense has gotten up. "
                    "Unless she's Wemby (she's not), find a ball handler."
                )
            }
        ]
    }
]

#Homepage
@app.route("/")
def index():
    return render_template(
        "index.html",
        title="Basketball Decision Making",
        videos=videos
    )


#Loop through the drills list. Compare each video "id" to video_id. When it finds a match, render 
# video.html, passing a title and the matching video as video. If no match exists, return a Drill not 
# found” message with status code 404.
@app.route("/videos/<video_id>")
def video(video_id):
    for video in videos:
        if video_id == video["id"]:
            return render_template(
                "video.html",
                title=video["title"],
                video=video
            )

    return "Video not found.", 404

@app.route("/about")
def about():
    return render_template("about.html", title="About | Think the Game")

#Tell Flask to start the web server
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


