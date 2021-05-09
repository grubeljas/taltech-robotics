"""
To use this helper file, please add it to the same directory as your OT10.py file along with the data files (the files that has the get_data() function in it).

The directory should have the following files in it:
.
├── OT10.py
├── PiBot.py
└── blue_approach.py

Add the following code to your OT10.py:

def test():
    robot = Robot()
    import blue_approach # or any other data file
    data = blue_approach.get_data()
    robot.robot.load_data_profile(data)
    for i in range(len(data)):
        print(f"objects = {robot.robot.get_camera_objects()}")
        robot.robot.sleep(0.05)

if __name__ == "__main__":
    test()
"""


class PiBot:
    def __init__(self):
        self.time = 0.0
        self.idx = 0
        self.CAMERA_RESOLUTION = (1080, 1080)  # (width, height) in pixels
        self.CAMERA_FIELD_OF_VIEW = (62.2, 48.8)  # (horizontal, vertical) in degrees
        self.data = None

    def load_data_profile(self, data):
        self.data = data

    def get_camera_objects(self):
        """
        Return the detected objects as a list of tuples. E.g., [(object ID, (center x coordinate, center y coordinate), object size radius), ...]
        """
        if self.data is not None:
            return self.data[self.idx][1][0]

    def sleep(self, seconds):
        self.time += seconds
        for i in range(self.idx, len(self.data)):
            if self.time >= self.data[i][0]:
                self.idx = i
            elif self.time < self.data[i][0]:
                break

    def get_time(self):
        return self.time
