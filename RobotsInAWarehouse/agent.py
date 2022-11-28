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
        return (f"Agent {self.number}:\tTag: {self.tag}, N: {self.N}, L: {self.L}")


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
            i.score = 0

    def request_help(self, requester):
        
        helper = self.get_helper(requester)


    def get_helper(self, requester):
        '''
        Run when an agent has items in their warehouse to unload
        Selects an agent that hasn't run yet, ideally with the same tag, and asks for help
        '''
        index = -1
        for i in range(self.num_agents):
            if self.agents[i].run == False and i != requester:
                if self.agents[i].tag == self.agents[requester].tag:
                    self.agents[i].run = True
                    return self.agents[i]
                if index == -1:
                    index = i
        return index


    def evolve(self, mutation1Chance = .1, mutation2Chance = .1):
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
        for a in self.agents:
            setAgent = False
            r = random.uniform(0,totalScore)
            for i in range(len(cumSum)-1):
                if r >= cumSum[i] and r < cumSum[i+1]:
                    a = self.agents[i]
                    setAgent = True
                    break
            if not setAgent: #Wants to evolve the last agent
                a = self.agents[len(self.agents)-1]
            

            #Mutation 1 changes if the agent collaborates or not
            mutation1 = random.random()
            if mutation1 < mutation1Chance:
                a.collaborate = not a.collaborate
            
            #Mutation 2 changes the agent's tag
            mutation2 = random.random()
            if mutation2 < mutation2Chance and self.useTags:
                a.tag = round(random.uniform(0,self.tags))

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

