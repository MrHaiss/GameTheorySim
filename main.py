from model import GameTheoryModel
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

GLOBAL_WIDTH = 10
GLOBAL_HEIGHT = 10


def agent_portrayal(agent):
    portrayal = {"Filled": "true",
                 "Layer": 1}

    if agent.type == "AlwaysShare":
        portrayal["Color"] = "green"
        portrayal["r"] = 0.8
        portrayal["Shape"] = "circle"
    elif agent.type == "AlwaysSteal":
        portrayal["Color"] = "red"
        portrayal["r"] = 0.8
        portrayal["Shape"] = "circle"
    elif agent.type == "Food":
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Layer"] = 0

        if agent.fully_grown:
            portrayal["Color"] = "orange"
        else:
            portrayal["Color"] = "black"

    return portrayal


grid = CanvasGrid(agent_portrayal, GLOBAL_WIDTH, GLOBAL_HEIGHT, 300, 300)
chart = ChartModule([{"Label": "Ratio of Share vs Steal",
                      "Color": "Black"}],
                    data_collector_name='datacollector')
server = ModularServer(GameTheoryModel,
                       [grid, chart],
                       "Game Theory Sim",
                       {"n_share": 15,
                        "n_steal": 15,
                        "n_food": 50,
                        "width": GLOBAL_WIDTH, "height": GLOBAL_HEIGHT})

server.port = 8521
server.launch()
