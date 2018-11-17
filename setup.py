from setuptools import setup

setup(
	# Application name:
	name="Responder3 Log Extension for Logstash",

	# Version number (initial):
	version="0.0.1",

	# Application author details:
	author="Tamas Jos",
	author_email="responder3@skelsec.com",

	# Packages
	packages=["responder3_log_logstash"],

	# Include additional files into the package
	include_package_data=True,


	# Details
	url="https://github.com/skelsec/Responder3-log-logstash",

	zip_safe = True,
	#
	# license="LICENSE.txt",
	description="Responder3 Log Extension for Discord responder3",

	# long_description=open("README.txt").read(),

	#Dependent packages (distributions)
	install_requires=[
	],

	python_requires='>=3.7',
)
