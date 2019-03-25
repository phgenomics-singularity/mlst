'''
Make an MLST DB for MLST
'''

import re
import click
import urllib.request
from Bio import SeqIO
import itertools
import pathlib
import subprocess
import shlex
import logging
import os
import json
import tarfile

EUK_DB = ['afumigatus', 'blastocystis',
          'calbicans', 'cglabrata', 'ckrusei', 'ctropicalis',
          'csinensis', 'kseptempunctata', 'sparasitica', 'tvaginalis']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p')
fh = logging.FileHandler(filename='mlst_db_update.log')
ch = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(fh)
logger.addHandler(ch)


def mkdir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def wget(url, filename):
    logger.info(f"Downloading {url} to {filename}")
    return urllib.request.urlretrieve(url, filename=filename)


def is_prokaryotic(url):
    '''
    Test if prokaryotic by testing if it exists in the EUK_DB
    '''
    res = any(url.find(pat) >= 0 for pat in EUK_DB)
    if res:
        logger.info(f"Excluding {url} because it is Eukcaryote.")
    return not res


def download_xml(pubmlst_url, outdir, filename):
    '''
    Download and process dbases.xml
    '''
    logger.info(f"Downloading {pubmlst_url}")
    local_filename, headers = wget(pubmlst_url,
                                   filename=os.path.join(outdir, filename))
    pattern = re.compile(r'(http.*txt|http.*tfa)')
    with open(local_filename) as fn:
        urls = [pattern.findall(l) for l in fn if pattern.findall(l)]
        urls = list(itertools.chain(*urls))
    logger.info(f"Downloading {pubmlst_url}... OK!")
    return urls


def relabel_alleles(filename, profile, gene_id):
    '''
    Add scheme name to alleles
    '''
    logger.info(f"Re-labelling alleles for {gene_id}.")
    with open(filename, 'r') as fn:
        seqs = SeqIO.parse(fn, format='fasta')
        seqs = [s for s in seqs]
    for seq in seqs:
        seq.id = f"{profile}.{seq.id.split('.')[-1]}"
        seq.description = ''
    with open(filename, 'w') as fn:
        SeqIO.write(seqs, fn, format='fasta')


def parse_urls(urls, outdir):
    '''
    Parse the URLs into a dictionary
    '''
    logger.info("Parsing URLs...")
    parsed_urls = {}
    for url in filter(is_prokaryotic, urls):
        filename = os.path.basename(url)
        name, ext = os.path.splitext(filename)
        if ext == '.txt':
            profile = name
            logger.info("Parsing {}".format(profile))
            profiledir = pathlib.Path(outdir, name)
            if not profiledir.exists():
                mkdir(profiledir)
            filename = profiledir / filename
            local_filename, header = wget(url, filename)
            parsed_urls[profile] = {}
            parsed_urls[profile]['profile'] = filename
            parsed_urls[profile]['tfa'] = []
        elif ext == '.tfa':
            logger.info(f"Working on gene {name} for profile {profile}")
            filename = profiledir / filename
            local_filename, headers = wget(url, filename)
            relabel_alleles(filename, profile, name)
            parsed_urls[profile]['tfa'].append(filename)
        else:
            pass
    return parsed_urls


def cat_tfa(parsed_urls, blast_db, blast_dir):
    logger.info("Cating all alleles...")
    all_alleles = []
    logger.debug(parsed_urls)
    for profile in parsed_urls:
        for tfa in parsed_urls[profile]['tfa']:
            with open(tfa, 'r') as fn:
                all_alleles.extend(fn.readlines())
    with open(os.path.join(blast_dir, blast_db), 'w') as fn:
        for a in all_alleles:
            fn.write(a)
    logger.info("Cating all alleles... OK!")


def makeblastdb(blast_db, blast_dir):
    logger.info("Building the BLAST DB...")
    title = 'PubMLST'
    outfolder = blast_dir / blast_db
    cmd = ("makeblastdb -hash_index -dbtype nucl -parse_seqids"
           f" -title {title} -in {outfolder}")
    p = subprocess.run(shlex.split(cmd),
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       encoding='utf8')
    logger.info("Building the BLAST DB... OK!")
    return p.stdout


def build_blast_db(blast_db, blast_dir, parsed_urls):
    mkdir(blast_dir)
    # cat the tfa
    cat_tfa(parsed_urls, blast_db, blast_dir)
    makeblastdb(blast_db, blast_dir)


def tar_files(outdir, blast_dir):
    '''
    Given the outdir and blast_dir, tar them to mlst_db.tar.gz
    '''
    logger.info("Creating tar of DB for archive.")
    with tarfile.open("mlst_db.tar.gz", mode='w:gz') as out:
        out.add(outdir)
        out.add(blast_dir)


def write_version_file(filename="mdu_mlst_db.json"):
    '''
    Write a json object that says when the DB was last updated, and by whom:

    {version: V2017-05-02,
     date: 2017-05-02,
     author: agoncalves,
     total_schemes: 10,
     git_commit: XXGAA90}
    '''

    pass


@click.command()
@click.argument("author")
@click.option("-o", "--outdir", default='pubmlst', show_default=True)
@click.option("-d", "--blast_db", default='mlst.fa', show_default=True)
@click.option("-b", "--blast_dir", default='blast', show_default=True)
@click.option("-p", "--pubmlst_url",
              default="http://pubmlst.org/data/dbases.xml",
              show_default=True)
def mlst_db(author, outdir, blast_db, blast_dir, pubmlst_url):
    log_level = 20
    outdir = pathlib.Path(outdir)
    mkdir(outdir)
    blast_dir = pathlib.Path(blast_dir)
    mkdir(blast_dir)
    logger.info(f"Welcome {author}")
    urls = download_xml(pubmlst_url, outdir, 'dbases.xml')
    parsed_urls = parse_urls(urls, outdir)
    build_blast_db(blast_db, blast_dir, parsed_urls)
    tar_files(outdir, blast_dir)
    logger.info("All done! Happy MLSTing!")


if __name__ == "__main__":
    mlst_db()
