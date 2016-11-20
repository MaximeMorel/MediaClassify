#!/usr/bin/env python2

# Classify picture and video script, by reading date metadata and move files to folders like 2015/2015_03
# Maxime Morel - maxime@mmorel.eu
# 2016/11/17

# Needs python2

# mode:
# 0 - year/
# 1 - year/year_month/
# 2 - year/year_month_day/

import os
import sys
import datetime
import shutil
from gi.repository import GExiv2
import pyexiv2
from os.path import join, normpath

class Classifier:
	def __init__(self):
		self.source = 'source'
		self.destination = 'destination'
		self.mode = 1

	def setParams(self, argv):
		if len(argv) >= 2:
			self.source = argv[1]
		if len(argv) >= 3:
			self.destination = argv[2]
		if len(argv) >= 4:
			self.mode = int(argv[3])

	def getMetaData(self, filename):
		#print(filename)
		try:
			#metadata = GExiv2.Metadata(filename)
			#print(metadata)
			metadata = pyexiv2.ImageMetadata(filename)
			metadata.read()
			#print(metadata.exif_keys)
			tag = metadata['Exif.Image.DateTime']
			#print(tag.raw_value)
			return tag.value
			#tag = metadata['Exif.Photo.DateTimeOriginal']
			#print(tag)
		except:
			pass
		return datetime.datetime(1, 1, 1, 0, 0, 0)

	def mkDestDir(self, date):
		dest = join(self.destination, str(date.year))
		if self.mode >= 1:
			dest = join(dest, str(date.year) + '_' + str(date.month))
		if self.mode >= 2:
			dest += '_' + str(date.day)
		try:
			os.makedirs(dest)
			print('mkdir: ' + dest)
		except:
			pass
		return dest

	def run(self):
		print('Working directory: ' + os.getcwd())
		print('Source: ' + self.source)
		print('Destination: ' + self.destination)

		print('Proceed? ')
		#res = input()
		res = raw_input()
		if res != 'y':
			sys.exit()

		if not os.path.isdir(self.destination):
			os.mkdir(self.destination)

		for root, dirs, files in os.walk(self.source):
			for file in files:
				basefile, extension = os.path.splitext(file)
				extension = extension.lower()
				srcfile = join(root, file)
				#if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2']:
				if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2', '.thm', '.mov', '.mp4', '.wmv', '.mod', '.mpg', '.avi', '.mts', '.mkv', ]:
					t = self.getMetaData(srcfile)
					if t.year != 1:
						dest = self.mkDestDir(t)
						print('copy: ' + srcfile + ' -> ' + join(dest, file))
						shutil.copy2(srcfile, dest)
					else:
						print('fail: ' + srcfile + ' -> ' + join(dest, file))
				else:
					print('unknown: ' + srcfile)
				sys.stdout.flush()

if __name__ == '__main__':
	print('Picture and video classification script')
	classifier = Classifier()
	classifier.setParams(sys.argv)
	classifier.run()

