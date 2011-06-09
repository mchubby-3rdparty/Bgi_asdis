# BGI ._bp file opcode table

import asdis

offsets = set()

def clear_offsets():
	offsets.clear()

def get_string(code, addr, *args):
	pos0 = addr + args[0]
	pos1 = code.find(b'\x00', pos0)
	string = code[pos0:pos1].decode('cp932')
	string = asdis.escape(string)
	return string
	
def get_offset(code, addr, *args):
	offset = addr + args[0]
	offsets.add(offset)
	return offset

ops = {
0x00: ('b', 'push_byte(%#x)', None),
0x01: ('<h', 'push_word(%#x)', None),
0x02: ('<i', 'push_dword(%#x)', None),

0x04: ('<h', 'cmd_04(%#x)', None),
0x05: ('<h', 'push_string("%s")', get_string),
0x06: ('<h', 'push_offset(L%05x)', get_offset),

0x08: ('b', 'cmd_08(%#x)', None),
0x09: ('b', 'cmd_09(%#x)', None),
0x0A: ('b', 'cmd_0a(%#x)', None),
0x0B: ('<bi', 'cmd_0b(%#x, %#x)', None),
0x0C: ('bb', 'cmd_0c(%#x, %#x)', None),

0x10: ('', 'cmd_10()', None),
0x11: ('', 'cmd_11()', None),

0x14: ('', 'jmp()', None),
0x15: ('b', 'je(%#x)', None),
#0x16: ('<I', 'call(L%05X)', None),
0x16: ('', 'call()', None),
0x17: ('', 'ret()', None),

0x20: ('', 'add()', None),
0x21: ('', 'sub()', None),
0x22: ('', 'mul()', None),
0x23: ('', 'div()', None),
0x24: ('', 'mod()', None),
0x25: ('', 'and()', None),
0x26: ('', 'or()', None),
0x27: ('', 'xor()', None),
0x28: ('', 'not()', None),
0x29: ('', 'shl()', None),
0x2A: ('', 'shr()', None),
0x2B: ('', 'sar()', None),

0x30: ('', 'eq()', None),
0x31: ('', 'neq()', None),
0x32: ('', 'leq()', None),
0x33: ('', 'geq()', None),
0x34: ('', 'lt()', None),
0x35: ('', 'gt()', None),

0x38: ('', 'cmd_38()', None),
0x39: ('', 'cmd_39()', None),
0x3A: ('', 'cmd_3a()', None),

0x40: ('', 'cmd_40()', None),

0x42: ('', 'cmd_42()', None),
0x43: ('', 'cmd_43()', None),

0x48: ('', 'cmd_48()', None),
0x49: ('', 'cmd_49()', None),

0x60: ('', 'cmd_60()', None),
0x61: ('', 'cmd_61()', None),
0x62: ('', 'cmd_62()', None),
0x63: ('', 'cmd_63()', None),

0x66: ('', 'cmd_66()', None),
0x67: ('', 'cmd_67()', None),
0x68: ('', 'cmd_68()', None),
0x69: ('', 'cmd_69()', None),
0x6A: ('', 'cmd_6a()', None),
0x6B: ('', 'cmd_6b()', None),
0x6C: ('', 'cmd_6c()', None),
0x6D: ('', 'cmd_6d()', None),
0x6E: ('', 'cmd_6e()', None),
0x6F: ('', 'cmd_6f()', None),
0x70: ('', 'cmd_70()', None),
0x71: ('', 'cmd_71()', None),

0x77: ('', 'cmd_77()', None),
0x78: ('', 'cmd_78()', None),
0x79: ('', 'cmd_79()', None),
0x7A: ('', 'cmd_7a()', None),
0x7B: ('', 'cmd_7b()', None),

0x7D: ('', 'cmd_7d()', None),

0x7F: ('', 'cmd_7f()', None),
0x80: ('B', 'cmd_80(%#02x)', None),
0x81: ('B', 'cmd_81(%#02x)', None),

0x90: ('B', 'cmd_90(%#02x)', None),
0x91: ('B', 'cmd_91(%#02x)', None),
0x92: ('B', 'cmd_92(%#02x)', None),

0xA0: ('B', 'cmd_a0(%#02x)', None),

0xB0: ('B', 'cmd_b0(%#02x)', None),

0xC0: ('B', 'cmd_c0(%#02x)', None),

}
