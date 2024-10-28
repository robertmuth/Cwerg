# deprecated
STR = r'"(?:[^"\\]|[\\].)*(?:"|$)'
R_STR = r'r"(?:[^"])*(?:"|$)'

START = r'x?"(?:[^"\\]|[\\].)*'
R_START = r'r"(?:[^"])*'
END = '(?:"|$)'   # Note, this also covers the unterminated case
#

# These cover just the first line
MULTI_START = r'"""(?:["]{0,2}(?:[^"\\]|[\\].))*(?:["]{3,5}|$)'
MULTI_START_R = r'r"""(?:["]{0,2}[^"])*(?:["]{3,5}|$)'
MULTI_START_X = r'x"""[a-fA-F0-9\s]*(?:"""|$)'


MULTI_END = r'^(?:["]{0,2}(?:[^"\\]|[\\].))*(?:["]{3,5})'
MULTI_END_R = r'^(?:["]{0,2}[^"])*(?:["]{3,5})'
MULTI_END_X = r'^[a-fA-F0-9\s]*(?:""")'