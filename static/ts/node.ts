import * as d3 from "d3";

// Global state to keep track of CVFunction objects
let cvFunctions: CVFunction[] = [];

// CANVAS //
const canvasWidth: number = 1000,
      canvasHeight: number = 700;

const gridSize: number = 25;
const numColumns: number = canvasWidth / gridSize;
const numRows: number = canvasHeight / gridSize;

// Append the svg canvas to the container div
const svg = d3.select<SVGSVGElement, unknown>("#canvas-container").append("svg")
    .attr("width", canvasWidth)
    .attr("height", canvasHeight)
    .attr("viewBox", `0 0 ${canvasWidth} ${canvasHeight}`);

// Create the group that will be transformed during zooming and panning
const g: d3.Selection<SVGGElement, unknown, HTMLElement, any> = svg.append("g");

// Create zoom behavior with constraints
const zoom: d3.ZoomBehavior<Element, unknown> = d3.zoom<Element, unknown>()
    .scaleExtent([1, 10])
    .translateExtent([[-gridSize, -gridSize], [canvasWidth + gridSize, canvasHeight + gridSize]])
    .on("zoom", (event: d3.D3ZoomEvent<Element, unknown>) => {
        g.attr("transform", event.transform.toString());
    });

// Apply the zoom behavior to the SVG
svg.call(zoom as any);

// Drawing grid lines
for (let i = 0; i <= numColumns; i++) {
    g.append("line")
        .attr("x1", i * gridSize)
        .attr("y1", 0)
        .attr("x2", i * gridSize)
        .attr("y2", canvasHeight)
        .style("stroke", "lightgrey")
        .style("stroke-width", "1px");
}
for (let i = 0; i <= numRows; i++) {
    g.append("line")
        .attr("x1", 0)
        .attr("y1", i * gridSize)
        .attr("x2", canvasWidth)
        .attr("y2", i * gridSize)
        .style("stroke", "lightgrey")
        .style("stroke-width", "1px");
}

// NODE CLASS
enum ImageType {
    ANY,
    MASK,
    IMAGE,
}

enum ConnectorDirection {
    OUTPUT,
    INPUT,
}

class NodeConnector {
    element: d3.Selection<SVGCircleElement, unknown, HTMLElement, any>;
    parent: NodeBlock;
    direction: ConnectorDirection;
    ctype: ImageType;
    connection: NodeConnector | null;
    line: d3.Selection<SVGLineElement, unknown, HTMLElement, any> | null;
    port: number;

    constructor(ctype: ImageType, direction: ConnectorDirection, portNumber: number, parent: NodeBlock) {
        this.parent = parent;
        this.element = g.append('circle')
                    .attr('cx', this.parent.x)
                    .attr('cy',this.parent.y)
                    .attr('r', 4)
                    .style('fill', 'white')
                    .style('stroke', 'black')
                    .classed('connector input', true);
        this.element.datum(this);
        this.port = portNumber;
        this.direction = direction;
        this.ctype = ctype;
        this.connection = null;
        this.line = null;

        this.element
            .on("mousedown", (event) => this.mouseDownHandler(event));
    }

    mouseDownHandler(event: MouseEvent) {
        event.stopPropagation();
        if (!this.connection) {
            this.line = g.append('line')
                             .attr('x1', this.element.attr('cx'))
                             .attr('y1', this.element.attr('cy'))
                             .attr('x2', this.element.attr('cx'))
                             .attr('y2', this.element.attr('cy'))
                             .attr('stroke', 'grey')
                             .attr('stroke-width', 2);
        }

        d3.select(window)
            .on('mousemove.connector', (e: MouseEvent) => this.mouseMoveHandler(e))
            .on('mouseup.connector', (e: MouseEvent) => this.mouseUpHandler(e, this));
    }

    mouseMoveHandler(event: MouseEvent) {
        if (!this.connection && this.line) {
            const coordinates = d3.pointer(event, g.node());
            this.line.attr('x2', coordinates[0])
                     .attr('y2', coordinates[1]);
        }
    }

