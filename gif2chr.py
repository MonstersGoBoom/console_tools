from PIL import Image, ImageSequence, ImageDraw
import os
import array as arr 
import sys


##########################################################################################################################
# globals .. oh boy 
block_width = 32
block_height = 32
bytes_written = 0
output_header_file = 0
block_index = 0
sprite_index = 0

from NESEncoder import NESEncoder
from C64Encoder import C64SpriteEncoder

##########################################################################################################################
# encodes a block 
# where block is in pixel dimensions 
# eg 32x32 

def encodeblockchars(input,x,y,frame,basename):
	global sprite_index,block_width,block_height,output_header_file,bytes_written,block_index,Encoder
	(w, h) = input.size
	imagebw = w // Encoder.charwidth
	imagebh = h // Encoder.charheight
	# create local grids 
	blockgrid = [0] * (imagebw * imagebh)
	palette= [0] * (imagebw * imagebh )
	# find the top and left most pixel
	xstart = block_width
	ystart = block_height
	# scanning here
	for py in range(0,block_height):
		for px in range(0,block_width):
			pixel = input.getpixel((x+px,y+py))
			if (pixel&3)!=0:
				if px<xstart:
					xstart=px
				if py<ystart:
					ystart=py
	#
	# if we have a valid block 
	# then xstart and ystart are NOT block_width and block_height ( we found an edge ) 
	#

	if xstart!=block_width and ystart!=block_height:
		for py in range(0,block_height):
			# debug string
			p = ""
			for px in range(0,block_width):
				# grid position for this block
				gridpos = (px//Encoder.charwidth) +((py//Encoder.charheight)*imagebw)
				# check if this internal char ( inside the block ) is occupied 
				pix = x+px+xstart
				piy = y+py+ystart
				pixel = 0
				if px+xstart<block_width and py+ystart<block_height:
					pixel = input.getpixel((pix,piy))
				if (pixel&3)!=0:
					if pixel>=4:
						palette[gridpos]=pixel//4
					blockgrid[gridpos]=1
					p = p + "*"
				else:
					p = p + "."
			# show debug pixels
			print(p)

		# begin actual output
		# set up header info 
		normal = "static const ubyte "+basename+"_block_" + str(block_index) + "_" + str(frame) + "[] = {"
		flipped = "static const ubyte "+basename+"_block_" + str(block_index) + "_xf_" + str(frame) + "[] = {"

		block_index = block_index + 1
		for py in range(0,block_height,Encoder.charheight):
			s = ""
			for px in range(0,block_width,Encoder.charwidth):
				# grid position for this block
				gridpos = (px//Encoder.charwidth) +((py//Encoder.charheight)*imagebw)
				if blockgrid[gridpos]==1:
					# if this char is occupied with pixels then we can output it
					s = s + "*"
					normal = normal + "\t" +str(xstart-16 + px) + "," + str(-24+ystart+ py) + "," +str(sprite_index)+ "," + str(palette[gridpos]) + ","
					flipped = flipped + "\t" +str(block_width - (xstart-16 + px)) + "," + str(-24+ystart+ py) + "," +str(sprite_index)+ "," + str(0x40 | palette[gridpos]) + ","
					sprite_index=sprite_index+1
					bytes_written =bytes_written + Encoder.encodeblock(input,x+xstart+px,y+ystart+py,x+block_width)
				else:
					s = s + "."
			# show debug occupancy
			print(s)

		normal = normal + "\t128 };\n"
		flipped = flipped + "\t128 };\n"

		if Encoder.defineMeta==True:
			output_header_file.write(normal)
			output_header_file.write(flipped)

##########################################################################################################################
# for each frame , encode the blocks

def frame2tiles(input,basename,index):
	global sprite_index,block_width,block_height,output_header_file,bytes_written,block_index,Encoder

	(w, h) = input.size
	# if there's a file per frame 
	# create it here 
	if Encoder.fileperframe==True: 
		outname = basename + "_" + str(index) + Encoder.ext
		Encoder.output_rom_file = open(outname, "wb")

	# sprite index
	sprite_index = 0
	# block index
	block_index = 0
	# bytes written 
	bytes_written = 0
	# for height in steps of sprite block height
	for sy in range(0, h, block_height):
		# for width in steps of sprite block width
			for sx in range(0, w, block_width):
				encodeblockchars(input,sx,sy,index,basename)

	# pad the rom
	while(bytes_written<Encoder.padsize):
		pad = 0 
		Encoder.output_rom_file.write(pad.to_bytes(1,byteorder='big'))
		bytes_written=bytes_written+1

	# if file per frame 
	# close it here 
	if Encoder.fileperframe==True: 
		Encoder.output_rom_file.close()

##########################################################################################################################
# for each gif 
# encode 

def gif2nes(name,outname,bw,bh):
	global sprite_index,block_width,block_height,output_header_file,block_index,Encoder

	block_width = bw 
	block_height = bh
	sprite_index = 0
	newname = name + ".gif"
	# if we make a meta file 
	# create it here 
	if Encoder.defineMeta==True:
		outputname = name + ".h"
		output_header_file = open(outputname,"w")
		output_header_file.write("//" + newname + "\n")

	# if we're one file for the entire data set 
	# create that here 
	if Encoder.fileperframe==False: 
		outputname = name + Encoder.ext
		Encoder.output_rom_file = open(outputname, "wb")

	# now chop em
	im = Image.open(newname)
	index = 0
	for frame in ImageSequence.Iterator(im):
		frame2tiles(frame,outname,index)
		index += 1
	#
	# write the final meta details for the animations 
	#
	for b in range(0, block_index):
		s = "const ubyte *" + name + "_" + str(b) + "[] = {"
		for f in range(0, index):
			s = s + name + "_block_"+str(b)+"_"+str(f) 
			if f!=index-1:
				s=s+","
		s = s + "};\n"

		if Encoder.defineMeta==True:
			output_header_file.write(s)

		s = "const ubyte *" + name + "_xf_" + str(b) + "[] = {"
		for f in range(0, index):
			s = s + name + "_block_"+str(b)+"_xf_"+str(f) 
			if f!=index-1:
				s=s+","
		s = s + "};\n"

		if Encoder.defineMeta==True:
			output_header_file.write(s)

	if Encoder.defineMeta==True:
		output_header_file.close()
	if Encoder.fileperframe==False: 
		Encoder.output_rom_file.close()

##########################################################################################################################
# the usual 

def main():
	global Encoder
	#
	# we make a lot of assumptions here 
	# 
	script = sys.argv[0]
	basename = sys.argv[1]
	machine = sys.argv[2]
	width = sys.argv[3]
	height = sys.argv[4]

	if machine=="NES":
		Encoder=NESEncoder()
	if machine=="C64":
		Encoder=C64SpriteEncoder()

	gif2nes(basename,basename,int(width),int(height))

if __name__ == '__main__':
   main()