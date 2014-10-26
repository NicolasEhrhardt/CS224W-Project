import disp
import cPickle as pickle
import gzip
from os import path

# var to file
def save(variable, outputFile):
  print "Saving in file: " + outputFile
  with gzip.open(outputFile, 'wb') as output:
    pickle.dump(variable, output, pickle.HIGHEST_PROTOCOL)

# file to var
def load(inputfile):
  if inputfile is not None:
    with gzip.open(inputfile, 'r') as inputFile:
      return pickle.load(inputFile)

def getParent(filename):
  return path.dirname(path.dirname(path.abspath(filename)))

def generateLine(filename, verbose = True):
  num = 0
  with open(filename) as f:
    for line in f:
      disp.tempPrint(str(num))
      num += 1
      yield line
