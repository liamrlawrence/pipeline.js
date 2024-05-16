import json

class Stage:
    def __init__(self, name, ID, options):
        self.name = name
        self.ID = ID
        self.options = options
        self.inputs = {}
        self.outputs = {}

    def add_input(self, stage, port):
        self.inputs[port] = stage

    def add_output(self, stage, port):
        self.outputs[port] = stage

    def run(self):
        raise NotImplementedError("Each stage must implement the run method.")

class Input(Stage):
    def run(self, data=None):
        data = ["[INPUT]>> "]
        return data

class Output(Stage):
    def run(self, data=None):
        data = self.inputs[1].run()
        data[0] += " >>[OUTPUT]"
        return data

class EdgeDetection(Stage):
    def run(self, data=None):
        x = self.inputs[1].run()
        x[0] += " >[EDGE]> "
        return x

class BitwiseAND(Stage):
    def run(self, data=None):
        a = self.inputs[1].run()
        b = self.inputs[2].run()
        a[0] += " >[B&ND1]"
        b[0] += " >[B&ND2]> "
        return [b[0], a[0]]

class HSVThreshold(Stage):
    def run(self, data=None):
        x = self.inputs[1].run()
        x[0] += " >[HSV]> "
        return x

class Blur(Stage):
    def run(self, data=None):
        x = self.inputs[1].run()
        x[0] += " >[Blurred]> "
        return x


class Pipeline:
    def __init__(self, input):
        self.stages = {}
        self.input = input

    def add_stage(self, stage):
        self.stages[stage.ID] = stage

    def connect_stages(self, from_stage_id, from_port, to_stage_id, to_port):
        from_stage = self.stages[from_stage_id]
        to_stage = self.stages[to_stage_id]
        from_stage.add_output(to_stage, from_port)
        to_stage.add_input(from_stage, to_port)

    def run(self):
        x = self.stages["Output-1"].run(self.input)
        return x


def setup_pipeline_from_json(json_data):
    output = []
    pipeline = Pipeline(output)

    # First pass: Create and add all stages
    for item in json_data:
        stage_class = {
            "Input": Input,
            "Output": Output,
            "Edge Detection": EdgeDetection,
            "Bitwise AND": BitwiseAND,
            "Threshold": HSVThreshold,
            "Blur": Blur
        }.get(item["name"])

        if stage_class:
            stage = stage_class(item["name"], item["ID"], item["options"])
            pipeline.add_stage(stage)

    # Second pass: Connect stages
    for item in json_data:
        node = item["node"]
        for output in node["outputs"]:
            if output["connection"]:
                pipeline.connect_stages(
                    from_stage_id=node["ID"],
                    from_port=output["port"],
                    to_stage_id=output["connection"]["parentID"],
                    to_port=output["connection"]["port"]
                )

    return pipeline

# Example usage
working_simple = '''[{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"x":300,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":300,"y":425,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":350,"y":425,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":175,"y":400,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":225,"y":425,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":550,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":550,"y":425,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[]}},{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":425,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":425,"y":425,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":475,"y":425,"connection":{"parentID":"Output-1","port":1}}]}}]'''
json_data = '''[{"name":"Edge Detection","ID":"Edge Detection-1","color":"red","options":{"min_area":400},"node":{"ID":"Edge Detection-1","color":"red","options":{"min_area":400},"x":575,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":575,"y":300,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":291.6666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":625,"y":308.3333333333333,"connection":{"parentID":"Bitwise AND-1","port":1}}]}},{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"node":{"ID":"Blur-1","color":"blue","options":{"kernelSize":0,"strength":50},"x":375,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":375,"y":300,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":425,"y":300,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":475,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":475,"y":300,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":525,"y":300,"connection":{"parentID":"Edge Detection-1","port":1}}]}},{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":275,"y":275,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":325,"y":300,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Input","ID":"Input-2","color":"silver","options":{},"node":{"ID":"Input-2","color":"silver","options":{},"x":275,"y":375,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":325,"y":400,"connection":{"parentID":"Threshold-2","port":1}}]}},{"name":"Threshold","ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":475,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":475,"y":400,"connection":{"parentID":"Input-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":525,"y":400,"connection":{"parentID":"Bitwise AND-1","port":2}}]}},{"name":"Bitwise AND","ID":"Bitwise AND-1","color":"teal","options":{},"node":{"ID":"Bitwise AND-1","color":"teal","options":{},"x":575,"y":375,"inputs":[{"ctype":1,"direction":1,"port":1,"x":575,"y":391.6666666666667,"connection":{"parentID":"Edge Detection-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":575,"y":408.3333333333333,"connection":{"parentID":"Threshold-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":400,"connection":{"parentID":"Threshold-3","port":1}}]}},{"name":"Threshold","ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":675,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":675,"y":400,"connection":{"parentID":"Bitwise AND-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":725,"y":400,"connection":{"parentID":"Output-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":775,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":775,"y":400,"connection":{"parentID":"Threshold-3","port":1}}],"outputs":[]}}]'''

pipeline = setup_pipeline_from_json(json.loads(json_data))
x = pipeline.run()
for z in x[::-1]:
    print(z)

