import json

# Sample JSON string
json_string = '[{"name":"Threshold","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"name":"Threshold","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":150,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":150,"y":300,"connection":null}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":200,"y":300,"connection":{"parentName":"Blur","port":1}}]}},{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"x":350,"y":275,"inputs":[{"ctype":0,"direction":1,"port":1,"x":350,"y":300,"connection":{"parentName":"Threshold","port":1}}],"outputs":[{"ctype":0,"direction":0,"port":1,"x":400,"y":300,"connection":{"parentName":"Edge Detection","port":1}}]}},{"name":"Edge Detection","color":"red","options":{"min_area":400},"node":{"name":"Edge Detection","color":"red","options":{"min_area":400},"x":575,"y":300,"inputs":[{"ctype":0,"direction":1,"port":1,"x":575,"y":325,"connection":{"parentName":"Blur","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":316.6666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":625,"y":333.3333333333333,"connection":null}]}}]'
json_string = '[{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"x":375,"y":450,"inputs":[{"ctype":0,"direction":1,"port":1,"x":375,"y":475,"connection":null}],"outputs":[{"ctype":0,"direction":0,"port":1,"x":425,"y":475,"connection":{"parentName":"Edge Detection","port":1}}]}},{"name":"Edge Detection","color":"red","options":{"min_area":400},"node":{"name":"Edge Detection","color":"red","options":{"min_area":400},"x":550,"y":400,"inputs":[{"ctype":0,"direction":1,"port":1,"x":550,"y":425,"connection":{"parentName":"Blur","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":600,"y":416.6666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":600,"y":433.3333333333333,"connection":{"parentName":"Blur","port":1}}]}},{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"x":725,"y":500,"inputs":[{"ctype":0,"direction":1,"port":1,"x":725,"y":525,"connection":{"parentName":"Edge Detection","port":2}}],"outputs":[{"ctype":0,"direction":0,"port":1,"x":775,"y":525,"connection":null}]}}]'
json_string = '[{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"x":375,"y":450,"inputs":[{"ctype":0,"direction":1,"port":1,"x":375,"y":475,"connection":null}],"outputs":[{"ctype":0,"direction":0,"port":1,"x":425,"y":475,"connection":{"parentName":"Edge Detection","port":1}}]}},{"name":"Edge Detection","color":"red","options":{"min_area":400},"node":{"name":"Edge Detection","color":"red","options":{"min_area":400},"x":550,"y":400,"inputs":[{"ctype":0,"direction":1,"port":1,"x":550,"y":425,"connection":{"parentName":"Blur","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":600,"y":416.6666666666667,"connection":{"parentName":"Threshold","port":1}},{"ctype":1,"direction":0,"port":2,"x":600,"y":433.3333333333333,"connection":{"parentName":"Blur","port":1}}]}},{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"name":"Blur","color":"blue","options":{"kernelSize":0,"strength":50},"x":675,"y":550,"inputs":[{"ctype":0,"direction":1,"port":1,"x":675,"y":575,"connection":{"parentName":"Edge Detection","port":2}}],"outputs":[{"ctype":0,"direction":0,"port":1,"x":725,"y":575,"connection":null}]}},{"name":"Threshold","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"name":"Threshold","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":750,"y":350,"inputs":[{"ctype":2,"direction":1,"port":1,"x":750,"y":375,"connection":{"parentName":"Edge Detection","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":800,"y":375,"connection":null}]}}]'

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
    def __init__(self, name, color, options, x, y, inputs, outputs):
        self.name = name
        self.color = color
        self.options = options
        self.x = x
        self.y = y
        self.inputs = [NodeConnector(**input_data) for input_data in inputs]
        self.outputs = [NodeConnector(**output_data) for output_data in outputs]

class CVFunction:
    def __init__(self, name, color, options, node_data):
        self.name = name
        self.color = color
        self.options = options
        self.node = NodeBlock(**node_data)

# Reconstruct the CVFunctions
cv_functions = [CVFunction(func_data['name'], func_data['color'], func_data['options'], func_data['node']) for func_data in pipeline_data]


def threshold(options, input_image):
    # Placeholder function for thresholding
    print(f"Applying Threshold with options: {options}")
    # Apply thresholding on input_image
    return input_image  # Replace with actual processing

def blur(options, input_image):
    # Placeholder function for blurring
    print(f"Applying Blur with options: {options}")
    # Apply blur on input_image
    return input_image  # Replace with actual processing

def edge_detection(options, input_image):
    # Placeholder function for edge detection
    print(f"Applying Edge Detection with options: {options}")
    # Apply edge detection on input_image
    return input_image  # Replace with actual processing

# Map function names to actual functions
function_map = {
    "Threshold": threshold,
    "Blur": blur,
    "Edge Detection": edge_detection,
}

# Function to execute the pipeline
def execute_pipeline(cv_functions):
    # Assuming input_image is provided
    input_image = "input_image_placeholder"  # Replace with actual input image

    # Create a dictionary to store the output of each function
    function_outputs = {}

    for func in cv_functions:
        # Get input from the connected function if exists
        input_data = input_image
        for input_connector in func.node.inputs:
            if input_connector.connection:
                parent_name = input_connector.connection['parentName']
                input_data = function_outputs[parent_name]

        # Execute the function
        output = function_map[func.name](func.options, input_data)

        # Store the output
        function_outputs[func.name] = output

execute_pipeline(cv_functions)

