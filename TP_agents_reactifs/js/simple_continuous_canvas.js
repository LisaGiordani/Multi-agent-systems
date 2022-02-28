var ContinuousVisualization = function(height, width, context) {
	var height = height;
	var width = width;
	var context = context;
    context.transform(1, 0, 0, -1, 0, height);

	this.draw = function(objects) {
		for (var i in objects) {
			var l = objects[i];
			for (var j in l){
			    var p = l[j]
                if (p.Shape == "circle")
                    this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
    		};
		};
	};

	this.drawCircle = function(x, y, radius, color, fill) {
		var cx = x * width;
		var cy = y * height;
		var r = radius;

		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();
		if (fill == "true") {
			context.fillStyle = color;
			context.fill();
		}

	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, height, width);
		context.beginPath();
	};
};

var Simple_Continuous_Module = function(canvas_width, canvas_height, ids) {
	// Create the element
	// ------------------

	// Create the tag:
	var canvas_tag = "<canvas id='" + ids + "' width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	$("#elements").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		canvasDraw.draw(data);
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