    mouseUpHandler(event: MouseEvent, originalConnector: NodeConnector) {
        const elements = document.elementsFromPoint(event.clientX, event.clientY);
        const targetElement = elements.find(el => el.classList.contains('connector'));
        let targetConnector: NodeConnector | null = null;
        if (targetElement) {
            targetConnector = d3.select(targetElement).datum();
        }

        try {
            // Delete connection if clicked inside a connector
            if (originalConnector.connection) {
                if (originalConnector == targetConnector) {
                    originalConnector.disconnect();
                }
            // Create a connection
            } else {
                originalConnector.removeLine();
                if (targetConnector && originalConnector !== targetConnector) {
                    originalConnector.connect(targetConnector);
                }
            }
        } catch (error) {
            console.error("Connection failed: ", error);
        } finally {
            d3.select(window)
                .on('mousemove.connector', null)
                .on('mouseup.connector', null);
        }
    }

    connect(otherConnector: NodeConnector) {
        if (
                (!this.connection && !otherConnector.connection)
                && (this.direction !== otherConnector.direction)
                && (this.ctype === ImageType.ANY || otherConnector.ctype === ImageType.ANY || this.ctype === otherConnector.ctype)
                && (this.parent !== otherConnector.parent)
            ) {

            // Connect together
            this.connection = otherConnector;
            otherConnector.connection = this;
            console.log("Connected!");

            // Determine start vs end
            const startConnector = this.direction === ConnectorDirection.INPUT ? otherConnector : this;
            const endConnector   = this.direction === ConnectorDirection.INPUT ? this : otherConnector;

            startConnector.element?.style('fill', 'black');
            endConnector.element?.style('fill', 'black');

            // Draw a line between connectors
            const connectionLine = g.append("line")
                .attr("x1", startConnector.element.attr("cx"))
                .attr("y1", startConnector.element.attr("cy"))
                .attr("x2", endConnector.element.attr("cx"))
                .attr("y2", endConnector.element.attr("cy"))
                .style("stroke", "black")
                .style("stroke-width", "2px");
            startConnector.line = connectionLine;
            endConnector.line = connectionLine;

        } else {
            throw new Error("Cannot connect these connectors.");
        }
    }

    disconnect() {
        if (this.connection) {
            this.connection.removeLine();
            this.removeLine();

            this.connection.element?.style('fill', 'white');
            this.element?.style('fill', 'white');

            this.connection.connection = null;
            this.connection = null;
        }
    }

    toJSON() {
        return {
            ctype: this.ctype,
            direction: this.direction,
            port: this.port,
            x: +this.element.attr('cx'),
            y: +this.element.attr('cy'),
            connection: this.connection ? {
                parentName: this.connection.parent.name,
                port: this.connection.port
            } : null
        };
    }

    removeLine() {
        this.line?.remove();
        this.line = null;
    }

    cleanup(): void {
        this.disconnect();
        this.element?.remove()
    }
}

function showPopup(x: number, y: number, node: NodeBlock) {
    const popup = d3.select('#popup');
    popup.style('left', `${x}px`).style('top', `${y}px`).style('display', 'block');
    d3.select('#nodeValue').node().value = node.showOptions();

    d3.select('#valueForm').on('submit', function (event) {
        //event.preventDefault();
        //const newValue = d3.select('#nodeValue').node().value;
        //node.setValue(newValue);
        popup.style('display', 'none');  // Hide after update
    });
}

class CVFunction {
    name: string;
    color: string;
    options: Options;
    node: NodeBlock;
    inputs: ImageType[];
    outputs: ImageType[];

    constructor(name: string, color: string, options: Options, x: number, y: number, inputs: ImageType[], outputs: ImageType[]) {
        this.name = name;
        this.color = color;
        this.options = options;
        this.inputs = inputs;
        this.outputs = outputs;
        this.node = new NodeBlock(this.name, this.color, this.options, x, y, this.inputs, this.outputs, false);

        // Add to global state
        cvFunctions.push(this);
    }
}

class NodeBlock {
    name: string;
    color: string;
    options: Options;
    x: number;
    y: number;
    width: number;
    height: number;
    inputs: NodeConnector[];
    outputs: NodeConnector[];
    nodeElement: d3.Selection<SVGRectElement, unknown, HTMLElement, any>;
    enableGui: boolean;

