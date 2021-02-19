# Elf Encoder/Decoder

This directory contains code for encoding and decoding of **little-endian** 
Elf executables. The C++ implementation assumes that the host system is also
little-endian.


The implementation is slightly more comprehensive than  what is needed by
Cwerg and might be useful by itself. Shared executables and dynamic
libraries have not been tested as they are out of scope for the project. 
The code is a bit opinionated about the format of the executable but should 
works for many executables found in the wild.

### Expected format

```
    [EhdrIdent]     16 bytes
    [Ehdr]          (32 or 64 bit version)
    [Phdr]+         (32 or 64 bit version)
    [Section Data]+ (mapped data precedes unmapped data)
    [Shdr]+         (32 or 64 bit version)
```

### Concepts

#### Symbol (Wraps Elf Symbol)

TBD

#### Reloc (Wraps Elf Relocation)

TBD 

#### Section (Wraps Elf Section)

A Section consists of an Elf Shdr and the corresponding data.

#### Segment (Wraps Elf Segment)

A Segment consists of an Elf Phdr and a list of Sections whose address range 
falls within the Segment.
Segments can be primary or auxiliary. If a Section belongs to multiple Segments at most one of them can be primary.
A special pseude Segment which is always comes last contains all the unmapped Sections.
This Segment is not reflected as a Phdr in the Elf executable.

##### Executable

An Executable consists of an Elf Ehdr and a list of Segments.




