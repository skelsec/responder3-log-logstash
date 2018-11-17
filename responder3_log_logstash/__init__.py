# Work with Python 3.7
import asyncio
import traceback
import json

from responder3.core.logging.logtask import LoggerExtensionTask
from responder3.core.logging.logger import Logger, r3exception
from responder3.core.logging.log_objects import *
from responder3.core.commons import UniversalEncoder

class UnifiedLog:
	def __init__(self):
		self.log_type = None #local or remote
		self.client_id = None

		self.connection_id = None
		self.remote_ip   = None
		self.remote_dns  = None
		self.remote_port = None
		self.local_ip    = None
		self.local_port  = None
		self.connection_timestamp = None

		self.logentry = None
		self.proxydata = None
		self.credential = None
		self.poisonresult = None
		self.email = None
		self.connection_opened = None
		self.connection_closed = None
		self.traffic = None

	@staticmethod
	def construct(log_obj):
		ul = UnifiedLog()
		
		if isinstance(log_obj, RemoteLog):
			ul.log_type = 'REMOTE'
			ul.client_id = log_obj.client_id

			log_obj = log_obj.log_obj

			if isinstance(log_obj, LogEntry):
				ul.logentry = log_obj

			else:
				ul.connection_id = log_obj.connection.connection_id
				ul.remote_ip   = log_obj.connection.remote_ip
				ul.remote_dns  = log_obj.connection.remote_dns
				ul.remote_port = log_obj.connection.remote_port
				ul.local_ip    = log_obj.connection.local_ip
				ul.local_port  = log_obj.connection.local_port
				ul.connection_timestamp = log_obj.connection.connection_timestamp


		else:
			ul.log_type = 'LOCAL'
			ul.local_ip    = None
			ul.local_port  = None

		if ul.log_type = 'LOCAL' and isinstance(log_obj, LogEntry):
			ul.logentry = log_obj
			
		else:
			#logentry doesnt have connection info
			ul.connection_id = log_obj.connection.connection_id
			ul.remote_ip   = log_obj.connection.remote_ip
			ul.remote_dns  = log_obj.connection.remote_dns
			ul.remote_port = log_obj.connection.remote_port
			ul.connection_timestamp = log_obj.connection.connection_timestamp
		
		if isinstance(log_obj, ProxyData):
			ul.proxydata = log_obj

		elif isinstance(log_obj, Credential):
			ul.credential = log_obj

		elif isinstance(log_obj, PoisonResult):
			ul.poisonresult = log_obj

		elif isinstance(log_obj, EmailEntry):
			ul.email = log_obj

		elif isinstance(log_obj, ConnectionOpened):
			ul.connection_opened = log_obj

		elif isinstance(log_obj, ConnectionClosed):
			ul.connection_closed = log_obj

		elif isinstance(log_obj, TrafficLog):
			ul.traffic = log_obj
			
		return ul

	def to_dict(self):
		t = {}
		t['log_type'] = self.log_type
		t['client_id'] = self.client_id
		t['connection_id'] = self.connection_id
		t['remote_ip'] = self.remote_ip
		t['remote_dns'] = self.remote_dns
		t['remote_port'] = self.remote_port
		t['local_ip'] = self.local_ip
		t['local_port'] = self.local_port
		t['connection_timestamp'] = self.connection_timestamp
		t['logentry'] = self.logentry.to_dict() if self.logentry is not None else None
		t['proxydata'] = self.proxydata.to_dict() if self.proxydata is not None else None
		t['credential'] = self.credential.to_dict() if self.credential is not None else None
		t['poisonresult'] = self.poisonresult.to_dict() if self.poisonresult is not None else None
		t['email'] = self.email.to_dict() if self.email is not None else None
		t['connection_opened'] = self.connection_opened.to_dict() if self.connection_opened is not None else None
		t['connection_closed'] = self.connection_closed.to_dict() if self.connection_closed is not None else None
		t['traffic'] = self.traffic.to_dict() if self.traffic is not None else None

		return t


	def to_json(self):
		json.dumps(self.to_dict())


		
class logstashHandler(LoggerExtensionTask):
	def init(self):
		try:
			self.logstash_ip = '127.0.0.1'
			self.logstash_port = 9563
			self.retry_timeout = 10
		except Exception as e:
			traceback.print_exc()

	async def setup(self):
		pass

	async def main(self):
		while True:
			try:
				await self.logger.info('Connecting to LogStash')
				reader, writer = await asyncio.open_connection(self.logstash_ip, self.logstash_port)
				await self.logger.info('Connected to LogStash!')
				while not reader.at_eof():
					msg = await self.result_queue.get()
					ul = UnifiedLog.construct(msg)
					try:
						logline = ul.to_json().encode() + b'\r\n'
					except:
						await self.logger.exception()
					else:
						writer.write(logline)
						await writer.drain()


			except Exception as e:
				await self.logger.exception()

			await self.logger.info('Connection lost! Reconnecting in %ss' % self.retry_timeout)
			await asyncio.sleep(self.retry_timeout)

