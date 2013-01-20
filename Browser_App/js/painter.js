var ObjectPainter = function(canvas, spacecraftImage) {
	this.canvas = canvas;
	this.ctx = canvas.getContext('2d');
	
	this.spacecraftImage = $('#spacecraft')[0];
	this.spacecraftY = this.canvas.height - this.spacecraftImage.height;
	
	this.backgroundImage = $('#background')[0];
	this.bombImage = $('#bomb')[0];
}

ObjectPainter.prototype.drawBomb = function(x, y) {
	this.ctx.drawImage(this.bombImage, x, y);
	/*var radius = 20;
	var ctx = this.context;
	this.ctx.beginPath();
	this.ctx.arc(x, y, radius, 0, Math.PI * 2, true); // Outer circle
	this.ctx.fillStyle = '#ff0000';
	this.ctx.fill();
	*/
	/*
	this.ctx.moveTo(110,75);
	this.ctx.arc(75,75,35,0,Math.PI,false);   // Mouth (clockwise)
	this.ctx.moveTo(65,65);
	this.ctx.arc(60,65,5,0,Math.PI*2,true);  // Left eye
	this.ctx.moveTo(95,65);
	this.ctx.arc(90,65,5,0,Math.PI*2,true);  // Right eye
	this.ctx.stroke();
	*/
}

ObjectPainter.prototype.drawSpacecraft = function(x) {
	this.ctx.drawImage(this.spacecraftImage, x, this.spacecraftY);
}

ObjectPainter.prototype.drawBackground = function() {
	this.ctx.drawImage(this.backgroundImage, 0, 0);
}

ObjectPainter.prototype.clear = function() {
	this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
}

ObjectPainter.prototype.initialize = function() {
	this.clear();
	this.drawBackground();
}

/*
world = {
	objects : [ { x : 1, y : 1 }, ... ],
	player : { x : 1 }
}
*/
ObjectPainter.prototype.updateScreen = function(world) {
	world = world || {
		objects: [],
		player: { 
			x: 0 
		}
	};
	
	// draw background
	this.clear();
	this.drawBackground();
	
	// draw player
	this.drawSpacecraft(world.player.x);
	
	for (var index in world.objects) {
		var x = world.objects[index].x;
		var y = world.objects[index].y;
		this.drawBomb(x, y);
	}
}