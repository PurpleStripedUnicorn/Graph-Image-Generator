
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

        x_min = data["window"]["x"]["min"]
        y_min = data["window"]["y"]["min"]
        x_max = data["window"]["x"]["max"]
        y_max = data["window"]["y"]["max"]

        x_valid = x < x_max and x > x_min
        y_valid = y < y_max and y > y_min

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

def add_image (grid, filename, name, color, x, y, scale = 1):

    x_max = len(grid[0]) - 1
    y_max = len(grid) - 1

    # get image data as array
    ndata = getjson("imagedata/" + filename + ".json")[name]

    for i in range(0, len(ndata[0])):
        for j in range(0, len(ndata)):
            if ndata[j][i] == 1:
                for ii in range(0, scale):
                    for jj in range(0, scale):

                        # check if point is a valid point on the grid
                        xc = i * scale + x + ii
                        yc = j * scale + y + jj

                        if xc <= x_max and xc >= 0 and yc <= y_max and yc >= 0:
                            grid[yc][xc] = color

    return grid

def add_text (grid, text, x, y):

    scale = int(ceil(max([len(grid), len(grid[0])]) * 0.005))

    n = 0
    m = 0
    for t in text:
        if t != "\n":
            xspacing = x + 4 * n * scale
            yspacing = y + 6 * m * scale
            color = (0, 0, 0)
            grid = add_image(grid, "text", t, color, xspacing, yspacing, scale)
            n += 1
        else:
            n = 0
            m += 1


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
    first = data["window"]["x"]["min"]
    first -= data["window"]["x"]["min"] % multiplier
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
    first = data["window"]["y"]["min"]
    first -= data["window"]["y"]["min"] % multiplier
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

    if data["displayformula"]:
        grdes = "x(t) = " + data["graph"]["x"].lower()
        grdes += "\ny(t) = " + data["graph"]["y"].lower()
        grid = add_text(grid, grdes, 7, 4)

    # show image
    gen_image(grid, "RGB", "out/main.png")
