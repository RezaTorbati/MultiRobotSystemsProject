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
N = 2
iterations = 450 #Run the simulation/experiment for 1000 steps (1000*0.033 ~= 33sec)
goal_points = np.array([[.5, -.5], [.2,-.2], [0,0]])

# Create single integrator position controller
single_integrator_position_controller = create_si_position_controller()
# Create barrier certificates to avoid collision
si_barrier_cert = create_single_integrator_barrier_certificate_with_boundary()

_, uni_to_si_states = create_si_to_uni_mapping()

# Create mapping from single integrator velocity commands to unicycle velocity commands
si_to_uni_dyn = create_si_to_uni_dynamics_with_backwards_motion()

agents = PD_Tagged_Agents(num_agents=100)
show_figure = False

trainingSteps = 2000
for step in range(trainingSteps):
    scores = [0,0]
    print(step)
    playingAgents = agents.select_agents()
    for p in playingAgents:
        print(p)
    goals = []
    for i in range(3):
        goal = []
        for j in range(N):
            if playingAgents[j].collaborate == True:
                if j == N-1:
                    goal.append(goal_points[i][0])
                else:
                    goal.append(goal_points[i][j+1])
            else:
                goal.append(goal_points[i][j])
        goals.append(goal)
    goals = np.array(goals)
    initial_conditions = np.array(np.mat('-1 1; 0 0; 0 3.14'))
    r = robotarium.Robotarium(number_of_robots=N, show_figure=show_figure, initial_conditions=initial_conditions, sim_in_real_time=False)

    # define x initially
    x = r.get_poses()
    x_si = uni_to_si_states(x)

    # Plotting Parameters
    CM = np.random.rand(N,3) # Random Colors

    goal_marker_size_m = 0.2
    boundaries = []
    for i in range(3):
        boundary = []
        for j in range(N):
            #boundary.append([[goal_points[0][i] - goal_marker_size_m, goal_points[0][i] + goal_marker_size_m], [goal_points[1][i] - goal_marker_size_m, goal_points[1][i] + goal_marker_size_m]])
            boundary.append([goal_points[i][j] - goal_marker_size_m,goal_points[i][j] + goal_marker_size_m])
        boundaries.append(boundary)

    scores = [0] * N #The score for each agent

    if show_figure:
        robot_marker_size_m = 0.2
        marker_size_goal = determine_marker_size(r,goal_marker_size_m)
        marker_size_robot = determine_marker_size(r, robot_marker_size_m)
        font_size = determine_font_size(r,0.1)
        line_width = 5

        # Create Goal Point Markers
        #Text with goal identification
        goal_caption = ['{0}'.format(ii) for ii in scores]
        #Plot text for caption
        goal_points_text = [r.axes.text(goal_points[0,ii], goal_points[1,ii]-robot_marker_size_m-.05, goal_caption[ii], fontsize=font_size, color='k',fontweight='bold',horizontalalignment='center',verticalalignment='center',zorder=-2)
        for ii in range(goal_points.shape[1])]

        goal_markers = [r.axes.scatter(goal_points[0,ii], goal_points[1,ii], s=marker_size_goal, marker='s', facecolors='none',edgecolors=CM[ii,:],linewidth=line_width,zorder=-2)
        for ii in range(goal_points.shape[1])]

        robot_markers = [r.axes.scatter(x[0,ii], x[1,ii], s=marker_size_robot, marker='o', facecolors='none',edgecolors=CM[ii,:],linewidth=line_width) 
        for ii in range(goal_points.shape[1])]

    r.step()

    for t in range(iterations):
        # Get poses of agents
        x = r.get_poses()

        #Update the agents' scores
        for i in range(N):
            for j in range(N):
                if x[0][j] >= boundaries[0][i][0] and x[0][j] <= boundaries[0][i][1]:
                    if x[1][j] >= boundaries[1][i][0] and x[1][j] <= boundaries[1][i][1]:
                        scores[i] += 1

        x_si = uni_to_si_states(x)

        #Update Plot
        # Update Robot Marker Plotted Visualization
        if show_figure:
            for i in range(x.shape[1]):
                robot_markers[i].set_offsets(x[:2,i].T)
                # This updates the marker sizes if the figure window size is changed. 
                # This should be removed when submitting to the Robotarium.
                robot_markers[i].set_sizes([determine_marker_size(r, robot_marker_size_m)])

            for j in range(goal_points.shape[1]):
                goal_points_text[j].set_text(scores[j])
                goal_markers[j].set_sizes([determine_marker_size(r, goal_marker_size_m)])

        # Create single-integrator control inputs
        dxi = single_integrator_position_controller(x_si, goals[:2][:])

        # Create safe control inputs (i.e., no collisions)
        dxi = si_barrier_cert(dxi, x_si)

        # Transform single integrator velocity commands to unicycle
        dxu = si_to_uni_dyn(dxi, x)

        # Set the velocities by mapping the single-integrator inputs to unciycle inputs
        r.set_velocities(np.arange(N), dxu)
        # Iterate the simulation
        r.step()
    for p in range(len(playingAgents)):
        playingAgents[p].score = scores[p]
    print(scores)
agents.stats.pltCollaborating()

#Call at end of script to print debug information and for your script to run on the Robotarium server properly
r.call_at_scripts_end()
