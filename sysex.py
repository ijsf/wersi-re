#!/usr/bin/env python
# 
# Copyright (c) 2015 Cecill Etheredge / ijsf (c@ijsf.nl)
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pypm
import array
import time
import getopt
import sys
from itertools import izip

def enum(**enums):
    return type('Enum', (), enums)

INPUT=0
OUTPUT=1

LO=1 << 4
HI=0 << 4

# Wersi block identifiers
BlockIdentifier = enum(
	ICB = ord('i'),				# Instrument Control Block
	VCF = ord('v'),				# VCF Parameter
	FREQ = ord('f'),			# FREQ Parameter
	AMPL = ord('a'),			# AMPL Parameter
	FIXWAVE = ord('q'),			# FIXWAVE Table
	RELWAVE = ord('w'),			# RELWAVE Table
)

# ==========================================================
# WERSI POINTERS
#
# 8-bit 76543210
# (MSB) CRPPPPPP (LSB)
#
# P		0-63: memory location
# R		0: location in ROM area
#		1: location in RAM area
# C		0: location on Wersi
#		1: location on cartridge
#
# Both the Wersi and its x`cartridges have ROM/RAM areas.
#
# ==========================================================
# [ICB]			Instrument Control Block
#
# Block size	16
# Block address	(Wersi pointer) + 1
#				0 == NULL
# ----------------------------------------------------------
# [VCF]			VCF parameters: envelope, Q, frequency
#
# Block size	10
# Block address	(Wersi pointer)
# ----------------------------------------------------------
# [FREQ]		Frequency envelope parameter block
#
# Block size	32
# Block address	(Wersi pointer)
# ----------------------------------------------------------
# [AMPL]		Amplitude envelope parameter block
#
# Block size	44
# Block address	(Wersi pointer)
# ----------------------------------------------------------
# [FIXWAVE]		Wavetable for fixed formant voice
#
# Block size	212
# Block address	(Wersi pointer)
# ----------------------------------------------------------
# [RELWAVE]		Wavetable for relative formant voice
#
# Block size	178
# Block address	(Wersi pointer)

def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)

def ConvertFromNibbles( nibbleArray ):
	byteArray = []
	for a, b in pairwise( nibbleArray ):
		c = 0
		if int( a ) & LO > 0 and int( b ) & LO == 0:
			c |= ( ( int( b ) & 0x0F ) << 4 ) | ( int( a ) & 0x0F )
		elif int( b ) & LO > 0 and int( a ) & LO == 0:
			c |= ( ( int( a ) & 0x0F ) << 4 ) | ( int( b ) & 0x0F )
		else:
			print "Invalid format!"
		byteArray.append( c )
	return byteArray
	
def PrintDevices():
	print "-------------------"
	print "Devices:"
	print "-------------------"
	for loop in range(pypm.CountDevices()):
		interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
		print loop, name," ",
		if (inp == 1): print "(input) ",
		else: print "(output) ",
		if (opened == 1): print "(opened)"
		else: print "(unopened)"

def SysexMessage( blockId, blockAddr, blockSize, data ):
	# Split into low/high nibbles
	blockIdLo		= int( blockId ) & 0x0F
	blockIdHi		= int( blockId ) >> 4
	blockAddrLo		= int( blockAddr ) & 0x0F
	blockAddrHi		= int( blockAddr ) >> 4
	blockSizeLo		= int( blockSize ) & 0x0F
	blockSizeHi		= int( blockSize ) >> 4
	
	buffer = []
	
	# Begin SysEx
	buffer.append( 0xF0 )
	
	# Append header
	buffer.append( 0x25 )							# Wersi header
	buffer.append( 0x01 )							# MK1 header
	buffer.append( 0x60 | LO | blockIdLo )			# Block identification
	buffer.append( 0x60 | HI | blockIdHi )
	buffer.append( 0x40 | LO | blockAddrLo )		# Block address
	buffer.append( 0x40 | HI | blockAddrHi )
	buffer.append( 0x20 | LO | blockSizeLo )		# Block size
	buffer.append( 0x20 | HI | blockSizeHi )
	
	# Append data
	for d in data:
		buffer.append( LO | (int( d ) & 0x0F) )
		buffer.append( HI | (int( d ) >> 4) )

	# End SysEx
	buffer.append( 0xF7 )

	return buffer
	
def SysexTest( deviceInput, deviceOutput, queryBlockAddress, latency ):
	#midiInput = None
	midiInput = pypm.Input( int( deviceInput ), 1024 )
	midiOutput = pypm.Output( int( deviceOutput ), latency )
	
	##################################################
	# Cycle through buttons
