import copy
import random
import numpy as np
import matplotlib.pyplot as plt

class Warehouse_Agent:
    def __init__(self, tag, number, N=False, L=False):
        self.tag = tag #The agent's tag number
        self.number = number #Does not change, agent's ID
        self.N = N #Agent will accept request for help if its own bay doesn't need unloaded
        self.L = L #Agent will accept request for help if its own bay needs unloaded
        self.run = False #If the agent has already run in an iteration or not
        self.score = 0 #The agents score

        self.goalZone = number #The number for the agent's goal zone
        self.needHelp = False #This is True is the agent's bay is not empty
     
    def __str__(self):
        return (f"Agent {self.number}:\tTag: {self.tag}, Agent Goal Zone: {self.goalZone}, N: {self.N}, L: {self.L}")


class Warehouse_Agents:
    def __init__(self, num_agents = 16, useTags = True, num_tags = -1):
        self.useTags = useTags

        self.num_agents = num_agents
        self.agents = []
        for i in range(self.num_agents):
            if self.useTags:
                self.agents.append(Warehouse_Agent(i,i))
            else: #sets tag to -1 for every agent if useTags == False
                self.agents.append(Warehouse_Agent(-1,i))
        if num_tags == -1:
            self.tags = num_agents
        else:
            self.tags = num_tags
        #self.stats = Agent_Stats(self.tags) #TODO: warehouse stats
        
    def reset_agents(self):
        '''resets the agent's scores and sets their run status to false'''
        for i in self.agents:
            i.run = False
            i.goalZone = i.number #TODO: is this really the best idea?

    def request_help(self, requester):       
        helper = self.get_helper(requester)

        if helper == requester:
            print("Warning: helper == requester")

        if not helper.needHelp: #Helper's goal zone is fully unloaded
            if helper.N:
                helper.goalZone = requester.number
            else:
                helper.goalZone = helper.number
        else:
            if helper.L:
                helper.goalZone = requester.number
            else:
                helper.goalZone = helper.number


    def get_helper(self, requester):
        '''
        Run when an agent has items in their warehouse to unload
        Selects an agent that hasn't run yet, ideally with the same tag, and asks for help
        '''
        agent = requester #This default value should never be used
        for a in self.agents:
            if not a.run and a != requester:
                if a.tag == requester.tag:
                    a.run = True
                    return a
                if agent == requester:
                    agent = a
        agent.run = True
        return agent


    def evolve(self, mutationNChance = .1, mutationLChance = .1, mutationTChance = .1):
        '''
        Updates the stats of the agents and then evolves them
        Evolution evolves agents proportionally to their score with a small chance of a mutation
        '''
        #self.stats.update(self.agents)
        #print(self.stats)
        #print()

        #Gets the total scores and the cummulative scores
        totalScore = 0
        cumSum = []
        for a in self.agents:
            totalScore+=a.score
            cumSum.append(totalScore)

        #Evolves the agents in proportion to their score
        startingAgents = copy.deepcopy(self.agents)
        for a in range(self.num_agents):
            setAgent = False
            r = random.uniform(0,totalScore)
            for i in range(len(cumSum)-1):
                if r >= cumSum[i] and r < cumSum[i+1]:
                    self.agents[a].N = startingAgents[i].N
                    self.agents[a].L = startingAgents[i].L
                    self.agents[a].tag = startingAgents[i].tag
                    setAgent = True
                    break
            if not setAgent: #Wants to evolve the last agent
                self.agents[a].N = startingAgents[len(startingAgents)-1].N
                self.agents[a].L = startingAgents[len(startingAgents)-1].L
                self.agents[a].tag = startingAgents[len(startingAgents)-1].tag
            

            #mutationN changes agent's N bit
            mutationN = random.random()
            if mutationN < mutationNChance:
                self.agents[a].N = not self.agents[a].N

            #mutationL changes agent's L bit
            mutationL = random.random()
            if mutationL < mutationLChance:
                self.agents[a].L = not self.agents[a].L
            
            #mutationT changes the agent's tag
            mutationT = random.random()
            if mutationT < mutationTChance and self.useTags:
                self.agents[a].tag = round(random.uniform(0,self.tags))

class Single_Iteration_Stats:
    def __init__(self, agents, tags):
        '''tags is the number of tags used'''
        self.stats = {}
        self.stats['collaborating'] = 0
        self.stats['selfish'] = 0
        self.stats['tags'] = [0] * tags
        for a in agents:
            if a.collaborate:
                self.stats['collaborating']+=1
            else:
                self.stats['selfish'] += 1
            self.stats['tags'][a.tag]+=1

    def __str__(self):
        return str(self.stats)

class Agent_Stats:
    def __init__(self, tags):
        self.iterations = []
        self.tags = tags

    def update(self, agents):
        self.iterations.append(Single_Iteration_Stats(agents, self.tags))

    def pltCollaborating(self):
        collab = []
        selfish = []
        evolutions = []
        for i in range(len(self.iterations)):
            collab.append(self.iterations[i].stats['collaborating'])
            selfish.append(self.iterations[i].stats['selfish'])
            evolutions.append((i+1)*10)
        print(collab)
        print(selfish)
        plt.plot(evolutions, collab, label='Collaborating Agents')
        plt.plot(evolutions, selfish, label = 'Selfish Agents')
        plt.xlabel("Evolutions")
        plt.ylabel("Agents")
        plt.legend()
        plt.show()

    def __str__(self):
        string = ''
        for i in self.iterations:
            string += str(i.stats)+'\n'
        return string

