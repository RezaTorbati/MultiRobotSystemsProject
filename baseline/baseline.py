#This code was heavily inspired by the Robotarium's si_go_to_point_with_plotting.py example code
import rps.robotarium as robotarium
from rps.utilities.transformations import *
from rps.utilities.barrier_certificates import *
from rps.utilities.misc import *
from rps.utilities.controllers import *
import matplotlib.cm as cm
from agent import *

import numpy as np
import time

# Instantiate Robotarium object
N = 5
iterations = 1000 #Run the simulation/experiment for 1000 steps (1000*0.033 ~= 33sec)
initial_conditions = generate_initial_conditions(N)
goal_points = np.array(np.mat('1 0.5 -0.5 0 0.28; 0.8 -0.3 -0.75 0.1 0.34; 0 0 0 0 0'))
# print('goal: ', generate_initial_conditions(5))
# goal:  [[-1.5        -1.2         0.         -1.5         0.9       ]
#  [ 0.6        -0.3        -0.6         0.3        -0.9       ]
#  [-1.05489246 -0.81535694  1.73402179  1.28526254  3.10837128]]

r = robotarium.Robotarium(number_of_robots=N, show_figure=True, initial_conditions=initial_conditions, sim_in_real_time=False)

# Create single integrator position controller
single_integrator_position_controller = create_si_position_controller()

# Create barrier certificates to avoid collision
#si_barrier_cert = create_single_integrator_barrier_certificate()
si_barrier_cert = create_single_integrator_barrier_certificate_with_boundary()

_, uni_to_si_states = create_si_to_uni_mapping()

# Create mapping from single integrator velocity commands to unicycle velocity commands
si_to_uni_dyn = create_si_to_uni_dynamics_with_backwards_motion()

reward = np.zeros(N)

# define x initially
x = r.get_poses()
x_si = uni_to_si_states(x)
r.step()

# Plotting Parameters
goal_marker_size_m = 0.2
show_figure = True
CM = plt.cm.get_cmap('hsv', N+1) # Agent/goal color scheme

if show_figure:
    robot_marker_size_m = 0.2
    marker_size_goal = determine_marker_size(r,goal_marker_size_m)
    marker_size_robot = determine_marker_size(r, robot_marker_size_m)
    font_size = determine_font_size(r,0.1)
    line_width = 5

    # Create Goal Point Markers
    #Text with goal identification
    goal_caption = ['{0}'.format(ii) for ii in reward]

    #Plot text for caption
    goal_points_text = [r.axes.text(goal_points[0,ii], goal_points[1,ii]-robot_marker_size_m-.05, goal_caption[ii], fontsize=font_size, color='k',fontweight='bold',horizontalalignment='center',verticalalignment='center',zorder=-2)
    for ii in range(goal_points.shape[1])]

    goal_markers = [r.axes.scatter(goal_points[0,ii], goal_points[1,ii], s=marker_size_goal, marker='s', facecolors='none',edgecolors=CM(ii),linewidth=line_width,zorder=-2)
    for ii in range(goal_points.shape[1])]

    robot_markers = [r.axes.scatter(x[0,ii], x[1,ii], s=marker_size_robot, marker='o', facecolors='none',edgecolors=CM(ii),linewidth=line_width) 
    for ii in range(goal_points.shape[1])]


# While the number of robots at the required poses is less than N...
it = 0
while (it < iterations):
    # Get poses of agents
    x = r.get_poses()
    x_si = uni_to_si_states(x)

    # Create single-integrator control inputs
    dxi = single_integrator_position_controller(x_si, goal_points[:2][:])

    # Create safe control inputs (i.e., no collisions)
    dxi = si_barrier_cert(dxi, x_si)

    # Transform single integrator velocity commands to unicycle
    dxu = si_to_uni_dyn(dxi, x)

    # Set the velocities by mapping the single-integrator inputs to unciycle inputs
    r.set_velocities(np.arange(N), dxu)

    # Check if the agent is in the goal zone, reward if so
    robot_pos_matrix = np.vstack((x_si, x[2,:]))
    
    for i in range(N):
        reward[at_pose(np.roll(robot_pos_matrix, i, axis=1), goal_points, position_error=robot_marker_size_m, rotation_error=100)] += 1
    print(reward)
    
    if show_figure:
        #Update Plot
        # Update Robot Marker Plotted Visualization
        for i in range(x.shape[1]):
            robot_markers[i].set_offsets(x[:2,i].T)
            # This updates the marker sizes if the figure window size is changed. 
            # This should be removed when submitting to the Robotarium.
            robot_markers[i].set_sizes([determine_marker_size(r, robot_marker_size_m)])

        for j in range(goal_points.shape[1]):
            goal_points_text[j].set_text(reward[j])
            goal_markers[j].set_sizes([determine_marker_size(r, goal_marker_size_m)])

    # Iterate the simulation
    r.step()
    it += 1

#Call at end of script to print debug information and for your script to run on the Robotarium server properly
r.call_at_scripts_end()
