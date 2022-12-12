#This code was heavily inspired by the Robotarium's si_go_to_point_with_plotting.py example code
import rps.robotarium as robotarium
from rps.utilities.transformations import *
from rps.utilities.barrier_certificates import *
from rps.utilities.misc import *
from rps.utilities.controllers import *
from agent import *

import numpy as np
import random

# Instantiate Robotarium object

#Run simulations where
#p = .25 and s=100, p=.05 s=400, p=.01 s=1000

N = 20 #Number of agents
G = 4 #Number of goals

p = .25 #How likely a zone will be reloaded every update iteration
s = 100 #How much a zone will be reloaded by every time one gets reloaded

expType = 'expResults/Local/local_notags_s100p25' #set to '' if don't want to save results
evolve = True
helpRadius = 1.2 #set to something large to ignore the radius parameter
evolveRadius = helpRadius #set to -1 to ignore
evolveFrequency = 5 #Evolves once per this many updates
updateFrequency = 100 #How many iterations per update
iterations = 500 * updateFrequency * evolveFrequency + 1 #Number of steps to run the simulation (each takes ~.033 seconds)
agents = Warehouse_Agents(num_agents=N, useTags = False, num_tags = N*10, N=False, L=False)

thetas = []
for i in range(G):
    thetas.append((2 * np.pi / G) *(i + 1))

goal_point_z = [0] * G
goal_point_x = []
goal_point_y = []

#Sets the goal points to 80% of the edge of the circle
for i in thetas:
    goal_point_x.append(1 * 0.8 * np.cos(i-(np.pi /G)))
    goal_point_y.append(1 * 0.8 * np.sin(i-(np.pi /G)))
goal_points = np.array([goal_point_x, goal_point_y, goal_point_z])

goal_text_x = []
goal_text_y = []
for i, g in enumerate(goal_points.T):
    if i % 3 == 0:
        goal_text_x.append(g[0] + .3)
    else:
        goal_text_x.append(g[0] - .3)

    if int(i/2) == 0:
        goal_text_y.append(g[1] + .3)
    else:
        goal_text_y.append(g[1] - .3)
goal_texts = np.array([goal_text_x, goal_text_y, goal_point_z])

# Create single integrator position controller
single_integrator_position_controller = create_si_position_controller()
# Create barrier certificates to avoid collision
si_barrier_cert = create_single_integrator_barrier_certificate_with_boundary()

_, uni_to_si_states = create_si_to_uni_mapping()

# Create mapping from single integrator velocity commands to unicycle velocity commands
si_to_uni_dyn = create_si_to_uni_dynamics_with_backwards_motion()

show_figure = False

initial_conditions = generate_initial_conditions(N)
r = robotarium.Robotarium(number_of_robots=N, show_figure=show_figure, initial_conditions=initial_conditions, sim_in_real_time=True)

# define x initially
x = r.get_poses()
x_si = uni_to_si_states(x)

# Plotting Parameters
CM = plt.cm.get_cmap('hsv', G+1) # Agent/goal color scheme

goal_marker_size_m = 2
loads = np.zeros(G) #Loads to be unloaded for each zone
scores = np.zeros(G) #The score for each group of agents

idle_count = np.zeros(N) #Number of time steps the agent spent idle
update_step = 0

if show_figure:
    pie_slice = [1.0 / G] * G
    p2,t2 = r.axes.pie(pie_slice, startangle=0, radius=1, center=(0, 0))
    [p.set_zorder(-1) for p in p2]
    [p.set_color(CM(i)) for i, p in enumerate(p2)]

    robot_marker_size_m = 0.2
    marker_size_goal = determine_marker_size(r,goal_marker_size_m)

    marker_size_robot = determine_marker_size(r, robot_marker_size_m)
    font_size = determine_font_size(r,0.08)
    line_width = 5

    # Create Goal Point Markers
    #Text with goal identification
    loads_caption = ['{0}'.format(ii) for ii in loads]
    goal_caption = ['{0}'.format(ii) for ii in scores]

    #Plot text for caption
    goal_points_text = [r.axes.text(goal_texts[0,ii], goal_texts[1,ii]-.05, goal_caption[ii], fontsize=font_size, color='k',fontweight='bold',horizontalalignment='center',verticalalignment='center',zorder=-2)
        for ii in range(goal_points.shape[1])] 
    loads_text = [r.axes.text(goal_texts[0,ii], goal_texts[1,ii]+.05, loads_caption[ii], fontsize=font_size, color='k',fontweight='bold',horizontalalignment='center',verticalalignment='center',zorder=-2)
        for ii in range(goal_points.shape[1])]    

    robot_markers = [r.axes.scatter(x[0,ii], x[1,ii], s=marker_size_robot, marker='o', facecolors='none',edgecolors=CM(ii%G),linewidth=line_width) 
        for ii in range(N)]
    robot_tags = [r.axes.text(x[0,ii], x[1,ii], agents.agents[ii].tag, fontsize=font_size, color='k',fontweight='bold',horizontalalignment='center',verticalalignment='center',zorder=1) 
        for ii in range(N)]

