import codecs
import re
import struct

from typing import List, Optional, BinaryIO


def read_leb128(r: BinaryIO, signed: bool = False) -> int:
    """
    cf. http://en.wikipedia.org/wiki/LEB128
    """
    out = 0
    shift = 0
    while True:
        b = ord(r.read(1))
        out |= (b & 0x7f) << shift
        shift += 7
        if (b & 0x80) == 0:
            if signed and b & 0x40:
                out -= (1 << shift)
            return out


def write_leb128(x: int, signed: bool = False) -> List[int]:
    out: List[int] = []
    if signed:
        while True:
            b = x & 0x7f
            x = x >> 7
            if (x == 0 and b & 0x40 == 0) or (x == -1 and b & 0x40 != 0):
                out.append(b)
                return out
            out.append(0x80 | b)
    else:
        while True:
            b = x & 0x7f
            x = x >> 7
            if x == 0:
                out.append(b)
                return out
            out.append(0x80 | b)


def EscapedStringToBytes(s) -> bytes:
    out = bytearray()
    escape = None
    prev = ""
    n = 0
    while n < len(s):
        char = s[n]
        n += 1
        if char != "\\":
            out.extend(char.encode('utf8'))
            continue
        char = s[n]
        n += 1
        if char == "n":
            out.append(ord("\n"))
        elif char == "x":
            start = n
            end = n + 2
            assert end <= len(s)
            out.append(int(s[start:end], 16))
            n = end
        elif "0" <= char <= "7":
            start = n - 1
            end = n
            if end < len(s) and "0" <= s[end] <= "7":
                end += 1
                if end < len(s) and "0" <= s[end] <= "7":
                    end += 1
            out.append(int(s[start:end], 8))
            n = end
        else:
            out.append(ord(char))

    return bytes(out)


def _MapEscape(char) -> int:
    if char == "n":
        return ord("\n")
    elif char == "r":
        return ord("\r")
    elif char == "t":
        return ord("\t")
    elif char == "b":
        return ord("\b")
    elif char == "f":
        return ord("\f")
    else:
        return ord(char)


def ParseChar(s) -> Optional[int]:
    if len(s) <= 2 or s[0] != "'" or s[-1] != "'":
        return None
    if s[1] != "\\":
        if len(s) != 3:
            return None
        return ord(s[1])
    if len(s) <= 2:
        return None
    char = s[2]
    if char == "x":
        if len(s) != 6:
            return None
        return int(s[3:5], 16)
    if len(s) != 4:
        return None
    return _MapEscape(char)


def HexStringToBytes(s) -> bytes:
    out = bytearray()
    last = None
    for c in s:
        if c in " \n\t":
            pass
        elif last is None:
            last = c
        else:
            last += c
            out.append(int(last, 16))
            last = None
    assert last is None
    return bytes(out)


def QuotedEscapedStringToBytes(s: str) -> bytes:
    r"""Note: this does NOT support many c-escape sequences.

    Supported are: \\ \" \' \n  \x??
    """
    assert '"' == s[-1]
    assert '"' == s[0]
    return EscapedStringToBytes(s[1:-1])


def StringLiteralToBytes(s: str) -> bytes:
    k = s[0]
    if k != '"':
        s = s[1:]
    if s.startswith('"""'):
        s = s[3:-3]
    else:
        s = s[1:-1]

    if k == '"':
        return EscapedStringToBytes(s)
    elif k == 'x':
        return HexStringToBytes(s)
    else:
        assert k == 'r'
        return s.encode('utf8')


_BYTE_TO_ESC = {
    # ord("\r"): "\\r",
    ord("\n"): "\\n",
    # ord("\t"): "\\t",
    # ord("\f"): "\\f",
    # ord("\b"): "\\b",
    ord('"'): '\\"',
    ord("\\"): "\\\\",
}


def BytesToEscapedString(data: bytes) -> str:
    """Convert bytes to a C escaped string
    The escaping uses the \\x.. escape mechanism for everything
    """
    out = []
    # print (repr(data))
    for b in data:
        e = _BYTE_TO_ESC.get(b)
        # print (b, e)
        if e is not None:
            out.append(e)
        elif 32 <= b <= 126:
            out.append(chr(b))
        else:
            out.append(r"\x%02x" % b)
    return "".join(out)


RE_NUMBER = re.compile(r"^([-+0-9.][-+0-9.a-fA-FpPxX]*|nan|inf)$")
RE_IDENTIFIER = re.compile(r"^[_a-zA-Z$%][_a-zA-Z$%@0-9.:/<>,]*$")
RE_INTEGER = re.compile(r"[-+]?([0-9]+|0[xX][0-9a-fA-F]+)$")
RE_CONSTANT = re.compile(r"^[-+0-9.].*")

# Note: we rely on the matching being done greedily
TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
TOKEN_NAMENUM = r'[^=\[\];"#\' \r\n\t,][^=\[\];"#\' \r\n\t]*'
TOKEN_COMMENT = r'[#].*$'
TOKEN_OP = r'[=\[\],;]'
RE_COMBINED = re.compile("|".join(["(?:" + x + ")" for x in [TOKEN_STR, TOKEN_COMMENT,
                                                             TOKEN_OP, TOKEN_NAMENUM]]))


def IsLikelyConst(s):
    return RE_CONSTANT.match(s)


def IsNum(s):
    return RE_NUMBER.match(s)


def IsInt(s):
    return RE_INTEGER.match(s)


def ParseInt64(s) -> Optional[int]:
    try:
        val = int(s, 0)
        if (1 << 63) <= val < (1 << 64):
            val -= (1 << 64)
        return val
    except Exception:
        return None


def ParseUint64(s) -> Optional[int]:
    try:
        val = int(s, 0)
        return val
    except Exception:
        return None


def ParseLine(line: str) -> List[str]:
    # TODO: hackish

    tokens = re.findall(RE_COMBINED, line)
    in_list = False
    out = []
    for t in tokens:
        if t == "=":
            continue
        if t == "," or t == ";":
            raise ValueError(
                f"commas and semicolons are not allowed {line}: {tokens}")
        elif t == "[":
            assert not in_list
            in_list = True
        elif t == "]":
            assert in_list
            in_list = False
        elif t.startswith('"'):
            assert t.endswith('"')
        out.append(t)
    assert not in_list, f"bad line {line}"
    return out


def ToHexString(key, n):
    out = []
    while 1:
        nibble = n & 15
        if nibble <= 9:
            out.append(chr(ord('0') + nibble))
        else:
            out.append(chr(ord('a') + nibble - 10))
        n >>= 4
        if n == 0:
            break
    return "#" + key + "".join(reversed(out))


def FltToHexString(n):
    x = struct.pack('<d', n)
    return ToHexString('F', int.from_bytes(x, "little"))
