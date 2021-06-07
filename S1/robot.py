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

        self.laser_left = 2
        self.laser_middle = 2
        self.laser_right = 2

        self.front = [0]
        self.front_left = [0]

        self.left_side = None
        self.left_diagonal = None
        self.left_back = None

        self.right_back = None
        self.right_side = None
        self.right_diagonal = None

        self.speed = 8
        self.adjust_low = 4
        self.adjust_high = 5

        self.saw_blue = False
        self.lined_up = False
        self.front_saw_blue = False
        self.wait_1_cycle = False
        self.rotation = 0
        self.rotation_threshold = 0
        self.rotation_value = 45
        self.blue_angle = 0
        self.completed = False
        self.turn_right = True
        self.number = 100
        self.reached_blue_ball = False

        self.red_number = 50
        self.lined_up_red = False
        self.ready = False
        self.drive_forward = 0
        self.rotation_start = -360
        self.rotation_add = 30
        self.red_angle = 0
        self.saw_red = False
        self.final = False
        self.current_rot = 0

        self.red_l = 0
        self.red_r = 0
        self.red_radius = 0

        self.long_drive = False
        self.stand_still = False
        self.forward_once = True
        self.end_left = 0
        self.end_right = 0

        self.fmd = 0.5
        self.fmc = 0.5
        self.fmb = 0.5
        self.fma = 0.5

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
        print(f"distance {self.laser_left} {self.laser_middle} {self.laser_right}")
        print("change")
        print(f"{self.left_encoder - self.left_encoder_previous} | {self.right_encoder - self.right_encoder_previous}")
        print("rotation")
        print(self.rotation, self.rotation_threshold, self.blue_angle, self.red_angle)
        print("nr fwr")
        print(self.number, self.drive_forward)

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        self.left_encoder_previous = self.left_encoder
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder_previous = self.right_encoder
        self.right_encoder = self.robot.get_right_wheel_encoder()

        self.laser_left = self.robot.get_front_left_laser()
        self.laser_middle = self.robot.get_front_middle_laser()
        self.laser_right = self.robot.get_front_right_laser()

        if self.laser_left > 0.5:
            self.laser_left = 0.5
        self.front_left.append(self.laser_left)
        if len(self.front_left) == 6:
            self.front_left.pop(0)

        if self.laser_middle > 0.5:
            self.laser_middle = 0.5
        self.front.append(self.laser_middle)
        if len(self.front) == 6:
            self.front.pop(0)

        self.left_diagonal = self.robot.get_rear_left_diagonal_ir()
        self.left_back = self.robot.get_rear_left_straight_ir()
        self.left_side = self.robot.get_rear_left_side_ir()

        self.right_diagonal = self.robot.get_rear_right_diagonal_ir()
        self.right_back = self.robot.get_rear_right_straight_ir()
        self.right_side = self.robot.get_rear_right_side_ir()

        self.rotation = self.robot.get_rotation()

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_left_wheel_speed(left_wheel * self.ln)
        self.robot.set_right_wheel_speed(right_wheel * self.rn)

    def set_rotation(self, blue=True):
        """Set the robot rotation to the needed value (blue or red angle)."""
        if blue:
            difference = abs(self.rotation - self.blue_angle)
            if difference < 0.25:
                self.lined_up = True
                self.stand_still = True
                self.act(0, 0)
            elif self.rotation > self.blue_angle:
                self.stand_still = False
                self.act(self.speed, -self.speed)
            elif self.rotation < self.blue_angle:
                self.stand_still = False
                self.act(-self.speed, self.speed)
        else:
            difference = abs(self.rotation - self.red_angle)
            if difference < 0.25:
                self.lined_up_red = True
                self.stand_still = True
                self.act(0, 0)
                if self.red_l == 0:
                    self.red_l = self.left_encoder
                    self.red_r = self.right_encoder
            elif self.rotation > self.red_angle:
                self.stand_still = False
                self.act(self.speed, -self.speed)
            elif self.rotation < self.red_angle:
                self.stand_still = False
                self.act(-self.speed, self.speed)

    def drive_forward_025_units(self):
        """Drive the robot forward 25(may change) units."""
        if self.forward_once:
            start_left = self.left_encoder
            start_right = self.right_encoder
            wh = self.robot.WHEEL_DIAMETER
            a = (0.10 * 360) / (wh * 3.1415)
            self.end_left = start_left + a
            self.end_right = start_right + a
            self.forward_once = False

        if self.left_encoder > self.end_left or self.right_encoder > self.end_right:
            print("drove 10")
            self.act(0, 0)
            self.stand_still = True
            self.take_picture()
            self.lined_up = False
            self.forward_once = True
            self.completed = True
        else:
            self.stand_still = False
            self.act(self.speed, self.speed)

    def turn_until_left_sees(self):
        """Turn the robot until front laser sees object."""
        if self.filter_left_close():
            self.ready = True
            self.rotation_start = -360
            self.act(0, 0)
            self.stand_still = True
        else:
            self.stand_still = False
            self.act(self.speed, -self.speed)

    def filter_left_close(self):
        """Filter front left laser until it sees object and it makes sure its not too close."""
        lista = self.front_left
        listb = list(filter(lambda x: x < 0.2, lista))
        listc = list(filter(lambda x: x < 0.15, lista))
        c = len(listc)
        if c > len(lista) - c:
            self.drive_forward = 200
        b = len(listb)
        a = len(lista) - b
        return b > a

    def filter(self):
        """Filter object (0.5)."""
        lista = self.front
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a

    def filter_left(self):
        """Filter object with front left laser."""
        lista = self.front_left
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a

    def filter_front(self):
        """Filter object with front laser if it is close."""
        lista = self.front
        listb = list(filter(lambda x: x < 0.15, lista))
        b = len(listb)
        a = len(lista) - b
        return b - 1 > a

    def avrage_fl(self):
        """Give the avraged value of laser."""
        value = 0
        for i in self.front:
            value += i
        return value / 5

    def rotate_right(self):
        """Rotate the robot 90(may change) degrees."""
        if self.rotation < self.current_rot + 80:
            self.act(-self.speed, self.speed)
            self.stand_still = False
        else:
            self.stand_still = True
            self.act(self.speed, self.speed)
            self.robot.sleep(2)
            self.act(0, 0)
            self.shutdown = True

    def drive_half(self, a):
        """Drive the half the distence calculated with the camera."""
        distance = self.robot.WHEEL_DIAMETER * 3.1415 * (self.left_encoder - self.red_l) / 360
        print(distance, a)
        if distance > a * 0.4:
            self.current_rot = self.rotation
            self.final = True
        else:
            self.act(self.speed, self.speed)
        pass

    def plan(self):
        """Main plan function."""
        if not self.stand_still:
            self.adjust_little()

        if self.final:
            self.rotate_right()
        elif self.lined_up_red:
            a = 30 / self.red_radius
            self.drive_half(a)
        elif self.saw_red:
            self.set_rotation(blue=False)
        elif self.ready and self.rotation_start + self.rotation_add < self.rotation:
            self.rotation_start = self.rotation
            self.act(0, 0)
            self.stand_still = True
            self.take_picture_red()
        elif self.ready:
            self.drives_around_object()
        else:
            self.blue_plan()

    def blue_plan(self):
        """Plan for getting to the blue ball."""
        if self.reached_blue_ball:
            self.turn_until_left_sees()
        elif self.lined_up:
            self.go_to_object()
        elif self.saw_blue:
            self.set_rotation()
        elif abs(self.rotation) > 360 and not self.long_drive:
            self.if_no_object()
        elif abs(self.rotation) > self.rotation_threshold:
            self.calculates_turn()
        else:
            self.robot_rotate()

    def robot_rotate(self):
        """Rotate robot right."""
        self.stand_still = False
        self.act(self.speed, -self.speed)

    def calculates_turn(self):
        """Calculate next turn threshold and take picture."""
        self.act(0, 0)
        self.rotation_threshold = ((abs(self.rotation) // self.rotation_value) + 1) * self.rotation_value
        self.take_picture()

    def if_no_object(self):
        """If didnt find object then drive forward."""
        self.long_drive = True
        self.act(-self.speed, self.speed)
        self.robot.sleep(4)
        self.act(self.speed + 2, self.speed + 2)
        self.robot.sleep(15)
        self.sense()
        self.rotation_threshold = ((abs(self.rotation) // self.rotation_value)) * self.rotation_value

    def go_to_object(self):
        """Drive towards the object."""
        if self.filter():
            self.number -= 1
            if self.number < 0:
                self.number = 75
                self.act(0, 0)
                self.lined_up = False
                self.stand_still = True
                self.take_picture()
            else:
                self.front_saw_blue = True
                self.act(self.speed, self.speed)
                self.stand_still = False
                self.turn_right = True
                if self.filter_front():
                    self.reached_blue_ball = True
                    self.act(0, 0)
                    self.stand_still = True
        elif self.front_saw_blue:
            self.act(self.speed, self.speed)
            self.robot.sleep(0.15)
            self.act(0, 0)
            self.lined_up = False
            self.stand_still = True
            self.take_picture()
        else:
            self.drive_forward_025_units()

    def drives_around_object(self):
        """Drive around the object (blue ball)."""
        self.stand_still = False
        if self.drive_forward > 0:
            self.drive_forward -= 1
            self.act(self.speed, self.speed)
        elif self.filter_left_close():
            self.act(self.speed, self.speed)
        else:
            self.act(-self.speed, self.speed)

    def take_picture_red(self):
        """Take the picture with the camera and finds red ball."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        print(camera)
        for image in camera:
            if image[0] == "red sphere":
                width_deg = self.robot.CAMERA_FIELD_OF_VIEW[0]
                width = self.robot.CAMERA_RESOLUTION[0]
                object = image[1]
                self.red_radius = image[2]
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
                self.red_angle = self.rotation + angle
                self.saw_red = True
                self.stand_still = True
                print(self.red_angle)

    def take_picture(self):
        """Take the picture with the camera and finds blue ball."""
        camera = self.robot.get_camera_objects()
        self.robot.sleep(0.3)
        print(camera)
        for image in camera:
            if image[0] == "blue sphere":
                width_deg = self.robot.CAMERA_FIELD_OF_VIEW[0]
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
                self.blue_angle = self.rotation + angle
                self.saw_blue = True
                self.stand_still = True
                print(self.blue_angle)

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

    def calculate_encoders(self):
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

    def adjust_little(self):
        """Adjust both encoders a little bit."""
        left = abs(self.left_encoder - self.left_encoder_previous)
        right = abs(self.right_encoder - self.right_encoder_previous)

        if left > self.adjust_low:
            self.ln -= 0.002
        elif left < self.adjust_low:
            self.ln += 0.002

        if right > self.adjust_low:
            self.rn -= 0.002
        elif right < self.adjust_low:
            self.rn += 0.002

    def spin(self):
        """The main loop of the robot."""
        self.calculate_encoders()
        print(self.ln, self.rn)
        self.robot.set_grabber_height(0)
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
