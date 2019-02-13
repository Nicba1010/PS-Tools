#include "sha1.h"
#include <stdio.h>
#include <string.h>
typedef unsigned char byte;


static inline void
add_byte(byte *array, long long size, byte k)
{
    for(int i = size-1;
        (i >= 0) && k;
        --i)
    {
        byte val = array[i];
        k = ((array[i] += k) < val);
    }
}

extern void
add(byte *array, long long size, long long k)
{
    for(int i = 7;
        i >= 0;
        --i)
    {
        byte v = k>>(8*i);
        add_byte(array, size-i, v);
    }
}

extern long long
next_multiple_of_16(long long n)
{
    return (n + 0xF) & ~0xF;
}

extern void
generate_xor_key(byte *pkg_data_riv, long long size, long long offset, byte *result)
{
    byte array[16];
    memcpy(array, pkg_data_riv, 16);
    add(array, 16, offset);
    for(long long i = 0;
        i < size;
        i += 16)
    {
        memcpy(result + i, array, 16);
        for(int j = 15, k = 1;
            (j >= 0) && k;
            --j)
        {
            k = (++array[j] == 0);
        }
    }
}

extern void
generate_debug_xor_key(byte *qa_digest, long long size, long long offset, byte *result)
{
    // TODO: SHA1 stuff, this doesnt work yet
    byte array[64];
    memcpy(array, qa_digest, 8);
    memcpy(array + 8, qa_digest, 8);
    memcpy(array + 16, qa_digest + 8, 8);
    memcpy(array + 24, qa_digest + 8, 8);
    memset(array + 32, 0, 32);

    add(array + 48, 16, offset);
    for(long long i = 0;
        i < size;
        i += 16)
    {
        byte hash[20];

        sha1(array, 64, hash);

        memcpy(result+i, hash, 16);

        for(int j = 63, k = 1;
            (j >= 0) && k;
            --j)
        {
            k = (++array[j] == 0);
        }
    }
}

extern void
xor(byte *source, byte *key, long long length, long long key_offset)
{
    for(int i = 0;
        i < length;
        ++i)
    {
        source[i] ^= key[i + key_offset];
    }
}

int main() {
    return 1;
}
