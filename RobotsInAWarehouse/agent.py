import random
import numpy as np
import matplotlib.pyplot as plt

class Warehouse_Agent:
    def __init__(self, tag, number, N=False, L=False, useTag = True):
        self.tag = tag #The agent's tag number
        self.number = number #Does not change, used purely for debugging
        self.N = N #Agent will accept request for help if its own bay doesn't need unloaded
        self.L = L #Agent will accept request for help if its own bay needs unloaded
        self.run = False #If the agent has already run in an iteration or not
        self.score = 0 #The agents score
        self.useTag = useTag
     
    def __str__(self):
        return (f"Agent {self.number}:\tTag: {self.tag}, Cooperating: {self.collaborate}")


class Warehouse_Agents:
    def __init__(self, num_agents = 16, useTags = True, tags = -1):
        self.useTags = useTags

        self.num_agents = num_agents
        self.agents = []
        for i in range(self.num_agents):
            if self.useTags:
                self.agents.append(Warehouse_Agent(i,i))
            else:
                self.agents.append(Warehouse_Agent(-1,i))
        if tags == -1:
            self.tags = len(self.agents)
        else:
            self.tags = tags
        self.stats = Agent_Stats(self.tags)
        
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
        index1 = -1
        index2 = -1

        #First, tries to find two agents with the same tag that haven't run
        #If it cannot find two agents with the same tag, takes the first agent it sees for index 1
        for i in range(self.num_agents):
            if self.agents[i].run == False:
                for j in range(i+1, self.num_agents):
                    if self.agents[j].run == False and self.agents[j].tag == self.agents[i].tag:
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
                if self.agents[i].run == False:
                    index2 = i
                    break

        self.agents[index1].run = True
        self.agents[index2].run = True
        return self.agents[index1], self.agents[index2]

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
        self.stats = {}
        self.stats['collaborating'] = 0
        self.stats['selfish'] = 0
        self.stats['tags'] = [0] * tags #Assumes number of tags == number of agents
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

