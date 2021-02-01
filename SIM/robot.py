from PiBot import PiBot
robot = PiBot()

front_distance = robot.get_front_middle_laser()
print(front_distance)
robot.set_wheels_speed(15)
while front_distance > 0.18:
    robot.sleep(0.01)
    front_distance = robot.get_front_middle_laser()
    print(front_distance)
robot.set_wheels_speed(0)
