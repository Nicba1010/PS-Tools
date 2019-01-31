# ISO 9660
## Data Type Formats
### Numerical Values

| Native Data Type    | Length    | Endianness    | Short    |
|---------------------|-----------|---------------|----------|
|`` unsigned int8   ``| 1         | X             |`` u8   ``|
|`` int8            ``| 1         | X             |`` i8   ``|
|`` unsigned int16  ``| 2         | LITTLE        |`` u16l ``|
|`` unsigned int16  ``| 2         | BIG           |`` u16b ``|
|`` unsigned int16  ``| 4         | DUAL          |`` u16d ``|
|`` int16           ``| 2         | LITTLE        |`` i16l ``|
|`` int16           ``| 2         | BIG           |`` i16b ``|
|`` int16           ``| 4         | DUAL          |`` i16d ``|
|`` unsigned int32  ``| 4         | LITTLE        |`` u32l ``|
|`` unsigned int32  ``| 4         | BIG           |`` u32b ``|
|`` unsigned int32  ``| 8         | DUAL          |`` u32d ``|
|`` int32           ``| 4         | LITTLE        |`` i32l ``|
|`` int32           ``| 4         | BIG           |`` i32b ``|
|`` int32           ``| 8         | DUAL          |`` i32d ``|

### Character Sets And Encoding
In each fixed-length field the content of which is specified by this
International Standard to be characters, the characters shall be
left-justified and any remaining positions on the right shall be
set to `0x2O`.

#### Type A

Regex:
~~~
[0-9A-Z_]
~~~
All Allowed Characters:
~~~
0123456789
ABCDEFGHIJKLMNOPQRSTUVWXYZ
_
~~~
Short:
~~~
str_a
~~~

#### Type D

Regex:

Regex:
~~~
[0-9A-Z_!"%&'()*+,-./:;<=>? ]
~~~
All Allowed Characters:
~~~
0123456789
ABCDEFGHIJKLMNOPQRSTUVWXYZ
_!"%&'()*+,-./:;<=>?
SPACE
~~~
Short:
~~~
str_d
~~~

#### Type C
The characters of the coded graphic character sets identified by the
escape sequences in a Supplementary Volume Descriptor.
Short:
~~~
str_c
~~~

#### Type A1
A subset of the [c-characters](#type-c). This subset is subject to
agreement between the originator and the recipient of the volume.
Short:
~~~
str_a1
~~~

#### Type D1
A subset of the [a1-characters](#type-a1). This subset is subject to
agreement between the originator and the recipient of the volume.
Short:
~~~
str_d1
~~~

### Separators

#### Separator 1
Represented by the dot character "." (`0x2E`)
Short:
~~~
sep_1
~~~

#### Separator 2
Represented by the semicolon character ";" (`0x3B`)
Short:
~~~
sep_2
~~~

## File Identifier

### Format
Example: ``test.wav;1``

| Name of Field       | Length   | Type         | Example |
|---------------------|----------|--------------|---------|
| File Name           | VARIABLE | str_d/str_d1 | test    |
| Separator 1         | 1        | sep_1        | .       |
| File Name Extension | VARIABLE | str_d/str_d1 | wav     |
| Separator 2         | 1        | sep_2        | ;       |
| File Version        | VARIABLE | i16          | 1       |
TODO: Check file version bytes!

### Conditions
 - If the File Name Field Length is 0, the File Name Extension Length
 may not be 0.
 - If the File Name Extension Field Length is 0, the File Name Length
 may not be 0.
 - The sum of the File Name Length and the File Name Extension Length
 may not exceed 30.

### Length
The length of the File identifier is the sum of the following:
 - The Length of the File Name Field
 - The Length of the File Name Extension Field
 - The Length of the File Version Number Field
 - The Number of Separators (Usually 2)

## Directory Identifier

### Format
Example: ``PS3_UPDATE``

| Name of Field        | Length   | Type         | Example    |
|----------------------|----------|--------------|------------|
| Directory Identifier | VARIABLE | str_d/str_d1 | PS3_UPDATE |

#### Reserved Identifiers
 - `0x00` - The Directory Identifier of a Directory Record describing the Root Directory
 - `0x00` - The Directory Identifier of the first Directory Record of each Directory
 - `0x01` - The Directory Identifier of the second Directory Record of each Directory

#### Conditions
 - The length of a Directory Identifier may not exceed 31

## Volume Descriptors

Volume Descriptors identify the volume, the partitions recorded on the
volume, the volume creator(s), certain attributes, location of other
recorded descriptors, and the version of the standard that applies.

### Base Format

| Offset | Length | Name of Field          | Type  | Example |
|--------|--------|------------------------|-------|---------|
| 0      | 1      | Descriptor Type        | u8    | 0x01    |
| 1      | 5      | Standard Identifier    | str_a | CD001   |
| 6      | 1      | Descriptor Version     | u8    | 0x01    |
| 7      | 2041   | Depends on Type        |       |         |

#### Conditions
 - Standard Identifier must always be `CD001`
 - Descriptor Version Field must always be `0x01`

### Descriptor Types

#### Boot Record
The Boot Record identifies a system which can recognize and act upon the
content of the field reserved for boot system use in the Boot Record,
and contains information which is used to achieve a specific state for a
system or for an application.

| Offset | Length | Name of Field          | Type  | Example |
|--------|--------|------------------------|-------|---------|
| 0      | 1      | Descriptor Type        | u8    | 0x01    |
| 1      | 5      | Standard Identifier    | str_a | CD001   |
| 6      | 1      | Descriptor Version     | u8    | 0x01    |
| 7      | 32     | Boot System Identifier | str_a |         |
| 39     | 32     | Boot Identifier        | str_a |         |
| 71     | 1977   | Boot System Use        |       |         |

#### Volume Descriptor Set Terminator
The recorded set of Volume Descriptors is terminated by a sequence of
one or more Volume Descriptor Set Terminators.

| Offset | Length | Name of Field          | Type  | Example |
|--------|--------|------------------------|-------|---------|
| 0      | 1      | Descriptor Type        | u8    | 0x01    |
| 1      | 5      | Standard Identifier    | str_a | CD001   |
| 6      | 1      | Descriptor Version     | u8    | 0x01    |
| 7      | 2041   | Reserved               |       |         |