#	for i in range(1,100):
#		msg = SysexMessage( ord('s'), 0, 1, [ i % 4 ] )
#		midiOutput.WriteSysEx( 0, str( bytearray( msg ) ) )
#		time.sleep(0.01)
	#'''

	##################################################
	# Set ICB
	#msg = SysexMessage( ord('i'), 67, 16, [ 0x00, 0x00, 0x41, 0x41, 0x41, 0x00, 0x08, 0x00, 0x00, 0xC4, 0x48, 0x55, 0x4D, 0x41, 0x4E, 0x4D ] )
	#midiOutput.WriteSysEx( 0, str( bytearray( msg ) ) )
	
	##################################################
	# Get ICB
	msg = SysexMessage( ord('r'), queryBlockAddress, 1, [ ord('i') ] )
	
	# Switch control key to B
	#msg = SysexMessage( ord('s'), 0, 1, [ 1 ] )

	# Get Instrument Control Block at address 66
	#msg = SysexMessage( ord('r'), 66, 1, [ ord('i') ] )
	
	# Get VCF parameters
	#msg = SysexMessage( ord('r'), queryBlockAddress, 1, [ ord('v') ] )
	
	# Get Amplitude envelope at address 65
	#msg = SysexMessage( ord('r'), 65, 1, [ BlockIdentifier.AMPL ] )
	
	# Get fixed wavetable
	#msg = SysexMessage( ord('r'), queryBlockAddress, 1, [ BlockIdentifier.FIXWAVE ] )
	
	# Get relative wavetable
	#msg = SysexMessage( ord('r'), queryBlockAddress, 1, [ BlockIdentifier.RELWAVE ] )
	
	# Change VCF parameters at address 64
	#msg = SysexMessage( ord('v'), 64, 10, [ 3, 0, 11, 149, 232, 232, 0, 49, 0, 49 ] )
	
	# Change Amplitude envelope at address 65
	'''
	msg = SysexMessage( ord('a'), 65, 44, [ 0x20, 0xb1, 0x0a, 0x20, 0x00, 0x00, 0xef, 0x00, 0x00, 0xc1, 0x00, 0x00, 0x85, 0x00, 0x00, 0xa2, 0x00, 0x00, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x08, 0x20, 0x20, 0xdf, 0x4b, 0x20, 0x07, 0xb1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ] )
	# '''
	
	# Test
	#msg = SysexMessage( ord('f'), 65, 32, [ 0x11 ] * 32 )
	
	# Change Frequency envelope at address 65
	#msg = SysexMessage( BlockIdentifier.FREQ, 65, 16, [ 0x02,0xFF,  0xA0,0x00,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0,  0,0 ] )
	##################################################
	
	# Print output message
	print 'Out:'
	print ' '.join('0x%02X    ' % b for b in msg)
	#print ' '.join((bin(b)[2:]).zfill(8) for b in msg)
	
	# Write message to MIDI
	midiOutput.WriteSysEx( 0, str( bytearray( msg ) ) )
	
	# Poll for MIDI input
	readTimeout = 0.5
	if midiInput:
		readTimeStart = time.time()
		readReady = True
		msg = []
		while readReady:
			if not midiInput.Poll():
				# Check timeout
				if (time.time() - readTimeStart) > readTimeout:
					# Timeout exceeded, abort reading
					readReady = False
			else:
				# Read data
				MidiData = midiInput.Read(1024)
				# Append data to buffer
				for m in MidiData:
					for n in m[0]:
						msg.append( n )
		if msg:
			# Parse SysEx header
			headerSize = 9
			if msg[0] == 0xF0 and msg[1] == 0x25 and msg[2] == 0x01 and len( msg ) > headerSize:
				# Wersi MK1 SysEx message
				#
				# 11110000: MIDI SysEx identifier
				# 00100101: Wersi identifier
				# 00000001: MK1 identifier
				# 011NXXXX: Block identifier (hi/lo)
				# 010NXXXX: Block address (hi/lo)
				# 001NXXXX: Block length (hi/lo)
				# 000NXXXX: Data (hi/lo)
				blockIdentifier = ConvertFromNibbles( [ msg[3], msg[4] ] )[0]
				blockAddress = ConvertFromNibbles( [ msg[5], msg[6] ] )[0]
				blockLength = ConvertFromNibbles( [ msg[7], msg[8] ] )[0]
				data = msg[9:]
				# Always one byte missing :(
				# Probably due to a crappy MIDI SysEx ROM implementation in the Wersi.
				if (len( data ) / 2) >= ( blockLength - 1 ):
					print "* Received Wersi MK1 SysEx message, length %u" % len(msg)
					print "Block identifier: %s (%u)" % ( chr( blockIdentifier ), blockIdentifier )
					print "Block address: %u (0x%02X)" % ( blockAddress, blockAddress )
					print "Block length: %u bytes" % ( blockLength )
					print "Data (got %u bytes):" % ( len( data ) / 2 )
					print ' '.join('0x%02X    ' % b for b in ConvertFromNibbles( data ))
					print ' '.join('(%s)     ' % (chr( b ) if b >= 32 else '?') for b in ConvertFromNibbles( data ))
					print ' '.join('%08u' % b for b in ConvertFromNibbles( data ))
					print ' '.join((bin(b)[2:]).zfill(8) for b in ConvertFromNibbles( data ))
				else:
					print "Received message was too short (got %u, expected %u). Try again." % ( (len( data ) / 2), blockLength - 1 )
		del midiInput
	
	# Cleanup
	del midiOutput

def usage():
	print "-i --input         DEVICE"
	print "-o --output        DEVICE"
	print "-b --blockAddress  ADDRESS"
	PrintDevices()

def main( argv ):
	pypm.Initialize()
	deviceInput = None
	deviceOutput = None
	blockAddress = None
	latency = 0
	try:
		opts, args = getopt.getopt( argv, "i:o:b:", [ "input=", "output=", "blockAddress=" ] )
		for opt, arg in opts:
			if opt in ( "-i", "--input" ):
				deviceInput = arg
			elif opt in ( "-o", "--output" ):
				deviceOutput = arg
			elif opt in ( "-b", "--blockAddress" ):
				blockAddress = arg
		if deviceInput == None or deviceOutput == None or blockAddress == None:
			usage()
			sys.exit( 2 )
	except getopt.GetoptError:
		usage()
		sys.exit( 2 )

	SysexTest( deviceInput, deviceOutput, blockAddress, latency )

	pypm.Terminate()

if __name__ == "__main__":
    main(sys.argv[1:])