import logging
import os

from clint.textui import puts

from format import PKG, IRD

logging.basicConfig(level=logging.DEBUG, format='%(name)-32s: %(levelname)-8s %(message)s')

if __name__ == '__main__':
    print("test")
    # Pkg("G:/OldBigBoiBackup/PSN/BCUS98132/Retail/UP9000-BCUS98132_00-HEAVENLYSWORDPA1-PE.pkg")
    # Pkg("NPUA70175 Resistance 3 Single-Player Demo.pkg")
    # PSARC("english.psarc")
    # Pkg(
    #     "G:\\OldBigBoiBackup\\PSNDL\\"
    #     "EP2144-NPEB02133_00-AARUSAWAKENINGE3_bg_2_b7bcc2fbf0a9b27437b1040cfb16d694a16cf83b.pkg"
    # )
    # BLES02078 INVALID
    PKG("C:\\Users\\Nicba1010\\Downloads\\BATTLEFIELD_HARDLINE_NPUB31511_DELUXE_PACK_DLC_FIX.pkg")
    skip = False
    for root, dirs, files in os.walk("G:\\OldBigBoiBackup\\PSNDL"):
        for file in files:
            if file.endswith(".pkg") and not skip:
                file = os.path.join(root, file)
                print(file)
                if file == "H:\\PSN\\NPIA00002\\Retail\\IP9100-NPIA00002_00-0000111122223333-A0122-V0100-PE.pkg" or \
                        'Debug' in file:
                    # noinspection PyBroadException
                    try:
                        a = PKG(file, verify_pkg_hash=False)
                        b = 4
                    except Exception:
                        pass
                else:
                    # noinspection PyBroadException
                    try:
                        a = PKG(file, verify_pkg_hash=False)
                        b = 4
                    except Exception:
                        print(file)
                        raise Exception
    for root, dirs, files in os.walk("H:\IRD"):
        for file in files:
            if file.endswith(".ird"):
                file = os.path.join(root, file)
                try:
                    IRD(file)
                except Exception as e:
                    puts(file)
                    raise e
