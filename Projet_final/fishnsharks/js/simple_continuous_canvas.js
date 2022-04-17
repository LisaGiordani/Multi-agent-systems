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
                if (p.Shape == "line")
                    this.drawLine(p.from_x, p.from_y, p.to_x, p.to_y, p.width, p.Color);
                if (p.Shape =="arrowHead")
                    this.drawArrrowHead(p.x,p.y,p.angle,p.s,p.Color,p.Filled);
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

    this.drawLine = function(fx,fy,tx,ty, w, color){
		context.beginPath();
		var fromX = fx * width;
		var fromY = fy * height;
		var toX = tx * width;
		var toY= ty * height;

		context.moveTo(fromX,fromY);
		context.lineTo(toX,toY);
		context.lineWidth = w;
		context.strokeStyle = color;
		context.stroke();
	};

    this.drawArrrowHead = function(x,y,angle,s,color,fill){
		var xc=x*width;
		var yc=y*height;
        context.lineWidth = 1;
        context.strokeStyle = color;
        context.fillStyle = color;

        context.save();
        context.translate(xc,yc);
        context.rotate(angle);
        context.scale(s,s);

        context.beginPath();
        context.moveTo(-5,-5);
        context.lineTo(5,0);
        context.lineTo(-5,5);
 	    context.closePath();

        if(fill == "true")
            context.fill();
                context.stroke();
        context.restore();
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
