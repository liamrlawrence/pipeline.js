// Set the dimensions of the canvas / graph
var canvasWidth = 1000,
    canvasHeight = 700;

// Grid size and number of lines
var gridSize = 25;
var numColumns = canvasWidth / gridSize;
var numRows = canvasHeight / gridSize;

// Append the svg canvas to the container div
var svg = d3.select("#canvas-container").append("svg")
    .attr("width", canvasWidth)
    .attr("height", canvasHeight)
    .attr("viewBox", `0 0 ${canvasWidth} ${canvasHeight}`);

// Create the group that will be transformed during zooming and panning
var g = svg.append("g");

// Create zoom behavior with constraints
var zoom = d3.zoom()
    .scaleExtent([1, 10])
    .translateExtent([[-gridSize, -gridSize], [canvasWidth + gridSize, canvasHeight + gridSize]])
    .on("zoom", function(event) {
        g.attr("transform", event.transform);
    });

// Apply the zoom behavior to the SVG
svg.call(zoom);

// Drawing grid lines
for (var i = 0; i <= numColumns; i++) {
    g.append("line")
        .attr("x1", i * gridSize)
        .attr("y1", 0)
        .attr("x2", i * gridSize)
        .attr("y2", canvasHeight)
        .style("stroke", "lightgrey")
        .style("stroke-width", "1px");
}
for (var i = 0; i <= numRows; i++) {
    g.append("line")
        .attr("x1", 0)
        .attr("y1", i * gridSize)
        .attr("x2", canvasWidth)
        .attr("y2", i * gridSize)
        .style("stroke", "lightgrey")
        .style("stroke-width", "1px");
}


const node = {
    x: 0,
    y: 0,
    width: 10,
    height: 10,

}


// Drag and drop logic for shapes
var shapes = document.querySelectorAll('#drawer .shape');
shapes.forEach(shape => {
    shape.addEventListener('dragstart', function(event) {
        var color = shape.style.backgroundColor;
        event.dataTransfer.setData("application/my-app", color);
        event.dataTransfer.effectAllowed = "move";
    });
});







///////////////////////////////////////////////////////////////////////////////
// Function to add connectors to a shape
function addShapeWithConnectors(coords, color, inputs, outputs) {
    const group = g.append('g'); // Create a group for the shape and its connectors

    const newShape = group.append('rect') // Append the shape to the group
        .attr('x', coords[0] - gridSize)
        .attr('y', coords[1] - gridSize)
        .attr('width', 50)
        .attr('height', 50)
        .style('fill', color);

    addConnectors(group, coords, 50, 50, inputs, outputs); // Add connectors
    applyDraggableToShapes();
}

function addConnectors(group, coords, width, height, inputs, outputs) {
    const connectorRadius = 5;
    // Creating input connectors
    for (let i = 0; i < inputs; i++) {
        group.append('circle')
            .attr('cx', coords[0] - gridSize)
            .attr('cy', parseInt(coords[1]) - gridSize + (i + 1) * height / (inputs + 1))
            .attr('r', connectorRadius)
            .style('fill', 'black');
    }
    // Creating output connectors
    for (let i = 0; i < outputs; i++) {
        group.append('circle')
            .attr('cx', parseInt(coords[0]) - gridSize + width)
            .attr('cy', parseInt(coords[1]) - gridSize + (i + 1) * height / (outputs + 1))
            .attr('r', connectorRadius)
            .style('fill', 'black');
    }
}



let currentLine = null;

svg.on("mousedown", function(event) {
    if (d3.select(event.target).node().tagName === 'circle') {
        var coords = d3.pointer(event);
        currentLine = g.append('line')
            .attr('x1', coords[0])
            .attr('y1', coords[1])
            .attr('x2', coords[0])
            .attr('y2', coords[1])
            .style('stroke', 'black')
            .style('stroke-width', '2px');
        svg.on("mousemove", function(event) {
            var coords = d3.pointer(event);
            currentLine.attr('x2', coords[0])
                       .attr('y2', coords[1]);
        });
    }
})
.on("mouseup", function() {
    svg.on("mousemove", null);
});


///////////////////////////////////////////////////////////////////////////////








svg.on("dragover", function(event) {
    event.preventDefault();
}).on("drop", function(event) {
    event.preventDefault();
    var color = event.dataTransfer.getData("application/my-app");
    var coords = d3.pointer(event, g.node());
    var newShape = g.append('rect')
        .attr('x', coords[0] - gridSize)
        .attr('y', coords[1] - gridSize)
        .attr('width', 50)
        .attr('height', 50)
        .style('fill', color);
    addConnectors(newShape, 3, 2); // Example with 3 inputs and 2 outputs
    applyDraggableToShapes();
});

// Drag behavior for shapes on the canvas
//function dragstarted(event, d) {
//    var shape = d3.select(this);
//    shape.target.classList.add('dragging');
//    shape.attr('data-original-stroke', shape.attr('stroke') || 'none');
//    shape.raise().attr('stroke', 'black');
//    svg.on(".zoom", null);
//}
//


function dragged(event, d) {
    var shape = d3.select(this);
    // Ensure the shape remains within the bounds of the canvas
    var x = Math.max(gridSize, Math.min(canvasWidth - gridSize - 50, event.x)); // Account for shape width
    var y = Math.max(gridSize, Math.min(canvasHeight - gridSize - 50, event.y)); // Account for shape height
    shape.attr("x", x - 25) // Adjust by half width of shape for centering
         .attr("y", y - 25); // Adjust by half height of shape for centering
}

function dragstarted(event, d) {
    var shape = d3.select(this); // 'this' is the shape being dragged
    shape.classed('dragging', true);
    shape.raise().attr('stroke', 'black');
    svg.on(".zoom", null); // Disable zooming when dragging starts
}

function dragended(event, d) {
    var shape = d3.select(this);
    shape.classed('dragging', false); // Remove the 'dragging' class
    shape.attr('stroke', shape.attr('data-original-stroke') || null); // Restore the original stroke
    svg.call(zoom); // Re-enable zooming
    // Additional check to remove the shape if it's outside the SVG bounds
    if (event.x < 0 || event.x > canvasWidth || event.y < 0 || event.y > canvasHeight) {
        shape.remove();
    }
}


function applyDraggableToShapes() {
    g.selectAll('rect')
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
}

applyDraggableToShapes();

