import json

# Sample JSON string
json_string = '[{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":425,"y":175,"inputs":[{"ctype":2,"direction":1,"port":1,"x":425,"y":200,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":475,"y":200,"connection":{"parentID":"Edge Detection-1","port":1}}]}},{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"x":325,"y":175,"inputs":[{"ctype":2,"direction":1,"port":1,"x":325,"y":200,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":375,"y":200,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":225,"y":175,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":275,"y":200,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Edge Detection","ID":"Edge Detection-1","color":"red","options":{"min_area":400},"node":{"ID":"Edge Detection-1","color":"red","options":{"min_area":400},"x":525,"y":175,"inputs":[{"ctype":2,"direction":1,"port":1,"x":525,"y":200,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":575,"y":191.66666666666666,"connection":null},{"ctype":1,"direction":0,"port":2,"x":575,"y":208.33333333333334,"connection":{"parentID":"Bitwise AND-1","port":1}}]}},{"name":"Input","ID":"Input-2","color":"silver","options":{},"node":{"ID":"Input-2","color":"silver","options":{},"x":225,"y":275,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":275,"y":300,"connection":{"parentID":"Threshold-3","port":1}}]}},{"name":"Bitwise AND","ID":"Bitwise AND-1","color":"teal","options":{},"node":{"ID":"Bitwise AND-1","color":"teal","options":{},"x":525,"y":275,"inputs":[{"ctype":1,"direction":1,"port":1,"x":525,"y":291.6666666666667,"connection":{"parentID":"Edge Detection-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":525,"y":308.3333333333,"connection":{"parentID":"Threshold-3","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":575,"y":300,"connection":{"parentID":"Threshold-2","port":1}}]}},{"name":"Threshold","ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":625,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":625,"y":300,"connection":{"parentID":"Bitwise AND-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":675,"y":300,"connection":{"parentID":"Output-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":725,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":725,"y":300,"connection":{"parentID":"Threshold-2","port":1}}],"outputs":[]}},{"name":"Threshold","ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":425,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":425,"y":300,"connection":{"parentID":"Input-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":475,"y":300,"connection":{"parentID":"Bitwise AND-1","port":2}}]}}]'

# Parse the JSON string
pipeline_data = json.loads(json_string)

class NodeConnector:
    def __init__(self, ctype, direction, port, connection, x, y):
        self.ctype = ctype
        self.direction = direction
        self.port = port
        self.connection = connection
        self.x = x
        self.y = y

class NodeBlock:
    def __init__(self, ID, color, options, x, y, inputs, outputs):
        self.ID = ID
        self.color = color
        self.options = options
        self.x = x
        self.y = y
        self.inputs = [NodeConnector(**input_data) for input_data in inputs]
        self.outputs = [NodeConnector(**output_data) for output_data in outputs]

class CVFunction:
    def __init__(self, name, ID, color, options, node_data):
        self.name = name
        self.ID = ID
        self.color = color
        self.options = options
        self.node = NodeBlock(**node_data)

# Reconstruct the CVFunctions
cv_functions = [CVFunction(func_data['name'], func_data['ID'], func_data['color'], func_data['options'], func_data['node']) for func_data in pipeline_data]

def threshold(options, input_image):
    print(f"Applying Threshold with options: {options}")
    return input_image  # Replace with actual processing

def blur(options, input_image):
    print(f"Applying Blur with options: {options}")
    return input_image  # Replace with actual processing

def bitwise_and(options, input_image):
    print(f"Applying Bitwise AND with options: {options}")
    return input_image  # Replace with actual processing

def edge_detection(options, input_image):
    print(f"Applying Edge Detection with options: {options}")
    return input_image  # Replace with actual processing

def inputF(options, input_image):
    print(f"Input >>")
    return input_image  # Replace with actual processing

def outputF(options, input_image):
    print(f">> Output")
    return input_image  # Replace with actual processing

# Map function names to actual functions
function_map = {
    "Input": inputF,
    "Output": outputF,
    "Threshold": threshold,
    "Blur": blur,
    "Edge Detection": edge_detection,
    "Bitwise AND": bitwise_and,
}

# Function to execute the pipeline starting from an "Input" block
def execute_pipeline(cv_functions):
    input_image = "input_image_placeholder"  # Replace with actual input image

    # Create a dictionary to store the output of each function
    function_outputs = {}

    # Create a mapping of ID to CVFunction objects
    id_to_function = {func.ID: func for func in cv_functions}

    # Find all input functions
    input_functions = [func for func in cv_functions if func.name.split('-')[0] == "Input"]

    def execute_function(func, input_data):
        output = function_map[func.name.split('-')[0]](func.options, input_data)
        function_outputs[func.ID] = output

        # Execute all connected functions
        for output_connector in func.node.outputs:
            if output_connector.connection:
                connected_func = id_to_function[output_connector.connection['parentID']]
                execute_function(connected_func, output)

    # Start execution from each input function
    for input_func in input_functions:
        execute_function(input_func, input_image)

execute_pipeline(cv_functions)

