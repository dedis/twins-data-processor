import tmtk
from chardet.universaldetector import UniversalDetector

import codecs
import glob
import json
import logging
import os


# Read file in chunks of !M
BLOCKSIZE = 1 << 20

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def convert(source, encoding):
    dst = source + '.tmp'
    with codecs.open(source, 'r', encoding) as sf:
        with codecs.open(dst, 'w', 'utf-8') as df:
            while True:
                contents = sf.read(BLOCKSIZE)
                if not contents:
                    break
                df.write(contents.replace('Ê', ''))
    os.remove(source)
    os.rename(dst, source)
    logger.info(f'converted file {source} from `{encoding}` to `utf-8`')

def crlf_lf(path):
    dst = path + '.tmp'
    df = open(dst, 'w')
    for line in open(path, 'r'):
        if line.strip() == '':
            continue
        df.write(line.rstrip('\r\n') + '\n')
    df.close()
    os.remove(path)
    os.rename(dst, path)
    logger.info(f'Changed line endings for {path} from CRLF to LF')

def preprocess(path):
    detector = UniversalDetector()
    for filename in glob.glob(f'{path}/*.txt'):
        detector.reset()
        cr = False
        for line in open(filename, 'rb'):
            if not cr and line[-2:] == b'\r\n':
                cr = True
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        if detector.result['encoding'] not in ('ascii', 'utf-8'):
            convert(filename, detector.result['encoding'])
        if cr:
            crlf_lf(filename)

def process():
    with open('config.json') as config_file:
        config = json.load(config_file)

    preprocess(f'{config["input_directory"]}/clinical')

    study = tmtk.Study(f'{config["input_directory"]}/study.params')

    export = tmtk.toolbox.SkinnyExport(study, config['output_directory'])
    export.to_disk()

if __name__ == '__main__':
    process()
