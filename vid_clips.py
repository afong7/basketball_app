#vid_clips.py
class VideoClip():
    def __init__(self, file_name:str, start_time:float, end_time:float):
        self.file_name = file_name
        self.start_time = start_time
        self.end_time = end_time
    def get_duration(self):
        if self.end_time > self.start_time:
            duration = self.end_time - self.start_time
        else:
            return None
        return duration
    def display_info(self):
        if self.end_time <= self.start_time:
            print("This time input is invalid. Try again.")
        else:
            print("This clip is {file_name}. It starts at {start_time} and ends at {end_time}".format(file_name=self.file_name, start_time=self.start_time, end_time=self.end_time))
            print("The total duration of this clip is {duration} seconds.".format(duration=self.get_duration()))

#TESTS#
if __name__ == "__main__":
    t1 = VideoClip('clip1.mov', 0.0, 4.9)
    t2 = VideoClip('clip1.mov', 5.0, 10.5)
    t3 = VideoClip('clip1.mov', 3.5, 2.7)
    t4 = VideoClip('clip1.mov', 8.9, 8.9)
    t1.get_duration()
    t2.get_duration()
    t1.display_info()
    t2.display_info()
    t3.get_duration()
    t3.get_duration()
    t4.display_info()
    t4.display_info()


