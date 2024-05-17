import * as d3 from "d3";


// Global state to keep track of NodeBlock objects
let nodeBlocks: NodeBlock[] = [];
const nodeBlockCounts: { [key: string]: number } = {};

// CANVAS //
const canvasWidth: number = 1280,
      canvasHeight: number = 720;

const gridSize: number = 20;
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

    nodeColor(ctype: ImageType) {
        switch (ctype) {
            case ImageType.ANY:
                return 'purple';
            case ImageType.IMAGE:
                return 'blue';
            case ImageType.MASK:
                return 'red';
        }
    }

    constructor(ctype: ImageType, direction: ConnectorDirection, portNumber: number, parent: NodeBlock) {
        this.parent = parent;
        this.ctype = ctype;
        this.element = g.append('circle')
                    .attr('cx', this.parent.x)
                    .attr('cy', this.parent.y)
                    .attr('r', 4)
                    .style('fill', this.nodeColor(this.ctype))
                    .style('stroke', 'black')
                    .classed('connector input', true);
        this.element.datum(this);
        this.port = portNumber;
        this.direction = direction;
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
                && (this.ctype === otherConnector.ctype)
                && (this.parent !== otherConnector.parent)
            ) {

            // Connect together
            this.connection = otherConnector;
            otherConnector.connection = this;
            //console.log("Connected!");

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

            this.connection.element?.style('fill', this.nodeColor(this.ctype));
            this.element?.style('fill', this.nodeColor(this.connection.ctype));

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
                parentID: this.connection.parent.ID,
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

// Update the showPopup function to populate options
function showPopup(x: number, y: number, node: NodeBlock) {
    const popup = d3.select('#popup');
    popup.style('left', `${x}px`).style('top', `${y}px`).style('display', 'block');

    const optionsContainer = d3.select('#optionsContainer');
    optionsContainer.selectAll('*').remove(); // Clear previous options

    Object.entries(node.options).forEach(([key, value]) => {
        const optionRow = optionsContainer.append('div');
        optionRow.append('label')
            .attr('for', `option-${key}`)
            .text(key);
        optionRow.append('input')
            .attr('type', 'number')
            .attr('id', `option-${key}`)
            .attr('value', value as number)
            .attr('name', key);
    });

    d3.select('#valueForm').on('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(this as HTMLFormElement);
        formData.forEach((value, key) => {
            node.options[key] = Number(value);
        });
        node.showOptions();
        popup.style('display', 'none'); // Hide after update
    });

     // Clear any existing delete button and add the delete button
    popup.select('#deleteButton').remove();
    const deleteButton = popup.append('button')
        .attr('id', 'deleteButton')
        .text('Delete Node')
        .on('click', () => {
            node.cleanup(); // Correctly using arrow function to preserve 'this' context
            popup.style('display', 'none'); // Hide the popup after deletion
        });

    // Add a one-time event listener to the document to hide the popup on outside click
    d3.select(document).on('click.popup', function (event) {
        const isClickInside = (popup.node() as HTMLElement).contains(event.target as Node);
        if (!isClickInside) {
            popup.style('display', 'none');
            d3.select(document).on('click.popup', null); // Remove the document click listener
        }
    });
}

class NodeBlock {
    stageName: string;
    ID: string;
    options: Options;
    inputs: NodeConnector[];
    outputs: NodeConnector[];
    color: string;
    textColor: string;
    width: number;
    height: number;
    x: number;
    y: number;
    lastX: number;
    lastY: number;
    nodeElement: d3.Selection<SVGRectElement, unknown, HTMLElement, any>;
    textElement: d3.Selection<SVGTextElement, unknown, HTMLElement, any>;
    enableGui: boolean;

