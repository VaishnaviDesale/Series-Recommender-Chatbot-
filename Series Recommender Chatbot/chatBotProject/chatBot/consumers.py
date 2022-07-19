import json
from channels.generic.websocket import WebsocketConsumer
from pyparsing import rest_of_line
from . import model

class Calculator(WebsocketConsumer):
	def connect(self):
		self.accept()
		self.chatObj = model.chatBot()

	def disconnect(self, close_code):
		self.close()

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		expression = text_data_json['expression']
		result = self.chatObj.related(expression)
		self.send(text_data=json.dumps({
			'result': result
		}))

