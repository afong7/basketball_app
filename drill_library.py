#DrillLibrary.py
from decisions import DecisionDrill
from vid_clips import VideoClip

class DrillLibrary():
    def __init__(self):
        self.drills = {}
    
    def add_drill(self, drill_id:str, drill):
        if drill_id in self.drills:
            print("A drill with that ID already exists.")
        else:
            self.drills[drill_id] = drill
    
    def get_drill(self, drill_id):
        if drill_id not in self.drills:
            return None
        else:
            return self.drills[drill_id]
    
    def list_drills(self):
        if not self.drills:
            print("This video is not in the library.")
        else:
            for key, value in self.drills.items():
                print("This is video " + str(key) + ". It tests the user's ability to know when to " + str(value.title.upper()) + ".")
    
    def delete_drill(self, drill_id):
        if drill_id not in self.drills:
            print("You can't do that. There's no video to delete here.")
        else:
            self.drills.pop(drill_id)
            print("The video was deleted.")

#TESTS#
if __name__ == "__main__":
    d1 = DecisionDrill('Pass', VideoClip('clip1.mov', 0.0, 4.9), VideoClip('clip1.mov', 5.0, 9.2), 'What should the player do', ['pass', 'drive', 'shoot'], 'pass', 'it is the start of the game')
    d2 = DecisionDrill('Shoot', VideoClip('clip1.mov', 9.3, 10.5), VideoClip('clip1.mov', 10.6, 20.0), 'What should the player do', ['pass', 'drive', 'shoot'], 'shoot')
    dl = DrillLibrary()
    dl.add_drill("1", d1)
    dl.add_drill("2", d2)
    dl.list_drills()
    dl.get_drill("1")
    dl.delete_drill("1")
    dl.list_drills()