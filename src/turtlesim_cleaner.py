#!/usr/bin/env python

#Libraries

import rospy
from geometry_msgs.msg import Twist # for velocity 
from turtlesim.msg import Pose # for pose
import math
import time
from std_srvs.srv import Empty


#variable initialisation
x =0.0
y=0.0
yaw = 0.0


#pose callback - to get x,y & yaw values
def pose_callback(pose_data):
	global x,y,yaw
	x = pose_data.x
	y = pose_data.y
	yaw = pose_data.theta

	'''
	print("Pose Callback\n")
	print("x={} ,y={} ,yaw={}\n".format(x,y,yaw))
	'''
# move method for linear motion - to move bot in desired speed and for distance & direction specified
def move(speed,distance,is_forward):

	vel_msg = Twist() # declare object of type Twist i.e. to use linear and angular components of velocity
	#variable initialisation and assignment
	global x,y
	x0 = x
	y0 = y

	#speed depending on direction
	if (is_forward):
		vel_msg.linear.x = abs(speed)
	else:
		vel_msg.linear.x = -abs(speed)

	#move bot untill you reach the desired distance
	distance_moved = 0.0
	loop_rate = rospy.Rate(10) # publish velocity 10 times in a second
	print("x={},y={}".format(x,y))
	#declare velocity publisher
	'''
	either do it here/in main()
	'''
	t0 = rospy.Time.now().to_sec()

	while not(rospy.is_shutdown()):
		rospy.loginfo("Turtlesim Moves")
		# publish vel_msg i.e. write to the velocities
		vel_publisher.publish(vel_msg)

		loop_rate.sleep() # delay/pause for 0.1 seconds

		t1 = rospy.Time.now().to_sec()
		# calculate distance
		# distance_moved = distance_moved + 0.5 * abs(math.sqrt((x-x0)**2 + (y-y0)**2))
		# print("Distance Moved = {}".format(distance_moved))
		# print("x={},x0={}, y={},y0={}".format(x,x0,y,y0))
		distance_moved = (t1-t0)*speed

		if not(distance_moved<distance):
			rospy.loginfo("Reached")
			break
	#stop the bot, once reached

	vel_msg.linear.x = 0.0
	vel_publisher.publish(vel_msg)

# method for angular motion
# ROS by default uses angles in radians
def rotate(ang_speed_deg,rel_ang_deg,clockwise):
	global yaw
	vel_msg = Twist()

	#initialise velocities to 0
	vel_msg.linear.x = 0
	vel_msg.linear.y = 0
	vel_msg.linear.z = 0
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0

	#get current orientation
	theta0 = yaw

	ang_speed = math.radians(abs(ang_speed_deg)) # ROS understands only radians

	if (clockwise): # if clockwise, negative else positive
		vel_msg.angular.z = -abs(ang_speed)
	else:
		vel_msg.angular.z = abs(ang_speed)

	angle_moved = 0.0
	loop_rate = rospy.Rate(10) # 10 times in 1 second

	t0 = rospy.Time.now().to_sec() # get starting time in seconds

	while not(rospy.is_shutdown()):
		rospy.loginfo("Turtlesim Rotates")
		# publish the velocity
		vel_publisher.publish(vel_msg)

		#get current time t1
		t1 = rospy.Time.now().to_sec()
		current_ang_deg = (t1-t0)*ang_speed_deg # w = theta/t, theta = w*t

		if not(current_ang_deg<rel_ang_deg):
			rospy.loginfo("Reached")
			break

	#stop the bot
	vel_msg.angular.z = 0
	vel_publisher.publish(vel_msg)

def go_to_goal(x_goal,y_goal):
	global x,y,z,yaw

	vel_msg = Twist()

	while not(rospy.is_shutdown()):
		Kp_linear = 0.5 # proportional gain for linear control
		# calculate euclidean distance using distance formula
		distance = abs(math.sqrt((x_goal-x)**2 + (y_goal-y)**2))
		# calculate linear speed
		linear_speed = Kp_linear * distance

		Kp_angular = 4 # proportional gain for angular control
		# calculate goal angle using slop formual
		angle_goal = math.atan2(y_goal-y,x_goal-x)
		# calculate angular speed
		ang_speed = (angle_goal - yaw) * Kp_angular

		#assign values to message
		vel_msg.linear.x = linear_speed
		vel_msg.angular.z = ang_speed

		# publish the topic i.e. write the values
		vel_publisher.publish(vel_msg)
		print("x = {}, y = {}".format(x,y))

		if(distance < 0.01):
			break


# set desired orientation
def set_desired_orient(des_ang_deg):
	global yaw
	des_ang_rad = math.radians(des_ang_deg)

	rel_ang_rad = des_ang_rad - yaw
	rel_ang_deg = math.degrees(rel_ang_rad)
	if (rel_ang_rad>0):
		clockwise = False
	else:
		clockwise = True
	rotate(60,rel_ang_deg,clockwise)



# functions for grid_cleanup

#move up in grid
def grid_up():
	move(5.0,1.0,True)
	rotate(30,90,False)
	move(5.0,9.0,True)
	rotate(30,90,True)

#move down in grid
def grid_down():
	move(5.0,1.0,True)
	rotate(30,90,True)
	move(5.0,9.0,True)
	rotate(30,90,False)

#move in grid to clean the room
def grid_clean():
	global x,y,yaw
	x_i = 1
	y_i = 1
	yaw_i = 0

	go_to_goal(x_i,y_i)
	set_desired_orient(90)

	# grid_initialise
	move(5.0,9.0,True)
	rotate(30,90,True)
	
	while (not(rospy.is_shutdown()) and x<=9.5):
		grid_down()
		grid_up()




def spiral_clean():
	vel_msg = Twist()
	loop_rate = rospy.Rate(10) # 10 times in 1 second
	w_k = 10
	v_k = 0
	vel_msg.linear.x = 0
	vel_msg.linear.y = 0
	vel_msg.linear.z = 0

	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0
	vel_publisher.publish(vel_msg)
	while (not(rospy.is_shutdown()) and x<=10 and y<=10):
		v_k = v_k + 1.0
		vel_msg.linear.x = v_k
		vel_msg.angular.z = w_k
		vel_publisher.publish(vel_msg)
		loop_rate.sleep()

	#stop the bot
	vel_msg.linear.x = 0
	vel_msg.angular.z = 0
	vel_publisher.publish(vel_msg)



#python code
if __name__ == '__main__':
	try:
		rospy.init_node("cleaner",anonymous = True) #initialise node

		# declare velocity publisher
		vel_publisher = rospy.Publisher("/turtle1/cmd_vel",Twist,queue_size=10)

		# declare pose subscriber
		pose_subscriber = rospy.Subscriber("/turtle1/pose",Pose,pose_callback)

		time.sleep(2) #pause/delay for 2 seconds

		#sequence of functions
		
		# move(1.0,5.0,False)
		# rotate(30,90,False)
		
		#clean in grid
		# grid_clean()

		#clean in spiral
		spiral_clean()

	except rospy.ROSInterruptException:
		rospy.loginfo("Node Terminated")
