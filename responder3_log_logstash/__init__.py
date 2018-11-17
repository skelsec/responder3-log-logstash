# Work with Python 3.7
import asyncio
import traceback

from responder3.core.logging.logtask import LoggerExtensionTask
from responder3.core.logging.logger import Logger, r3exception

		
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
				reader, writer = await asyncio.open_connection(self.logstash_ip, self.logstash_port)
				while not reader.at_eof():
					msg = await self.result_queue.get()
					writer.write(msg.to_json())
					await wrtier.drain()

			except Exception as e:
				await self.logger.exception()

			await asyncio.sleep(self.retry_timeout)

