var World = function() {
	
}

var Controller = function() {
	var host = 'ws://localhost:8080/echo';
	this.socket = new WebSocket(host);
	this.canvas = $('#gameViewCanvas');
	this.painter = new ObjectPainter(this.canvas[0]);
	this.eventHandlers = {};
	this.events();
}

Controller.prototype.events = function() {
	var self = this;
	this.eventHandlers.canvasClick = function(event) {
		var position = self.canvas.position();
		var x = event.pageX - position.left;
		var y = event.pageY - position.top;
		console.log('clicked !!!', x, y);
		self.painter.updateScreen({
			objects : [ { x: x, y : y }, { x: x+60, y: y+60 } ],
			player : { x : x }
		});
		/*self.painter.clear();
		self.painter.drawBackground();
		self.painter.drawAsteroid(x, y);
		self.painter.drawSpacecraft(x);
		*/
	};
	
	this.eventHandlers.onServerMessage = function(msg) {
		console.log('message ', msg);
		console.log('data', msg.data);
		
		var world = JSON.parse(msg.data);
		console.log('parsed data', world);
		self.painter.updateScreen(world);
	};
	
	this.eventHandlers.onOpen = function() {
		console.log('opened socket');
		self.socket.send('hello');
	};
	
	this.eventHandlers.onClose = function() {
		console.log('closing socket');
	};
}

Controller.prototype.initEventHandlers = function() {
	this.canvas.click(this.eventHandlers.canvasClick);
	this.socket.onopen = this.eventHandlers.onOpen;
	this.socket.onmessage = this.eventHandlers.onServerMessage;
	this.socket.onclose = this.eventHandlers.onClose;
}

// on load
$(function() {
	var controller = new Controller();
	controller.initEventHandlers();
	controller.painter.drawAsteroid(100, 100);
})