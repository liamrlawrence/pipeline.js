import streamlit as st
import streamlit.components.v1 as components
from fastapi.responses import FileResponse
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import uvicorn
from threading import Thread
import json
import os
import asyncio
from PIL import Image



import json
import cv2
import numpy as np
import time


st.set_page_config(layout="wide")

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
        image_path = './static/leaf.png'
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
        output_path = './static/output.png'
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

        cv2.imwrite(f"./static/{self.ID}-mask.png", mask)
        cv2.imwrite(f"./static/{self.ID}-image.png", image)
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

        cv2.imwrite(f"./static/{self.ID}-mask.png", mask)
        cv2.imwrite(f"./static/{self.ID}-image.png", image)
        return mask


class BitwiseAND(Stage):
    def run(self, data=None):
        print("AND")
        image = self.inputs[2].run(data)
        mask = self.inputs[1].run(data)
        result = cv2.bitwise_and(image, image, mask=mask)
        cv2.imwrite(f"./static/{self.ID}.png", result)
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
        cv2.imwrite(f"./static/{self.ID}.png", result)
        return result

class Blur(Stage):
    def run(self, data=None):
        print("Blur")
        image = self.inputs[1].run(data)
        bk = self.options.get('kernel_size', 35)
        if bk % 2 == 0:
            bk += 1
        result = cv2.GaussianBlur(image, (bk, bk), 0)
        cv2.imwrite(f"./static/{self.ID}.png", result)
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
        cv2.imwrite(f"./static/{self.ID}.png", result)
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
        cv2.imwrite(f"./static/{self.ID}.png", result)
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








# Ensure the directory exists
os.makedirs("./static/", exist_ok=True)

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the data you expect to receive
class DataModel(BaseModel):
    canvas: list

# Endpoint to handle POST requests
@app.post("/api/save_data")
async def save_data(item: DataModel):
    print("HIT /save_data !")
    with open("./static/canvas.json", "w") as file:
        json.dump(item.canvas, file)

    with open("./static/canvas.json", "r") as f:
        json_data = f.read()
    t1_s = time.time()
    pipeline = setup_pipeline_from_json(json.loads(json_data))
    t1_e = time.time()

    t2_s = time.time()
    pipeline.run()
    t2_e = time.time()

    print(f"T1: {t1_e - t1_s}\nT2: {t2_e - t2_s}\n")


    return {"message": "Data saved successfully"}

# Endpoint to serve the image
@app.get("/api/image")
async def get_image():
    image_path = "./static/output.png"
    return FileResponse(image_path)

# WebSocket endpoint to notify client to refresh the image
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text("update")
            await asyncio.sleep(0.1)  # Update every 100 milliseconds
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

# Function to run FastAPI in a separate thread
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8007)

# Start FastAPI in a separate thread
thread = Thread(target=run_fastapi)
thread.start()

# Function to read the content of the file
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()



# Read the HTML and CSS files
app_html = read_file("./static/app.html")
app_css = read_file("./static/css/styles.css")
app_js = read_file("./static/dist/node.mjs")

# Define the HTML content
drawer_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"></meta>
        <title>D3 Canvas with Gridlines and Draggable CVFunctions</title>
        <style>
            {app_css}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="canvas-container"></div>
            <div id="image-container">
                <img id="myImage" alt="Image to reload">
            </div>
        </div>
        <div id="drawer"></div>
        <div>
            <button id="saveButton">Save Canvas</button>
            <button id="loadButton">Load Canvas</button>
            <button id="clearButton">Clear Canvas</button>
        </div>
        <div>
            <button id="saveToFileButton">Save to File</button>
            <button id="loadFromFileButton">Load from File</button>
        </div>
        <br>
        <div>
            <input type="file" id="fileInput" style="display:none"></input>
            <button id="runCanvas">Run Canvas</button>
        </div>

        <script>
            {app_js}
        </script>
        <div id="popup" style="display:none; position: absolute; border: 1px solid black; background: white; padding: 10px;">
            <form id="valueForm">
                <div id="optionsContainer"></div>
                <button type="submit">Update</button>
            </form>

        </div>
    </body>

    </html>
'''

# Embed the HTML in Streamlit
components.html(drawer_html, height=1500, width=1500)


# Additional Streamlit content
st.title('Streamlit with Embedded JavaScript App')
st.write('This is a Streamlit app with a sliding drawer that contains a custom JavaScript app.')

