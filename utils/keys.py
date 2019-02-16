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

"""
PS3 GPKG Key
Used for:
    - Decrypting PS3 PKG Data
"""
PS3_GPKG_KEY = unhexlify('2E7B71D7C9C9A14EA3221F188828B8F8')

"""
PSP GPKG Key
Used for:
    - Decrypting PSP PKG Data
"""
PSP_GPKG_KEY = unhexlify('07F2C68290B50D2C33818D709B60E62B')

"""
PSP2 (PSVita) GPKG Key 0
Used for:
    - Decrypting PSP2 (PSVita) PKG Data for PSP2GD Content Type (0x15)
"""
PSP2_GPKG_KEY0 = unhexlify('E31A70C9CE1DD72BF3C0622963F2ECCB')

"""
PSP2 (PSVita) GPKG Key 1
Used for:
    - Decrypting PSP2 (PSVita) PKG Data for PSP2AC Content Type (0x16)
"""
PSP2_GPKG_KEY1 = unhexlify('423ACA3A2BD5649F9686ABAD6FD8801F')

"""
PSP2 (PSVita) GPKG Key 2
Used for:
    - Decrypting PSP2 (PSVita) PKG Data for PSP2LA Content Type (0x17)
"""
PSP2_GPKG_KEY2 = unhexlify('AF07FD59652527BAF13389668B17D9EA')
