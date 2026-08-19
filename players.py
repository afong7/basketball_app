#players.py
class Player():
    # def __init__(self, name:str, points:int, correct_answers:int, attempts:int):
    #     self.name = name
    #     self.points = points
    #     self.correct_answers = correct_answers
    #     self.attempts = attempts
        
    #     points = 0
    #     correct_answers = 0
    #     attempts = 0
    def __init__(self, name: str):
        self.name = name
        self.points = 0
        self.correct_answers = 0
        self.attempts = 0
    
    def add_attempt(self, was_correct):
        self.attempts += 1
        if was_correct:
            self.correct_answers += 1
            self.points += 10
    
    def get_accuracy(self):
        if self.attempts == 0:
            return 0
        else:
            return round(self.correct_answers / self.attempts * 100, 2)
    
    def display_stats(self):
        print('{name} finished with {points} points, having {correct_answers} answers correct out of {attempts} attempts.'.format(name=self.name, points=self.points, correct_answers=self.correct_answers, attempts=self.attempts))
        print('Total accuracy: {accuracy}%'.format(accuracy=self.get_accuracy()))

#TESTS#
if __name__ == "__main__":
    p1 = Player('Lex')
    p1.add_attempt(True)
    p1.add_attempt(False)
    p1.add_attempt(True)
    p1.display_stats()


