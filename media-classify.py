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

# 2016/11/28
# Check if media is correclty classified
# Needs exiftool (perl-image-exiftool)

import os
import sys
import string
import datetime
import shutil
import subprocess
#from gi.repository import GExiv2
import pyexiv2
from os.path import join, normpath

class Classifier:
	def __init__(self):
		self.source = 'source'
		self.destination = 'destination'
		self.mode = 1
		self.checker = False
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
		if len(argv) == 2:
			self.checker = True

		if self.checker:
			self.destination = ''

	def getMetaDataDate(self, filename):
		res = self.getMetaDataDatePyExiv2(filename)
		if isinstance(res, datetime.datetime) and res.year != 1:
			return res
		return self.getMetaDataDateExiftool(filename)

	def getMetaDataDateExiftool(self, filename):
		try:
			res = subprocess.check_output(["exiftool", "-CreateDate", "-DateTimeOriginal", filename])
			pos = string.find(res, ': ')
			if pos >= 0:
				d = datetime.datetime.strptime(res[pos+2:pos+21], '%Y:%m:%d %H:%M:%S')
				return d
		except BaseException as err:
			print('except: ' + str(err) + ' -> ' + filename)
			pass
		return datetime.datetime(1, 1, 1, 0, 0, 0)

	def getMetaDataDatePyExiv2(self, filename):
		try:
			metadata = pyexiv2.ImageMetadata(filename)
			metadata.read()
			#print(metadata.exif_keys)
			keys = ['Exif.Image.DateTime', 'Exif.Image.DateTimeOriginal', 'Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized']
			for key in keys:
				if key in metadata:
					tag = metadata[key]
					#print(tag.raw_value)
					return tag.value
		except:
			pass
		return datetime.datetime(1, 1, 1, 0, 0, 0)

	def processFile(self, dir, file, t):
		if self.checker:
			self.processFileCheck(dir, file, t)
		else:
			self.processFileCopy(dir, file, t)

	def processFileCopy(self, dir, file, t):
		srcfile = join(dir, file)
		if isinstance(t, datetime.datetime) and t.year != 1:
			dest = self.genDestDirName(t)
			self.copy(srcfile, dest, file)
			print('copy: ' + srcfile + ' -> ' + join(dest, file))
			self.numClassifed += 1
		else:
			faildest = join(self.destination, 'fail', dir[len(self.source):])
			self.copy(srcfile, faildest, file)
			print('fail: ' + srcfile + ' -> ' + join(faildest, file))
			self.numFailed += 1

	def processFileCheck(self, dir, file, t):
		srcfile = join(dir, file)
		if isinstance(t, datetime.datetime) and t.year != 1:
			dest = self.genDestDirName(t)
			if string.find(dir, dest) >= 0:
				print('check ok: ' + srcfile + ' -> ' + dest)
				self.numClassifed += 1
			else:
				print('check fail: ' + srcfile + ' -> ' + dest)
				self.numFailed += 1
		else:
			print('no check (no metadata): ' + srcfile)

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
		if not self.checker:
			print('Destination: ' + self.destination)

		print('Proceed? ')
		#res = input()
		res = raw_input()
		if res != 'y':
			sys.exit()

		for root, dirs, files in os.walk(self.source):
			for file in files:
				basefile, extension = os.path.splitext(file)
				extension = extension.lower()
				srcfile = join(root, file)
				if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2', '.thm', '.mov', '.mp4', '.wmv', '.mod', '.mpg', '.avi', '.mts', '.mkv', ]:
					t = self.getMetaDataDate(srcfile)
					self.processFile(root, file, t)
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

