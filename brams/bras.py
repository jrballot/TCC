import argparse
import os
from ftplib import FTP

# Test INPE FTP access
#
#ftp = FTP("ftp1.cptec.inpe.br")
#ftp.login()
#ftp.cwd('/modelos/io/tempo/global/T126L28')
#ftp.retrlines('LIST')



def main():
    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BRAS - BRAMS Automation Suit")
    args = parser.parse_args()

    main
