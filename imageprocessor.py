
# import packages
from PIL import Image



# function to generate an image form a 2-dimensional array
# input is a 2 dimensional array
#   1st dimension -> list of rows
#   2nd dimension -> list of cells
# input is mode
#   RGB or RGBA
# input is output filename
def gen_image (grid, mode, output):

    # get the dimensions of the array
    height = len(grid)
    width = len(grid[0])

    # generate data by concatenating all sub-arrays in main grid array
    o = []
    for row in grid:
        o += row

    # save image to given output file
    img = Image.new(mode, (width, height), "white")
    img.putdata(o)
    img.save(output)

    # return true on success
    return True
