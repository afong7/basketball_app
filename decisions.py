#decisions.py
from vid_clips import VideoClip

class DecisionDrill():
    def __init__(self, title:str, clip1:VideoClip, clip2:VideoClip, question:str, choices:list, correct_answer:str, explanation:str =''):
        self.title = title
        self.clip1 = clip1
        self.clip2 = clip2
        self.question = question
        self.choices = choices
        self.correct_answer = correct_answer
        self.explanation = explanation
    
    def show_question(self):
        print(self.question)
        for index, choice in enumerate(self.choices, start=1):
            print(index, choice)
    
    def is_correct(self, choice_answer):
        if choice_answer < 1 or choice_answer > len(self.choices):
            return False
        user_answer = self.choices[choice_answer - 1]
        if user_answer == self.correct_answer:
            return True
        else:
            return False
            
    def get_feedback(self):
        if self.explanation:
            return self.explanation
        else:
            return "No coaching explanation was added for this video."

#TESTS#
if __name__ == "__main__":
    t1 = DecisionDrill('Pass', VideoClip('clip1.mov', 0.0, 4.9), VideoClip('clip1.mov', 5.0, 9.2), 'What should the player do', ['pass', 'drive', 'shoot'], 'pass', 'it is the start of the game')
    t2 = DecisionDrill('Pass', VideoClip('clip1.mov', 0.0, 4.9), VideoClip('clip1.mov', 5.0, 9.2), 'What should the player do', ['pass', 'drive', 'shoot'], 'pass')
    t1.show_question()
    print(t1.is_correct("pass"))
    print(t1.is_correct("shoot"))
    print(t1.get_feedback())
    t2.show_question()
    print(t2.is_correct("pass"))
    print(t2.is_correct("shoot"))
    print(t2.get_feedback())
    
    
    
    
    