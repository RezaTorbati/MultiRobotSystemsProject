import random

class PD_Tagged_Agent:
    def __init__(self, tag, number, collaborate=False):
        self.collaborate = collaborate
        self.tag = tag
        self.number = number #Does not change, used purely for coloring
        self.run = False
        self.score = 0
     
    def __str__(self):
        return (f"Agent {self.number}:\tTag: {self.tag}, Cooperating: {self.collaborate}")


class PD_Tagged_Agents:
    def __init__(self, num_agents = 50):
        if num_agents % 2 == 1:
            print(f'Expects even number of agents. Using {num_agents+1} agents')
            self.num_agents = num_agents + 1
        else:
            self.num_agents = num_agents
        self.agents = []
        for i in range(self.num_agents):
            self.agents.append(PD_Tagged_Agent(i,i))
        
    def reset_agents(self):
        for i in self.agents:
            i.run = False
            i.score = 0

    def select_agents(self):
        index1 = -1
        index2 = -1
        for i in range(self.num_agents):
            if self.agents[i].run == False:
                for j in range(i+1, self.num_agents):
                    if self.agents[j].run == False and self.agents[j].tag == self.agents[i].tag:
                        index1 = i
                        index2 = j
                        break
                if index1 == -1:
                    index1 = i
        if index1 == -1:
            self.evolve()
            self.reset_agents()
            return self.select_agents()

        if index2 == -1:
            for i in range(index1+1, self.num_agents):
                if self.agents[i].run == False:
                    index2 = i
                    break

        self.agents[index1].run = True
        self.agents[index2].run = True
        return self.agents[index1], self.agents[index2]

    def evolve(self):
        print('Evolving!!!\n')
        totalScore = 0
        cumSum = []
        for a in self.agents:
            totalScore+=a.score
            cumSum.append(totalScore)
        
        for a in self.agents:
            setAgent = False
            r = random.uniform(0,totalScore)
            for i in range(len(cumSum)-1):
                if r >= cumSum[i] and r < cumSum[i+1]:
                    a = self.agents[i]
                    setAgent = True
                    break
            if not setAgent:
                a = self.agents[len(self.agents)-1]
            
            mutation1 = random.random()
            if mutation1 < .1:
                a.collaborate = not a.collaborate
            
            mutation2 = random.random()
            if mutation2 < .1:
                a.tag = round(random.uniform(0,self.num_agents-1))


        



