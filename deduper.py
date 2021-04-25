import os, os.path, argparse, sys, hashlib

# BUF_SIZE is to keep the app from using lots of memory on big files
BUF_SIZE = 65536  # read stuff in 64kb chunks!

# create parser
parser = argparse.ArgumentParser(description='Simple, fast file de-duplicator.')
 
# add arguments to the parser
parser.add_argument('paths', metavar='path', nargs='+', help='a path on a file system')
 
# parse the arguments
args = parser.parse_args()

# hello
print("Deduper, at your service.")

# check that paths are real
print("Checking paths... ", end='')
paths = []
for arg in args.paths:
    if os.path.isdir(arg) != True:
        print(f"{arg} is not a valid path.")
        quit()
    else:
        paths.append(os.path.abspath(arg))
print("done. ")

# walk thru each path, only record unique items
filelist = []
for path in paths:
    print(f"Walking through {path}... ", end='')
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filelist.append([path, os.path.join(root, name)])
    print("done. ")

# total number of items
filenum = len(filelist)
print(f"Found {filenum} items.")

# generate a hash of each item
print("Generating hashes... ")
hashes = []
uniquefiles = []
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
uniquenum = len(uniquefiles)
print(f"\nTotal of {uniquenum} hashes generated:")

# sort by hash
hashes = sorted(hashes, key = lambda x: x[0])

# separate into keep and move
prevhash = ''
keep = []
move = []
for hash in hashes:
    print(f"{hash[0]} {hash[2]}")
    if prevhash != hash[0]:
        keep.append(hash)
    else:
        move.append(hash)
    prevhash = hash[0]

print(f"Keep {len(keep)}, delete {len(move)}:")

# iterate thru those we need to move
for movefile in move:
    lastpart = movefile[2][len(movefile[1]):]
    print(f"rm -f '{movefile[2]}'")