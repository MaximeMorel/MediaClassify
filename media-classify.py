#!/usr/bin/env python2

# Classify picture and video script, by reading date metadata and move files to folders like 2015/2015_03
# Maxime Morel - maxime@mmorel.eu
# 2016/11/17

# Needs python2

# mode:
# 0 - year/
# 1 - year/year_month/
# 2 - year/year_month_day/

# Changelog
# 2016/11/23
# Show some stats at the end of execution
# Do not overwrite existing files in destination folder, but append a number to the file
# Copy failed files (metadata could not be found) to destination under fail folder

import os
import sys
import string
import datetime
import shutil
#from gi.repository import GExiv2
import pyexiv2
from os.path import join, normpath

class Classifier:
	def __init__(self):
		self.source = 'source'
		self.destination = 'destination'
		self.mode = 1
		self.numClassifed = 0
		self.numFailed = 0
		self.numIgnored = 0

	def setParams(self, argv):
		if len(argv) >= 2:
			self.source = argv[1]
		if len(argv) >= 3:
			self.destination = argv[2]
		if len(argv) >= 4:
			self.mode = int(argv[3])

	def getMetaData(self, filename):
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

	def genDestDirName(self, date):
		dest = join(self.destination, str(date.year))
		if self.mode >= 1:
			dest = join(dest, str(date.year) + '_' + str(date.month).zfill(2))
		if self.mode >= 2:
			dest += '_' + str(date.day).zfill(2)
		return dest

	def copy(self, src, dstdir, dstfile):
		try:
			os.makedirs(dstdir)
			print('mkdir: ' + dstdir)
		except:
			pass
		dest = join(dstdir, dstfile)
		dst = dest
		pos = string.rfind(dest, '.')
		i = 0
		if pos < 0:
			print('bad src: ' + src)
		else:
			while os.path.isfile(dest):
				# destination already exists, generate new name
				i += 1
				dest = dst[:pos] + '_' + str(i) + dst[pos:]
			shutil.copy2(src, dest)
			if i > 0:
				print('  renamed: ' + dest)

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
				if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2', '.thm', '.mov', '.mp4', '.wmv', '.mod', '.mpg', '.avi', '.mts', '.mkv', ]:
					t = self.getMetaData(srcfile)
					if isinstance(t, datetime.datetime) and t.year != 1:
						dest = self.genDestDirName(t)
						self.copy(srcfile, dest, file)
						print('copy: ' + srcfile + ' -> ' + join(dest, file))
						self.numClassifed += 1
					else:
						faildest = join(self.destination, 'fail', root[len(self.source):])
						self.copy(srcfile, faildest, file)
						print('fail: ' + srcfile + ' -> ' + join(faildest, file))
						self.numFailed += 1
				else:
					print('unknown: ' + srcfile)
					self.numIgnored += 1
				sys.stdout.flush()

	def showStats(self):
		print('Num classified: ' + str(self.numClassifed))
		print('Num failed: ' + str(self.numFailed))
		print('Num ignored: ' + str(self.numIgnored))

if __name__ == '__main__':
	print('Picture and video classification script')
	classifier = Classifier()
	classifier.setParams(sys.argv)
	classifier.run()
	classifier.showStats()

