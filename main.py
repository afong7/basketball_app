#main.py
from vid_clips import VideoClip
from players import Player
from decisions import DecisionDrill
from drill_library import DrillLibrary
from app import run_drill

p1 = Player("User")
dl = DrillLibrary()
d1 = DecisionDrill('Pass', VideoClip('clip1.mov', 0.0, 4.9), VideoClip('clip1.mov', 5.0, 9.2), 'What should the player do', ['pass', 'drive', 'shoot'], 'pass', 'it is the start of the game')
d2 = DecisionDrill('Shoot', VideoClip('clip1.mov', 9.3, 10.5), VideoClip('clip1.mov', 10.6, 20.0), 'What should the player do', ['pass', 'drive', 'shoot'], 'shoot')
dl.add_drill("1", d1)
dl.add_drill("2", d2)

def show_menu():
    print("BASKETBALL DECISION MAKING")
    print("1. List videos \n2. Practice a specific drill \n3. Exit")

while True:
    show_menu()
    menu_choice = input("Choose an option: ")
    if menu_choice == "1":
        dl.list_drills()
    elif menu_choice == "2":
        dl.list_drills()
        drill_id = input("Enter the drill ID: ")
        selected_drill = dl.get_drill(drill_id)
        if selected_drill is None:
            print("That drill ID does not exist.")
        else:
            run_drill(p1, selected_drill)
    elif menu_choice == "3":
        print("Closing the app now. Thanks for playing, and good luck on the court!")
        break
    else:
        print("Your choice was invalid. Try again")
        
#TESTS#
# List drills
# Practice each drill
# Enter a drill ID that does not exist
# Enter an invalid menu option
# Exit
    












