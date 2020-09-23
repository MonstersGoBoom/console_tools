# console_tools
a collection of handy scripts for converting data to older consoles.

# we're assuming 4 colors per "chunk" 
gif2chr.py    : chops up an animated gif into blocks ( including animation ).

C64Encoder.py : for encoding C64 sprites as 3 seperate planes of color.

NESEncoder.py : for 8x8 NES sprites.

do.bat      : an example of using it.

# info 
  this splits the animated GIF into sub blocks for example 32x32.
  
  we then encode each of those sub blocks into console specific format.

  we start the sub block encode from the top most and left most occupied pixels vs the top corner of the sub block.
  
  for NES this is 8x8 tiles. we don't encode empty blocks, we also output metasprite information for lazynes(VBCC) / shiru spec meta sprites.

  for C64 this is 24x21 tiles. 
  