    constructor(stage_name: string, options: Options, inputs: ImageType[], outputs: ImageType[], color: string, textColor: string, x: number, y: number, enableGui: boolean) {
        if (!nodeBlockCounts[stage_name]) {
            nodeBlockCounts[stage_name] = 0;
        }
        nodeBlockCounts[stage_name] += 1;
        this.stageName = stage_name;
        this.ID = `${stage_name}-${nodeBlockCounts[stage_name]}`;
        this.options = { ...options };
        this.inputs = [];
        this.outputs = [];
        this.color = color;
        this.textColor = textColor;
        this.x = x;
        this.y = y;
        this.lastX = x;
        this.lastY = y;
        this.width = 40;        // TODO: Calculate based on inputs
        this.height = 40;
        this.enableGui = enableGui;
        this.draw();

        // Create connectors
        for (let i = 0; i < inputs.length; i++) {
            const input = new NodeConnector(
                inputs[i],
                ConnectorDirection.INPUT,
                i + 1,
                this
            );
            this.inputs.push(input);
        }
        for (let i = 0; i < outputs.length; i++) {
            const output = new NodeConnector(
                outputs[i],
                ConnectorDirection.OUTPUT,
                i + 1,
                this
            );
            this.outputs.push(output);
        }
        this.updatePosition();

        // Create hooks TODO: Move?
        this.nodeElement.on('contextmenu', (event, d) => {
            event.preventDefault();  // Prevent the default context menu
            const x = event.pageX;
            const y = event.pageY;
            showPopup(x, y, this);
        });

        // Add to global state
        nodeBlocks.push(this);
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

        this.textElement = g.append('text')
            .attr('x', this.x + this.width / 2)
            .attr('y', this.y + this.height / 2)
            .attr('dy', '.35em')            // Vertical align middle
            .attr('text-anchor', 'middle')  // Horizontal align center
            .style('fill', this.textColor)
            .style('user-select', 'none')   // Disable highlighting
            .text(this.ID);
    }

    startDrag(event): void {
        d3.select(this.nodeElement.node()).classed('dragging', true);
    }

    drag(event): void {
        let newX = event.x - this.width / 2;
        let newY = event.y - this.height / 2;

        const collision = this.detectCollision(newX, newY);
        if (collision) {
            const { node, direction } = collision;
            switch (direction) {
                case 'left':
                    newX = node.x - this.width;
                    break;
                case 'right':
                    newX = node.x + node.width;
                    break;
                case 'top':
                    newY = node.y - this.height;
                    break;
                case 'bottom':
                    newY = node.y + node.height;
                    break;
            }

            // Check for further collisions in the sliding direction with a limit
            const maxAttempts = 100;
            let attempt = 0;
            let furtherCollision = this.detectCollision(newX, newY);
            while (furtherCollision && attempt < maxAttempts) {
                const { node: furtherNode, direction: furtherDirection } = furtherCollision;
                switch (furtherDirection) {
                    case 'left':
                        newX = furtherNode.x - this.width;
                        break;
                    case 'right':
                        newX = furtherNode.x + furtherNode.width;
                        break;
                    case 'top':
                        newY = furtherNode.y - this.height;
                        break;
                    case 'bottom':
                        newY = furtherNode.y + furtherNode.height;
                        break;
                }
                furtherCollision = this.detectCollision(newX, newY);
                attempt++;
            }
        }

        this.x = newX;
        this.y = newY;
        this.lastX = newX;
        this.lastY = newY;
        this.updatePosition();
    }

    endDrag(event): void {
        const snappedX = snapToGrid(event.x, gridSize) - this.width / 2;
        const snappedY = snapToGrid(event.y, gridSize) - this.height / 2;

        let newX = snappedX;
        let newY = snappedY;

        const collision = this.detectCollision(newX, newY);
        if (collision) {
            const { node, direction } = collision;
            switch (direction) {
                case 'left':
                    newX = node.x - this.width;
                    break;
                case 'right':
                    newX = node.x + node.width;
                    break;
                case 'top':
                    newY = node.y - this.height;
                    break;
                case 'bottom':
                    newY = node.y + node.height;
                    break;
            }

            // Check for further collisions in the sliding direction
            const maxAttempts = 100;
            let attempt = 0;
            let furtherCollision = this.detectCollision(newX, newY);
            while (furtherCollision && attempt < maxAttempts) {
                const { node: furtherNode, direction: furtherDirection } = furtherCollision;
                switch (furtherDirection) {
                    case 'left':
                        newX = furtherNode.x - this.width;
                        break;
                    case 'right':
                        newX = furtherNode.x + furtherNode.width;
                        break;
                    case 'top':
                        newY = furtherNode.y - this.height;
                        break;
                    case 'bottom':
                        newY = furtherNode.y + furtherNode.height;
                        break;
                }
                furtherCollision = this.detectCollision(newX, newY);
                attempt++;
            }
        }

        this.x = newX;
        this.y = newY;
        this.lastX = newX;
        this.lastY = newY;
        this.updatePosition();
        d3.select(this.nodeElement.node()).classed('dragging', false);
    }

