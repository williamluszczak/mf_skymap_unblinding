#!/usr/bin/env python

import numpy as np
import healpy as hp
import os
import sys
import itertools
import time
import glob
from operator import itemgetter
from math import floor

import scipy.optimize
import bisect

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import histlite as hl
import csky as cy
from csky import hyp

print("env is okay")
