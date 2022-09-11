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


def QuotedEscapedStringToBytes(s: str) -> bytes:
    r"""Note: this does NOT support many c-escape sequences.

    Supported are: \\ \" \' \n  \x??
    """
    assert '"' == s[-1]
    assert '"' == s[0]
    return EscapedStringToBytes(s[1:-1])


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


RE_NUMBER = re.compile(r"^([-+0-9.][-+0-9.a-fA-FpPxX]*|nan|NAN|inf|INF)$")
RE_IDENTIFIER = re.compile(r"^[_a-zA-Z$%][_a-zA-Z$%@0-9.:]*$")
RE_INTEGER = re.compile(r"[-+]?([0-9]+|0[xX][0-9a-fA-F]+)$")
RE_CONSTANT = re.compile(r"^[-+0-9.].*")

# Note: we rely on the matching being done greedily
TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
TOKEN_NAMENUM = r'[^=\[\],;"#\' \r\n\t]+'
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


def Flt64FromBits(data: int) -> float:
    return struct.unpack('<d', int.to_bytes(data, 8, "little"))[0]


def Flt64ToBits(num: float) -> int:
    b = struct.pack('<d', num)
    assert len(b) == 8
    return int.from_bytes(b, "little")


def ParseFlt64(s) -> Optional[float]:
    try:
        if s.startswith("0x") or s.startswith("0X"):
            val = int(s, 0)
            return Flt64FromBits(val)
        return float(s)
    except Exception as err:
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
            raise ValueError(f"commas and semicolons are not allowed {line}")
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
        if n == 0: break
    return "#" + key + "".join(reversed(out))


def FltToHexString(n):
    x = struct.pack('<d', n)
    return ToHexString('F', int.from_bytes(x, "little"))
