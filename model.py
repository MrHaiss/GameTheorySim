import datetime
from random import random, choice
from mesa import Model
from mesa.time import RandomActivation
from agents import AlwaysShareAgent, AlwaysStealAgent, FoodPatch
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


def calc_share_steal_ratio(model):
    share_agent_list = [agent for agent in model.schedule.agents if agent.type == "AlwaysShare"]
    steal_agent_list = [agent for agent in model.schedule.agents if agent.type == "AlwaysSteal"]

    if len(steal_agent_list) == 0:
        divide_num = 1
    else:
        divide_num = len(steal_agent_list)

    ratio = len(share_agent_list) / divide_num

    return ratio


class GameTheoryModel(Model):
    description = "A basic simulation of game theory population dynamics employing 2 strategies: Share vs Steal."

    def __init__(self, n_share, n_steal, n_food, width, height):
        self.num_agents_share = n_share
        self.num_agents_steal = n_steal
        self.n_food = n_food
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.running = True

        # Create food sources (one off)
        for i in range(self.n_food):
            fully_grown = choice([True, False])

            f = FoodPatch(str(i) + "-food", self, fully_grown=fully_grown)
            self.schedule.add(f)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(f, (x, y))

        # Create Agents
        for i in range(self.num_agents_share):
            a = AlwaysShareAgent(str(i) + "-share", self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents_steal):
            a = AlwaysStealAgent(str(i) + "-steal", self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(model_reporters={"Ratio of Share vs Steal": calc_share_steal_ratio},
                                           agent_reporters={"Food": "food"})

    def new_agent(self, agent_type, u_id, pos):
        split_uid = u_id.split("-")
        timestamp = datetime.datetime.now().strftime("%H-%M-%S-%f")
        new_id = split_uid[0] + "-" + agent_type + "-r-" + timestamp + "-" + str(random())

        if agent_type == "AlwaysShare":
            a = AlwaysShareAgent(new_id, self)
        elif agent_type == "AlwaysSteal":
            a = AlwaysStealAgent(new_id, self)

        self.schedule.add(a)
        self.grid.place_agent(a, pos)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

        # Stop running if everyone died
        if len([agent for agent in self.schedule.agents if agent.type != "Food"]) == 0:
            self.running = False
