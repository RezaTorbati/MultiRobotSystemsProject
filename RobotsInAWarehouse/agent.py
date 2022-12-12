import copy
import math
import random
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

class Warehouse_Agent:
    def __init__(self, tag, number, N=False, L=False):
        self.tag = tag #The agent's tag number
        self.number = number #Does not change, agent's home zone
        self.N = N #Agent will accept request for help if its own bay doesn't need unloaded
        self.L = L #Agent will accept request for help if its own bay needs unloaded
        self.run = False #If the agent has already run in an iteration or not
        self.score = 0 #The agents score

        self.xPos = 0
        self.yPos = 0

        self.idlePercent = -1
        self.goalZone = number #The number for the agent's goal zone
        self.needHelp = False #This is True is the agent's bay is not empty
     
    def __str__(self):
        return (f"Agent {self.number}:\tTag: {self.tag}, Agent Goal Zone: {self.goalZone}, N: {self.N}, L: {self.L}")


class Warehouse_Agents:
    def __init__(self, num_agents = 16, useTags = True, num_tags = -1, N=False, L=False):
        '''
        num_tags is the range of tags that may be given during evolution
        N is the default value for the N bit
        L is the default value for the L bit
        '''
        self.useTags = useTags

        self.num_agents = num_agents
        self.agents = []
        for i in range(self.num_agents):
            if self.useTags:
                self.agents.append(Warehouse_Agent(i,i, N=N, L=L))
            else: #sets tag to -1 for every agent if useTags == False
                self.agents.append(Warehouse_Agent(-1,i, N=N, L=L))
        if num_tags == -1:
            self.tags = num_agents
        else:
            self.tags = num_tags
        self.stats = Agent_Stats(self.tags)
        
    def reset_agents(self):
        '''resets the agent's scores and sets their run status to false'''
        for i in self.agents:
            i.run = False
            i.goalZone = i.number #TODO: is this really the best idea?

    def request_help(self, requester, radius=2):     
        '''
        Finds an agent to request help from
        requester should be of type agent and is the agent asking for help
        '''  
        helper = self.get_helper(requester, radius)

        if helper == requester: #TODO: figure out why this occasionally happens
            print("Warning: helper == requester")
            return


        if not helper.needHelp: #Helper's goal zone is fully unloaded
            if helper.N: #Accepts the request
                #print('accept1', requester.number, helper.number)
                helper.goalZone = requester.number
            else: #Rejects the request
                #print('reject1', requester.number, helper.number)
                helper.goalZone = helper.number
        else:
            if helper.L: #Accepts the request
                #print('accept2', requester.number, helper.number)
                helper.goalZone = requester.number
            else: #Rejects the request
                #print('reject2', requester.number, helper.number)
                helper.goalZone = helper.number

    def getDistance(self, a1, a2):
        return ((a1.xPos-a2.xPos)**2 + (a1.yPos - a2.yPos)**2)**.5

    def get_helper(self, requester, radius):
        '''
        Selects an agent that hasn't run yet, ideally with the same tag, and asks for help
        '''
        agent = requester
        shuffled_list = self.agents.copy()
        random.shuffle(shuffled_list)
        for a in shuffled_list:
            dist = self.getDistance(a, requester)
            if not a.run and a.number != requester.number and dist <= radius:
                if a.tag == requester.tag:
                    a.run = True
                    return a
                if agent == requester:
                    agent = a
        if agent != requester:
            agent.run = True
        return agent


    def evolve(self, mutationNChance = .02, mutationLChance = .02, mutationTChance = .05, radius = -1):
        '''
        Updates the stats of the agents and then evolves them
        Evolution evolves agents proportionally to their score with a small chance of a mutation
        '''
        self.stats.update(self.agents)
        print(self.stats)
        print()

        if radius == -1:
            #Gets the total scores and the cummulative scores
            totalScore = 0
            cumSum = []
            for a in self.agents:
                totalScore+=a.score
                #print(a.number, ', ', a.score)
                cumSum.append(totalScore)

        #Evolves the agents in proportion to their score
        startingAgents = copy.deepcopy(self.agents)
        for a in range(self.num_agents):
            if radius == -1:
                if totalScore == 0:
                    r = random.randint(0,self.num_agents-1)
                    self.agents[a].N = startingAgents[r].N
                    self.agents[a].L = startingAgents[r].L
                    self.agents[a].tag = startingAgents[r].tag
                else:
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
            else:
                cumSum = []
                validAgents = []
                totalScore = 0
                for aa in startingAgents:
                    if self.getDistance(self.agents[a], aa) <= radius:
                        totalScore += aa.score
                        cumSum.append(totalScore)
                        validAgents.append(aa)
                
                if totalScore == 0:
                    r = random.randint(0, len(validAgents)-1)
                    self.agents[a].N = validAgents[r].N
                    self.agents[a].L = validAgents[r].L
                    self.agents[a].tag = validAgents[r].tag
                else:
                    setAgent = False
                    r = random.uniform(0,totalScore)
                    for i in range(len(cumSum)-1):
                        if r >= cumSum[i] and r < cumSum[i+1]:
                            self.agents[a].N = validAgents[i].N
                            self.agents[a].L = validAgents[i].L
                            self.agents[a].tag = validAgents[i].tag
                            setAgent = True
                            break
                    if not setAgent: #Wants to evolve the last agent
                        self.agents[a].N = validAgents[len(validAgents)-1].N
                        self.agents[a].L = validAgents[len(validAgents)-1].L
                        self.agents[a].tag = validAgents[len(validAgents)-1].tag

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
        self.stats['N'] = 0
        self.stats['L'] = 0
        self.stats['score'] = 0
        self.stats['idlePercent'] = 0
        self.stats['tags'] = [0] * tags
        for a in agents:
            if a.N:
                self.stats['N']+=1
            if a.L:
                self.stats['L'] += 1
            self.stats['score'] += a.score
            self.stats['idlePercent'] += a.idlePercent
            self.stats['tags'][a.tag-1]+=1

        self.stats['idlePercent']/=len(agents)
        if math.isnan(self.stats['idlePercent']):
            self.stats['idlePercent'] = 1.0
            

    def __str__(self):
        return str(self.stats)

