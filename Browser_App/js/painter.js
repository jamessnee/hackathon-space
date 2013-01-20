var ObjectPainter = function() {
	this.canvas = $('#gameViewCanvas')[0];
	this.ctx = this.canvas.getContext('2d');
	
	this.backgroundCanvas = $('#backgroundCanvas')[0];
	this.backgroundCtx = this.backgroundCanvas.getContext('2d');
	
	var self = this;
	this.spacecraftImage = $('#spacecraft')[0];
	this.spacecraftImage.onload = function() {
		self.spacecraftY = self.canvas.height - self.spacecraftImage.height;
	}
	
	this.backgroundImage = $('#background')[0];
	this.bombImage = $('#bomb')[0];
}

ObjectPainter.prototype.drawBomb = function(x, y) {
	this.ctx.drawImage(this.bombImage, x, y);
}

ObjectPainter.prototype.drawSpacecraft = function(x) {
	this.ctx.drawImage(this.spacecraftImage, x + 20, this.spacecraftY);
}

ObjectPainter.prototype.drawBackground = function() {
	this.backgroundCtx.drawImage(this.backgroundImage, 0, 0);
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
	
	// clear objects from canvas
	this.clear();
	
	// draw player
	this.drawSpacecraft(world.player.x);
	
	for (var index in world.objects) {
		var x = world.objects[index].x;
		var y = world.objects[index].y;
		this.drawBomb(x, y);
	}
}