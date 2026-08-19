from flask import Flask, render_template, request

app = Flask(__name__)

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
    app.run(debug=True)


