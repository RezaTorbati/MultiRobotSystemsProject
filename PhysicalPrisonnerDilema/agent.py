from cProfile import label
import copy
import random
import numpy as np
import matplotlib.pyplot as plt

class PD_Tagged_Agent:
    def __init__(self, tag, number, collaborate=False, useTag = True):
        self.collaborate = collaborate #Whether or not the agent will go to its own goal or the other goal
        self.tag = tag #The agent's tag number
        self.number = number #Does not change, used purely for debugging
        self.run = False #If the agent has already run in an iteration or not
        self.score = 0 #The agents score
        self.useTag = useTag
     
    def __str__(self):
        return (f"Agent {self.number}:\tTag: {self.tag}, Cooperating: {self.collaborate}")


class PD_Tagged_Agents:
    def __init__(self, num_agents = 50, useTags = True):
        self.useTags = useTags
        if num_agents % 2 == 1:
            print(f'Expects even number of agents. Using {num_agents+1} agents')
            self.num_agents = num_agents + 1
        else:
            self.num_agents = num_agents
        self.agents = []
        for i in range(self.num_agents):
            if self.useTags:
                self.agents.append(PD_Tagged_Agent(i,i))
            else:
                self.agents.append(PD_Tagged_Agent(-1,i))
        self.stats = Agent_Stats()
        
    def reset_agents(self):
        '''resets the agent's scores and sets their run status to false'''
        for i in self.agents:
            i.run = False
            i.score = 0

    def select_agents(self):
        '''
        Returns two agents that have not run and, if possible, with the same tag
        If all agents has run, evolves the agents, resets them, and then choose two new agents to return
        '''
        shuffled_list = self.agents.copy()
        random.shuffle(shuffled_list)
        index1 = -1
        index2 = -1

        #First, tries to find two agents with the same tag that haven't run
        #If it cannot find two agents with the same tag, takes the first agent it sees for index 1
        for i in range(self.num_agents):
            if shuffled_list[i].run == False:
                for j in range(i+1, self.num_agents):
                    if shuffled_list[j].run == False and shuffled_list[j].tag == shuffled_list[i].tag:
                        index1 = i
                        index2 = j
                        break
                if index1 == -1:
                    index1 = i

        #If all of the agents have run
        if index1 == -1:
            self.evolve()
            self.reset_agents()
            return self.select_agents()

        #If none of the agents that haven't run have the same tags
        if index2 == -1:
            for i in range(index1+1, self.num_agents):
                if shuffled_list[i].run == False:
                    index2 = i
                    break

        shuffled_list[index1].run = True
        shuffled_list[index2].run = True
        return shuffled_list[index1], shuffled_list[index2]

    def evolve(self, mutation1Chance = .01, mutation2Chance = .01):
        '''
        Updates the stats of the agents and then evolves them
        Evolution evolves agents proportionally to their score with a small chance of a mutation
        '''
        self.stats.update(self.agents)
        print(self.stats)
        print()

        #Gets the total scores and the cummulative scores
        totalScore = 0
        cumSum = []
        for a in self.agents:
            totalScore+=a.score
            cumSum.append(totalScore)
        
        #Evolves the agents in proportion to their score
        startingAgents = copy.deepcopy(self.agents)
        for a in self.agents:
            setAgent = False
            r = random.uniform(0,totalScore)
            for i in range(len(cumSum)-1):
                if r >= cumSum[i] and r < cumSum[i+1]:
                    a.tag = startingAgents[i].tag
                    a.collaborate = startingAgents[i].collaborate
                    setAgent = True
                    break
            if not setAgent: #Wants to evolve the last agent
                a.tag = startingAgents[len(self.agents)-1].tag
                a.collaborate = startingAgents[len(self.agents)-1].collaborate
            

            #Mutation 1 changes if the agent collaborates or not
            mutation1 = random.random()
            if mutation1 < mutation1Chance:
                a.collaborate = not a.collaborate
            
            #Mutation 2 changes the agent's tag
            mutation2 = random.random()
            if mutation2 < mutation2Chance and self.useTags:
                a.tag = round(random.uniform(0,self.num_agents*2-1))

class Single_Iteration_Stats:
    def __init__(self, agents):
        self.stats = {}
        self.stats['collaborating'] = 0
        self.stats['selfish'] = 0
        self.stats['tags'] = [0] * len(agents)*2 #Assumes number of tags == number of agents
        for a in agents:
            if a.collaborate:
                self.stats['collaborating']+=1
            else:
                self.stats['selfish'] += 1
            self.stats['tags'][a.tag]+=1

    def __str__(self):
        return str(self.stats)

class Agent_Stats:
    def __init__(self):
        self.iterations = []

    def update(self, agents):
        self.iterations.append(Single_Iteration_Stats(agents))

    def pltCollaborating(self):
        collab = []
        selfish = []
        evolutions = []
        for i in range(len(self.iterations)):
            collab.append(self.iterations[i].stats['collaborating'])
            selfish.append(self.iterations[i].stats['selfish'])
            evolutions.append(i+1)
        print(collab)
        print(selfish)
        plt.plot(evolutions, collab, label='Collaborating Agents')
        plt.plot(evolutions, selfish, label = 'Selfish Agents')
        plt.xlabel("Evolutions")
        plt.ylabel("Agents")
        plt.legend()
        plt.show()

    def __str__(self):
        #string = ''
        #for i in self.iterations:
        #    string += str(i.stats)+'\n'
        #return string
        return str(self.iterations[-1])

