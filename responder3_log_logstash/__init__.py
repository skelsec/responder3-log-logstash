# Work with Python 3.7
import asyncio
import traceback

from responder3.core.logging.logtask import LoggerExtensionTask
from responder3.core.logging.logger import Logger, r3exception
from responder3.core.logging.log_objects import *
from responder3.core.commons import UniversalEncoder

		
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
					if isinstance(msg, RemoteLog):
						data = msg.to_dict()
						data['logsource'] = 'REMOTE'
						data['log_obj']['logtype'] = logobj2type_inv[type(msg)].name
					else:
						data = msg.to_dict()
						data['logsource'] = 'LOCAL'
						data['logtype'] = logobj2type_inv[type(msg)].name
					writer.write(json.dumps(data, cls=UniversalEncoder).encode() + b'\r\n')
					await writer.drain()

			except Exception as e:
				await self.logger.exception()

			await self.logger.info('Connection lost! Reconnecting in %ss' % self.retry_timeout)
			await asyncio.sleep(self.retry_timeout)

