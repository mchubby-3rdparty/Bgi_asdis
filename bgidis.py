#! /usr/bin/env python3

# BGI script file disassembler

import glob
import os
import struct
import sys
import base64

import bgiop

def get_code_end(data):
	pos = -1
	while 1:
		res = data.find(b'\x1B\x00\x00\x00', pos+1)
		if res == -1:
			break
		pos = res
	return pos + 4

def parse(code, hdr):
	bgiop.clear_offsets()
	inst = {}
	size = get_code_end(code)
	pos = 0
	while pos < size:
		addr = pos
		op, = struct.unpack('<I', code[addr:addr+4])
		if op not in bgiop.ops:
			raise Exception('size unknown for op %02x @ offset %05x' % (op, addr))
		pos += 4
		fmt, pfmt, fcn = bgiop.ops[op]
		if fmt:
			n = struct.calcsize(fmt)
			args = struct.unpack(fmt, code[pos:pos+n])
			if fcn:
				args = fcn(code, hdr, addr, *args)
			inst[addr] = pfmt % args
			pos += n
		else:
			inst[addr] = pfmt
	offsets = bgiop.offsets.copy()
	return inst, offsets
	
def out(fo, inst, offsets, hdr):
	fo.write('#HDR_BASE64\n%s#END_BASE64\n\n' % base64.encodebytes(hdr).decode('ascii'))
	for addr in sorted(inst):
		if addr in offsets:
			fo.write('L%05x:\n' % addr)
		fo.write('\t%s;\n' % inst[addr])
		
def dis(file):
	ofile = os.path.splitext(file)[0] + '.bsd'
	fi = open(file, 'rb')
	hdr_test = fi.read(0x20)
	if hdr_test.startswith(b'BurikoCompiledScriptVer1.00\x00'):
		hdrsize = 0x1C + struct.unpack('<I', hdr_test[0x1C:0x20])[0]
	else:
		hdrsize = 0
	fi.seek(0, 0)
	hdr = fi.read(hdrsize)
	code = fi.read()
	fi.close()
	inst, offsets = parse(code, hdr)
	fo = open(ofile, 'w', encoding='utf-8')
	out(fo, inst, offsets, hdr)
	fo.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage: bgidis.py <file(s)>')
		print('(only extension-less files amongst <file(s)> will be processed)')
		sys.exit(1)
	for arg in sys.argv[1:]:
		for script in glob.glob(arg):
			base, ext = os.path.splitext(script)
			if not ext:
				print('Disassembling %s...' % script)
				dis(script)