    detectCollision(x: number, y: number): { node: NodeBlock, direction: 'left' | 'right' | 'top' | 'bottom' } | null {
        for (const node of nodeBlocks) {
            if (node !== this) {
                if (
                    x < node.x + node.width &&
                    x + this.width > node.x &&
                    y < node.y + node.height &&
                    y + this.height > node.y
                ) {
                    const leftOverlap = x + this.width - node.x;
                    const rightOverlap = node.x + node.width - x;
                    const topOverlap = y + this.height - node.y;
                    const bottomOverlap = node.y + node.height - y;

                    const minOverlap = Math.min(leftOverlap, rightOverlap, topOverlap, bottomOverlap);

                    if (minOverlap === leftOverlap) return { node, direction: 'left' };
                    if (minOverlap === rightOverlap) return { node, direction: 'right' };
                    if (minOverlap === topOverlap) return { node, direction: 'top' };
                    if (minOverlap === bottomOverlap) return { node, direction: 'bottom' };
                }
            }
        }
        return null;
    }

    updatePosition(): void {
        this.nodeElement.attr('x', this.x).attr('y', this.y);
        this.updateTextPosition();
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

    updateTextPosition(): void {
        this.adjustFontSizeToFit();

        const textX = this.x + this.width / 2;
        const textY = this.y + this.height / 2;
        this.textElement
            .attr('x', textX)
            .attr('y', textY);
    }

    adjustFontSizeToFit(): void {
        const maxWidth = this.width - 10;

        let fontSize = parseFloat(this.textElement.style('font-size'));
        if (isNaN(fontSize)) {
            fontSize = 16;
        }

        let textLength = this.textElement.node().getComputedTextLength();
        while (textLength > maxWidth && fontSize > 1) {
            fontSize -= 1;
            this.textElement.style('font-size', `${fontSize}px`);
            textLength = this.textElement.node().getComputedTextLength();
        }
    }

    toJSON() {
        return {
            stage_name: this.stageName,
            ID: this.ID,
            options: this.options,
            inputs: this.inputs.map(input => input.toJSON()),
            outputs: this.outputs.map(output => output.toJSON()),
            color: this.color,
            text_color: this.textColor,
            x: this.x,
            y: this.y,
        };
    }

    static fromJSON(data: any) {
        const nodeBlock = new NodeBlock(
            data.stage_name,
            data.options,
            data.inputs.map(input => input.ctype),
            data.outputs.map(output => output.ctype),
            data.color,
            data.text_color,
            data.x,
            data.y,
            false,
        );
        return nodeBlock;
    }

    cleanup() {
        this.nodeElement?.remove();
        this.textElement?.remove();
        this.inputs.forEach(connector => connector.cleanup());
        this.outputs.forEach(connector => connector.cleanup());
        nodeBlocks = nodeBlocks.filter(n => n !== this);
        nodeBlockCounts[this.stageName]--;
    }
}

// Save and Load functions
function saveCanvas() {
    const state = nodeBlocks.map(block => block.toJSON());

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

    // Create a mapping of IDs to NodeBlock objects
    const idToBlock: { [key: string]: NodeBlock } = {};

    // First, recreate all NodeBlock objects without restoring connections
    state.forEach((blockState: any) => {
        const nodeBlock = NodeBlock.fromJSON(blockState);
        idToBlock[nodeBlock.ID] = nodeBlock;
    });

    // Then, restore all connections
    state.forEach((blockState: any) => {
        const nodeBlock = idToBlock[blockState.ID];
        blockState.inputs.forEach((inputData: any, index: number) => {
            if (inputData.connection) {
                const targetBlock = idToBlock[inputData.connection.parentID];
                if (targetBlock) {
                    const targetConnector = targetBlock.outputs.find(output => output.port === inputData.connection.port);
                    if (targetConnector) {
                        nodeBlock.inputs[index].connect(targetConnector);
                    }
                }
            }
        });
    });
}

function clearCanvas() {
    nodeBlocks.forEach(block => block.cleanup());
    nodeBlocks = [];
    // Reset the counts
    for (const key in nodeBlockCounts) {
        if (nodeBlockCounts.hasOwnProperty(key)) {
            nodeBlockCounts[key] = 0;
        }
    }
    console.log(nodeBlocks);
}

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
    const nodeTemplate = nodeTemplates.find(func => func.stage_name === functionName);
    if (nodeTemplate) {
        new NodeBlock(nodeTemplate.stage_name, nodeTemplate.options, nodeTemplate.inputs, nodeTemplate.outputs, nodeTemplate.color, nodeTemplate.text_color, x, y, false);
    }
});

function snapToGrid(coordinate: number, gridSize: number): number {
    const nearestLower = Math.floor(coordinate / gridSize) * gridSize;
    const nearestHigher = Math.ceil(coordinate / gridSize) * gridSize;
    return (Math.abs(nearestLower - coordinate) < Math.abs(nearestHigher - coordinate))
        ? nearestLower
        : nearestHigher;
}

interface Options {
    [key: string]: number;
}

