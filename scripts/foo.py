class PipelineStage:
    def __init__(self, func, name):
        self.func = func
        self.name = name
        self.inputs = []
        self.output = None

    def set_inputs(self, *stages):
        self.inputs = stages

    def run(self):
        input_values = [stage.output for stage in self.inputs]
        if len(input_values) == 1:
            input_values = input_values[0]
        self.output = self.func(*input_values)



class Pipeline:
    def __init__(self):
        self.stages = {}

    def add_stage(self, name, func):
        stage = PipelineStage(func, name)
        self.stages[name] = stage

    def connect(self, output_stage, *input_stages):
        output_stage = self.stages[output_stage]
        input_stages = [self.stages[name] for name in input_stages]
        output_stage.set_inputs(*input_stages)

    def run(self, initial_inputs):
        for name, stage in self.stages.items():
            if not stage.inputs:  # Initial input stage
                stage.output = initial_inputs[name]
            stage.run()
        return {name: stage.output for name, stage in self.stages.items()}



def multiply_by_two(x):
    return x * 2

def add_numbers(x, y):
    return x + y

def split_string(s):
    return s.split()

def concatenate_strings(*args):
    flattened_args = []
    for arg in args:
        if isinstance(arg, list):
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)
    return ' '.join(flattened_args)


# Create the pipeline
pipeline = Pipeline()

# Add stages to the pipeline
pipeline.add_stage("A", add_numbers)
pipeline.add_stage("B", multiply_by_two)
pipeline.add_stage("C", split_string)

# Connect stages
pipeline.connect("A", "B", "C")  # A takes input from B and C

# Set initial inputs
initial_inputs = {
    "B": 5,  # Initial input for B
    "C": "hello world"  # Initial input for C
}

# Run the pipeline
results = pipeline.run(initial_inputs)
print(results)  # Output should show the result of stage A

