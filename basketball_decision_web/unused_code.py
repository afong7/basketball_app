# def create_data():
#     sample_title = "Start of the game"

#     existing_video = Video.query.filter_by(title=sample_title).first()

#     if existing_video:
#         return

#     new_video = Video(
#         title=sample_title,
#         description=(
#             "Watch this opening possession and make the best decision "
#             "at each pause."
#         ),
#         category="Jump ball",
#         video_file="clip1.mp4"
#     )

#     decision1 = DecisionPoint(
#         video=new_video,
#         pause_time=14.9,
#         reveal_time=16.3,
#         question="Where should the centre tip it to?",
#         explanation="There is no defense behind. It's the safest option."
#     )

#     answer_choice1 = AnswerChoice(
#         decision_point=decision1,
#         text="Behind",
#         is_correct=True,
#         position=1
#     )

#     answer_choice2 = AnswerChoice(
#         decision_point=decision1,
#         text="In front",
#         is_correct=False,
#         position=2
#     )

#     answer_choice3 = AnswerChoice(
#         decision_point=decision1,
#         text="To the side",
#         is_correct=False,
#         position=3
#     )

#     decision2 = DecisionPoint(
#         video=new_video,
#         pause_time=16.8,
#         reveal_time=19.4,
#         question="What is the best next decision?",
#         explanation=(
#             "The player who caught the jump ball is a 4 and defense has "
#             "gotten up. Unless she's Wemby (she's not), find a ball handler."
#         )
#     )

#     answer_choice4 = AnswerChoice(
#         decision_point=decision2,
#         text="Dribble across half",
#         is_correct=False,
#         position=1
#     )

#     answer_choice5 = AnswerChoice(
#         decision_point=decision2,
#         text="Find a ball handler",
#         is_correct=True,
#         position=2
#     )

#     answer_choice6 = AnswerChoice(
#         decision_point=decision2,
#         text="Throw the ball out of bounds",
#         is_correct=False,
#         position=3
#     )

#     db.session.add_all([
#         new_video,
#         decision1,
#         decision2,
#         answer_choice1,
#         answer_choice2,
#         answer_choice3,
#         answer_choice4,
#         answer_choice5,
#         answer_choice6
#     ])

#     db.session.commit()
