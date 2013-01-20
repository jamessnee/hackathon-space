var Controller = function() {
	this.id = 0;
	var host = 'ws://localhost:8080/drop';
	if (typeof localStorage.socket !== 'undefined') {
	//	this.socket = localStorage.socket;
	//	this.socket.close();
	}
	
	this.socket = new WebSocket(host);
	localStorage.socket = this.socket;
	
	this.canvas = $('#gameViewCanvas');
	this.painter = new ObjectPainter();
	
	// initialize events
	this.eventHandlers = {};
	this.events();
	
	// initialize canvas
	this.painter.initialize();
}

Controller.prototype.send = function(msg) {
	this.socket.send('ID:' + this.id + ' ' + msg);
	// this.socket.send(msg);
}

Controller.prototype.events = function() {
	var self = this;
	this.eventHandlers.canvasClick = function(event) {
		var position = self.canvas.position();
		var x = event.pageX - position.left;
		var y = event.pageY - position.top;
		console.log('clicked !!!', x, y);
		self.send('DSEND ' + x);
	};
	
	this.eventHandlers.onServerMessage = function(msg) {
		// console.log('message ', msg);
		// console.log('data', msg.data);
		if (!msg) {
			return;
		}
		
		if (msg.data === 'PING') {
			self.send('PONG');
			return;
		}
		
		if (msg.data.indexOf("ID") == 0) {
			self.id = msg.data.substring(3);
			console.log('id ' + self.id);
			return;
		}
		
		// parse world state
		var statePrefix = 'STATE K:';
		if (msg.data.indexOf(statePrefix) != 0) {
			return;
		}
		
		var dataString = msg.data.substring(statePrefix.length);
		var dataArray = dataString.split(' ');
		
		// set up state object
		var state = {};
		state.player = { x : parseInt(dataArray[0]) };
		state.objects = [];
		
		// Queue dataArray[1]

		// Lives dataArray[2]
		var livesString = dataArray[2];
		livesString = livesString.substring(livesString.indexOf(':') + 1)
		state.player.livesCount = parseInt(livesString);
		
		// parse dropped item positions
		if (dataArray.length > 3) {
			dataArray = dataArray.splice(3);
			for (var index in dataArray) {
				var colonIndex = dataArray[index].indexOf(':');
				var xyString = dataArray[index].substring(colonIndex + 1);
				var xy = xyString.split(',');
				state.objects.push({ x : parseInt(xy[0]), y : parseInt(xy[1]) });
			}			
		}
		
		//var world = JSON.parse(msg.data);
		//console.log('parsed data', state);
		self.painter.updateScreen(state);
	};
	
	this.eventHandlers.onOpen = function() {
		console.log('opened socket; trying to connect...');
		self.send('REQ CON D');
		// self.send('REQ CON K');
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
})