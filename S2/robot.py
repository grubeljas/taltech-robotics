"""."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        # encoders
        self.leftep = 0
        self.lefte = 0
        self.righte = 0
        self.rightep = 0

        # index
        self.rn = 1.0
        self.ln = 1.0

        # front lasers
        self.fl = 2
        self.fm = 2
        self.fr = 2

        # last value is the newest
        self.front = [0]
        self.front_left = [0]
        self.front_right = [0]

        self.left_side = None
        self.left_diagonal = None
        self.left_back = None

        self.right_back = None
        self.right_side = None
        self.right_diagonal = None

        # min speed of the robot
        self.speed = 8
        self.adjust_low = 4
        self.adjust_high = 5
        self.stand_still = True

        # rotation
        self.rotation_threshold = 0
        self.rotvalue = 40

        # balls
        self.blue_ball_angle = None
        self.red_ball_angle = None
        self.blue_ball_dis = None
        self.red_ball_dis = None
        self.rotated = False

        # drive
        self.distance = None
        self.drive_left = None
        self.i_have_driven = False
        self.drive_left_check = 0
        self.once = True
        self.once2 = True
        self.left_saw_ball = False
        self.right_saw_ball = False
        self.ball_saw_immunity = 0

        # turn
        self.turn_left = True
        self.immunity = 0
        self.rotvalue2 = 10
        self.rotated2 = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to PiBot object.

        Returns:
          None
        """
        self.robot = robot

    def get_state(self):
        """Return the current state."""
        print("------")
        print("front lasers")
        print(f"dis {self.fl} {self.fm} {self.fr}")
        print("blue")
        print(self.blue_ball_angle, self.blue_ball_dis)
        print("red")
        print(self.red_ball_angle, self.red_ball_dis)
        print("dis")
        print(self.distance)
        print("drive, rot2, drive_left, immunity")
        print(self.i_have_driven, self.rotated2, self.drive_left, self.immunity)
        print("left, right")
        print(self.left_saw_ball, self.right_saw_ball, self.ball_saw_immunity)


    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        # encoders
        self.leftep = self.lefte
        self.lefte = self.robot.get_left_wheel_encoder()
        self.rightep = self.righte
        self.righte = self.robot.get_right_wheel_encoder()

        # front 10-100 cm
        self.fl = self.robot.get_front_left_laser()
        self.fm = self.robot.get_front_middle_laser()
        self.fr = self.robot.get_front_right_laser()

        if self.fl > 0.5:
            self.fl = 0.5
        self.front_left.append(self.fl)
        if len(self.front_left) == 6:
            self.front_left.pop(0)

        if self.fr > 0.5:
            self.fr = 0.5
        self.front_right.append(self.fr)
        if len(self.front_right) == 6:
            self.front_right.pop(0)

        # front lasers
        if self.fm > 0.5:
            self.fm = 0.5
        self.front.append(self.fm)
        if len(self.front) == 6:
            self.front.pop(0)

        # 2-16 cm
        self.left_back = self.robot.get_rear_left_straight_ir()
        self.left_diagonal = self.robot.get_rear_left_diagonal_ir()
        self.left_side = self.robot.get_rear_left_side_ir()

        self.right_back = self.robot.get_rear_right_straight_ir()
        self.right_diagonal = self.robot.get_rear_right_diagonal_ir()
        self.right_side = self.robot.get_rear_right_side_ir()

        self.rotation = self.robot.get_rotation()

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_left_wheel_speed(left_wheel * self.ln)
        self.robot.set_right_wheel_speed(right_wheel * self.rn)

    def drive(self):
        """Drive robot until balls or required distance."""
        dis = self.robot.WHEEL_DIAMETER * 3.1415 * (self.lefte - self.drive_left) / 360
        print("i have driven", dis)

        if dis > self.distance * 0.1:
            if self.i_have_driven and self.filter_fl():
                self.left_saw_ball = True
            if self.i_have_driven and self.filter_fr():
                self.right_saw_ball = True
        if self.left_saw_ball and self.right_saw_ball:
            self.ball_saw_immunity += 1

        if dis > self.distance or self.ball_saw_immunity > 75:
            self.i_have_driven = True
            self.blue_ball_angle = None
            self.blue_ball_dis = None
            self.red_ball_dis = None
            self.red_ball_angle = None
            self.drive_left = None
            self.rotated2 = False
            self.left_saw_ball = False
            self.right_saw_ball = False
            self.once = True
            self.once2 = True
            self.ball_saw_immunity = 0
        # elif self.i_have_driven and dis > self.distance * 0.3 and (self.once or self.once2):
        #     if self.once is False:
        #         self.once2 = False
        #     self.once = False
        #     self.act(0,0)
        #     self.take_picture()
        #     self.drive_left = None
        #     self.left_saw_ball = False
        #     self.right_saw_ball = False
        else:
            self.stand_still = False
            self.act(self.speed, self.speed)

    def set_rotation(self):
        """Set the rotation of the middle of the to closest balls."""
        angle = (self.blue_ball_angle + self.red_ball_angle) / 2
        diff = abs(self.rotation - angle)
        if diff < 0.25:
            self.drive_left = self.lefte
            a = 30 / self.blue_ball_dis
            b = 30 / self.red_ball_dis
            # -0.1 on sest kaamera on roboti ees ja rattad taga
            c = ((a + b) / 2)
            # if c < 1:
            if self.i_have_driven:
                c = c - 0.25
            else:
                c = c - 0.25
            # else:
            #     c = c * 0.9
            self.distance = c
        elif self.rotation > angle:
            self.stand_still = False
            self.act(self.speed, -self.speed)
        else:
            self.stand_still = False
            self.act(-self.speed, self.speed)

    def filter(self):
        """Filter front value."""
        lista = self.front
        a = lista.count(0.5)
        b = len(lista) - a
        return a > b

    def filter_fl(self):
        """Filter fl value."""
        lista = self.front_left
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a + 1

    def filter_fr(self):
        """Filter fr value."""
        lista = self.front_right
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a + 1

    def detect_new_balls(self):
        """Rotate robot until it finds both balls on either side and in the mean time take pictures."""
        if self.turn_left:
            if not self.filter_fl():
                self.act(-self.speed, self.speed)
                self.immunity -= 1
            else:
                self.turn_left = False
                self.immunity = 10
                self.rotation_threshold = self.rotation
        else:
            if not self.filter_fr() or self.immunity > 0:
                self.act(self.speed, -self.speed)
                self.immunity -= 1
            else:
                self.turn_left = True
                self.immunity = 10
                self.rotated2 = True

    def plan(self):
        """Main plan function."""
        if not self.stand_still:
            self.adjust()

        if False:
            pass
        elif self.i_have_driven and self.drive_left is not None:
            self.drive()
        elif self.i_have_driven and self.rotated2:
            self.set_rotation()

        elif self.i_have_driven and abs(self.rotation) > self.rotation_threshold:
            self.act(0, 0)
            self.take_picture_close()
            self.rotation_threshold = ((abs(self.rotation) // self.rotvalue2) + 1) * self.rotvalue2
        elif self.i_have_driven:
            self.detect_new_balls()

        # getting to ball
        elif self.drive_left is not None:
            self.drive()
        elif abs(self.rotation) > 360 or self.rotated:
            self.rotated = True
            self.set_rotation()
        elif abs(self.rotation) > self.rotation_threshold:
            self.stand_still = True
            self.act(0, 0)
            self.rotation_threshold = ((abs(self.rotation) // self.rotvalue) + 1) * self.rotvalue
            self.take_picture()
        else:
            self.stand_still = False
            self.act(self.speed, -self.speed)

    def take_picture_close(self):
        """Take the picture with the camera and finds balls."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        for image in camera:
            angle = self.camera_helper(image)
            if image[0] == "blue sphere":
                if self.blue_ball_angle is None and image[2] < 30:
                    self.blue_ball_angle = self.rotation + angle
                    self.blue_ball_dis = image[2]
                else:
                    self.blue_ball_angle = self.rotation + angle
                    self.blue_ball_dis = image[2]
            else:
                if self.red_ball_angle is None and image[2] < 30:
                    self.red_ball_angle = self.rotation + angle
                    self.red_ball_dis = image[2]
                else:
                    if image[2] >= self.red_ball_dis and image[2] < 30:
                        self.red_ball_angle = self.rotation + angle
                        self.red_ball_dis = image[2]

    def take_picture(self):
        """Take the picture with the camera and finds balls."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        print(camera)
        for image in camera:
            angle = self.camera_helper(image)
            if image[0] == "blue sphere":
                if self.blue_ball_angle is None:
                    self.blue_ball_angle = self.rotation + angle
                    self.blue_ball_dis = image[2]
                else:
                    if image[2] >= self.blue_ball_dis:
                        self.blue_ball_angle = self.rotation + angle
                        self.blue_ball_dis = image[2]
            else:
                if self.red_ball_angle is None:
                    self.red_ball_angle = self.rotation + angle
                    self.red_ball_dis = image[2]
                else:
                    if image[2] >= self.red_ball_dis:
                        self.red_ball_angle = self.rotation + angle
                        self.red_ball_dis = image[2]

    def camera_helper(self, image):
        """Take image and decide where is object and with what angle."""
        width_deg = self.robot.CAMERA_FIELD_OF_VIEW[0]  # deg
        width = self.robot.CAMERA_RESOLUTION[0]
        object = image[1]
        x = object[0]
        half_width = width / 2
        half_width_deg = width_deg / 2
        if x > half_width:
            right = True
            xpos = x - half_width
        else:
            right = False
            xpos = half_width - x
        ratio = xpos / half_width
        ratio_deg = half_width_deg * ratio
        if right:
            angle = -ratio_deg
        else:
            angle = ratio_deg
        return angle

    def calc_left(self):
        """Adjust left encoder."""
        while True:
            print(self.ln, self.rn)
            prev = self.robot.get_left_wheel_encoder()
            self.act(self.speed, 0)
            self.robot.sleep(0.05)
            self.act(0, 0)
            cur = self.robot.get_left_wheel_encoder()
            change = cur - prev
            if change <= 0:
                self.ln += 0.002
            else:
                break
        self.act(-self.speed, 0)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calc_right(self):
        """Adjust the right encoder."""
        while True:
            print(self.ln, self.rn)
            prev = self.robot.get_right_wheel_encoder()
            self.act(0, self.speed)
            self.robot.sleep(0.05)
            self.act(0, 0)
            cur = self.robot.get_right_wheel_encoder()
            change = cur - prev
            if change <= 0:
                self.rn += 0.002
            else:
                break
        self.act(0, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calculate(self):
        """Adjust both encoders."""
        rightep = self.robot.get_right_wheel_encoder()
        leftep = self.robot.get_left_wheel_encoder()
        self.act(self.speed, self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)
        righte = self.robot.get_right_wheel_encoder()
        lefte = self.robot.get_left_wheel_encoder()
        self.act(-self.speed, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)
        right = righte - rightep
        left = lefte - leftep
        if right <= 0:
            self.calc_right()
        if left <= 0:
            self.calc_left()

    def adjust(self):
        """Adjust both encoders a little bit."""
        left = abs(self.lefte - self.leftep)
        right = abs(self.righte - self.rightep)

        if left > self.adjust_high:
            self.ln -= 0.002
        elif left < self.adjust_low:
            self.ln += 0.002

        if right > self.adjust_high:
            self.rn -= 0.002
        elif right < self.adjust_low:
            self.rn += 0.002

        if right > left:
            self.ln += 0.001
        elif right < left:
            self.rn += 0.001

    def spin(self):
        """The main loop of the robot."""
        self.calculate()
        print(self.ln, self.rn)
        self.robot.close_grabber(0)
        self.robot.sleep(0.2)
        self.rotation_threshold = 0
        while not self.shutdown:
            self.sense()
            self.get_state()
            self.plan()
            self.robot.sleep(0.05)


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
