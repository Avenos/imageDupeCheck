#Henry Thomas
#March 8, 2018
#
#Description:
#    This program moves all picture duplicates in 'userdir' to a subfolder
#    called '\dupes' which can then be easily sorted by the user.  Images
#    are considered duplicates if their iamge checksums match.  Checksums
#    are stored in table.csv to speed up successive runs.
#
#Dependencies:
#    Python 3.x.x
#    pip install pillow, pandas, imagehash
#
#Todo:
#    SHA-256 file verification

from PIL import Image
import pandas as pd
import imagehash
import os

tablepath = r'A:\table.csv'

class PictureFile(object):
    def __init__(self, directory = '', filename = '', checksum = ''):
        self.directory = directory
        self.filename = filename
        self.fullpath = directory + '\\' + filename
        self.checksum = checksum

#returns a list of all pictures in a directory (no checksums)
def getPics(directory):
    files = os.listdir(directory)
    pictures = []
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.gif', '.bmp')):
            picture = PictureFile(directory, filename, '')
            pictures.append(picture)
    return pictures

#returns a list of picture objects already stored in table.csv
def getStored():
    data = pd.read_csv(tablepath, names = ['dirs', 'filenames', 'checksums'], encoding = 'ansi')
    storedPictures = []
    for i in range(len(data.dirs)):
        picture = PictureFile(data.dirs[i], data.filenames[i], data.checksums[i])
        storedPictures.append(picture)
    return storedPictures

#returns a list of duplicate pictures
def getDupes(pictures):
    checksums = [PictureFile.checksum for PictureFile in pictures]
    duplicates = []
    for picture in pictures:
        if checksums.count(picture.checksum) > 1:
            duplicates.append(picture)
    return duplicates

#calculates the checksums for a list of pictures
def calcChecksum(pictures):
    for picture in pictures:
        checksum = str(imagehash.average_hash(Image.open(picture.fullpath)))
        picture.checksum = checksum
        print('File: ' + picture.filename)
        print('Checksum: ' + checksum)
    return pictures

#move a list of pictures to a directory
def move(directory, pictures):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for picture in pictures:
        os.rename(picture.fullpath, '%s\\%s' % (directory, picture.filename))

#write picture objects to table.csv
def store(pictures):
    pictures.sort(key = lambda x: x.fullpath)
    with open(tablepath, 'w') as f: 
        for picture in pictures:
            if all(ord(c) < 128 for c in picture.filename) and ',' not in picture.filename:
                f.write(picture.directory + ',' + picture.filename + ',' + picture.checksum + '\n')
            else:
                print('Bad filename: ' + picture.filename)

if __name__ == '__main__':
    if os.path.isfile(tablepath):
        print('Found ' + tablepath)
    else:
        print(tablepath + ' does not exist!')

    while(True):
        userdir = input('Enter the directory to scan: ').lower()
        #sanitize input
        if ':' not in userdir or '\\' not in userdir or '/' in userdir:
            print('Invalid path! format - D:\\folder\\subfolder')
        if not os.path.exists(userdir):
            print('Directory does not exist!')
        else:
            break

    #scan pictures and create dupe dir
    dupedir = userdir + '\\dupes'
    pictures = getPics(userdir)
    if len(pictures) == 0:
        print('No pictures found in directory!')
        exit()

    #check table for already scanned pictures
    if os.path.isfile(tablepath):
        storedPictures = getStored()
    else:
        storedPictures = []
    print('Scanning...')

    #get fullpaths of all pictures in userdir
    fullpaths = [PictureFile.fullpath for PictureFile in pictures]

    #find out which pictures are already stored
    storedinpath = []
    for picture in storedPictures:
        if picture.fullpath in fullpaths:
            storedinpath.append(picture)

    #fullpaths of already stored pictures
    storedpaths = [PictureFile.fullpath for PictureFile in storedinpath]

    #list of pictures that need to be hashed
    tocheck = []
    for picture in pictures:
        if picture.fullpath not in storedpaths:
            tocheck.append(picture)

    hashed = calcChecksum(tocheck) + storedinpath
    allpictures = hashed + storedPictures
    duplicates = getDupes(hashed)

    #store both new and previously stored hashes
    if os.path.isfile(tablepath):
        store(list(set(allpictures) - set(duplicates)))

    if len(duplicates) != 0:
        move(dupedir, duplicates)
        print('Complete! ' + str(len(duplicates)) + ' duplicate pictures were moved to ' + dupedir)
    else:
        print('Complete! No duplicate pictures were found.')