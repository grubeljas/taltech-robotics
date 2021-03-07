"""OT08 - PID."""
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()

        self.left_setpoint = 0
        self.right_setpoint = 0

        self.right_pid = 0
        self.left_pid = 0

        self.left_cur = 0
        self.left_prev = 0
        self.right_cur = 0
        self.right_prev = 0

        self.p = None
        self.i = None
        self.d = None

        self.cur_time = 0
        self.prev_time = 0

        self.right_error_dt = 0
        self.left_error_dt = 0

        self.right_error = 0
        self.left_error = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

    def set_pid_parameters(self, p: float, i: float, d: float):
        """
        Set the PID parameters.

        Arguments:
          p -- The proportional component.
          i -- The integral component.
          d -- The derivative component.
        """
        self.p = p
        self.i = i
        self.d = d
        pass

    def set_left_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.left_setpoint = speed

    def set_right_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.right_setpoint = speed

    def get_left_wheel_pid_output(self):
        """
        Get the controller output value for the left motor.

        Returns:
          The controller output value.
        """
        return self.left_pid

    def get_right_wheel_pid_output(self):
        """
        Get the controller output value for the right motor.

        Returns:
          The controller output value.
        """
        return self.right_pid

    def sense(self):
        """SPA architecture sense block."""
        # Your code here...
        self.left_prev = self.left_cur
        self.left_cur = self.robot.get_left_wheel_encoder()
        self.right_prev = self.right_cur
        self.right_cur = self.robot.get_right_wheel_encoder()
        self.prev_time = self.cur_time
        self.cur_time = self.robot.get_time()

        pass

    def act(self):
        """SPA architecture act block."""
        dt = self.cur_time - self.prev_time

        if self.right_prev is not None and self.right_setpoint is not None:
            self.prev_right_error = self.right_error
            self.right_error = self.right_setpoint - self.robot.right_wheel_speed
            right_error_dif = self.right_error - self.prev_right_error
            self.right_error_dt += self.right_error * dt
            self.right_pid = self.p * self.right_error + self.i * self.right_error_dt + self.d * right_error_dif
        else:
            self.right_pid = 0

        if self.left_prev is not None and self.left_setpoint is not None:
            self.prev_left_error = self.left_error
            self.left_error = self.left_setpoint - self.robot.left_wheel_speed
            left_error_dif = self.left_error - self.prev_left_error
            self.left_error_dt += self.left_error * dt
            self.left_pid = self.p * self.left_error + self.i * self.left_error_dt + self.d * left_error_dif
        else:
            self.left_pid = 0

        self.robot.set_left_wheel_speed(self.left_pid)
        self.robot.set_right_wheel_speed(self.right_pid)

    def spin(self):
        """Spin loop."""
        for _ in range(200):
            self.sense()
            self.act()
            print(self.get_left_wheel_pid_output(), self.get_right_wheel_pid_output())
            self.robot.sleep(0.20)


def main():
    """The main entry point."""
    robot = Robot()
    robot.robot.set_coefficients(1.0, 0.7)
    robot.set_pid_parameters(0.1, 0.04, 0.001)
    robot.set_left_wheel_speed(400)  # degs/s
    robot.set_right_wheel_speed(400)  # degs/s
    robot.spin()


if __name__ == "__main__":
    main()
