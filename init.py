
# import local files
import copy
from getjson import *
from imageprocessor import *
from math import *
import parser
from random import *



def parse_formula (formula, parameter):

    code = parser.expr(formula).compile()
    t = parameter
    try:
        ev = eval(code)
    except:
        return 0
    return ev

def draw_formula (grid, data):

    line_color = (data["colors"]["line"][0],
        data["colors"]["line"][1],
        data["colors"]["line"][2])

    # go through every t value in range with given intervals
    t = data["window"]["t"]["min"]
    while t <= data["window"]["t"]["max"]:

        # get coordinates of the point
        x = parse_formula(data["graph"]["x"], t)
        y = parse_formula(data["graph"]["y"], t)

        x_valid = x < data["window"]["x"]["max"] and x > data["window"]["x"]["min"]
        y_valid = y < data["window"]["y"]["max"] and y > data["window"]["y"]["min"]

        if x_valid and y_valid:

            # convert coords to point coords on the grid
            gx = x
            gx -= data["window"]["x"]["min"]
            gx /= (data["window"]["x"]["max"] - data["window"]["x"]["min"])
            gx *= data["window"]["resolution"]["x"]
            gx = int(round(gx, 0))

            gy = y
            gy -= data["window"]["y"]["min"]
            gy /= (data["window"]["y"]["max"] - data["window"]["y"]["min"])
            gy *= data["window"]["resolution"]["y"]
            gy = data["window"]["resolution"]["y"] - gy
            gy = int(round(gy, 0))

            # project the point on the grid
            dotsize = data["dotsize"]
            for i in range(gx - dotsize, gx + dotsize + 1):
                for j in range(gy - dotsize, gy + dotsize + 1):
                    if j >= 0 and j < len(grid) and i >= 0 and i < len(grid[0]):
                        grid[j][i] = line_color

        t += data["window"]["t"]["step"]

    return grid



# get source data
data = getjson("source.json")

# generate grid for the window
bg_color = (data["colors"]["background"][0],
    data["colors"]["background"][1],
    data["colors"]["background"][2])
pre_grid = [bg_color] * data["window"]["resolution"]["x"]
grid = []
for i in range(0, data["window"]["resolution"]["y"]):
    grid.append(pre_grid.copy())

# check what mode the graph is on
mode = data["type"]

# code for parametric style
if mode == "parametric":

    xsize = data["window"]["x"]["max"] - data["window"]["x"]["min"]
    ysize = data["window"]["y"]["max"] - data["window"]["y"]["min"]

    # draw x-axis
    xdata = copy.deepcopy(data)
    xdata["window"]["t"]["min"] = xdata["window"]["x"]["min"]
    xdata["window"]["t"]["max"] = xdata["window"]["x"]["max"]
    xdata["window"]["t"]["step"] = 0.001 * xsize
    xdata["graph"]["x"] = "t"
    xdata["graph"]["y"] = "0"
    xdata["colors"]["line"] = xdata["colors"]["axis"]
    xdata["dotsize"] = xdata["axissize"]
    grid = draw_formula(grid, xdata)

    # draw y-axis
    ydata = copy.deepcopy(data)
    ydata["window"]["t"]["min"] = ydata["window"]["y"]["min"]
    ydata["window"]["t"]["max"] = ydata["window"]["y"]["max"]
    ydata["window"]["t"]["step"] = 0.001 * ysize
    ydata["graph"]["x"] = "0"
    ydata["graph"]["y"] = "t"
    ydata["colors"]["line"] = ydata["colors"]["axis"]
    ydata["dotsize"] = ydata["axissize"]
    grid = draw_formula(grid, ydata)

    # draw size indicators on x-axis
    # first, check which indicators should be shown
    # then, see draw the lines on the axis

    multiplier = 10 ** floor(log10(xsize) - 0.6)
    first = data["window"]["x"]["min"] - (data["window"]["x"]["min"] % multiplier)
    cur = first
    while (cur <= data["window"]["x"]["max"]):
        idata = copy.deepcopy(data)
        idata["window"]["t"]["min"] = -0.01 * ysize
        idata["window"]["t"]["max"] = 0.01 * ysize
        idata["window"]["t"]["step"] = 0.001 * ysize
        idata["graph"]["x"] = str(cur)
        idata["graph"]["y"] = "t"
        idata["colors"]["line"] = idata["colors"]["axis"]
        idata["dotsize"] = idata["axissize"]
        grid = draw_formula(grid, idata)
        cur += multiplier

    # draw size indicators on x-axis
    # first, check which indicators should be shown
    multiplier = 10 ** floor(log10(ysize) - 0.6)
    first = data["window"]["y"]["min"] - (data["window"]["y"]["min"] % multiplier)
    cur = first
    while (cur <= data["window"]["y"]["max"]):
        idata = copy.deepcopy(data)
        idata["window"]["t"]["min"] = -0.01 * xsize
        idata["window"]["t"]["max"] = 0.01 * xsize
        idata["window"]["t"]["step"] = 0.001 * xsize
        idata["graph"]["x"] = "t"
        idata["graph"]["y"] = str(cur)
        idata["colors"]["line"] = idata["colors"]["axis"]
        idata["dotsize"] = idata["axissize"]
        grid = draw_formula(grid, idata)
        cur += multiplier

    # draw graph
    grid = draw_formula(grid, data)

    # show image
    gen_image(grid, "RGB", "out/main.png")
