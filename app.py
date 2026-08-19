#app_v1.py
from decisions import DecisionDrill
from vid_clips import VideoClip
from players import Player

def run_drill(player, drill):
    print("Now playing clip 1.")
    drill.show_question()
    user_answer = int(input("Your answer (the number): "))
    answer = drill.is_correct(user_answer)
    player.add_attempt(answer)
    
    if answer:
        print("You're correct!")
    else:
        print("Try again.")
        drill.show_question()
        user_answer = int(input("Your answer (the number): "))
        answer = drill.is_correct(user_answer)
        player.add_attempt(answer)
    
    print("Now playing the end of the clip.")
    print(drill.get_feedback())
    player.display_stats()

#TESTS#
if __name__ == "__main__":
    v1 = VideoClip('clip1.mov', 0.0, 4.9)
    v2 = VideoClip('clip1.mov', 5.0, 10.5)
    d1 = DecisionDrill('Pass', VideoClip('clip1.mov', 0.0, 4.9), VideoClip('clip1.mov', 5.0, 10.5), 'What should the player do', ['pass', 'drive', 'shoot'], 'pass')
    p1 = Player('Lex')
    run_drill(p1, d1)


    
    
    