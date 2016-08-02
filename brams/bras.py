import os
from ftplib import FTP


ftp = FTP("ftp1.cptec.inpe.br")
ftp.login()
ftp.cwd('/modelos/io/tempo/global/T126L28')
ftp.retrlines('LIST')