r.step()

for t in range(iterations):
    # Get poses of agents
    x = r.get_poses()

    if t % updateFrequency == 0: #Only changes agent's goals/updates agents every 100 iterations
        #Reloads the zones
        for i in range(G):
            if loads[i] == 0:
                if random.random() <= p:
                    loads[i]+=s
        # loads[0]+=s
        if t != 0:
            update_step += 1
        
        #Updates the statuses of each agent
        for i in range(N):
            if loads[i%G] == 0:
                agents.agents[i].needHelp = False
            else:
                agents.agents[i].needHelp = True
            # print(agents.agents[i].needHelp)

        #Request for help
        for a in agents.agents:
            if a.needHelp:
                agents.request_help(a, helpRadius)
        
        #for a in agents.agents:
        #    print(a)
        #print()

        #Gets the goal locations for each agent
        goals = []
        for i in range(3): #X, Y and Z
            goal = []
            for j in range(N):
                goal.append(goal_points[i][agents.agents[j].goalZone%G])
            goals.append(goal)
        goals = np.array(goals)        

        #Update the agents' scores
        for j in range(N):
            idle = True
            if x[0][j]**2 + x[1][j]**2 <= 1**2:
                for k in range(G):
                    current_theta = np.arctan2(x[1][j], x[0][j])
                    if current_theta < 0:
                        current_theta += 2*np.pi
                    if current_theta < thetas[k]:
                        if loads[k] > 0:
                            scores[k] += 1
                            loads[k] -= 1
                            idle = False
                        break
            if idle and t != 0:
                idle_count[j] += 1
            agents.agents[j].xPos = x[0][j]
            agents.agents[j].yPos = x[1][j]
            agents.agents[j].idlePercent = idle_count[j] / update_step
        for j in range(N):
            agents.agents[j].score = scores[j%G]
        
        #if t != 0:
        #    print('idle percent: ', idle_count / update_step)
        #    print('Total idle percent: ', sum(idle_count)/(update_step*N))

        if t % (updateFrequency*evolveFrequency) == 0 and evolve:
            print(t)
            agents.evolve(radius=evolveRadius)
        elif t % (updateFrequency*evolveFrequency) == 0:
            print(t)
            agents.stats.update(agents.agents)
            print(agents.stats)
            print()
        
        agents.reset_agents()

    x_si = uni_to_si_states(x)

    # Update Robot Marker Plotted Visualization
    if show_figure:
        for i in range(x.shape[1]):
            robot_markers[i].set_offsets(x[:2,i].T)
            robot_tags[i].set_text(agents.agents[i].tag)
            robot_tags[i].set_position(x[:2,i].T)
            # This updates the marker sizes if the figure window size is changed. 
            # This should be removed when submitting to the Robotarium.
            robot_markers[i].set_sizes([determine_marker_size(r, robot_marker_size_m)])

        for i in range(goal_points.shape[1]):
            goal_points_text[i].set_text(scores[i])
            goal_points_text[i].set_zorder(-1)

            loads_text[i].set_text(loads[i])
            loads_text[i].set_zorder(-1)

            # goal_markers[j].set_sizes([determine_marker_size(r, goal_marker_size_m)])

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

    # time.sleep(2)

print(scores, '\t', sum(scores))

#Call at end of script to print debug information and for your script to run on the Robotarium server properly
r.call_at_scripts_end()
agents.stats.pltCollaborating(name = expType)
#f = open(f'{expType}.csv', 'a')
#f.write('idle percent: ', idle_count / update_step)
#f.write('Total idle percent: ', sum(idle_count)/(update_step*N))