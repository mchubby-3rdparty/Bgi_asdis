#! /usr/bin/env python3

# BGI script file assembler

import glob
import os
import struct
import sys
import base64

import asdis
import bgiop

def parse_instr(line, n):
	strings = set([])
	fcn, argstr = asdis.re_instr.match(line).groups()
	argstr = argstr.strip()
	if argstr:
		argstr = argstr.replace('\\"', asdis.quote_replace)
		quotes = asdis.get_quotes(argstr, n)
		if len(quotes) % 2 != 0:
			raise asdis.QuoteMismatch('Mismatched quotes @ line %d' % n)
		argstr = asdis.replace_quote_commas(argstr, quotes)
		args = [x.strip().replace(asdis.comma_replace, ',').replace(asdis.quote_replace, '"') for x in argstr.split(',')]
		for arg in args:
			if arg and arg[0] == '"' and arg[-1] == '"':
				strings.add(arg)
	else:
		args = []
	return fcn, args, strings
	
def fcn2op(fcn, n):
	for op in bgiop.ops:
		if bgiop.ops[op][1].startswith(fcn):
			return op
	raise asdis.InvalidFunction('Invalid function @ line %d' % n)

def parse(asmtxt):
	instrs = []
	symbols = {}
	text_set = set()
	in_hdr = False
	hdr_lines = []
	pos = 0
	for id, line in enumerate(asmtxt.split('\n')):
		line = line.strip()
		line = asdis.remove_comment(line)
		if not line:
			continue
		if line == '#HDR_BASE64':
			in_hdr = True
		elif line == '#END_BASE64':
			in_hdr = False
			hdr64 = '\n'.join(hdr_lines)
		elif in_hdr:
			hdr_lines.append(line)
		elif asdis.re_label.match(line):
			symbol, = asdis.re_label.match(line).groups()
			symbols[symbol] = pos
		elif asdis.re_instr.match(line):
			fcn, args, strings = parse_instr(line, id+1)	
			record = fcn, args, pos, id+1
			text_set.update(strings)
			instrs.append(record)
			pos += 4*len(args) + 4
		else:
			raise asdis.InvalidInstructionFormat('Invalid instruction format @ line %d' % (id+1))
	texts = []
	for text in text_set:
		symbols[text] = pos
		text = asdis.unescape(text[1:-1])
		texts.append(text)
		pos += len(text.encode('cp932')) + 1
	return instrs, symbols, texts, hdr64
	
def out(fo, instrs, symbols, texts, hdr64):
	hdr = base64.decodebytes(hdr64.encode('ascii'))
	fo.write(hdr)
	for fcn, args, pos, n in instrs:
		op = fcn2op(fcn, n)
		fo.write(struct.pack('<I', op))
		for arg in args:
			if arg in symbols:
				fo.write(struct.pack('<I', symbols[arg]))
			elif arg.startswith('0x') or arg.startswith('-0x'):
				fo.write(struct.pack('<i', int(arg, 16)))
			elif arg:
				fo.write(struct.pack('<i', int(arg)))
	for text in texts:
		fo.write(text.encode('cp932') + b'\x00')

def asm(file):
	ofile = os.path.splitext(file)[0]
	asmtxt = open(file, 'r', encoding='utf-8').read()
	instrs, symbols, texts, hdr64 = parse(asmtxt)
	out(open(ofile, 'wb'), instrs, symbols, texts, hdr64)
	
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage: bgias.py <file(s)>')
		print('(only .bsd files amongst <file(s)> will be processed)')
		sys.exit(1)
	for arg in sys.argv[1:]:
		for script in glob.glob(arg):
			base, ext = os.path.splitext(script)
			if ext == '.bsd':
				print('Assembling %s...' % script)
				asm(script)
