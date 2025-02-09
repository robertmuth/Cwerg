# for use with @num classes
def NameValues(cls, lower=False):
    return [(x.name.lower() if lower else x.name, x.value) for x in cls]


def RenderEnum(cls, name, fout, prefix=""):
    print(f"\nenum {name} {{", file=fout)
    for name, value in cls:
        if value <= 255:
            print(f"    {prefix}{name} = {value},", file=fout)
        else:
            print(f"    {prefix}{name} = 0x{value:x},", file=fout)
    print("};", file=fout)


def RenderEnumClass(cls, name, fout, prefix=""):
    print(f"\nenum class {name} : uint8_t {{", file=fout)
    for name, value in cls:
        if value <= 255:
            print(f"    {prefix}{name} = {value},", file=fout)
        else:
            print(f"    {prefix}{name} = 0x{value:x},", file=fout)
    print("};", file=fout)


def RenderEnumToStringMap(cls, name, fout, initial=0, lower=False):
    print(f"\nconst char* const {name}_ToStringMap[] = {{", file=fout)
    last = initial  # this should really be called `next`
    for name, value in cls:
        if lower:
            name = name.lower()
        while last != value:
            print(f'    "", // {last}', file=fout)
            last += 1
        if value <= 255:
            print(f'    "{name}", // {value}', file=fout)
        else:
            print(f'    "{name}", // 0x{value:x}', file=fout)
        last += 1
    print("};", file=fout)


def RenderEnumToStringMapFlag(cls, name, fout):
    last = 0
    print(f"\nconst char* const {name}_ToStringMap[] = {{", file=fout)
    for name, value in cls:
        assert value & (
            value - 1) == 0, f"value 0x{value:x} must have one bit set"
        while last != 0 and last != value:
            print(f'    "", // {last}', file=fout)
            last *= 2
        if value <= 255:
            print(f'    "{name}", // {value},', file=fout)
        else:
            print(f'    "{name}", // 0x{value:x},', file=fout)
        last *= 2
    print("};", file=fout)


def RenderStringToEnumMap(cls, map_name, jumper_name, fout, lower=False):
    print(f"\nconst struct StringKind {map_name}[] = {{", file=fout)

    jumper = {}
    alpha = sorted(cls)
    for count, (name, val) in enumerate(alpha):
        print('    {"%s", %d},' % (name, val), file=fout)
        char = name[0]
        if char not in jumper:
            jumper[char] = count

    print('    {"ZZZ", 0},', file=fout)
    print("};", file=fout)

    print(f"\nconst uint8_t {jumper_name}[128] = {{", file=fout)
    for i in range(128):
        print(" %d," % jumper.get(chr(i), 255), end="", file=fout)
        if i % 16 == 15:
            print("", file=fout)
    print("};", file=fout)


def RenderEnumToStringFun(name, fout):
    print(f"const char* EnumToString({name} x) {{"
          f" return {name}_ToStringMap[unsigned(x)]; }}\n", file=fout)


def ReplaceContent(emitter, fin, fout):
    in_auto_gen = False
    for line in fin:
        if not in_auto_gen:
            print(line, end="", file=fout)
            if "@AUTOGEN-START@" in line:
                in_auto_gen = True
                emitter(fout)
        else:
            if "@AUTOGEN-END@" in line:
                print(line, end="", file=fout)
                in_auto_gen = False
    assert not in_auto_gen
