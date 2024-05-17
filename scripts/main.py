import json
import cv2
import numpy as np
import time

class Stage:
    def __init__(self, stage_name, ID, options):
        self.stage_name = stage_name
        self.ID = ID
        self.options = options
        self.inputs = {}
        self.outputs = {}

    def add_input(self, stage, port):
        self.inputs[port] = stage

    def add_output(self, stage, port):
        self.outputs[port] = stage

    def run(self, data):
        raise NotImplementedError("Each stage must implement the run method.")


class Input(Stage):
    def run(self, data=None):
        print("Input")
        # Load the image from disk (use a placeholder image path for now)
        image_path = './scripts/static/leaf.png'
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Could not load image from {image_path}")
            exit()

        image = cv2.resize(image,(int(6048 / 4), int(4024 / 4)))
        return image

class Output(Stage):
    def run(self, data=None):
        print("Output")
        # Get input image from the previous stage
        image = self.inputs[1].run(data)

        # Save the resulting image
        output_path = './scripts/static/output.png'
        cv2.imwrite(output_path, image)
        print(f"Processed image saved at {output_path}")
        return image

class Contours_Circle(Stage):
    def run(self, data=None):
        print("EDGE")
        image = self.inputs[1].run(data)

        # Find contours
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a mask with circles
        mask = np.zeros_like(gray)
        min_radius = self.options.get('min_radius', 0)

        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            if radius > min_radius:
                cv2.circle(mask, (int(x), int(y)), radius, (255), -1)
                cv2.circle(image, (int(x), int(y)), radius, (255, 0, 255), 2)

        cv2.imwrite(f"./scripts/static/{self.ID}-mask.png", mask)
        cv2.imwrite(f"./scripts/static/{self.ID}-image.png", image)
        return mask


class Contours_ConvexHull(Stage):
    def run(self, data=None):
        print("EDGE")
        image = self.inputs[1].run(data)

        # Find contours
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a mask with circles
        mask = np.zeros_like(gray)
        min_area = self.options.get('min_area', 0)

        hulls = []
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if cv2.contourArea(contour) > min_area:
                hull = cv2.convexHull(contour)
                hulls.append(hull)

        cv2.drawContours(image, hulls, -1, (0, 0, 255), 2)
        cv2.drawContours(mask, hulls, -1, (255, 255, 255), -1)

        cv2.imwrite(f"./scripts/static/{self.ID}-mask.png", mask)
        cv2.imwrite(f"./scripts/static/{self.ID}-image.png", image)
        return mask


class BitwiseAND(Stage):
    def run(self, data=None):
        print("AND")
        image = self.inputs[2].run(data)
        mask = self.inputs[1].run(data)
        result = cv2.bitwise_and(image, image, mask=mask)
        cv2.imwrite(f"./scripts/static/{self.ID}.png", result)
        return result

class HSVThreshold(Stage):
    def run(self, data=None):
        print("HSV")
        image = self.inputs[1].run(data)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_bound = (self.options.get('min_h', 0), self.options.get('min_s', 0), self.options.get('min_v', 0))
        upper_bound = (self.options.get('max_h', 180), self.options.get('max_s', 255), self.options.get('max_v', 255))
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        result = cv2.bitwise_and(image, image, mask=mask)
        cv2.imwrite(f"./scripts/static/{self.ID}.png", result)
        return result

class Blur(Stage):
    def run(self, data=None):
        print("Blur")
        image = self.inputs[1].run(data)
        bk = self.options.get('kernel_size', 35)
        if bk % 2 == 0:
            bk += 1
        result = cv2.GaussianBlur(image, (bk, bk), 0)
        cv2.imwrite(f"./scripts/static/{self.ID}.png", result)
        return result

class Dilate(Stage):
    def run(self, data=None):
        print("Dilate")
        img = self.inputs[1].run(data)
        dk = self.options.get('kernel_size', 1)
        itr = self.options.get('iterations', 1)
        if dk % 2 == 0:
            dk += 1
        result = cv2.dilate(img, (dk, dk), iterations=itr)
        cv2.imwrite(f"./scripts/static/{self.ID}.png", result)
        return result

