import os

from ps.pkg import Pkg

if __name__ == '__main__':
    print("test")
    # Pkg("G:/OldBigBoiBackup/PSN/BCUS98132/Retail/UP9000-BCUS98132_00-HEAVENLYSWORDPA1-PE.pkg")
    # Pkg("NPUA70175 Resistance 3 Single-Player Demo.pkg")
    # PSARC("english.psarc")
    # Pkg(
    #     "G:\\OldBigBoiBackup\\PSNDL\\"
    #     "EP2144-NPEB02133_00-AARUSAWAKENINGE3_bg_2_b7bcc2fbf0a9b27437b1040cfb16d694a16cf83b.pkg"
    # )
    skip = True
    for root, dirs, files in os.walk("H:\PSN"):
        for file in files:
            if 'BCES01436' in file:
                skip = False
            if file.endswith(".pkg") and not skip:
                file = os.path.join(root, file)
                print(file)
                if file == "H:\\PSN\\NPIA00002\\Retail\\IP9100-NPIA00002_00-0000111122223333-A0122-V0100-PE.pkg" or 'Debug' in file:
                    try:
                        Pkg(file).verify()
                    except:
                        pass
                else:
                    try:
                        Pkg(file).verify()
                    except:
                        print(file)
                        raise Exception