    constructor(name: string, color: string, options: Options, x: number, y: number, inputs: ImageType[], outputs: ImageType[], enableGui: boolean) {
        this.name = name;
        this.color = color;
        this.options = options;
        this.x = x;
        this.y = y;
        this.width = 50;        // TODO: Calculate based on inputs
        this.height = 50;
        this.inputs = [];
        this.outputs = [];
        this.enableGui = enableGui;
        this.draw();

        // Create connectors
        for (let i = 0; i < inputs.length; i++) {
            const input = new NodeConnector(
                inputs[i],
                ConnectorDirection.INPUT,
                i+1,
                this
            );
            this.inputs.push(input);
        }
        for (let i = 0; i < outputs.length; i++) {
            const output = new NodeConnector(
                outputs[i],
                ConnectorDirection.OUTPUT,
                i+1,
                this
            );
            this.outputs.push(output);
        }
        this.updatePosition();

        this.nodeElement.on('contextmenu', (event, d) => {
            event.preventDefault();  // Prevent the default context menu
            const x = event.pageX;
            const y = event.pageY;
            showPopup(x, y, this);
        });
    }

    showOptions() {
       return JSON.stringify(this.options);
    }

    draw(): void {
        this.nodeElement = g.append('rect')
            .attr('x', this.x)
            .attr('y', this.y)
            .attr('width', this.width)
            .attr('height', this.height)
            .style('fill', this.color)
            .attr('cursor', 'move')
            .call(d3.drag<SVGRectElement, any>()
                .on('start', event => this.startDrag(event))
                .on('drag', event => this.drag(event))
                .on('end', event => this.endDrag(event)));

        this.nodeElement.append('text')
            .attr('x', this.x + this.width / 2)
            .attr('y', this.y + this.height / 2)
            .attr('dy', '.35em') // Vertical align middle
            .attr('text-anchor', 'middle') // Horizontal align center
            .text(this.name);
    }

    startDrag(event): void {
        d3.select(this.nodeElement.node()).classed('dragging', true);
    }

    drag(event): void {
        const newX = event.x - this.width / 2;
        const newY = event.y - this.height / 2;
        this.x = newX;
        this.y = newY;
        this.updatePosition();
    }

    endDrag(event): void {
        const snappedX = snapToGrid(event.x, gridSize) - this.width / 2;
        const snappedY = snapToGrid(event.y, gridSize) - this.height / 2;
        this.x = snappedX;
        this.y = snappedY;
        this.updatePosition();
        d3.select(this.nodeElement.node()).classed('dragging', false);
    }

    updatePosition(): void {
        this.nodeElement.attr('x', this.x).attr('y', this.y);
        this.inputs.forEach((input, index) => {
            const cx = this.x;
            const cy = this.y + this.height / (this.inputs.length + 1) * (index + 1);
            input.element.attr('cx', cx).attr('cy', cy);
            if (input.connection && input.line) {
                input.line.attr("x2", cx).attr("y2", cy);
            }
        });
        this.outputs.forEach((output, index) => {
            const cx = this.x + this.width;
            const cy = this.y + this.height / (this.outputs.length + 1) * (index + 1);
            output.element.attr('cx', cx).attr('cy', cy);
            if (output.connection && output.line) {
                output.line.attr("x1", cx).attr("y1", cy);
            }
        });
    }

    toJSON() {
        return {
            name: this.name,
            color: this.color,
            options: this.options,
            x: this.x,
            y: this.y,
            inputs: this.inputs.map(input => input.toJSON()),
            outputs: this.outputs.map(output => output.toJSON())
        };
    }

    static fromJSON(data: any) {
        const nodeBlock = new NodeBlock(
            data.name,
            data.color,
            data.options,
            data.x,
            data.y,
            data.inputs.map(input => input.ctype),
            data.outputs.map(output => output.ctype),
            false
        );
        return nodeBlock;
    }
}

// Save and Load functions
function saveCanvas() {
    const state = cvFunctions.map(func => ({
        name: func.name,
        color: func.color,
        options: func.options,
        node: func.node.toJSON()
    }));

    const json = JSON.stringify(state);
    localStorage.setItem('canvasState', json);
    console.log(json);
}

