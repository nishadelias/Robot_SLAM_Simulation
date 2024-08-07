# Implement the second move model for the Lego robot.
# The difference to the first implementation is:
# - added a scanner displacement
# - added a different start pose (measured in the real world)
# - result is now output to a file, as "F" ("filtered") records.
#
# 02_b_filter_motor_file
# Claus Brenner, 09 NOV 2012
from math import sin, cos, pi
from lego_robot import *

# This function takes the old (x, y, heading) pose and the motor ticks
# (ticks_left, ticks_right) and returns the new (x, y, heading).
def filter_step(old_pose, motor_ticks, ticks_to_mm, robot_width,
                scanner_displacement):

    l = motor_ticks[0] * ticks_to_mm
    r = motor_ticks[1] * ticks_to_mm
    
    # Find out if there is a turn at all.
    if l == r:
        # No turn. Just drive straight.

        theta = old_pose[2]
        x = old_pose[0] + l * cos(theta)
        y = old_pose[1] + l * sin(theta)
        return (x, y, theta)

    else:
        # Turn. Compute alpha, R, etc.

        old_x = old_pose[0] - (scanner_displacement * cos(old_pose[2]))
        old_y = old_pose[1] - (scanner_displacement * sin(old_pose[2]))

        alpha = (r - l) / robot_width
        R = l / alpha
        cx = old_x - ((R + robot_width/2) * sin(old_pose[2]))
        cy = old_y + ((R + robot_width/2) * cos(old_pose[2]))
        theta = (old_pose[2] + alpha) % (2*pi)
        x = cx + ((R + robot_width/2) * sin(theta))
        x = x + (scanner_displacement * cos(theta))
        y = cy - ((R + robot_width/2) * cos(theta))
        y = y + (scanner_displacement * sin(theta))
        return (x, y, theta)


if __name__ == '__main__':
    # Empirically derived distance between scanner and assumed
    # center of robot.
    scanner_displacement = 30.0

    # Empirically derived conversion from ticks to mm.
    ticks_to_mm = 0.349

    # Measured width of the robot (wheel gauge), in mm.
    robot_width = 173.0

    # Measured start position.
    pose = (1850.0, 1897.0, 213.0 / 180.0 * pi)

    # Read data.
    logfile = LegoLogfile()
    logfile.read("robot4_motors.txt")

    # Loop over all motor tick records generate filtered position list.
    filtered = []
    for ticks in logfile.motor_ticks:
        pose = filter_step(pose, ticks, ticks_to_mm, robot_width,
                           scanner_displacement)
        filtered.append(pose)

    # Write all filtered positions to file.
    f = open("poses_from_ticks.txt", "w")
    for pose in filtered:
        line = "F %f %f %f\n" % pose
        f.write(line)
    f.close()
