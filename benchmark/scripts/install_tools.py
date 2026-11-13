#!/usr/bin/env python3
"""Instala scanner oficial em diretório privado após conferir SHA-256 fixo."""
import hashlib
from pathlib import Path
import platform
from urllib.request import urlopen
VERSION='2.7.0'
SHA256='160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b'
URL='https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64'
ROOT=Path(__file__).resolve().parents[2]

def main():
    if platform.system()!='Linux' or platform.machine() not in ('x86_64','amd64'):raise SystemExit('Installer fixado para Linux amd64; instalar scanner oficial equivalente e registrar outra plataforma')
    target=ROOT/'.private/tools/osv-scanner';target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=SHA256:
        with urlopen(URL,timeout=60) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=SHA256:raise SystemExit('Digest do scanner diverge; nenhum binário foi executado')
        temp=target.with_suffix('.download');temp.write_bytes(data);temp.chmod(0o700);temp.replace(target)
    print('OSV-Scanner '+VERSION+' verificado por SHA-256; binário privado disponível.')
if __name__=='__main__':main()
