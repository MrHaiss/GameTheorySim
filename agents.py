from mesa import Agent

# Globals
repro_req = 2.5
repro_baseline = 3.5
daily_food_req = 0.5
max_gain_from_food = 3
food_life_cycle = 5


def share_share(agent1, agent2):
    agent1.food += 1
    agent2.food += 1


def steal_steal(agent1, agent2):
    agent1.food += 0.25
    agent2.food += 0.25


def share_steal(sharer, stealer):
    stealer.food += 1.75
    sharer.food += 0.25


def handle_interaction(agent1, agent2):
    matrix = {
        ("AlwaysShare", "AlwaysShare"): share_share,
        ("AlwaysShare", "AlwaysSteal"): share_steal,
        ("AlwaysSteal", "AlwaysSteal"): steal_steal,
    }
    if agent2.type == "AlwaysShare":
        agent1, agent2 = agent2, agent1
    func = matrix[agent1.type, agent2.type]
    func(agent1, agent2)


# Agent common methods
def interact_neighbour(agent):
    neighbours = agent.model.grid.get_cell_list_contents([agent.pos])
    if len(neighbours) > 1:
        # Don't want to get self
        other_agent = agent.random.choice(neighbours)
        while True:
            if agent != other_agent:
                break
            else:
                other_agent = agent.random.choice(neighbours)
        if other_agent.type != "Food":
            handle_interaction(agent, other_agent)
        else:
            forage_food(agent, other_agent)


def forage_food(agent, food_patch):
    if food_patch.fully_grown:
        agent.food += agent.random.randint(1, max_gain_from_food)
        food_patch.fully_grown = False


class AlwaysShareAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.food = 1
        self.type = "AlwaysShare"

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def reproduce(self):
        if self.food >= repro_baseline:
            self.food -= repro_req
            self.model.new_agent(agent_type=self.type, u_id=self.unique_id, pos=self.pos)

    def step(self):
        # 1 food per day needed to survive
        self.food -= daily_food_req

        self.move()
        interact_neighbour(self)
        self.reproduce()

        if self.food <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


class AlwaysStealAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.food = 1
        self.type = "AlwaysSteal"

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def reproduce(self):
        if self.food >= repro_baseline:
            self.food -= repro_req
            self.model.new_agent(agent_type=self.type, u_id=self.unique_id, pos=self.pos)

    def step(self):
        # 1 food per day needed to survive
        self.food -= daily_food_req

        self.move()
        interact_neighbour(self)
        self.reproduce()

        if self.food <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


class FoodPatch(Agent):
    def __init__(self, unique_id, model, fully_grown):
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.growth_full_cycle = food_life_cycle
        self.growth_progress = self.random.randint(1, self.growth_full_cycle)
        self.type = "Food"
        self.food = 0

    def step(self):
        if not self.fully_grown:
            if self.growth_progress <= 0:
                self.fully_grown = True
                self.growth_progress = self.growth_full_cycle
            else:
                self.growth_progress -= 1
