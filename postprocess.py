#!/usr/local/bin/python
import csv
import sys
import numpy as np
from itertools import chain
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

if len(sys.argv) != 4:
  print sys.argv[0], '<input>', '<seeds>', '<output>'
  sys.exit()

# Import predictions and create a dict of dicts
# contours[pid][pslice] = [c_0, c_1, c_2, ...]
# where:
# pid = patient ID
# pslice = patient slice
# c_j = ordered array of coordinates along contour boundary (j=0,1,2...)
contours = {}
with open(sys.argv[1], 'rb') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    pid = row[0]
    pslice = int(row[1])
    pcontour = np.array(row[2:], dtype=float).reshape(-1,2)
    if pid not in contours.keys():
      contours[pid] = {}
    if pslice not in contours[pid].keys():
      contours[pid][pslice] = []
    contours[pid][pslice].append(pcontour)

print 'Number of PIDs (contours): ', len(contours)

if False:
  for pid in contours.keys()[:2]:
    for pslice in contours[pid].keys():
      print pid, pslice, contours[pid][pslice]
  raw_input()

# Import seeds and create a dict of dicts
# seeds[pid][pslice] = [s_0, s_1, s_2, ...]
# where:
# pid = patient ID
# pslice = patient slice
# s_j = coordinate of a seed location (j=0,1,2...)
seeds = {}
with open(sys.argv[2], 'rb') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    pid = row[0]
    pslice = int(row[1])
    pseed = np.array(row[2:], dtype=float)
    if pid not in seeds.keys():
      seeds[pid] = {}
    if pslice not in seeds[pid].keys():
      seeds[pid][pslice] = []
    seeds[pid][pslice].append(pseed)

print 'Number of PIDs (seeds): ', len(seeds)

if False:
  for pid in seeds.keys():
    for pslice in seeds[pid].keys():
      print pid, pslice, seeds[pid][pslice]
  raw_input()


def find_contiguous_slices(pslices):
  g = []
  h = []
  prev=-1
  for pslice in sorted(pslices):
    if prev+1==pslice:
      h.append(pslice)
    else:
      g.append(h)
      h=[pslice]
    prev=pslice
  g.append(h)
  return g[1:]

with open(sys.argv[3], 'w') as f:
  for pid in contours.keys():
    print '\nPID:', pid
    seed_slices = seeds[pid].keys()
    print 'Seed Slices:', seed_slices
    padding = 7 # Tune to maximize provisional score
    print 'Seed Padding:', padding
    padded_seed_slices = [ range(x-padding, x+padding+1) for x in seed_slices ]
    seed_slices = [ x for x in chain(*padded_seed_slices) ]
    print 'Padded Seed Slices:', seed_slices
    pslices = contours[pid].keys()
    print 'Patient Contour Slices:', pslices
    pslices_splits = find_contiguous_slices( pslices )
    print 'Contiguous Patient Contour Slices:', pslices_splits
    # For each patient ID, identify groups of contiguous slices
    # That are within 'padding' distance of seed
    for pslices_split in pslices_splits:
      if set(pslices_split) & set(seed_slices) != set([]):
        print 'Keeper Slices: ', pslices_split
        for pslice in pslices_split:
          #print str(pslice)
          for c in contours[pid][pslice]:
            f.write(pid+','+str(pslice)+','+','.join([str(elem) for elem in chain(*c)])+'\n')

