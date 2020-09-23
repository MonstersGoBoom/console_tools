##########################################################################################################################
# C64 sprite export 
# as 3 planes 24x21 pixels 

class C64SpriteEncoder():
	def __init__(self):
		self.charwidth = 24
		self.charheight = 21
		self.padsize = 2048
		self.defineMeta = False
		self.fileperframe = False
		self.ext = ".c64"
	
	def encodeblock(self,input,px,py,ex):
		bitsets=[0] * 3
		bitsets[0]=[0] * 64
		bitsets[1]=[0] * 64
		bitsets[2]=[0] * 64
		
		(w, h) = input.size
		# for each pixel Y
		for iy in range(0,self.charheight):
			# reset the byte
			bitsa = 0
			bitsb = 0
			# for each pixel X
			for ix in range(0,self.charwidth):
				tx = (ix // 8) + (iy*3) 
				fx = 7-(ix&7)

				# flip the index 
				# get the color ( we assume 4 color gif )
				pixel = 0 
				if px+ix<w and py+iy<h and px+ix<ex: 
					pixel = input.getpixel((px+ix,py+iy))
				pixel=pixel&3
				if pixel!=0:
					bitsets[pixel-1][tx]|=1<<fx

		# set fake colors and attributes 
		# for sprpad 0x10 means the next sprite is overlayed 
		# pink
		bitsets[0][63]=0x1a
		# red
		bitsets[1][63]=0x12
		# white
		bitsets[2][63]=1
		# write all 3 blocks
		for iy in range(0,64):
			self.output_rom_file.write(bitsets[0][iy].to_bytes(1,byteorder='big'))
		for iy in range(0,64):
			self.output_rom_file.write(bitsets[1][iy].to_bytes(1,byteorder='big'))
		for iy in range(0,64):
			self.output_rom_file.write(bitsets[2][iy].to_bytes(1,byteorder='big'))

		return (64*3)
