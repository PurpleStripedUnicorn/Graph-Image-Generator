
# import local files
import copy
from getjson import *
from imageprocessor import *
from math import *
import parser
from random import *



# parse a formaula, which includes 't' as parameter
# parameter is given, value on this t is output
def parse_formula (formula, parameter):

    # compile formula and set parameter 't'
    code = parser.expr(formula).compile()
    t = parameter
    # try to evaluate code
    # this is in case of wrong user input or invalid values
    try:
        # evaulate code and get value
        ev = eval(code)
    except:
        # return 0 on failure
        # BUG: currently projects straight line on x-axis
        return 0
    # return the value
    return ev

# draw a given formaula(s) (included in data) on a grid
# return grid with formula(s) draw on it
def draw_formula (grid, data):

    # go through every formula given and performs same actions
    for formula in data["graph"]:

        # convert given line color to proper object type
        line_color = (formula["color"][0],
            formula["color"][1],
            formula["color"][2])

        # get the minimum and maximum values of "t"
        # first, check if they are overwritten by the formula
        if "t" in formula:
            t_min = formula["t"]["min"]
            t_max = formula["t"]["max"]
            t_step = formula["t"]["step"]
        else:
            t_min = data["window"]["t"]["min"]
            t_max = data["window"]["t"]["max"]
            t_step = data["window"]["t"]["step"]

        # go through every t value in range with given intervals
        t = t_min
        while t <= t_max:

            # get coordinates of the point
            x = parse_formula(formula["x"], t)
            y = parse_formula(formula["y"], t)

            # convert coords to point coords on the grid

            # convert x-coord, round to nearest whole integer point
            gx = x
            gx -= data["window"]["x"]["min"]
            gx /= (data["window"]["x"]["max"] - data["window"]["x"]["min"])
            gx *= data["window"]["resolution"]["x"]
            gx = int(round(gx, 0))

            # convert y-coord, round to nearest whole integer point
            gy = y
            gy -= data["window"]["y"]["min"]
            gy /= (data["window"]["y"]["max"] - data["window"]["y"]["min"])
            gy *= data["window"]["resolution"]["y"]
            gy = data["window"]["resolution"]["y"] - gy
            gy = int(round(gy, 0))

            # get the maximum values of x and y as grid point coords
            max_x = len(grid[0]) - 1
            max_y = len(grid) - 1

            # project the point on the grid
            # first, get the dotsize, projected as a circle on the image
            dotsize = formula["dotsize"]
            # go through every point that needs to be painted on the grid
            # first, go through x values
            for i in range(floor(gx - dotsize - 1), ceil(gx + dotsize + 2)):
                # go through y values
                for j in range(floor(gy - dotsize - 1), ceil(gy + dotsize + 2)):
                    # check if point is within range of allowed values
                    if j >= 0 and j <= max_y and i >= 0 and i <= max_x:
                        # check if point is within circle radius of source point
                        val = (i - gx) ** 2 + (j - gy) ** 2
                        if val <= dotsize ** 2:
                            # paint pixel on image
                            grid[j][i] = line_color

            # go check next value of t
            t += t_step

    # return grid as output
    return grid

# function to add an image (defined as data), to input grid
# input are:
# - grid to change
# - filename of file of image data
# - name of image data container in JSON file
# - coordinates (x, y) of upper left corner
# - (optional) scaling of image
def add_image (grid, filename, name, color, x, y, scale = 1):

    # get max allowed coords on the image
    x_max = len(grid[0]) - 1
    y_max = len(grid) - 1

    # get image data as array
    ndata = getjson("imagedata/" + filename + ".json")[name]

    # go thwough every data point in the image data
    for i in range(0, len(ndata[0])):
        for j in range(0, len(ndata)):
            # check if pixel is marked
            if ndata[j][i] == 1:
                # go through every pixel in data point
                # only more than 1 with scaling set
                for ii in range(0, scale):
                    for jj in range(0, scale):

                        # check if point is a valid point on the grid
                        xc = i * scale + x + ii
                        yc = j * scale + y + jj

                        if xc <= x_max and xc >= 0 and yc <= y_max and yc >= 0:
                            # paint pixel on grid
                            grid[yc][xc] = color

    # return generated grid
    return grid

# add text (as image) to grid
# text data is in JSON file
def add_text (grid, text, x, y):

    # calculate appropriate scaling for the text to insert
    scale = int(ceil(max([len(grid), len(grid[0])]) * 0.005))

    # go through every character in the text
    # keep track of the distance from the left and top of the start
    n = 0
    m = 0
    for t in text:
        # check if line break is inserted, to add vertical spacing
        if t != "\n":
            # calculate distance from top and left
            xspacing = x + 4 * n * scale
            yspacing = y + 6 * m * scale
            # set color of text
            color = (0, 0, 0)
            # add image data of text to the grid
            grid = add_image(grid, "text", t, color, xspacing, yspacing, scale)
            n += 1
        else:
            n = 0
            m += 1

    # return generated new grid
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

    # check if there is only 1 formula added, to allow formula display
    if len(data["graph"]) != 1:
        data["displayformula"] = False

    xsize = data["window"]["x"]["max"] - data["window"]["x"]["min"]
    ysize = data["window"]["y"]["max"] - data["window"]["y"]["min"]

    # draw x-axis
    data["graph"].append({
        "x": "t",
        "y": "0",
        "color": data["colors"]["axis"],
        "dotsize": 0.5,
        "t": {
            "min": data["window"]["x"]["min"],
            "max": data["window"]["x"]["max"],
            "step": 0.001
        }
    })

    # draw y-axis
    data["graph"].append({
        "x": "0",
        "y": "t",
        "color": data["colors"]["axis"],
        "dotsize": 0.5,
        "t": {
            "min": data["window"]["y"]["min"],
            "max": data["window"]["y"]["max"],
            "step": 0.001
        }
    })

    # draw size indicators on x-axis
    # first, check which indicators should be shown
    # then, see draw the lines on the axis

    multiplier = 10 ** floor(log10(xsize) - 0.6)
    first = data["window"]["x"]["min"]
    first -= data["window"]["x"]["min"] % multiplier
    cur = first
    while (cur <= data["window"]["x"]["max"]):
        data["graph"].append({
            "x": str(cur),
            "y": "t",
            "color": data["colors"]["axis"],
            "dotsize": 0.5,
            # overwrite default window "t" properties
            "t": {
                "min": -0.01 * ysize,
                "max": 0.01 * ysize,
                "step": 0.001 * ysize
            }
        })
        cur += multiplier

    # draw size indicators on x-axis
    # first, check which indicators should be shown
    multiplier = 10 ** floor(log10(ysize) - 0.6)
    first = data["window"]["y"]["min"]
    first -= data["window"]["y"]["min"] % multiplier
    cur = first
    while (cur <= data["window"]["y"]["max"]):
        data["graph"].append({
            "x": "t",
            "y": str(cur),
            "color": data["colors"]["axis"],
            "dotsize": 0.5,
            # overwrite default window "t" properties
            "t": {
                "min": -0.01 * xsize,
                "max": 0.01 * xsize,
                "step": 0.001 * xsize
            }
        })
        cur += multiplier

    # draw graphs
    grid = draw_formula(grid, data)

    # check if the formula should be shown on the output image
    if data["displayformula"]:
        # prepare text to display
        grdes = "x(t) = " + data["graph"][0]["x"].lower()
        grdes += "\ny(t) = " + data["graph"][0]["y"].lower()
        # add text to image
        grid = add_text(grid, grdes, 7, 4)

    # show image
    gen_image(grid, "RGB", "out/main.png")
