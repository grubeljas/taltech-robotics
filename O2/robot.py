"""O2."""
import PiBot
from collections import Counter


class Robot:
    """Robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        # 1 is more recent value
        self.laser1 = None
        self.laser2 = None
        self.laser3 = None
        self.laser4 = None
        self.laser5 = None

        self.right_turn = 0
        self.last_right = None
        self.right = None

        self.left_turn = 0
        self.last_left = None
        self.left = None

        self.angle = 0
        self.added = False
        self.objects = []

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set Robot reference."""
        self.robot = robot

    def get_objects(self) -> list:
        """
        Return the list with the detected objects so far.

        (i.e., add new objects to the list as you detect them).

        Returns:
          The list with detected object angles, the angles are in
          degrees [0..360), 0 degrees being the start angle and following
          the right-hand rule (e.g., turning left 90 degrees is 90, turning
          right 90 degrees is 270 degrees).
        """
        i = self.get_front_middle_laser()
        if i > 0.5:
            i = 0.5
        if i < 0.45 and not self.added and i != 0:
            self.objects.append(360 - self.angle)
            self.added = True
        elif i > 0.45 and self.added:
            self.added = False
        return self.objects

    def get_front_middle_laser(self):
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        lista = [self.laser5, self.laser4, self.laser3, self.laser2, self.laser1]
        lista = list(filter(lambda x: x is not None, lista))
        lista.sort()

        if not lista:
            return None
        else:
            while len(lista) <= 2:
                lista.insert(0, 0)
            return lista[2]

    def sense(self):
        """Sense method according to the SPA architecture."""
        self.laser5 = self.laser4
        self.laser4 = self.laser3
        self.laser3 = self.laser2
        self.laser2 = self.laser1
        self.laser1 = self.robot.get_front_middle_laser()

        self.last_left = self.left
        self.last_right = self.right
        self.left = self.robot.get_left_wheel_encoder()
        self.right = self.robot.get_right_wheel_encoder()

        if self.last_left is not None:
            right_delta = self.right - self.last_right
            left_delta = self.left - self.last_left
            if left_delta != 0 or right_delta != 0:
                self.left_turn += left_delta
                self.right_turn += right_delta
                while self.left_turn > 0 and self.right_turn < 0:
                    self.left_turn -= 1
                    self.right_turn += 1
                    self.get_angle(True)
                while self.left_turn < 0 and self.right_turn > 0:
                    self.left_turn += 1
                    self.right_turn -= 1
                    self.get_angle(False)

    def get_angle(self, right):
        """."""
        wd = self.robot.WHEEL_DIAMETER
        al = self.robot.AXIS_LENGTH
        a = wd / al
        if right:
            self.angle += a
        else:
            self.angle -= a
        pass

    def plan(self):
        """Plan - decides what to do based on the information."""
        pass

    def act(self):
        """Act - does stuff based on the decision made."""
        self.robot.set_left_wheel_speed(self.left_wheel_speed)
        self.robot.set_right_wheel_speed(self.right_wheel_speed)

    def spin(self):
        """The main loop."""
        while not self.shutdown:
            self.sense()
            print(f'Value is {self.get_front_middle_laser()}')
            self.plan()
            self.act()
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