class Clahe(Stage):
    def run(self, data=None):
        print("CLAHE")
        img = self.inputs[1].run(data)
        cl = self.options.get('clip_limit', 1)
        tgs = self.options.get('tile_grid_size', 1)
        clahe = cv2.createCLAHE(clipLimit=float(cl), tileGridSize=(tgs, tgs))
        lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_img)
        l_clahe = clahe.apply(l)
        lab_clahe_img = cv2.merge((l_clahe, a, b))
        result = cv2.cvtColor(lab_clahe_img, cv2.COLOR_LAB2BGR)
        cv2.imwrite(f"./scripts/static/{self.ID}.png", result)
        return result

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
        return self.stages["Output-1"].run(self.input)


def setup_pipeline_from_json(json_data):
    output = None
    pipeline = Pipeline(output)

    # First pass: Create and add all stages
    for item in json_data:
        stage_class = {
            "Input": Input,
            "Output": Output,
            "Contours-Circle": Contours_Circle,
            "Contours-ConvexHull": Contours_ConvexHull,
            "Bitwise AND": BitwiseAND,
            "Threshold": HSVThreshold,
            "Blur": Blur,
            "Dilate": Dilate,
            "CLAHE": Clahe,
        }.get(item["stage_name"])

        if stage_class:
            stage = stage_class(item["stage_name"], item["ID"], item["options"])
            pipeline.add_stage(stage)

    # Second pass: Connect stages
    for item in json_data:
        node = item
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
# json_data = '''[{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernel_size":15},"node":{"ID":"Blur-1","color":"blue","options":{"kernel_size":15},"x":300,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":300,"y":425,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":350,"y":425,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":175,"y":400,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":225,"y":425,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":550,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":550,"y":425,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[]}},{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":425,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":425,"y":425,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":475,"y":425,"connection":{"parentID":"Output-1","port":1}}]}}]'''
# json_data = '''[{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":350,"y":400,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":400,"y":425,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernel_size":0,"strength":50},"node":{"ID":"Blur-1","color":"blue","options":{"kernel_size":0,"strength":50},"x":475,"y":350,"inputs":[{"ctype":2,"direction":1,"port":1,"x":475,"y":375,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":525,"y":375,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":600,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":600,"y":400,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":650,"y":400,"connection":{"parentID":"Output-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":725,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":725,"y":425,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[]}}]'''
# json_data = '''[{"name":"Edge Detection","ID":"Edge Detection-1","color":"red","options":{"min_area":90},"node":{"ID":"Edge Detection-1","color":"red","options":{"min_area":90},"x":575,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":575,"y":300,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":291.6666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":625,"y":308.3333333333333,"connection":{"parentID":"Bitwise AND-1","port":1}}]}},{"name":"Blur","ID":"Blur-1","color":"blue","options":{"kernel_size":30,"strength":1},"node":{"ID":"Blur-1","color":"blue","options":{"kernel_size":30,"strength":1},"x":375,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":375,"y":300,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":425,"y":300,"connection":{"parentID":"Threshold-1","port":1}}]}},{"name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":5,"min_s":0,"min_v":75,"max_h":107,"max_s":255,"max_v":255},"node":{"ID":"Threshold-1","color":"green","options":{"min_h":5,"min_s":0,"min_v":75,"max_h":107,"max_s":255,"max_v":255},"x":475,"y":275,"inputs":[{"ctype":2,"direction":1,"port":1,"x":475,"y":300,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":525,"y":300,"connection":{"parentID":"Edge Detection-1","port":1}}]}},{"name":"Input","ID":"Input-1","color":"silver","options":{},"node":{"ID":"Input-1","color":"silver","options":{},"x":275,"y":275,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":325,"y":300,"connection":{"parentID":"Blur-1","port":1}}]}},{"name":"Input","ID":"Input-2","color":"silver","options":{},"node":{"ID":"Input-2","color":"silver","options":{},"x":275,"y":375,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":325,"y":400,"connection":{"parentID":"Bitwise AND-1","port":2}}]}},{"name":"Threshold","ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-2","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":450,"y":450,"inputs":[{"ctype":2,"direction":1,"port":1,"x":450,"y":475,"connection":null}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":500,"y":475,"connection":null}]}},{"name":"Bitwise AND","ID":"Bitwise AND-1","color":"teal","options":{},"node":{"ID":"Bitwise AND-1","color":"teal","options":{},"x":575,"y":375,"inputs":[{"ctype":1,"direction":1,"port":1,"x":575,"y":391.6666666666667,"connection":{"parentID":"Edge Detection-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":575,"y":408.3333333333333,"connection":{"parentID":"Input-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":400,"connection":{"parentID":"Threshold-3","port":1}}]}},{"name":"Threshold","ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"node":{"ID":"Threshold-3","color":"green","options":{"min_h":0,"min_s":0,"min_v":0,"max_h":180,"max_s":255,"max_v":255},"x":675,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":675,"y":400,"connection":{"parentID":"Bitwise AND-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":725,"y":400,"connection":{"parentID":"Output-1","port":1}}]}},{"name":"Output","ID":"Output-1","color":"silver","options":{},"node":{"ID":"Output-1","color":"silver","options":{},"x":775,"y":375,"inputs":[{"ctype":2,"direction":1,"port":1,"x":775,"y":400,"connection":{"parentID":"Threshold-3","port":1}}],"outputs":[]}}]'''
# json_data = '''[{"stage_name":"Input","ID":"Input-1","color":"silver","options":{},"x":250,"y":300,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":300,"y":325,"connection":{"parentID":"Blur-1","port":1}}]},{"stage_name":"Blur","ID":"Blur-1","color":"blue","options":{"kernel_size":30,"strength":1},"x":350,"y":300,"inputs":[{"ctype":2,"direction":1,"port":1,"x":350,"y":325,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":400,"y":325,"connection":{"parentID":"Threshold-1","port":1}}]},{"stage_name":"Threshold","ID":"Threshold-1","color":"green","options":{"min_h":5,"min_s":0,"min_v":75,"max_h":107,"max_s":255,"max_v":255},"x":450,"y":300,"inputs":[{"ctype":2,"direction":1,"port":1,"x":450,"y":325,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":500,"y":325,"connection":{"parentID":"Edge Detection-1","port":1}}]},{"stage_name":"Output","ID":"Output-1","color":"silver","options":{},"x":750,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":750,"y":425,"connection":{"parentID":"Threshold-2","port":1}}],"outputs":[]},{"stage_name":"Threshold","ID":"Threshold-2","color":"green","options":{"min_h":10,"min_s":0,"min_v":0,"max_h":154,"max_s":255,"max_v":200},"x":650,"y":400,"inputs":[{"ctype":2,"direction":1,"port":1,"x":650,"y":425,"connection":{"parentID":"Bitwise AND-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":700,"y":425,"connection":{"parentID":"Output-1","port":1}}]},{"stage_name":"Bitwise AND","ID":"Bitwise AND-1","color":"teal","options":{},"x":550,"y":400,"inputs":[{"ctype":1,"direction":1,"port":1,"x":550,"y":416.6666666666667,"connection":{"parentID":"Edge Detection-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":550,"y":433.3333333333333,"connection":{"parentID":"Input-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":600,"y":425,"connection":{"parentID":"Threshold-2","port":1}}]},{"stage_name":"Input","ID":"Input-2","color":"silver","options":{},"x":250,"y":400,"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":300,"y":425,"connection":{"parentID":"Bitwise AND-1","port":2}}]},{"stage_name":"Edge Detection","ID":"Edge Detection-1","color":"red","options":{"min_area":400},"x":550,"y":300,"inputs":[{"ctype":2,"direction":1,"port":1,"x":550,"y":325,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":600,"y":316.6666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":600,"y":333.3333333333333,"connection":{"parentID":"Bitwise AND-1","port":1}}]}]'''
# json_data = '''[{"stage_name":"Input","ID":"Input-1","options":{},"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":125,"y":100,"connection":{"parentID":"Blur-1","port":1}}],"color":"silver","textColor":"black","x":75,"y":75},{"stage_name":"Blur","ID":"Blur-1","options":{"kernel_size":31,"strength":1},"inputs":[{"ctype":2,"direction":1,"port":1,"x":175,"y":100,"connection":{"parentID":"Input-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":225,"y":100,"connection":{"parentID":"Threshold-1","port":1}}],"color":"blue","textColor":"white","x":175,"y":75},{"stage_name":"Threshold","ID":"Threshold-1","options":{"min_h":5,"min_s":0,"min_v":75,"max_h":107,"max_s":255,"max_v":255},"inputs":[{"ctype":2,"direction":1,"port":1,"x":275,"y":100,"connection":{"parentID":"Blur-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":325,"y":100,"connection":{"parentID":"Contours-Circle-1","port":1}}],"color":"green","textColor":"white","x":275,"y":75},{"stage_name":"Contours-Circle","ID":"Contours-Circle-1","options":{"min_radius":90},"inputs":[{"ctype":2,"direction":1,"port":1,"x":375,"y":100,"connection":{"parentID":"Threshold-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":425,"y":91.66666666666667,"connection":null},{"ctype":1,"direction":0,"port":2,"x":425,"y":108.33333333333334,"connection":{"parentID":"Bitwise AND-1","port":1}}],"color":"red","textColor":"white","x":375,"y":75},{"stage_name":"Input","ID":"Input-2","options":{},"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":125,"y":225,"connection":{"parentID":"Bitwise AND-1","port":2}}],"color":"silver","textColor":"black","x":75,"y":200},{"stage_name":"Bitwise AND","ID":"Bitwise AND-1","options":{},"inputs":[{"ctype":1,"direction":1,"port":1,"x":375,"y":216.66666666666666,"connection":{"parentID":"Contours-Circle-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":375,"y":233.33333333333334,"connection":{"parentID":"Input-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":425,"y":225,"connection":{"parentID":"Dilate-1","port":1}}],"color":"teal","textColor":"white","x":375,"y":200},{"stage_name":"Dilate","ID":"Dilate-1","options":{"kernel_size":3,"iterations":2},"inputs":[{"ctype":2,"direction":1,"port":1,"x":475,"y":225,"connection":{"parentID":"Bitwise AND-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":525,"y":225,"connection":{"parentID":"Threshold-2","port":1}}],"color":"blue","textColor":"white","x":475,"y":200},{"stage_name":"Threshold","ID":"Threshold-2","options":{"min_h":10,"min_s":0,"min_v":0,"max_h":154,"max_s":255,"max_v":200},"inputs":[{"ctype":2,"direction":1,"port":1,"x":575,"y":225,"connection":{"parentID":"Dilate-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":225,"connection":{"parentID":"Contours-ConvexHull-1","port":1}}],"color":"green","textColor":"white","x":575,"y":200},{"stage_name":"CLAHE","ID":"CLAHE-1","options":{"clip_limit":2,"tile_grid_size":8},"inputs":[{"ctype":2,"direction":1,"port":1,"x":575,"y":325,"connection":{"parentID":"Input-3","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":625,"y":325,"connection":{"parentID":"Bitwise AND-2","port":2}}],"color":"blue","textColor":"white","x":575,"y":300},{"stage_name":"Contours-ConvexHull","ID":"Contours-ConvexHull-1","options":{"min_area":4000},"inputs":[{"ctype":2,"direction":1,"port":1,"x":675,"y":225,"connection":{"parentID":"Threshold-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":725,"y":216.66666666666666,"connection":null},{"ctype":1,"direction":0,"port":2,"x":725,"y":233.33333333333334,"connection":{"parentID":"Bitwise AND-2","port":1}}],"color":"red","textColor":"white","x":675,"y":200},{"stage_name":"Input","ID":"Input-3","options":{},"inputs":[],"outputs":[{"ctype":2,"direction":0,"port":1,"x":125,"y":325,"connection":{"parentID":"CLAHE-1","port":1}}],"color":"silver","textColor":"black","x":75,"y":300},{"stage_name":"Bitwise AND","ID":"Bitwise AND-2","options":{},"inputs":[{"ctype":1,"direction":1,"port":1,"x":675,"y":316.6666666666667,"connection":{"parentID":"Contours-ConvexHull-1","port":2}},{"ctype":2,"direction":1,"port":2,"x":675,"y":333.3333333333333,"connection":{"parentID":"CLAHE-1","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":725,"y":325,"connection":{"parentID":"Threshold-3","port":1}}],"color":"teal","textColor":"white","x":675,"y":300},{"stage_name":"Threshold","ID":"Threshold-3","options":{"min_h":60,"min_s":0,"min_v":0,"max_h":170,"max_s":255,"max_v":255},"inputs":[{"ctype":2,"direction":1,"port":1,"x":775,"y":325,"connection":{"parentID":"Bitwise AND-2","port":1}}],"outputs":[{"ctype":2,"direction":0,"port":1,"x":825,"y":325,"connection":{"parentID":"Output-1","port":1}}],"color":"green","textColor":"white","x":775,"y":300},{"stage_name":"Output","ID":"Output-1","options":{},"inputs":[{"ctype":2,"direction":1,"port":1,"x":875,"y":325,"connection":{"parentID":"Threshold-3","port":1}}],"outputs":[],"color":"silver","textColor":"black","x":875,"y":300}]'''

if __name__ == "__main__":
    with open("./static/canvas.json") as f:
        json_data = f.read()
    pipeline = setup_pipeline_from_json(json.loads(json_data))
    pipeline.run()
    time.sleep(0.01)

