"""."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.once = True

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

        self.fm4 = 0.5
        self.fm3 = 0.5
        self.fm2 = 0.5
        self.fm1 = 0.5
        # last value is the newest
        self.front = []

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
        self.lenght = 0
        self.left_start = 0
        self.right_start = 0

        self.ihaveseen = False

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
        # print("left lasers")
        # print(f"dis {self.left_side} {self.left_diagonal} {self.left_back}")
        # print("right lasers")
        # print(f"dis {self.right_side} {self.right_diagonal} {self.right_back}")
        print("front lasers")
        print(f"dis {self.fl} {self.fm} {self.fr}")
        print("indexs")
        print(f"{self.ln} | {self.rn}")
        print("prev encoders")
        print(f"{self.leftep} | {self.rightep}")
        print("encoders")
        print(f"{self.lefte} | {self.righte} | An {self.lenght}")
        print("change")
        print(f"{self.lefte - self.leftep} | {self.righte - self.rightep}")

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        # encoders
        self.leftep = self.lefte
        self.lefte = self.robot.get_left_wheel_encoder()
        self.rightep = self.righte
        self.righte = self.robot.get_right_wheel_encoder()

        # # fm
        # self.fm4 = self.fm3
        # self.fm3 = self.fm2
        # self.fm2 = self.fm1
        # self.fm1 = self.fm

        # front 10-100 cm
        self.fl = self.robot.get_front_left_laser()
        self.fm = self.robot.get_front_middle_laser()
        self.fr = self.robot.get_front_right_laser()

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

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_left_wheel_speed(left_wheel * self.ln)
        self.robot.set_right_wheel_speed(right_wheel * self.rn)

    def filter(self):
        """."""
        # if self.fm > 0.5:
        #     self.fm = 0.5
        lista = self.front
        a = lista.count(0.5)
        b = len(lista) - a
        return b > a

    def filter2(self):
        """."""
        lista = self.front
        listb = list(filter(lambda x: x < 0.11, lista))
        # väiksemad kui 0.11
        b = len(listb)
        # suuremad
        a = len(lista) - b
        return b > a

    def plan_left(self, left):
        """."""
        if left > self.adjust_high:
            self.ln -= 0.002
        elif left < self.adjust_low:
            self.ln += 0.002

    def plan_right(self, right):
        """."""
        if right > self.adjust_high:
            self.rn -= 0.002
        elif right < self.adjust_low:
            self.rn += 0.002

    def plan_both(self, left, right):
        """."""
        if right > left:
            self.rn -= 0.001
            self.ln += 0.001
        elif right < left:
            self.rn += 0.001
            self.ln -= 0.001

    def plan_fwrd(self):
        """."""
        if abs(self.left_start) + self.lenght <= self.lefte or abs(self.right_start) + self.lenght <= self.righte:
            self.right_start = self.robot.get_right_wheel_encoder()
            self.left_start = self.robot.get_left_wheel_encoder()
            print("drive fwrd")
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
            self.ihaveseen = True
            print("smaller")
            self.right_start = self.robot.get_right_wheel_encoder()
            self.left_start = self.robot.get_left_wheel_encoder()
            if self.once:
                print("ONCE")
                self.once = False
                self.act(self.speed, -self.speed)
                self.robot.sleep(0.1)
            self.act(self.speed, self.speed)
            if self.filter2():
                self.ultra_spin()
                self.shutdown = True
        elif self.ihaveseen:
            if self.fm == 0.5 and self.fl == 0.5:
                self.act(self.speed, -self.speed)
        else:
            self.act(-self.speed, self.speed)

    def ultra_spin(self):
        """."""
        print("spin")
        self.act(0, 0)

    def calc_left(self):
        """."""
        # ln = self.ln
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
            # elif change < 0:
            #     self.ln = ln
            #     break
            else:
                break
        self.act(-self.speed, 0)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calc_right(self):
        """."""
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
            # elif change < 0:
            #     self.rn = rn
            #     break
            else:
                break
        self.act(0, -self.speed)
        self.robot.sleep(0.05)
        self.act(0, 0)

    def calculate(self):
        """."""
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

    def calc_angle(self):
        """."""
        wh = self.robot.WHEEL_DIAMETER
        al = self.robot.AXIS_LENGTH
        lenght = (360 * al) / wh
        self.lenght = int(0.9 * lenght)

    def spin(self):
        """The main loop of the robot."""
        self.calculate()
        print(self.ln, self.rn)
        self.calc_angle()
        self.right_start = self.robot.get_right_wheel_encoder()
        self.left_start = self.robot.get_left_wheel_encoder()
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
