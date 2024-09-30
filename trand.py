from os import getenv
import time
import re
import random
from pathlib import Path as P
from dotenv import load_dotenv
import argparse
import logging

VER='1.0.0.1'
load_dotenv()
MP3DIR = getenv('MP3DIR')                           # path to music files directory
REDICT = '0123456789ABCDEFGHIGKLMNOPQRSTUVWXYZ'     # charset for prefix word
REPREFX = f'^\[[{REDICT}]+\]'                       # regex to match prefix in filename
NUMRND = 6                                          # number of random chars in prefix

log = logging.getLogger(__name__)
parser = argparse.ArgumentParser(
          prog='trackRandomizer'
        , usage='./trackRandomizer add|undo -d mp3DIR [-v]'
        , description='перемешивает треки в каталоге'
        , epilog=f'trackRandomizer {VER}'
    )

parser.add_argument('cmd', choices=['add','undo'])
parser.add_argument('-d', dest='mp3dir', help='music directory path', type=P, default=MP3DIR)
parser.add_argument('-v', dest='verbose', help='be verbose', action='store_true')

def process_files(dir:P):
    for filepath in dir.glob('*'):
        U = filepath.rename(P.joinpath(filepath.parent, randname(filepath.name)))
        log.debug(f'fl {filepath.name} -> {U.name}')

def randname(name:str):
    
    match = re.search(REPREFX, name)
    if match:
        return re.sub(REPREFX, rnd_word(), name)
    else:
        return rnd_word() + name

def rnd_word():  
    ww = '['
    for l in random.sample(REDICT, NUMRND):
        ww = ww + l
    return ww + ']'

def remove_prefixes(dir:P):
    log.info('remove prefixes from filenames')
    for filepath in dir.glob('*'):    
        match = re.search(REPREFX, filepath.name)
        if match:
            newname = filepath.name[2+NUMRND:]
            U = filepath.rename(P.joinpath(filepath.parent, newname))
            log.debug(f'fl{filepath.name} -> {U.name}')


if __name__== '__main__':
    args = parser.parse_args()
    log_fmt = '%(asctime)s - %(levelname)s [%(funcName)s:%(lineno)d] - %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_fmt)
    else:
        logging.basicConfig(level=logging.INFO, format=log_fmt, filename=f'{parser.prog}.log')
    log.info(f'{parser.prog} {VER} started. CMD= "{args.cmd.upper()}"')

    random.seed()
    begin = time.time()
    if args.mp3dir is None:
        raise ValueError('mp3 dir path required')

    if args.cmd=='add':
        process_files(args.mp3dir)
    elif args.cmd=='undo':
        remove_prefixes(args.mp3dir)

    total = time.time() - begin
    print('Total time: ', round(total,2),'s.')
    log.info('finished succes')