// NodeBlock templates for the drawer
const nodeTemplates: { stage_name: string, options: Options, inputs: ImageType[], outputs: ImageType[], color: string, text_color: string }[] = [
    {
        stage_name: "Input",
        options: {},
        inputs: [],
        outputs: [ImageType.IMAGE],
        color: "silver",
        text_color: "black",
    },
    {
        stage_name: "Output",
        options: {},
        inputs: [ImageType.IMAGE],
        outputs: [],
        color: "silver",
        text_color: "black",
    },
    {
        stage_name: "Blur",
        options: {
            "kernel_size": 1,
            "strength": 1
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE],
        color: "blue",
        text_color: "white",
    },
    {
        stage_name: "Threshold",
        options: {
            "min_h": 0,
            "min_s": 0,
            "min_v": 0,
            "max_h": 180,
            "max_s": 255,
            "max_v": 255,
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE],
        color: "green",
        text_color: "white",
    },
    {
        stage_name: "Contours-Circle",
        options: {
            "min_radius": 400,
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE, ImageType.MASK],
        color: "red",
        text_color: "white",
    },
    {
        stage_name: "Contours-ConvexHull",
        options: {
            "min_area": 400,
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE, ImageType.MASK],
        color: "red",
        text_color: "white",
    },
    {
        stage_name: "Bitwise AND",
        options: {},
        inputs: [ImageType.MASK, ImageType.IMAGE],
        outputs: [ImageType.IMAGE],
        color: "teal",
        text_color: "white",
    },
    {
        stage_name: "Dilate",
        options: {
            "kernel_size": 1,
            "iterations": 1
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE],
        color: "blue",
        text_color: "white",
    },
    {
        stage_name: "CLAHE",
        options: {
            "clip_limit": 2,
            "tile_grid_size": 2
        },
        inputs: [ImageType.IMAGE],
        outputs: [ImageType.IMAGE],
        color: "blue",
        text_color: "white",
    }
];

const drawer = d3.select("#drawer");

nodeTemplates.forEach((template) => {
    const nodeElement = drawer.append("div")
        .attr("class", "cv-function")
        .attr("draggable", true)
        .style("background-color", template.color)
        .text(template.stage_name)
        .on("dragstart", (event) => {
            event.dataTransfer.setData("function-name", template.stage_name);
        });
});

// Save the canvas state to a file
function saveCanvasToFile() {
    const state = nodeBlocks.map(block => block.toJSON());

    const json = JSON.stringify(state);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "canvasState.json";
    a.click();
    URL.revokeObjectURL(url);
}

// Load the canvas state from a file and add to the existing state
function loadCanvasFromFile(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
        const json = e.target?.result as string;
        const state = JSON.parse(json);

        // Create a mapping of old IDs to new IDs and NodeBlock objects
        const oldToNewIDMap: { [key: string]: string } = {};
        const idToBlock: { [key: string]: NodeBlock } = {};

        // First, recreate all NodeBlock objects without restoring connections
        state.forEach((blockState: any) => {
            const nodeBlock = NodeBlock.fromJSON(blockState);
            idToBlock[nodeBlock.ID] = nodeBlock;
            oldToNewIDMap[blockState.ID] = nodeBlock.ID;
        });

        console.log(oldToNewIDMap);

        // Then, restore all connections
        state.forEach((blockState: any) => {
            const newID = oldToNewIDMap[blockState.ID];
            const nodeBlock = idToBlock[newID];
            blockState.inputs.forEach((inputData: any, index: number) => {
                if (inputData.connection) {
                    const targetOldID = inputData.connection.parentID;
                    const targetNewID = oldToNewIDMap[targetOldID];
                    const targetBlock = idToBlock[targetNewID];
                    if (targetBlock) {
                        const targetConnector = targetBlock.outputs.find(output => output.port === inputData.connection.port);
                        if (targetConnector) {
                            nodeBlock.inputs[index].connect(targetConnector);
                        }
                    }
                }
            });
        });

        // Allow the same file to be loaded again
        input.value = '';
    };
    reader.readAsText(file);
}

// Connect buttons to save and load functions
document.getElementById("saveButton").addEventListener("click", saveCanvas);
document.getElementById("loadButton").addEventListener("click", loadCanvas);
document.getElementById("clearButton")?.addEventListener("click", clearCanvas);
document.getElementById("saveToFileButton").addEventListener("click", saveCanvasToFile);
document.getElementById("fileInput").addEventListener("change", loadCanvasFromFile);
document.getElementById("loadFromFileButton").addEventListener("click", () => {
    document.getElementById("fileInput").click();
});

