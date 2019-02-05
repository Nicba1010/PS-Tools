from binascii import unhexlify

"""
SYSCON Manager Key
Used for:
    - Decrypting PFD file header table
"""
SYSCON_MANAGER_KEY = unhexlify('D413B89663E1FE9F75143D3BB4565274')

"""
Keygen Key
Used for:
    - PFD Header Real Key
"""
KEYGEN_KEY = unhexlify('6B1ACEA246B745FD8F93763B920594CD53483B82')