function loadCanvas() {
    const json = localStorage.getItem('canvasState');
    if (!json) {
        return;
    }
    console.log(json);

    const state = JSON.parse(json);
    clearCanvas();
    state.forEach((funcState: any) => {
        const cvFunction = new CVFunction(
            funcState.name,
            funcState.color,
            funcState.options,
            funcState.node.x,
            funcState.node.y,
            funcState.node.inputs.map(input => input.ctype),
            funcState.node.outputs.map(output => output.ctype)
        );

        // Restore connections
        funcState.node.inputs.forEach((inputData: any, index: number) => {
            if (inputData.connection) {
                const targetFunc = cvFunctions.find(f => f.name === inputData.connection.parentName);
                if (targetFunc) {
                    const targetConnector = targetFunc.node.outputs.find(output => output.port === inputData.connection.port);
                    if (targetConnector) {
                        cvFunction.node.inputs[index].connect(targetConnector);
                    }
                }
            }
        });
    });
}

function clearCanvas() {
    cvFunctions.forEach(func => {
        func.node.nodeElement.remove();
        func.node.inputs.forEach(connector => connector.cleanup());
        func.node.outputs.forEach(connector => connector.cleanup());
    });
    cvFunctions = [];
}

// Connect buttons to save and load functions
document.getElementById("saveButton").addEventListener("click", saveCanvas);
document.getElementById("loadButton").addEventListener("click", loadCanvas);

// HANDLERS
const shapes = d3.selectAll('.shape');
shapes.on('dragstart', (event, d) => {
    const shape = d3.select(event.currentTarget);

    event.dataTransfer.setData('color', shape.style('background-color'));
});

svg.on('dragover', (event) => {
    event.preventDefault();  // Necessary to allow dropping
})
.on('drop', (event) => {
    event.preventDefault();
    const functionName = event.dataTransfer.getData('function-name');
    const point = d3.pointer(event, g.node());
    const x = Math.floor(point[0] / gridSize) * gridSize;
    const y = Math.floor(point[1] / gridSize) * gridSize;
    const cvTemplate = cvFunctionTemplates.find(func => func.name === functionName);
    if (cvTemplate) {
        new CVFunction(cvTemplate.name, cvTemplate.color, cvTemplate.options, x, y, cvTemplate.inputs, cvTemplate.outputs);
    }
});

function snapToGrid(coordinate: number, gridSize: number): number {
    const nearestLower = Math.floor(coordinate / gridSize) * gridSize;
    const nearestHigher = Math.ceil(coordinate / gridSize) * gridSize;
    return (Math.abs(nearestLower - coordinate) < Math.abs(nearestHigher - coordinate))
        ? nearestLower
        : nearestHigher;
}

function createNodeBlock(x: number, y: number, color: string): void {
    const nodeBlock = new NodeBlock(color, x, y, 50, 50, 3, 2, false);
}

interface Options {
    [key: string]: number;
}

// CVFunction templates for the drawer
const cvFunctionTemplates: { name: string, color: string, options: Options, inputs: ImageType[], outputs: ImageType[] }[] = [
    {
        name: "Blur",
        color: "blue",
        options: {
            "kernelSize": 0,
            "strength": 50
        },
        inputs: [ImageType.ANY],
        outputs: [ImageType.ANY]
    },
    {
        name: "Threshold",
        color: "green",
        options: {
            "min_h": 0,
            "min_s": 0,
            "min_v": 0,
            "max_h": 180,
            "max_s": 255,
            "max_v": 255,
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE]
    },
    {
        name: "Edge Detection",
        color: "red",
        options: {
            "min_area": 400,
        },
        inputs: [ImageType.ANY],
        outputs: [ImageType.IMAGE, ImageType.MASK]
    },
];

const drawer = d3.select("#drawer");

cvFunctionTemplates.forEach((template) => {
    const cvElement = drawer.append("div")
        .attr("class", "cv-function")
        .attr("draggable", true)
        .style("background-color", template.color)
        .text(template.name)
        .on("dragstart", (event) => {
            event.dataTransfer.setData("function-name", template.name);
        });
});

