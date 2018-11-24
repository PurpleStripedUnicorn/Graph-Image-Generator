
import json

# get json data as dictionary from a json file given
# input is the filename of the file to read from
def getjson (filename):

    # get content of the json file
    file = open(filename)
    content = file.read()

    # convert json data to dictionary
    dic = json.loads(content)

    # return the converted data
    return dic
