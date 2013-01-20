var Controller = function() {
	var host = 'ws://localhost:8080/drop';
	this.socket = new WebSocket(host);
	this.canvas = $('#gameViewCanvas');
	this.painter = new ObjectPainter(this.canvas[0]);
	
	// initialize events
	this.eventHandlers = {};
	this.events();
	
	// initialize canvas
	this.painter.initialize();
}

Controller.prototype.events = function() {
	var self = this;
	this.eventHandlers.canvasClick = function(event) {
		var position = self.canvas.position();
		var x = event.pageX - position.left;
		var y = event.pageY - position.top;
		console.log('clicked !!!', x, y);
		self.socket.send('DSEND ' + x);
		/*
		self.painter.updateScreen({
			objects : [ { x: x, y : y }, { x: x+60, y: y+60 } ],
			player : { x : x }
		});
		*/
		/*self.painter.clear();
		self.painter.drawBackground();
		self.painter.drawAsteroid(x, y);
		self.painter.drawSpacecraft(x);
		*/
	};
	
	this.eventHandlers.onServerMessage = function(msg) {
		console.log('message ', msg);
		console.log('data', msg.data);
		
		if (msg && msg.data === 'PING') {
			self.socket.send('PONG');
			return;
		}
		
		//var world = JSON.parse(msg.data);
		//console.log('parsed data', world);
		//self.painter.updateScreen(world);
	};
	
	this.eventHandlers.onOpen = function() {
		console.log('opened socket; trying to connect...');
		self.socket.send('REQ CON D');
		self.painter.initialize();
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
	controller.painter.drawBomb(100, 100);
})