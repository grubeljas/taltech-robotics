"""."""
import PiBot


class Robot:
    """Robot classes."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.once = True
        self.front_left_laser = 2
        self.front_middle_laser = 2
        self.front_right_laser = 2

        self.rn = 1.0
        self.ln = 1.0

        self.fm4 = 0.5
        self.fm3 = 0.5
        self.fm2 = 0.5
        self.fm1 = 0.5

        self.leftep = 0
        self.lefte = 0
        self.righte = 0
        self.rightep = 0

        self.front = []

        self.left_side = None
        self.left_diagonal = None
        self.left_back = None

        self.right_back = None
        self.right_side = None
        self.right_diagonal = None

        self.speed = 8
        self.change_to_low = 4
        self.change_to_high = 5
        self.length = 0
        self.left_start_speed = 0
        self.right_start_speed = 0

        self.has_been = False

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
        print(f"dis {self.front_left_laser} {self.front_middle_laser} {self.front_right_laser}")
        print("indexs")
        print(f"{self.ln} | {self.rn}")
        print("prev encoders")
        print(f"{self.leftep} | {self.rightep}")
        print("change")
        print(f"{self.lefte - self.leftep} | {self.righte - self.rightep}")
        print("encoders")
        print(f"{self.lefte} | {self.righte} | An {self.length}")

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        self.leftep = self.lefte
        self.lefte = self.robot.get_left_wheel_encoder()
        self.rightep = self.righte
        self.righte = self.robot.get_right_wheel_encoder()

        self.front_left_laser = self.robot.get_front_left_laser()
        self.front_middle_laser = self.robot.get_front_middle_laser()
        self.front_right_laser = self.robot.get_front_right_laser()

        if self.front_middle_laser > 0.5:
            self.front_middle_laser = 0.5
        self.front.append(self.front_middle_laser)
        if len(self.front) == 6:
            self.front.pop(0)

        self.left_back = self.robot.get_rear_left_straight_ir()
        self.left_diagonal = self.robot.get_rear_left_diagonal_ir()
        self.left_side = self.robot.get_rear_left_side_ir()

        self.right_back = self.robot.get_rear_right_straight_ir()
        self.right_diagonal = self.robot.get_rear_right_diagonal_ir()
        self.right_side = self.robot.get_rear_right_side_ir()

    def act(self, left_wheel, right_wheel):
        """Set the left and right wheel value that has been modified to change the speed the right amount."""
        self.robot.set_left_wheel_speed(left_wheel * self.ln)
        self.robot.set_right_wheel_speed(right_wheel * self.rn)

    def filter(self):
        """Filter the front laser to tell if there is an object there."""
        lista = self.front
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a

    def filter2(self):
        """Filter the front laser to tell if the robot is close enough to the object."""
        lista = self.front
        listb = list(filter(lambda x: x < 0.11, lista))
        b = len(listb)
        a = len(lista) - b
        return b > a

    def plan_left(self, left):
        """Adjust the left wheel to be in the correct change range."""
        if left > self.change_to_high:
            self.ln -= 0.002
        elif left < self.change_to_low:
            self.ln += 0.002

    def plan_right(self, right):
        """Adjust the right wheel to be in the correct change range."""
        if right > self.change_to_high:
            self.rn -= 0.002
        elif right < self.change_to_low:
            self.rn += 0.002

    def plan_both(self, left, right):
        """Adjust both wheels to give the same change value (4 or 5)."""
        if right > left:
            self.rn -= 0.001
            self.ln += 0.001
        elif right < left:
            self.rn += 0.001
            self.ln -= 0.001

    def plan_fwrd(self):
        """Drive the robot forward if it has spun enough degrees."""
        if abs(self.left_start_speed) + self.length <= self.lefte or abs(
                self.right_start_speed) + self.length <= self.righte:
            self.right_start_speed = self.robot.get_right_wheel_encoder()
            self.left_start_speed = self.robot.get_left_wheel_encoder()
            print("drive forward")
            self.act(self.speed, self.speed)
            self.robot.sleep(2)

    def plan(self):
        """Perform the planning steps as required by the problem statement."""
        left = abs(self.lefte - self.leftep)
        right = abs(self.righte - self.rightep)

        # adjust
        self.plan_left(left)
        self.plan_right(right)
        self.plan_both(left, right)
        self.plan_fwrd()

        if self.filter():
            self.has_been = True
            print("smaller")
            self.right_start_speed = self.robot.get_right_wheel_encoder()
            self.left_start_speed = self.robot.get_left_wheel_encoder()
            if self.once:
                print("ONCE")
                self.once = False
                self.act(self.speed, -self.speed)
                self.robot.sleep(0.1)
            self.act(self.speed, self.speed)
            if self.filter2():
                self.ultra_spin()
                self.shutdown = True
        elif self.has_been:
            if self.front_middle_laser == 0.5 and self.front_left_laser == 0.5:
                self.act(self.speed, -self.speed)
        else:
            self.act(-self.speed, self.speed)

    def ultra_spin(self):
        """Stop the robot robot."""
        print("spin robot")
        self.act(0, 0)

    def calculate(self):
        """Adjust both wheels so that they change the right amount."""
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

    def calc_right(self):
        """Adjust the right wheel to change the right amount."""
        while True:
            print(self.ln, self.rn)
            prev = self.robot.get_right_wheel_encoder()
            self.act(0, self.speed)
            self.robot.sleep(0.05)
            self.act(0, 0)
            cur = self.robot.get_right_wheel_encoder()
            change = cur - prev
            print(cur, prev)
            if change <= 0:
                self.rn += 0.002
            else:
                break
        self.act(0, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calc_left(self):
        """Adjust the left wheel to change the right amount."""
        while True:
            print(self.ln, self.rn)
            prev = self.robot.get_left_wheel_encoder()
            self.act(self.speed, 0)
            self.robot.sleep(0.05)
            self.act(0, 0)
            cur = self.robot.get_left_wheel_encoder()
            change = cur - prev
            print(cur, prev)
            if change <= 0:
                self.ln += 0.002
            else:
                break
        self.act(-self.speed, 0)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calc_angle(self):
        """Find the angle needed to spin before driving forward."""
        wh = self.robot.WHEEL_DIAMETER
        al = self.robot.AXIS_LENGTH
        lenght = (360 * al) / wh
        self.length = int(0.9 * lenght)

    def spin(self):
        """The main loop of the robot."""
        self.calculate()
        print(self.ln, self.rn)
        self.calc_angle()
        self.right_start_speed = self.robot.get_right_wheel_encoder()
        self.left_start_speed = self.robot.get_left_wheel_encoder()
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