class Agent_Stats:
    def __init__(self, tags):
        #Tags is the number of tags used here
        self.iterations = []
        self.tags = tags

    def update(self, agents):
        self.iterations.append(Single_Iteration_Stats(agents, self.tags))

    def pltCollaborating(self, name=''):
        N = []
        L = []
        scores = []
        evolutions = []
        if name != '':
            f = open(f'{name}.csv', 'w')
            f.write('N,L,score,idlePercent\n')
        for i in range(len(self.iterations)):
            N.append(self.iterations[i].stats['N'])
            L.append(self.iterations[i].stats['L'])
            scores.append(self.iterations[i].stats['score'])
            evolutions.append(i+1)

            #Writes out key information. This could probably be done better
            if name != '':
                f.write(f'{self.iterations[i].stats["N"]},{self.iterations[i].stats["L"]},{self.iterations[i].stats["score"]},{self.iterations[i].stats["idlePercent"]}\n')
        if name != '':
            f.close()
        
        plt.close()
        fig,a = plt.subplots(2)
        
        #Figure that shows how the N and L bits changed over time
        a[0].plot(evolutions,N, label='N bits true')
        a[0].plot(evolutions,L, label = 'L bits true')
        a[0].set_ylabel("Agents")
        a[0].legend()

        #Figure that shows how the score changes over time
        a[1].plot(evolutions,scores, label = 'Total Score')
        a[1].set_ylabel("Score")

        plt.xlabel("Evolutions")
        print('MANUALLY SAVE THIS, SAVEFIG ISN"T WORKING')
        plt.show()
        

    def __str__(self):
        #string = ''
        #for i in self.iterations:
        #    string += str(i.stats)+'\n'
        #return string
        return str(self.iterations[-1])

