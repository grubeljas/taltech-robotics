"""."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        self.left_encoder_previous = 0
        self.left_encoder = 0
        self.right_encoder = 0
        self.right_encoder_previous = 0

        self.rn = 1.0
        self.ln = 1.0

        self.front_left_laser = 2
        self.front_middle_laser = 2
        self.front_right_laser = 2

        self.front = [0]
        self.front_left = [0]
        self.front_right = [0]

        self.speed = 8
        self.change_speed_low = 4
        self.change_speed_high = 5

        self.rotation_threshold = 0
        self.rotate_value = 30

        self.blue_angle = None
        self.red_angle = None
        self.blue_distance = None
        self.red_distance = None

        self.distance = None
        self.drive_left = None
        self.drive_left_check = 0

        self.ball_saw_immunity = 0
        self.immunity = 0
        self.rotate_value_second = 10

        self.left_side = None
        self.left_diagonal = None
        self.left_back = None

        self.right_back = None
        self.right_side = None
        self.right_diagonal = None

        self.stand_still = True
        self.turn_left = True
        self.rotated_one = False
        self.rotated2 = False

        self.has_driven = False
        self.once = True
        self.once2 = True
        self.left_saw_ball = False
        self.right_saw_ball = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to PiBot object.

        Returns:
          None
        """
        self.robot = robot

    def get_state(self):
        """Return the current state."""

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_left_wheel_speed(left_wheel * self.ln)
        self.robot.set_right_wheel_speed(right_wheel * self.rn)

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        self.right_encoder_previous = self.right_encoder
        self.left_encoder_previous = self.left_encoder
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

        self.front_left_laser = self.robot.get_front_left_laser()
        self.front_right_laser = self.robot.get_front_right_laser()
        self.front_middle_laser = self.robot.get_front_middle_laser()

        if self.front_middle_laser > 0.5:
            self.front_middle_laser = 0.5
        self.front.append(self.front_middle_laser)
        if len(self.front) == 6:
            self.front.pop(0)

        if self.front_right_laser > 0.5:
            self.front_right_laser = 0.5
        self.front_right.append(self.front_right_laser)
        if len(self.front_right) == 6:
            self.front_right.pop(0)

        if self.front_left_laser > 0.5:
            self.front_left_laser = 0.5
        self.front_left.append(self.front_left_laser)
        if len(self.front_left) == 6:
            self.front_left.pop(0)

        self.left_back = self.robot.get_rear_left_straight_ir()
        self.left_side = self.robot.get_rear_left_side_ir()
        self.left_diagonal = self.robot.get_rear_left_diagonal_ir()

        self.right_back = self.robot.get_rear_right_straight_ir()
        self.right_side = self.robot.get_rear_right_side_ir()
        self.right_diagonal = self.robot.get_rear_right_diagonal_ir()

        self.rotation = self.robot.get_rotation()

    def drive(self):
        """Drive robot until balls or required distance."""
        distance = self.robot.WHEEL_DIAMETER * 3.1415 * (self.left_encoder - self.drive_left) / 360

        if distance > self.distance * 0.1:
            if self.has_driven and self.filter_front_left():
                self.left_saw_ball = True
            if self.has_driven and self.filter_front_right():
                self.right_saw_ball = True
        if self.left_saw_ball and self.right_saw_ball:
            self.ball_saw_immunity += 1

        if distance > self.distance or self.ball_saw_immunity > 75:
            self.has_driven = True
            self.blue_angle = None
            self.blue_distance = None
            self.red_distance = None
            self.red_angle = None
            self.drive_left = None
            self.rotated2 = False
            self.left_saw_ball = False
            self.right_saw_ball = False
            self.once = True
            self.once2 = True
            self.ball_saw_immunity = 0
        else:
            self.stand_still = False
            self.act(self.speed, self.speed)

    def set_rotation(self):
        """Set the rotation of the middle of the to closest balls."""
        if self.blue_angle is None or self.red_angle is None:
            self.act(0, 0)
            self.shutdown = True
            return None
        angle = (self.blue_angle + self.red_angle) / 2
        difference = abs(self.rotation - angle)
        if difference < 0.25:
            self.drive_left = self.left_encoder
            a = 30 / self.blue_distance
            b = 30 / self.red_distance
            c = ((a + b) / 2)
            if self.has_driven:
                c = c - 0.25
            else:
                c = c - 0.25
            self.distance = c
        elif self.rotation > angle:
            self.stand_still = False
            self.act(self.speed, -self.speed)
        else:
            self.stand_still = False
            self.act(-self.speed, self.speed)

    def filter_front(self):
        """Filter front value."""
        list_one = self.front
        a = list_one.count(0.5)
        b = len(list_one) - a
        return a > b

    def filter_front_left(self):
        """Filter fl value."""
        list_one = self.front_left
        a = list_one.count(0.5)
        b = len(list_one) - a
        return b > a + 1

    def filter_front_right(self):
        """Filter fr value."""
        list_one = self.front_right
        a = list_one.count(0.5)
        b = len(list_one) - a
        return b > a + 1

    def plan(self):
        """Main plan function."""
        if not self.stand_still:
            self.adjust_all_minimal()

        if False:
            pass
        elif self.has_driven and self.drive_left is not None:
            self.drive()
        elif self.has_driven and self.rotated2:
            self.set_rotation()

        elif self.has_driven and abs(self.rotation) > self.rotation_threshold:
            self.act(0, 0)
            self.take_picture_found_ball()
            self.rotation_threshold = ((abs(self.rotation) // self.rotate_value_second) + 1) * self.rotate_value_second
        elif self.has_driven:
            self.detect_new_balls()

        elif self.drive_left is not None:
            self.drive()
        elif abs(self.rotation) > 360 or self.rotated_one:
            self.rotated_one = True
            self.set_rotation()
        elif abs(self.rotation) > self.rotation_threshold:
            self.stand_still = True
            self.act(0, 0)
            self.rotation_threshold = ((abs(self.rotation) // self.rotate_value) + 1) * self.rotate_value
            self.take_picture()
        else:
            self.stand_still = False
            self.act(self.speed, -self.speed)

    def detect_new_balls(self):
        """Rotate robot until it finds both balls on either side and in the mean time take pictures."""
        if self.turn_left:
            if not self.filter_front_left():
                self.act(-self.speed, self.speed)
                self.immunity -= 1
            else:
                self.turn_left = False
                self.immunity = 10
                self.rotation_threshold = self.rotation
        else:
            if not self.filter_front_right() or self.immunity > 0:
                self.act(self.speed, -self.speed)
                self.immunity -= 1
            else:
                self.turn_left = True
                self.immunity = 10
                self.rotated2 = True

    def take_picture_found_ball(self):
        """Take the picture with the camera and finds balls."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        for image in camera:
            angle = self.camera_ball_angle(image)
            if image[0] == "blue ball":
                if self.blue_angle is None and image[2] < 30:
                    self.blue_angle = self.rotation + angle
                    self.blue_distance = image[2]
                else:
                    self.blue_angle = self.rotation + angle
                    self.blue_distance = image[2]
            else:
                if self.red_angle is None and image[2] < 30:
                    self.red_angle = self.rotation + angle
                    self.red_distance = image[2]
                else:
                    if image[2] >= self.red_distance and image[2] < 30:
                        self.red_angle = self.rotation + angle
                        self.red_distance = image[2]

    def take_picture(self):
        """Take the picture with the camera and finds balls."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        print(camera)
        for image in camera:
            angle = self.camera_ball_angle(image)
            if image[0] == "blue ball":
                if self.blue_angle is None:
                    self.blue_angle = self.rotation + angle
                    self.blue_distance = image[2]
                else:
                    if image[2] >= self.blue_distance:
                        self.blue_angle = self.rotation + angle
                        self.blue_distance = image[2]
            else:
                if self.red_angle is None:
                    self.red_angle = self.rotation + angle
                    self.red_distance = image[2]
                else:
                    if image[2] >= self.red_distance:
                        self.red_angle = self.rotation + angle
                        self.red_distance = image[2]

    def camera_ball_angle(self, image):
        """Take image and decide where is object and with what angle."""
        ball_width_degrees = self.robot.CAMERA_FIELD_OF_VIEW[0]  # deg
        ball_width = self.robot.CAMERA_RESOLUTION[0]
        object = image[1]
        x = object[0]
        half_width = ball_width / 2
        half_width_deg = ball_width_degrees / 2
        if x > half_width:
            right = True
            xpos = x - half_width
        else:
            right = False
            xpos = half_width - x
        ratio = xpos / half_width
        ratio_degrees = half_width_deg * ratio
        if right:
            angle = -ratio_degrees
        else:
            angle = ratio_degrees
        return angle

    def calculate_left_encoder(self):
        """Adjust left encoder."""
        while True:
            previous = self.robot.get_left_wheel_encoder()
            self.act(self.speed, 0)
            self.robot.sleep(0.05)
            self.act(0, 0)
            cur = self.robot.get_left_wheel_encoder()
            change = cur - previous
            if change <= 0:
                self.ln += 0.002
            else:
                break
        self.act(-self.speed, 0)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calculate_right_encoder(self):
        """Adjust the right encoder."""
        while True:
            previous = self.robot.get_right_wheel_encoder()
            self.act(0, self.speed)
            self.robot.sleep(0.05)
            self.act(0, 0)
            current = self.robot.get_right_wheel_encoder()
            change = current - previous
            if change <= 0:
                self.rn += 0.002
            else:
                break
        self.act(0, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calculate_all_encoders(self):
        """Adjust both encoders."""
        right_encoder_previous = self.robot.get_right_wheel_encoder()
        left_encoder_previous = self.robot.get_left_wheel_encoder()
        self.act(self.speed, self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)
        right_encoder = self.robot.get_right_wheel_encoder()
        left_encoder = self.robot.get_left_wheel_encoder()
        self.act(-self.speed, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)
        right_new = right_encoder - right_encoder_previous
        left_new = left_encoder - left_encoder_previous
        if left_new <= 0:
            self.calculate_left_encoder()
        if right_new <= 0:
            self.calculate_right_encoder()

    def adjust_all_minimal(self):
        """Adjust both encoders a little bit."""
        left_new = abs(self.left_encoder - self.left_encoder_previous)
        right_new = abs(self.right_encoder - self.right_encoder_previous)

        if right_new > self.change_speed_high:
            self.rn -= 0.002
        elif right_new < self.change_speed_low:
            self.rn += 0.002

        if left_new > self.change_speed_high:
            self.ln -= 0.002
        elif left_new < self.change_speed_low:
            self.ln += 0.002

        if right_new > left_new:
            self.ln += 0.001
        elif right_new < left_new:
            self.rn += 0.001

    def spin(self):
        """The main loop of the robot."""
        self.calculate_all_encoders()
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
