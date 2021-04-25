import os, os.path, argparse, sys, hashlib
from pathlib import Path

# BUF_SIZE is to keep the app from using lots of memory on big files
BUF_SIZE = 65536  # read stuff in 64kb chunks!

# create parser
parser = argparse.ArgumentParser(description='Simple, fast file de-duplicator.')
 
# add arguments to the parser
parser.add_argument('paths', metavar='path', nargs='+', help='a path on a file system')
 
# parse the arguments
args = parser.parse_args()

# hello
print("Deduper, at your service.", flush=True)

# check that paths are real
print("Checking paths... ", end='', flush=True)
paths = []
for arg in args.paths:
    if os.path.isdir(arg) != True:
        print(f"{arg} is not a valid path.", flush=True)
        quit()
    else:
        paths.append(os.path.abspath(arg))
print("done. ", flush=True)

# walk thru each path, only record unique items
filelist = []
for path in paths:
    print(f"Walking through {path}... ", end='', flush=True)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filelist.append([path, os.path.join(root, name)])
    print("done. ", flush=True)

# total number of items
filenum = len(filelist)
print(f"Found {filenum} items. Processing...", flush=True)

# generate a hash of each unique uri
hashes = []
uniquefiles = []
fstot = 0 # file size total
for fileitem in filelist:
    if fileitem[1] not in uniquefiles:
        uniquefiles.append(fileitem[1])
        md5 = hashlib.md5()
        with open(fileitem[1], 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        hashes.append([format(md5.hexdigest()), fileitem[0], fileitem[1]])
        print(f"{format(md5.hexdigest())} {fileitem[1]}", flush=True)
        fstot += Path(fileitem[1]).stat().st_size
uniquenum = len(uniquefiles)
print(f"{uniquenum} hashes generated from {filenum} items.", flush=True)

# sort by hash
hashes = sorted(hashes, key = lambda x: x[0])

# separate into keep and move
prevhash = ''
keep = []
move = []
fsdupe = 0
for hash in hashes:
    if prevhash != hash[0]:
        keep.append(hash)
    else:
        move.append(hash)
        fsdupe += Path(hash[2]).stat().st_size
    prevhash = hash[0]

print(f"There are {len(move)} duplicates you can delete.", flush=True)
print(f"{fsdupe:,} bytes duplicate in {fstot:,} bytes total.")

# iterate thru those we need to move
print("Use these commands to delete all duplicates:")
for movefile in move:
    # lastpart = movefile[2][len(movefile[1]):]
    print(f"rm -f '{movefile[2]}'", flush=True)