

##########################################################################################################################
# NES 8x8 sprites 
# saves a header file for meta data 
class NESEncoder():
	def __init__(self):
		self.charwidth = 8
		self.charheight = 8
		self.padsize = 4096
		self.defineMeta = True
		self.fileperframe = True
		self.ext = ".chr"

	def encodeblock(self,input,px,py,ex):
		bitset0=[]
		bitset1=[]
		(w, h) = input.size

		# for each pixel Y
		for iy in range(0,8):
			# reset the byte
			bitsa = 0
			bitsb = 0
			# for each pixel X
			for ix in range(0,8):
				# flip the index 
				fx = 7-ix
				# get the color ( we assume 4 color gif )
				pixel = 0 
				if px+ix<w and py+iy<h and px+ix<ex: 
					pixel = input.getpixel((px+ix,py+iy))
				if pixel>=4:
					palette=pixel//4
				pixel=pixel&3
				# set the bits 
				if pixel&1==1:
					bitsa|=1<<fx
				if pixel&2==2:
					bitsb|=1<<fx
			# store the bytes per Y 
			bitset0.append(bitsa)
			bitset1.append(bitsb)
			# save the set out as bytes
				# nes stores bitplanes 8 bytes per plane * 2
		for iy in range(0,8):
			self.output_rom_file.write(bitset0[iy].to_bytes(1,byteorder='big'))
		for iy in range(0,8):
			self.output_rom_file.write(bitset1[iy].to_bytes(1,byteorder='big'))
		return 16
		