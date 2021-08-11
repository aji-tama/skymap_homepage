#mprof run ASC_mpl.py
#mprof plot

###################### TODO list ######################
# REPLACE MATH WITH NUMPY
# milkyway (across screen)
# check boundary (across screen)
# check jupiter plot scale
# check ephemeris for >2 events a day
# check moon projection
# fix ephemeris mag
# update sunspot only once a day
# predownload weather icon from HKO
# fit parameters
# cloud detection
# record 24hr stat per day

###################### TODO list ######################

import time

#import timeit
#from numba import jit
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError, ContentTooShortError
import socket
import requests
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from matplotlib import font_manager
from matplotlib import collections as mc
import matplotlib.animation
import pandas
import numpy
import math
import cv2
from skyfield import almanac, almanac_east_asia
from skyfield.api import load, wgs84, PlanetaryConstants
from skyfield.framelib import ecliptic_frame
from skyfield.almanac import find_discrete, risings_and_settings
from skyfield.magnitudelib import planetary_magnitude
from pytz import timezone, common_timezones
from datetime import date, datetime, timedelta
import cartopy.crs as ccrs
import pathlib
from PIL import Image
import itertools
from operator import itemgetter
import sys
from sys import platform
import os
import gc
import feedparser
import re
import objgraph

##################
#memory leak
debug_mode = 0
##################

######################
# initial parameters #
######################

count=0
T0 = time.time()

#matplotlib.rcParams['savefig.facecolor'] = ('#F0F0F0')

#####################################
# ephem setting
tz          = timezone('Asia/Hong_Kong')

ephem       = load('de421.bsp') #1900-2050 only
#ephem      = load('de422.bsp') #-3000-3000 only
#ephem      = load('de430t.bsp') #1550-2650 only
ephemJ      = load('jup310.bsp') #Jupiter
sun         = ephem['sun']
mercury     = ephem['mercury']
venus       = ephem['venus']
earthmoon   = ephem['earth_barycenter']
earth       = ephem['earth']
moon        = ephem['moon']
mars        = ephem['mars']
jupiter     = ephem['jupiter_barycenter']
jupiterJ    = ephemJ['jupiter_barycenter']
io          = ephemJ['Io']
europa      = ephemJ['Europa']
ganymede    = ephemJ['Ganymede']
callisto    = ephemJ['Callisto']
saturn      = ephem['saturn_barycenter']
uranus      = ephem['uranus_barycenter']
neptune     = ephem['neptune_barycenter']
pluto       = ephem['pluto_barycenter']
#####################################
# moon geometry
pc = PlanetaryConstants()
pc.read_text(load('moon_080317.tf'))
pc.read_text(load('pck00008.tpc'))
pc.read_binary(load('moon_pa_de421_1900-2050.bpc'))
frame = pc.build_frame_named('MOON_ME_DE421')
#####################################

#####################################
# location information
#HKO
Trig_0      = (earth + wgs84.latlon((22+18/60+7.3/3600),(114+10/60+27.6/3600)),\
               22+18/60+7.3/3600,114+10/60+27.6/3600,'22:18:07.3','N','114:10:27.6','E')

#Hokoon
hokoon      = (earth + wgs84.latlon((22+23/60+1/3600),(114+6/60+29/3600)),\
               22+23/60+1/3600,114+6/60+29/3600,'22:23:01','N','114:06:29','E')

Obs         = hokoon #<= set your observatory

ts          = load.timescale()
date_UTC    = ts.utc(ts.now().utc_datetime().replace(second=0,microsecond=0))
date_local  = date_UTC.astimezone(tz)
#####################################

# plot parameters
image_size = 1.6
#side_space = 6
fig = plt.figure(figsize=(image_size*7.2,image_size*11.85), facecolor='black')
fig.subplots_adjust(0,0,1,1,0,0)

gs = matplotlib.gridspec.GridSpec(4, 2, wspace=0, hspace=0, width_ratios=[1,1], height_ratios=[720,180,180,105])

ax0 = plt.subplot(gs[0, :])
ax0.set_facecolor('black')
ax0.set_aspect('equal', anchor='N')
ax0.axis('off')

ax1 = plt.subplot(gs[1:3, 0])
ax1.set_facecolor('black')
ax1.set_aspect('equal', anchor='NE')
ax1.axis('off')

ax2 = plt.subplot(gs[1, 1])
ax2.set_facecolor('black')
ax2.set_aspect('equal', anchor='NW')
ax2.axis('off')

ax3 = plt.subplot(gs[2, 1])
ax3.set_facecolor('black')
ax3.set_aspect('equal', anchor='SW')
ax3.axis('off')

# ax4 = plt.subplot(gs[3, 0])
# ax4.set_facecolor('black')
# ax4.set_aspect('equal', anchor='NE')

ax5 = plt.subplot(gs[3, :])
ax5.set_facecolor('black')
ax5.set_aspect('equal', anchor='N')
ax5.axis('off')

# ax6 = plt.subplot(gs[5, 1])
# ax6.set_facecolor('black')
# #ax6.set_aspect('equal', anchor='NW')
    
matplotlib.rcParams['savefig.facecolor'] = (0,0,0)
matplotlib.rcParams['axes.edgecolor'] = (1,1,0,0.75)

plot_scale          = 150

if platform == 'win32':
    DjV_S_6     = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/DEJAVUSANS.TTF', size=6)
    DjV_S_8     = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/DEJAVUSANS.TTF', size=8)
    DjV_S_9     = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/DEJAVUSANS.TTF', size=9)
    DjV_S_10    = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/DEJAVUSANS.TTF', size=10)
    DjV_S_12    = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/DEJAVUSANS.TTF', size=12)
    #emoji_20    = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/YUGOTHB.TTC', size=20)
    chara_chi   = font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/YUGOTHR.TTC')
    chara_chi_16= font_manager.FontProperties(fname = 'C:/WINDOWS/Fonts/YUGOTHR.TTC', size=16)
elif platform == 'darwin':
    DjV_S_6     = font_manager.FontProperties(fname = '/Library/Fonts/DEJAVUSANS.TTF', size=6)
    DjV_S_8     = font_manager.FontProperties(fname = '/Library/Fonts/DEJAVUSANS.TTF', size=8)
    DjV_S_9     = font_manager.FontProperties(fname = '/Library/Fonts/DEJAVUSANS.TTF', size=9)
    DjV_S_10    = font_manager.FontProperties(fname = '/Library/Fonts/DEJAVUSANS.TTF', size=10)
    DjV_S_12    = font_manager.FontProperties(fname = '/Library/Fonts/DEJAVUSANS.TTF', size=12)
    #emoji_20    = font_manager.FontProperties(fname = '/Library/Fonts/YUGOTHB.TTC', size=20)
    chara_chi   = font_manager.FontProperties(fname = '/Library/Fonts/SIMHEI.TTF')
    chara_chi_16= font_manager.FontProperties(fname = '/Library/Fonts/SIMHEI.TTF', size=16)
elif platform == 'linux':
    DjV_S_6     = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/DejaVu Sans/DejaVu_Sans_Book.ttf', size=6)
    DjV_S_8     = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/DejaVu Sans/DejaVu_Sans_Book.ttf', size=8)
    DjV_S_9     = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/DejaVu Sans/DejaVu_Sans_Book.ttf', size=9)
    DjV_S_10    = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/DejaVu Sans/DejaVu_Sans_Book.ttf', size=10)
    DjV_S_12    = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/DejaVu Sans/DejaVu_Sans_Book.ttf', size=12)
    #emoji_20    = font_manager.FontProperties(fname = '/usr/local/share/fonts/YuGothB.ttc', size=20)
    chara_chi   = font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/Yu Gothic/Yu_Gothic_Bold.ttc')
    chara_chi_16= font_manager.FontProperties(fname = '/home/pi/.local/share/fonts/Unknown Vendor/TrueType/Yu Gothic/Yu_Gothic_Bold.ttc', size=16)
# raw data
horizon     = pandas.DataFrame(0,index=range(360),columns=['RA','Dec','x','y']).apply(pandas.to_numeric)
twlight     = pandas.DataFrame(0,index=range(360),columns=['RA','Dec','x','y']).apply(pandas.to_numeric)
equator     = pandas.DataFrame(0,index=range(360),columns=['RA','Dec','x','y']).apply(pandas.to_numeric)
ecliptic    = pandas.DataFrame(0,index=range(360),columns=['RA','Dec','x','y']).apply(pandas.to_numeric)

# log
def timelog(log):
    print(str(datetime.now().time().replace(microsecond=0))+'> '+log)
    
# make relative path (pathlib.Path.cwd() <=> current Dir)
timelog('importing star catalogue')
And = numpy.zeros(shape=(178,5))
And = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','And.csv'))
Ant = numpy.zeros(shape=(48,5))
Ant = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ant.csv'))
Aps = numpy.zeros(shape=(36,5))
Aps = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Aps.csv'))
Aqr = numpy.zeros(shape=(171,5))
Aqr = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Aqr.csv'))
Aql = numpy.zeros(shape=(131,5))
Aql = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Aql.csv'))
Ara = numpy.zeros(shape=(64,5))
Ara = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ara.csv'))
Ari = numpy.zeros(shape=(86,5))
Ari = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ari.csv'))
Aur = numpy.zeros(shape=(161,5))
Aur = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Aur.csv'))
Boo = numpy.zeros(shape=(154,5))
Boo = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Boo.csv'))
Cae = numpy.zeros(shape=(21,5))
Cae = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cae.csv'))
Cam = numpy.zeros(shape=(158,5))
Cam = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cam.csv'))
Cnc = numpy.zeros(shape=(112,5))
Cnc = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cnc.csv'))
CVn = numpy.zeros(shape=(61,5))
CVn = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CVn.csv'))
CMa = numpy.zeros(shape=(155,5))
CMa = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CMa.csv'))
CMi = numpy.zeros(shape=(44,5))
CMi = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CMi.csv'))
Cap = numpy.zeros(shape=(87,5))
Cap = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cap.csv'))
Car = numpy.zeros(shape=(210,5))
Car = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Car.csv'))
Cas = numpy.zeros(shape=(164,5))
Cas = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cas.csv'))
Cen = numpy.zeros(shape=(281,5))
Cen = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cen.csv'))
Cep = numpy.zeros(shape=(157,5))
Cep = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cep.csv'))
Cet = numpy.zeros(shape=(177,5))
Cet = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cet.csv'))
Cha = numpy.zeros(shape=(34,5))
Cha = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cha.csv'))
Cir = numpy.zeros(shape=(34,5))
Cir = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cir.csv'))
Col = numpy.zeros(shape=(78,5))
Col = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Col.csv'))
Com = numpy.zeros(shape=(71,5))
Com = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Com.csv'))
CrA = numpy.zeros(shape=(46,5))
CrA = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CrA.csv'))
CrB = numpy.zeros(shape=(40,5))
CrB = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CrB.csv'))
Crv = numpy.zeros(shape=(28,5))
Crv = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Crv.csv'))
Crt = numpy.zeros(shape=(33,5))
Crt = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Crt.csv'))
Cru = numpy.zeros(shape=(48,5))
Cru = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cru.csv'))
Cyg = numpy.zeros(shape=(291,5))
Cyg = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Cyg.csv'))
Del = numpy.zeros(shape=(47,5))
Del = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Del.csv'))
Dor = numpy.zeros(shape=(34,5))
Dor = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Dor.csv'))
Dra = numpy.zeros(shape=(226,5))
Dra = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Dra.csv'))
Equ = numpy.zeros(shape=(15,5))
Equ = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Equ.csv'))
Eri = numpy.zeros(shape=(197,5))
Eri = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Eri.csv'))
For = numpy.zeros(shape=(64,5))
For = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','For.csv'))
Gem = numpy.zeros(shape=(123,5))
Gem = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Gem.csv'))
Gru = numpy.zeros(shape=(62,5))
Gru = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Gru.csv'))
Her = numpy.zeros(shape=(263,5))
Her = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Her.csv'))
Hor = numpy.zeros(shape=(36,5))
Hor = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Hor.csv'))
Hya = numpy.zeros(shape=(246,5))
Hya = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Hya.csv'))
Hyi = numpy.zeros(shape=(33,5))
Hyi = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Hyi.csv'))
Ind = numpy.zeros(shape=(39,5))
Ind = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ind.csv'))
Lac = numpy.zeros(shape=(67,5))
Lac = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lac.csv'))
Leo = numpy.zeros(shape=(130,5))
Leo = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Leo.csv'))
LMi = numpy.zeros(shape=(36,5))
LMi = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','LMi.csv'))
Lep = numpy.zeros(shape=(76,5))
Lep = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lep.csv'))
Lib = numpy.zeros(shape=(86,5))
Lib = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lib.csv'))
Lup = numpy.zeros(shape=(117,5))
Lup = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lup.csv'))
Lyn = numpy.zeros(shape=(100,5))
Lyn = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lyn.csv'))
Lyr = numpy.zeros(shape=(83,5))
Lyr = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Lyr.csv'))
Men = numpy.zeros(shape=(26,5))
Men = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Men.csv'))
Mic = numpy.zeros(shape=(39,5))
Mic = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Mic.csv'))
Mon = numpy.zeros(shape=(153,5))
Mon = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Mon.csv'))
Mus = numpy.zeros(shape=(59,5))
Mus = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Mus.csv'))
Nor = numpy.zeros(shape=(41,5))
Nor = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Nor.csv'))
Oct = numpy.zeros(shape=(67,5))
Oct = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Oct.csv'))
Oph = numpy.zeros(shape=(179,5))
Oph = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Oph.csv'))
Ori = numpy.zeros(shape=(225,5))
Ori = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ori.csv'))
Pav = numpy.zeros(shape=(82,5))
Pav = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Pav.csv'))
Peg = numpy.zeros(shape=(176,5))
Peg = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Peg.csv'))
Per = numpy.zeros(shape=(160,5))
Per = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Per.csv'))
Phe = numpy.zeros(shape=(70,5))
Phe = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Phe.csv'))
Pic = numpy.zeros(shape=(50,5))
Pic = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Pic.csv'))
Psc = numpy.zeros(shape=(141,5))
Psc = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Psc.csv'))
PsA = numpy.zeros(shape=(49,5))
PsA = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','PsA.csv'))
Pup = numpy.zeros(shape=(275,5))
Pup = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Pup.csv'))
Pyx = numpy.zeros(shape=(48,5))
Pyx = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Pyx.csv'))
Ret = numpy.zeros(shape=(24,5))
Ret = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ret.csv'))
Sge = numpy.zeros(shape=(31,5))
Sge = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Sge.csv'))
Sgr = numpy.zeros(shape=(219,5))
Sgr = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Sgr.csv'))
Sco = numpy.zeros(shape=(174,5))
Sco = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Sco.csv'))
Scl = numpy.zeros(shape=(59,5))
Scl = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Scl.csv'))
Sct = numpy.zeros(shape=(30,5))
Sct = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Sct.csv'))
Ser = numpy.zeros(shape=(112,5))
Ser = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Ser.csv'))
Sex = numpy.zeros(shape=(40,5))
Sex = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Sex.csv'))
Tau = numpy.zeros(shape=(223,5))
Tau = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Tau.csv'))
Tel = numpy.zeros(shape=(51,5))
Tel = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Tel.csv'))
Tri = numpy.zeros(shape=(26,5))
Tri = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Tri.csv'))
TrA = numpy.zeros(shape=(35,5))
TrA = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','TrA.csv'))
Tuc = numpy.zeros(shape=(50,5))
Tuc = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Tuc.csv'))
UMa = numpy.zeros(shape=(224,5))
UMa = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','UMa.csv'))
UMi = numpy.zeros(shape=(42,5))
UMi = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','UMi.csv'))
Vel = numpy.zeros(shape=(193,5))
Vel = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Vel.csv'))
Vir = numpy.zeros(shape=(174,5))
Vir = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Vir.csv'))
Vol = numpy.zeros(shape=(33,5))
Vol = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Vol.csv'))
Vul = numpy.zeros(shape=(77,5))
Vul = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','Vul.csv'))
# LROC WAC basemap Shapefile
Mare    = numpy.zeros(shape=(267482,5)) 
Mare    = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','moon_mare.csv'))
Crater  = numpy.zeros(shape=(182111,5))
Crater  = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','moon_crater.csv'))
# milkyway
MW_southernedge = numpy.zeros(shape=(263,4))
MW_southernedge = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_southernedge.csv'))
MW_MonPer       = numpy.zeros(shape=(71,4))
MW_MonPer       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_MonPer.csv'))
MW_CamCas       = numpy.zeros(shape=(13,4))
MW_CamCas       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_CamCas.csv'))
MW_Cep          = numpy.zeros(shape=(13,4))
MW_Cep          = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_Cep.csv'))
MW_CygOph       = numpy.zeros(shape=(40,4))
MW_CygOph       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_CygOph.csv'))
MW_OphSco       = numpy.zeros(shape=(17,4))
MW_OphSco       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_OphSco.csv'))
MW_LupVel       = numpy.zeros(shape=(78,4))
MW_LupVel       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_LupVel.csv'))
MW_VelMon       = numpy.zeros(shape=(34,4))
MW_VelMon       = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_VelMon.csv'))
dark_PerCas     = numpy.zeros(shape=(35,4))
dark_PerCas     = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_PerCas.csv'))
dark_CasCep     = numpy.zeros(shape=(28,4))
dark_CasCep     = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_CasCep.csv'))
dark_betaCas    = numpy.zeros(shape=(20,4))
dark_betaCas    = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_betaCas.csv'))
dark_CygCep     = numpy.zeros(shape=(22,4))
dark_CygCep     = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_CygCep.csv'))
dark_CygOph     = numpy.zeros(shape=(197,4))
dark_CygOph     = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_CygOph.csv'))
dark_thetaOph   = numpy.zeros(shape=(28,4))
dark_thetaOph   = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_thetaOph.csv'))
dark_lambdaSco  = numpy.zeros(shape=(17,4))
dark_lambdaSco  = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_lambdaSco.csv'))
dark_ScoNor     = numpy.zeros(shape=(31,4))
dark_ScoNor     = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_ScoNor.csv'))
dark_Coalsack   = numpy.zeros(shape=(32,4))
dark_Coalsack   = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_Coalsack.csv'))
dark_Vel        = numpy.zeros(shape=(22,4))
dark_Vel        = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','dark_Vel.csv'))
MW_LMC1         = numpy.zeros(shape=(34,4))
MW_LMC1         = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_LMC1.csv'))
MW_LMC2         = numpy.zeros(shape=(12,4))
MW_LMC2         = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_LMC2.csv'))
MW_SMC          = numpy.zeros(shape=(14,4))
MW_SMC          = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','MW_SMC.csv'))
# constellation boundaries
boundary        = numpy.zeros(shape=(13238,5))
boundary        = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','boundary.csv'))

if debug_mode == 1:
    timelog('ref count And: '+str(sys.getrefcount(And)))
    timelog('ref count Mare: '+str(sys.getrefcount(Mare)))
    timelog('ref count MW_southernedge: '+str(sys.getrefcount(MW_southernedge)))
    timelog('ref count boundary: '+str(sys.getrefcount(boundary)))
    
####################
# define functions #
####################

def plot_solar():
    global plot_alpha, hori_border, hori_xmax, hori_xmin, hori_ymax, hori_ymin, horizon_line, equator_line, ecliptic_line, twlight_line,\
           Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune,\
           solar_obj,solar_color,moon_chi,\
           Sun_x,Moon_x,Mercury_x,Venus_x,Mars_x,Jupiter_x,Saturn_x,Uranus_x,Neptune_x,\
           Sun_y,Moon_y,Mercury_y,Venus_y,Mars_y,Jupiter_y,Saturn_y,Uranus_y,Neptune_y,\
           sun_vector,mercury_vector,venus_vector,moon_vector,mars_vector,jupiter_vector,\
           saturn_vector,uranus_vector,neptune_vector,pluto_vector

    sun_vector      = Obs[0].at(date_UTC).observe(sun).apparent()
    mercury_vector  = Obs[0].at(date_UTC).observe(mercury).apparent()
    venus_vector    = Obs[0].at(date_UTC).observe(venus).apparent()
    moon_vector     = Obs[0].at(date_UTC).observe(moon).apparent()
    mars_vector     = Obs[0].at(date_UTC).observe(mars).apparent()
    jupiter_vector  = Obs[0].at(date_UTC).observe(jupiter).apparent()
    saturn_vector   = Obs[0].at(date_UTC).observe(saturn).apparent()
    uranus_vector   = Obs[0].at(date_UTC).observe(uranus).apparent()
    neptune_vector  = Obs[0].at(date_UTC).observe(neptune).apparent()
    pluto_vector    = Obs[0].at(date_UTC).observe(pluto).apparent()
    
    # position angle of the Moon's bright limb from North point of the disc of the Moon to East
    moon_chi = math.degrees(math.atan2(math.cos(sun_vector.radec()[1].radians)*math.sin(sun_vector.radec()[0].radians-moon_vector.radec()[0].radians),\
                                       math.sin(sun_vector.radec()[1].radians)*math.cos(moon_vector.radec()[1].radians)-\
                                       math.cos(sun_vector.radec()[1].radians)*math.sin(moon_vector.radec()[1].radians)*math.cos(sun_vector.radec()[0].radians-moon_vector.radec()[0].radians)))
   
    if moon_chi < 0:
        moon_chi = moon_chi+360
 
    timelog('drawing grids')

    # alpha
    plot_alpha = 0.3
        
    # horizon
    horizon_pt = []
    for i in range(361):
        hori_ra = Obs[0].at(date_UTC).from_altaz(alt_degrees=0, az_degrees=i).radec()[0].hours*15
        hori_dec= Obs[0].at(date_UTC).from_altaz(alt_degrees=0, az_degrees=i).radec()[1].degrees
        
        horizon_pt.append((transform_x(hori_ra,hori_dec),transform_y(hori_ra,hori_dec)))
        
    horizon_line = plt.Polygon(horizon_pt, closed=True, fill=None, edgecolor=(0,0,1,1), zorder=1+2.5)
    ax0.add_patch(horizon_line)

    # horizon size
    hori_xmax = max(horizon_pt,key=itemgetter(0))[0]
    hori_xmin = min(horizon_pt,key=itemgetter(0))[0]
    hori_ymax = max(horizon_pt,key=itemgetter(1))[1]
    hori_ymin = min(horizon_pt,key=itemgetter(1))[1]
    hori_border = hori_xmax-hori_xmin

    
    ax0.annotate('z',((hori_xmax+hori_xmin)/2+2.5,(hori_ymax+hori_ymin)/2+1),color='g')
    z_m = matplotlib.markers.MarkerStyle(marker='+')
    z_m._transform = z_m.get_transform()
    ax0.scatter((hori_xmax+hori_xmin)/2,(hori_ymax+hori_ymin)/2,c='g',marker=z_m,zorder=0+2.6)

    g_step=250
    patches = []
    for i in range(g_step):
        circle = plt.Circle((0, 0), (hori_xmax-hori_xmin)/2*(1-0.5/g_step*i), color=(0,0.05*(1-1/g_step*i),0.15*(1-1/g_step*i)), zorder=0+2.5)
        ax0.add_patch(circle)

    # twlight
    for i in range(360):
        twlight.loc[i] = [ra0-math.degrees(math.atan2(math.sin(math.radians(i)),(math.cos(math.radians(i))*math.sin(math.radians(dec0))+math.tan(math.radians(-18))*math.cos(math.radians(dec0))))),\
                          math.degrees(math.asin(math.sin(math.radians(dec0))*math.sin(math.radians(-18))-math.cos(math.radians(dec0))*math.cos(math.radians(-18))*math.cos(math.radians(i)))),0,0]

    twlight.x = list(map(transform_x, twlight.RA, twlight.Dec))
    twlight.y = list(map(transform_y, twlight.RA, twlight.Dec))
    
    twlight_pt = []
    for i in range(len(twlight)-1):
        twlight_pt.append([twlight['x'].tolist()[i],twlight['y'].tolist()[i]])

    twlight_line = plt.Polygon(twlight_pt, closed=True, fill=None, edgecolor=(0,1,0,0.75), linestyle='--', zorder=0+2.5)
    ax0.add_patch(twlight_line)

    ax0.annotate('\u2212'+'18'+'\u00b0',((max(twlight.x)-min(twlight.y))/2*math.cos(math.radians(45)),(min(twlight.y)-max(twlight.x))/2*math.sin(math.radians(45))),rotation=45,ha='center',va='center',color='c', backgroundcolor= 'black', zorder=1+2.5)
    
    # equator  
    equator_pt = []
    for i in range(361):
        equator_pt.append((transform_x(i,0),transform_y(i,0)))
    
    equator_line = plt.Polygon(equator_pt, closed=False, fill=None, edgecolor=(1,0,0,plot_alpha), zorder=1+2.5)
    equator_line.set_clip_path(horizon_line)
    ax0.add_patch(equator_line)

    # ecliptic
    epsilon_J2000 = 23.4392911
    for i in range(360):
        ecliptic.loc[i] = [math.degrees(math.atan2(math.sin(math.radians(i))*math.cos(math.radians(epsilon_J2000)),math.cos(math.radians(i)))),\
                           math.degrees(math.asin(math.sin(math.radians(epsilon_J2000))*math.sin(math.radians(i)))),0,0]

    ecliptic.x = list(map(transform_x, ecliptic.RA, ecliptic.Dec))
    ecliptic.y = list(map(transform_y, ecliptic.RA, ecliptic.Dec))

    ecliptic_pt = []
    for i in range(len(ecliptic)-1):
        ecliptic_pt.append([ecliptic['x'].tolist()[i],ecliptic['y'].tolist()[i]])
            
    ecliptic_line = plt.Polygon(ecliptic_pt, closed=False, fill=None, edgecolor=(1,1,0,plot_alpha), zorder=1+2.5)
    ecliptic_line.set_clip_path(horizon_line)
    ax0.add_patch(ecliptic_line)   
    
    timelog('plotting solar system objects')
           
    Sun_x       = transform_x(sun_vector.radec()[0]._degrees,sun_vector.radec()[1]._degrees)
    Sun_y       = transform_y(sun_vector.radec()[0]._degrees,sun_vector.radec()[1]._degrees)
    Moon_x      = transform_x(moon_vector.radec()[0]._degrees,moon_vector.radec()[1]._degrees)
    Moon_y      = transform_y(moon_vector.radec()[0]._degrees,moon_vector.radec()[1]._degrees)
    Mercury_x   = transform_x(mercury_vector.radec()[0]._degrees,mercury_vector.radec()[1]._degrees)
    Mercury_y   = transform_y(mercury_vector.radec()[0]._degrees,mercury_vector.radec()[1]._degrees)
    Venus_x     = transform_x(venus_vector.radec()[0]._degrees,venus_vector.radec()[1]._degrees)
    Venus_y     = transform_y(venus_vector.radec()[0]._degrees,venus_vector.radec()[1]._degrees)
    Mars_x      = transform_x(mars_vector.radec()[0]._degrees,mars_vector.radec()[1]._degrees)
    Mars_y      = transform_y(mars_vector.radec()[0]._degrees,mars_vector.radec()[1]._degrees)
    Jupiter_x   = transform_x(jupiter_vector.radec()[0]._degrees,jupiter_vector.radec()[1]._degrees)
    Jupiter_y   = transform_y(jupiter_vector.radec()[0]._degrees,jupiter_vector.radec()[1]._degrees)
    Saturn_x    = transform_x(saturn_vector.radec()[0]._degrees,saturn_vector.radec()[1]._degrees)
    Saturn_y    = transform_y(saturn_vector.radec()[0]._degrees,saturn_vector.radec()[1]._degrees)
    Uranus_x    = transform_x(uranus_vector.radec()[0]._degrees,uranus_vector.radec()[1]._degrees)
    Uranus_y    = transform_y(uranus_vector.radec()[0]._degrees,uranus_vector.radec()[1]._degrees)
    Neptune_x   = transform_x(neptune_vector.radec()[0]._degrees,neptune_vector.radec()[1]._degrees)
    Neptune_y   = transform_y(neptune_vector.radec()[0]._degrees,neptune_vector.radec()[1]._degrees)

    solar_pos_x = [Sun_x,Moon_x,Mercury_x,Venus_x,Mars_x,Jupiter_x,Saturn_x,Uranus_x,Neptune_x]
    solar_pos_y = [Sun_y,Moon_y,Mercury_y,Venus_y,Mars_y,Jupiter_y,Saturn_y,Uranus_y,Neptune_y]
    solar_color = ['#FFCC33','#DAD9D7','#97979F','#C18F17','#E27B58','#C88B3A','#A49B72','#D5FBFC','#3E66F9']
    
    solar_obj = ax0.scatter(solar_pos_x,solar_pos_y,alpha=plot_alpha+0.25,color=solar_color,zorder=4+2.5)
    solar_leg = ax0.scatter([-160,-120,-80,-40,0,40,80,120,160],[min(twlight.y)-10]*9,alpha=plot_alpha+0.25,color=solar_color,zorder=4+2.5)
    
    ax0.annotate('$\u263C$',(Sun_x+2.5,Sun_y+1),color=solar_color[0])
    ax0.annotate('$\u263C$',(-160,min(twlight.y)-15),color=solar_color[0],ha='center',va='top')
    ax0.annotate('SUN',(-160,min(twlight.y)-25),color=solar_color[0],ha='center',va='top')
    if moon_chi>180:
        ax0.annotate('$\u263D$',(Moon_x+2.5,Moon_y+1),color=solar_color[1])
        ax0.annotate('$\u263D$',(-120,min(twlight.y)-15),color=solar_color[1],ha='center',va='top')
        ax0.annotate('MOON',(-120,min(twlight.y)-25),color=solar_color[1],ha='center',va='top')
    else:
        ax0.annotate('$\u263E$',(Moon_x+2.5,Moon_y+1),color=solar_color[1])
        ax0.annotate('$\u263E$',(-120,min(twlight.y)-15),color=solar_color[1],ha='center',va='top')
        ax0.annotate('MOON',(-120,min(twlight.y)-25),color=solar_color[1],ha='center',va='top')
    ax0.annotate('$\u263F$',(Mercury_x+2.5,Mercury_y+1),color=solar_color[2])
    ax0.annotate('$\u263F$',(-80,min(twlight.y)-15),color=solar_color[2],ha='center',va='top')
    ax0.annotate('MERCURY',(-80,min(twlight.y)-25),color=solar_color[2],ha='center',va='top')
    ax0.annotate('$\u2640$',(Venus_x+2.5,Venus_y+1),color=solar_color[3])
    ax0.annotate('$\u2640$',(-40,min(twlight.y)-15),color=solar_color[3],ha='center',va='top')
    ax0.annotate('VENUS',(-40,min(twlight.y)-25),color=solar_color[3],ha='center',va='top')
    ax0.annotate('$\u2642$',(Mars_x+2.5,Mars_y+1),color=solar_color[4])
    ax0.annotate('$\u2642$',(0,min(twlight.y)-15),color=solar_color[4],ha='center',va='top')
    ax0.annotate('MARS',(0,min(twlight.y)-25),color=solar_color[4],ha='center',va='top')
    ax0.annotate('$\u2643$',(Jupiter_x+2.5,Jupiter_y+1),color=solar_color[5])
    ax0.annotate('$\u2643$',(40,min(twlight.y)-15),color=solar_color[5],ha='center',va='top')
    ax0.annotate('JUPITER',(40,min(twlight.y)-25),color=solar_color[5],ha='center',va='top')
    ax0.annotate('$\u2644$',(Saturn_x+2.5,Saturn_y+1),color=solar_color[6])
    ax0.annotate('$\u2644$',(80,min(twlight.y)-15),color=solar_color[6],ha='center',va='top')
    ax0.annotate('SATURN',(80,min(twlight.y)-25),color=solar_color[6],ha='center',va='top')
    ax0.annotate('$\u2645$',(Uranus_x+2.5,Uranus_y+1),color=solar_color[7])
    ax0.annotate('$\u2645$',(120,min(twlight.y)-15),color=solar_color[7],ha='center',va='top')
    ax0.annotate('URANUS',(120,min(twlight.y)-25),color=solar_color[7],ha='center',va='top')
    ax0.annotate('$\u2646$',(Neptune_x+2.5,Neptune_y+1),color=solar_color[8])
    ax0.annotate('$\u2646$',(160,min(twlight.y)-15),color=solar_color[8],ha='center',va='top')
    ax0.annotate('NEPTUNE',(160,min(twlight.y)-25),color=solar_color[8],ha='center',va='top')

    if debug_mode == 1:
        timelog('ref count horizon_line: '+str(sys.getrefcount(horizon_line)))
        timelog('ref count equator_line: '+str(sys.getrefcount(equator_line)))
        timelog('ref count ecliptic_pt: '+str(sys.getrefcount(ecliptic_pt)))
        timelog('ref count ecliptic_line: '+str(sys.getrefcount(ecliptic_line)))
        timelog('ref count Sun_x: '+str(sys.getrefcount(Sun_x)))
        timelog('ref count Sun_y: '+str(sys.getrefcount(Sun_y)))
        timelog('ref count solar_pos_x: '+str(sys.getrefcount(solar_pos_x)))
        timelog('ref count solar_pos_y: '+str(sys.getrefcount(solar_pos_y)))
        timelog('ref count solar_color: '+str(sys.getrefcount(solar_color)))
        timelog('ref count solar_obj: '+str(sys.getrefcount(solar_obj)))

def plot_constellation():
    global constellation_list, lc_west, lc_west_z, lc_west_dotted, labelxy
    
    timelog('drawing constellations')
    
    constellation_list = [And,Ant,Aps,Aqr,Aql,Ara,Ari,Aur,Boo,Cae,Cam,Cnc,CVn,CMa,CMi,Cap,Car,Cas,Cen,Cep,\
                          Cet,Cha,Cir,Col,Com,CrA,CrB,Crv,Crt,Cru,Cyg,Del,Dor,Dra,Equ,Eri,For,Gem,Gru,Her,\
                          Hor,Hya,Hyi,Ind,Lac,Leo,LMi,Lep,Lib,Lup,Lyn,Lyr,Men,Mic,Mon,Mus,Nor,Oct,Oph,Ori,\
                          Pav,Peg,Per,Phe,Pic,Psc,PsA,Pup,Pyx,Ret,Sge,Sgr,Sco,Scl,Sct,Ser,Sex,Tau,Tel,Tri,\
                          TrA,Tuc,UMa,UMi,Vel,Vir,Vol,Vul]
    
    for df in constellation_list:
        df.x = list(map(transform_x, df.RA, df.Dec))
        df.y = list(map(transform_y, df.RA, df.Dec))

    labelxy = 2
    

    constellation_star = [[And.x,And.y,And.mag],[Ant.x,Ant.y,Ant.mag],[Aps.x,Aps.y,Aps.mag],[Aqr.x,Aqr.y,Aqr.mag],\
                          [Aql.x,Aql.y,Aql.mag],[Ara.x,Ara.y,Ara.mag],[Ari.x,Ari.y,Ari.mag],[Aur.x,Aur.y,Aur.mag],\
                          [Boo.x,Boo.y,Boo.mag],[Cae.x,Cae.y,Cae.mag],[Cam.x,Cam.y,Cam.mag],[Cnc.x,Cnc.y,Cnc.mag],\
                          [CVn.x,CVn.y,CVn.mag],[CMa.x,CMa.y,CMa.mag],[CMi.x,CMi.y,CMi.mag],[Cap.x,Cap.y,Cap.mag],\
                          [Car.x,Car.y,Car.mag],[Cas.x,Cas.y,Cas.mag],[Cen.x,Cen.y,Cen.mag],[Cep.x,Cep.y,Cep.mag],\
                          [Cet.x,Cet.y,Cet.mag],[Cha.x,Cha.y,Cha.mag],[Cir.x,Cir.y,Cir.mag],[Col.x,Col.y,Col.mag],\
                          [Com.x,Com.y,Com.mag],[CrA.x,CrA.y,CrA.mag],[CrB.x,CrB.y,CrB.mag],[Crv.x,Crv.y,Crv.mag],\
                          [Crt.x,Crt.y,Crt.mag],[Cru.x,Cru.y,Cru.mag],[Cyg.x,Cyg.y,Cyg.mag],[Del.x,Del.y,Del.mag],\
                          [Dor.x,Dor.y,Dor.mag],[Dra.x,Dra.y,Dra.mag],[Equ.x,Equ.y,Equ.mag],[Eri.x,Eri.y,Eri.mag],\
                          [For.x,For.y,For.mag],[Gem.x,Gem.y,Gem.mag],[Gru.x,Gru.y,Gru.mag],[Her.x,Her.y,Her.mag],\
                          [Hor.x,Hor.y,Hor.mag],[Hya.x,Hya.y,Hya.mag],[Hyi.x,Hyi.y,Hyi.mag],[Ind.x,Ind.y,Ind.mag],\
                          [Lac.x,Lac.y,Lac.mag],[Leo.x,Leo.y,Leo.mag],[LMi.x,LMi.y,LMi.mag],[Lep.x,Lep.y,Lep.mag],\
                          [Lib.x,Lib.y,Lib.mag],[Lup.x,Lup.y,Lup.mag],[Lyn.x,Lyn.y,Lyn.mag],[Lyr.x,Lyr.y,Lyr.mag],\
                          [Men.x,Men.y,Men.mag],[Mic.x,Mic.y,Mic.mag],[Mon.x,Mon.y,Mon.mag],[Mus.x,Mus.y,Mus.mag],\
                          [Nor.x,Nor.y,Nor.mag],[Oct.x,Oct.y,Oct.mag],[Oph.x,Oph.y,Oph.mag],[Ori.x,Ori.y,Ori.mag],\
                          [Pav.x,Pav.y,Pav.mag],[Peg.x,Peg.y,Peg.mag],[Per.x,Per.y,Per.mag],[Phe.x,Phe.y,Phe.mag],\
                          [Pic.x,Pic.y,Pic.mag],[Psc.x,Psc.y,Psc.mag],[PsA.x,PsA.y,PsA.mag],[Pup.x,Pup.y,Pup.mag],\
                          [Pyx.x,Pyx.y,Pyx.mag],[Ret.x,Ret.y,Ret.mag],[Sge.x,Sge.y,Sge.mag],[Sgr.x,Sgr.y,Sgr.mag],\
                          [Sco.x,Sco.y,Sco.mag],[Scl.x,Scl.y,Scl.mag],[Sct.x,Sct.y,Sct.mag],[Ser.x,Ser.y,Ser.mag],\
                          [Sex.x,Sex.y,Sex.mag],[Tau.x,Tau.y,Tau.mag],[Tel.x,Tel.y,Tel.mag],[Tri.x,Tri.y,Tri.mag],\
                          [TrA.x,TrA.y,TrA.mag],[Tuc.x,Tuc.y,Tuc.mag],[UMa.x,UMa.y,UMa.mag],[UMi.x,UMi.y,UMi.mag],\
                          [Vel.x,Vel.y,Vel.mag],[Vir.x,Vir.y,Vir.mag],[Vol.x,Vol.y,Vol.mag],[Vul.x,Vul.y,Vul.mag]]


    stars_x = []
    stars_y = []
    stars_m = []
    
    for x,y,z in constellation_star:
        for j in range(len(x)):
            if x[j]**2 < (hori_border/2)**2-(y[j])**2 and z[j] <= 6: #limiting mag
                stars_x.append(x[j])
                stars_y.append(y[j])
                stars_m.append(5*(10**(-0.4*z[j]))**0.5)
                
    ax0.scatter(stars_x,stars_y, stars_m, c='white', alpha=plot_alpha, zorder=3+2.5)

    # mag scale
    shift_mag = 0
    for i in range(7):
        ax0.scatter(hori_xmin+shift_mag+i*10+5,hori_ymin+20, 5*(10**(-0.4*i))**0.5, c='white',alpha=plot_alpha,zorder=14+2.5)
        ax0.scatter(hori_xmin+shift_mag+i*10+5,hori_ymin+20, 5*(10**(-0.4*i))**0.5+20, c='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5,hori_ymin+2),ha='center',va='bottom',color='w',zorder=14+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5-1,hori_ymin+2+1),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5,hori_ymin+2+1),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5+1,hori_ymin+2+1),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5-1,hori_ymin+2),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5+1,hori_ymin+2),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5-1,hori_ymin+2-1),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5,hori_ymin+2-1),ha='center',va='bottom',color='k',zorder=13+2.5)
        ax0.annotate(str(i),(hori_xmin+shift_mag+i*10+5+1,hori_ymin+2-1),ha='center',va='bottom',color='k',zorder=13+2.5)

    olw = 1 #text outline width
    
    ########
    #紫微垣#
    ########
    #北極#
    C_A01 = [[UMi.x[1],UMi.x[2]],[UMi.y[1],UMi.y[2]],[UMi.x[1],UMi.x[4]],[UMi.y[1],UMi.y[4]],\
             [UMi.x[4],UMi.x[8]],[UMi.y[4],UMi.y[8]],[UMi.x[8],Cam.x[29]],[UMi.y[8],Cam.y[29]]]
    CA01n = [numpy.mean([UMi.x[2],UMi.x[4],UMi.x[8],Cam.x[29]]),\
             numpy.mean([UMi.y[2],UMi.y[4],UMi.y[8],Cam.y[29]])]
    #四輔#
    C_A02 = [[Cam.x[26],Cam.x[43]],[Cam.y[26],Cam.y[43]]]
    CA02n = [numpy.mean([Cam.x[26],Cam.x[43]]),\
             numpy.mean([Cam.y[26],Cam.y[43]])-labelxy]
    #天乙#
    C_A03 = []
    CA03n = [Dra.x[19],Dra.y[19]-labelxy]
    #太乙#
    C_A04 = []
    CA04n = [Dra.x[101]+labelxy,Dra.y[101]-labelxy]
    #紫微左垣#
    C_A05 = [[Cas.x[44],Cep.x[14]],[Cas.y[44],Cep.y[14]],[Cep.x[14],Dra.x[50]],[Cep.y[14],Dra.y[50]],\
             [Dra.x[1],Dra.x[4]],[Dra.y[1],Dra.y[4]],[Dra.x[1],Dra.x[12]],[Dra.y[1],Dra.y[12]],\
             [Dra.x[4],Dra.x[25]],[Dra.y[4],Dra.y[25]],[Dra.x[5],Dra.x[12]],[Dra.y[5],Dra.y[12]],\
             [Dra.x[25],Dra.x[50]],[Dra.y[25],Dra.y[50]]]
    CA05n = [numpy.mean([Cep.x[14],Dra.x[50]]),\
             numpy.mean([Cep.y[14],Dra.y[50]])]
    #紫微右垣#
    C_A06 = [[Cam.x[2],Cam.x[10]],[Cam.y[2],Cam.y[10]],[Cam.x[2],Cam.x[20]],[Cam.y[2],Cam.y[20]],\
             [Cam.x[20],UMa.x[23]],[Cam.y[20],UMa.y[23]],[Dra.x[7],Dra.x[11]],[Dra.y[7],Dra.y[11]],\
             [Dra.x[10],Dra.x[11]],[Dra.y[10],Dra.y[11]],[Dra.x[10],UMa.x[23]],[Dra.y[10],UMa.y[23]]]
    CA06n = [numpy.mean([Cam.x[20],Dra.x[10],UMa.x[23]]),\
             numpy.mean([Cam.y[20],Dra.y[10],UMa.y[23]])]
    #陰德#
    C_A07 = []
    CA07n = [Dra.x[27],Dra.y[27]-labelxy]
    #尚書#
    C_A08= [[Dra.x[26],Dra.x[43]],[Dra.y[26],Dra.y[43]],[Dra.x[31],Dra.x[43]],[Dra.y[31],Dra.y[43]],\
             [Dra.x[38],Dra.x[43]],[Dra.y[38],Dra.y[43]]]
    CA08n = [numpy.mean([Dra.x[26],Dra.x[31],Dra.x[38],Dra.x[43]])+labelxy,\
             numpy.mean([Dra.y[26],Dra.y[31],Dra.y[38],Dra.y[43]])]
    #女史#
    C_A09 = []
    CA09n = [Dra.x[17],Dra.y[17]-labelxy]
    #柱史#
    C_A10 = []
    CA10n = [Dra.x[13],Dra.y[13]-labelxy]
    #御女#
    C_A11 = [[Dra.x[6],Dra.x[15]],[Dra.y[6],Dra.y[15]],[Dra.x[15],Dra.x[59]],[Dra.y[15],Dra.y[59]]]
    CA11n = [numpy.mean([Dra.x[6],Dra.x[15],Dra.x[59]])+labelxy,\
             numpy.mean([Dra.y[6],Dra.y[15],Dra.y[59]])]
    #天柱#
    C_A12 = [[Cep.x[84],Dra.x[92]],[Cep.y[84],Dra.y[92]],[Cep.x[84],Dra.x[146]],[Cep.y[84],Dra.y[146]],\
             [Dra.x[47],Dra.x[126]],[Dra.y[47],Dra.y[126]],[Dra.x[47],Dra.x[146]],[Dra.y[47],Dra.y[146]]]
    CA12n = [numpy.mean([Cep.x[84],Dra.x[47],Dra.x[126],Dra.x[146]]),\
             numpy.mean([Cep.y[84],Dra.y[47],Dra.y[126],Dra.y[146]])]
    #大理#
    C_A13 = []
    CA13n = [Cam.x[22],Cam.y[22]-labelxy]
    #勾陳#
    C_A14 = [[Cep.x[10],Cep.x[17]],[Cep.y[10],Cep.y[17]],[Cep.x[10],UMi.x[0]],[Cep.y[10],UMi.y[0]],\
             [UMi.x[0],UMi.x[6]],[UMi.y[0],UMi.y[6]],[UMi.x[3],UMi.x[5]],[UMi.y[3],UMi.y[5]],\
             [UMi.x[3],UMi.x[6]],[UMi.y[3],UMi.y[6]]]
    CA14n = [numpy.mean([Cep.x[10],Cep.x[17],UMi.x[0],UMi.x[3],UMi.x[5],UMi.x[6]]),\
             numpy.mean([Cep.y[10],Cep.y[17],UMi.y[0],UMi.y[3],UMi.y[5],UMi.y[6]])-labelxy]
    #六甲#
    C_A15 = [[Cam.x[6],Cam.x[42]],[Cam.y[6],Cam.y[42]],[Cam.x[11],Cam.x[42]],[Cam.y[11],Cam.y[42]],\
             [Cam.x[11],Cep.x[26]],[Cam.y[11],Cep.y[26]],[Cam.x[15],Cep.x[26]],[Cam.y[15],Cep.y[26]]]
    CA15n = [numpy.mean([Cam.x[6],Cam.x[11],Cam.x[15],Cam.x[42],Cep.x[26]]),\
             numpy.mean([Cam.y[6],Cam.y[11],Cam.y[15],Cam.y[42],Cep.y[26]])+labelxy]
    #天皇大帝#
    C_A16 = []
    CA16n = [Cep.x[37],Cep.y[37]-labelxy]
    #五帝內座#
    C_A17 = [[Cas.x[41],Cep.x[46]],[Cas.y[41],Cep.y[46]],[Cep.x[29],Cep.x[46]],[Cep.y[29],Cep.y[46]],\
             [Cep.x[42],Cep.x[46]],[Cep.y[42],Cep.y[46]],[Cep.x[46],Cep.x[69]],[Cep.y[46],Cep.y[69]]]
    CA17n = [numpy.mean([Cas.x[41],Cep.x[29],Cep.x[42],Cep.x[46],Cep.x[69]]),\
             numpy.mean([Cas.y[41],Cep.y[29],Cep.y[42],Cep.y[46],Cep.y[69]])-labelxy]
    #華蓋#
    C_A18 = [[Cas.x[17],Cas.x[40]],[Cas.y[17],Cas.y[40]],[Cas.x[17],Cas.x[61]],[Cas.y[17],Cas.y[61]],\
             [Cas.x[31],Cas.x[61]],[Cas.y[31],Cas.y[61]],[Cas.x[39],Cas.x[40]],[Cas.y[39],Cas.y[40]]]
    CA18n = [numpy.mean([Cas.x[17],Cas.x[31],Cas.x[39],Cas.x[40],Cas.x[61]]),\
             numpy.mean([Cas.y[17],Cas.y[31],Cas.y[39],Cas.y[40],Cas.y[61]])]
    #杠#
    C_A19 = [[Cam.x[7],Cas.x[23]],[Cam.y[7],Cas.y[23]],[Cas.x[7],Cas.x[12]],[Cas.y[7],Cas.y[12]],\
             [Cas.x[7],Cas.x[37]],[Cas.y[7],Cas.y[37]],[Cas.x[12],Cas.x[36]],[Cas.y[12],Cas.y[36]],\
             [Cas.x[23],Cas.x[37]],[Cas.y[23],Cas.y[37]],[Cas.x[36],Cas.x[77]],[Cas.y[36],Cas.y[77]]]
    CA19n = [numpy.mean([Cam.x[7],Cas.x[7],Cas.x[12],Cas.x[23],Cas.x[36],Cas.x[37],Cas.x[77]]),\
             numpy.mean([Cam.y[7],Cas.y[7],Cas.y[12],Cas.y[23],Cas.y[36],Cas.y[37],Cas.y[77]])]
    #傳舍#
    C_A20 = [[Cam.x[1],Cam.x[5]],[Cam.y[1],Cam.y[5]],[Cam.x[1],Cas.x[62]],[Cam.y[1],Cas.y[62]],\
             [Cam.x[5],Cam.x[18]],[Cam.y[5],Cam.y[18]],[Cas.x[58],Cas.x[96]],[Cas.y[58],Cas.y[96]],\
             [Cas.x[58],Cep.x[25]],[Cas.y[58],Cep.y[25]],[Cas.x[62],Cas.x[96]],[Cas.y[62],Cas.y[96]]]
    CA20n = [numpy.mean([Cam.x[1],Cam.x[5],Cam.x[18],Cas.x[58],Cas.x[62],Cas.x[96],Cep.x[25]]),\
             numpy.mean([Cam.y[1],Cam.y[5],Cam.y[18],Cas.y[58],Cas.y[62],Cas.y[96],Cep.y[25]])]
    #內階#
    C_A21 = [[UMa.x[11],UMa.x[46]],[UMa.y[11],UMa.y[46]],[UMa.x[15],UMa.x[88]],[UMa.y[15],UMa.y[88]],\
             [UMa.x[46],UMa.x[71]],[UMa.y[46],UMa.y[71]],[UMa.x[53],UMa.x[88]],[UMa.y[53],UMa.y[88]]]
    CA21n = [numpy.mean([UMa.x[11],UMa.x[15],UMa.x[46],UMa.x[53],UMa.x[71],UMa.x[88]]),\
             numpy.mean([UMa.y[11],UMa.y[15],UMa.y[46],UMa.y[53],UMa.y[71],UMa.y[88]])-labelxy]
    #天廚#
    C_A22 = [[Dra.x[3],Dra.x[21]],[Dra.y[3],Dra.y[21]],[Dra.x[9],Dra.x[16]],[Dra.y[9],Dra.y[16]],\
             [Dra.x[9],Dra.x[21]],[Dra.y[9],Dra.y[21]],[Dra.x[16],Dra.x[55]],[Dra.y[16],Dra.y[55]],\
             [Dra.x[18],Dra.x[55]],[Dra.y[18],Dra.y[55]]]
    CA22n = [numpy.mean([Dra.x[3],Dra.x[9],Dra.x[16],Dra.x[18],Dra.x[21],Dra.x[55]]),\
             numpy.mean([Dra.y[3],Dra.y[9],Dra.y[16],Dra.y[18],Dra.y[21],Dra.y[55]])]
    #八穀#
    C_A23 = [[Aur.x[6],Cam.x[69]],[Aur.y[6],Cam.y[69]],[Cam.x[4],Cam.x[69]],[Cam.y[4],Cam.y[69]],\
             [Cam.x[17],Cam.x[24]],[Cam.y[17],Cam.y[24]]]
    CA23n = [numpy.mean([Aur.x[6],Cam.x[4],Cam.x[17],Cam.x[24],Cam.x[69]]),\
             numpy.mean([Aur.y[6],Cam.y[4],Cam.y[17],Cam.y[24],Cam.y[69]])]
    #天棓#
    C_A24 = [[Dra.x[0],Dra.x[2]],[Dra.y[0],Dra.y[2]],[Dra.x[0],Her.x[9]],[Dra.y[0],Her.y[9]],\
             [Dra.x[2],Dra.x[30]],[Dra.y[2],Dra.y[30]],[Dra.x[8],Dra.x[30]],[Dra.y[8],Dra.y[30]]]
    CA24n = [numpy.mean([Dra.x[0],Dra.x[2],Dra.x[8],Dra.x[30]]),\
             numpy.mean([Dra.y[0],Dra.y[2],Dra.y[8],Dra.y[30]])]
    #內廚#
    C_A25 = [[Dra.x[52],Dra.x[67]],[Dra.y[52],Dra.y[67]]]
    CA25n = [numpy.mean([Dra.x[52],Dra.x[67]]),\
             numpy.mean([Dra.y[52],Dra.y[67]])-labelxy]
    #文昌#
    C_A26 = [[UMa.x[9],UMa.x[21]],[UMa.y[9],UMa.y[21]],[UMa.x[9],UMa.x[24]],[UMa.y[9],UMa.y[24]],\
             [UMa.x[17],UMa.x[24]],[UMa.y[17],UMa.y[24]],[UMa.x[21],UMa.x[33]],[UMa.y[21],UMa.y[33]]]
    CA26n = [numpy.mean([UMa.x[9],UMa.x[17],UMa.x[21],UMa.x[24],UMa.x[33]]),\
             numpy.mean([UMa.y[9],UMa.y[17],UMa.y[21],UMa.y[24],UMa.y[33]])]
    #三師#
    C_A27 = [[UMa.x[30],UMa.x[47]],[UMa.y[30],UMa.y[47]]]
    CA27n = [numpy.mean([UMa.x[30],UMa.x[47]]),\
             numpy.mean([UMa.y[30],UMa.y[47]])-labelxy]
    #三公#
    C_A28 = [[CVn.x[2],CVn.x[11]],[CVn.y[2],CVn.y[11]]]
    CA28n = [numpy.mean([CVn.x[2],CVn.x[11]]),\
             numpy.mean([CVn.y[2],CVn.y[11]])-labelxy]
    #天床#
    C_A29 = [[Dra.x[48],UMi.x[7]],[Dra.y[48],UMi.y[7]],[Dra.x[48],UMi.x[12]],[Dra.y[48],UMi.y[12]],\
             [UMi.x[12],UMi.x[13]],[UMi.y[12],UMi.y[13]]]
    CA29n = [numpy.mean([UMi.x[7],UMi.x[12],UMi.x[13]]),\
             numpy.mean([UMi.y[7],UMi.y[12],UMi.y[13]])]
    #太尊#
    C_A30 = []
    CA30n = [UMa.x[6],UMa.y[6]-labelxy]
    #天牢#
    C_A31 = [[UMa.x[28],UMa.x[56]],[UMa.y[28],UMa.y[56]],[UMa.x[38],UMa.x[42]],[UMa.y[38],UMa.y[42]],\
             [UMa.x[41],UMa.x[113]],[UMa.y[41],UMa.y[113]]]
    CA31n = [numpy.mean([UMa.x[28],UMa.x[38],UMa.x[41],UMa.x[42],UMa.x[56],UMa.x[113]]),\
             numpy.mean([UMa.y[28],UMa.y[38],UMa.y[41],UMa.y[42],UMa.y[56],UMa.y[113]])-labelxy]
    #太陽守#
    C_A32 = []
    CA32n = [UMa.x[16],UMa.y[16]-labelxy]
    #勢#
    C_A33 = [[LMi.x[0],LMi.x[8]],[LMi.y[0],LMi.y[8]],[LMi.x[8],LMi.x[21]],[LMi.y[8],LMi.y[21]],\
             [LMi.x[15],LMi.x[21]],[LMi.y[15],LMi.y[21]]]
    CA33n = [numpy.mean([LMi.x[0],LMi.x[8],LMi.x[15],LMi.x[21]]),\
             numpy.mean([LMi.y[0],LMi.y[8],LMi.y[15],LMi.y[21]])]
    #相#
    C_A34 = []
    CA34n = [CVn.x[5],CVn.y[5]-labelxy]
    #玄戈#
    C_A35 = []
    CA35n = [Boo.x[9],Boo.y[9]-labelxy]
    #玄戈#
    C_A36 = []
    CA36n = [UMa.x[103],UMa.y[103]-labelxy]
    #北斗#
    C_A37 = [[UMa.x[0],UMa.x[3]],[UMa.y[0],UMa.y[3]],[UMa.x[0],UMa.x[10]],[UMa.y[0],UMa.y[10]],\
             [UMa.x[1],UMa.x[4]],[UMa.y[1],UMa.y[4]],[UMa.x[2],UMa.x[3]],[UMa.y[2],UMa.y[3]],\
             [UMa.x[4],UMa.x[5]],[UMa.y[4],UMa.y[5]],[UMa.x[5],UMa.x[10]],[UMa.y[5],UMa.y[10]]]
    CA37n = [numpy.mean([UMa.x[0],UMa.x[1],UMa.x[4],UMa.x[5],UMa.x[10]]),\
             numpy.mean([UMa.y[0],UMa.y[1],UMa.y[4],UMa.y[5],UMa.y[10]])]
    #輔#
    C_A38 = []
    CA38n = [UMa.x[19]+labelxy,UMa.y[19]-labelxy]
    #天槍#
    C_A39 = [[Boo.x[7],Boo.x[18]],[Boo.y[7],Boo.y[18]],[Boo.x[14],Boo.x[18]],[Boo.y[14],Boo.y[18]]]
    CA39n = [numpy.mean([Boo.x[7],Boo.x[14],Boo.x[18]]),\
             numpy.mean([Boo.y[7],Boo.y[14],Boo.y[18]])-labelxy]
    
    C_A_list = [C_A01,C_A02,C_A03,C_A04,C_A05,C_A06,C_A07,C_A08,C_A09,C_A10,\
                C_A11,C_A12,C_A13,C_A14,C_A15,C_A16,C_A17,C_A18,C_A19,C_A20,\
                C_A21,C_A22,C_A23,C_A24,C_A25,C_A26,C_A27,C_A28,C_A29,C_A30,\
                C_A31,C_A32,C_A33,C_A34,C_A35,C_A36,C_A37,C_A38,C_A39]

    # 紫微垣 linecollection
    C_A_line_xy1 = []
    C_A_line_xy2 = []        
    for i in range(len(C_A_list)):
        for j in range(len(C_A_list[i]))[0::2]:
            if math.hypot(C_A_list[i][j][0]-C_A_list[i][j][1],C_A_list[i][j+1][0]-C_A_list[i][j+1][1]) < hori_border:
                C_A_line_xy1.append((C_A_list[i][j][0],C_A_list[i][j+1][0]))
                C_A_line_xy2.append((C_A_list[i][j][1],C_A_list[i][j+1][1]))

    C_A_line_list = []
    for i in range(len(C_A_line_xy1)):            
        C_A_line_list.append([C_A_line_xy1[i],C_A_line_xy2[i]])
    
    lc_C_A = mc.LineCollection(C_A_line_list, colors='white', zorder=2+2.5)
    lc_C_A.set_alpha(plot_alpha)
    lc_C_A.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_A)

    CAn_list = [[CA01n,'北極'],[CA02n,'四輔'],[CA03n,'天乙'],[CA04n,'太乙'],[CA05n,'紫微左垣'],\
                [CA06n,'紫微右垣'],[CA07n,'陰德'],[CA08n,'尚書'],[CA09n,'女史'],[CA10n,'柱史'],\
                [CA11n,'御女'],[CA12n,'天柱'],[CA13n,'大理'],[CA14n,'勾陳'],[CA15n,'六甲'],\
                [CA16n,'天皇大帝'],[CA17n,'五帝內座'],[CA18n,'華蓋'],[CA19n,'杠'],[CA20n,'傳舍'],\
                [CA21n,'內階'],[CA22n,'天廚'],[CA23n,'八穀'],[CA24n,'天棓'],[CA25n,'內廚'],\
                [CA26n,'文昌'],[CA27n,'三師'],[CA28n,'三公'],[CA29n,'天床'],[CA30n,'太尊'],\
                [CA31n,'天牢'],[CA32n,'太陽守'],[CA33n,'勢'],[CA34n,'相'],[CA35n,'玄戈'],\
                [CA36n,'玄戈'],[CA37n,'北斗'],[CA38n,'輔'],[CA39n,'天槍']]
  
##    for i in range(len(CAn_list)):
##        if len(CAn_list[i][0]) != 0:
##            if (CAn_list[i][0][0])**2 < (hori_border/2)**2-(CAn_list[i][0][1])**2 \
##               and max(CAn_list[i][0])-min(CAn_list[i][0]) < hori_border:
##                ax0.annotate(str(CAn_list[i][1]),(CAn_list[i][0][0],CAn_list[i][0][1]),color='w',\
##                                  fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ########
    #太微垣#
    ########
    #太微左垣#
    C_B01 = [[Com.x[19],Vir.x[1]],[Com.y[19],Vir.y[1]],[Vir.x[1],Vir.x[3]],[Vir.y[1],Vir.y[3]],\
             [Vir.x[3],Vir.x[5]],[Vir.y[3],Vir.y[5]],[Vir.x[5],Vir.x[9]],[Vir.y[5],Vir.y[9]]]
    CB01n = [numpy.mean([Vir.x[1],Vir.x[3],Vir.x[5],Vir.x[9]]),\
             numpy.mean([Vir.y[1],Vir.y[3],Vir.y[5],Vir.y[9]])]
    #太微右垣#
    C_B02 = [[Leo.x[2],Leo.x[5]],[Leo.y[2],Leo.y[5]],[Leo.x[5],Leo.x[12]],[Leo.y[5],Leo.y[12]],\
             [Leo.x[12],Leo.x[13]],[Leo.y[12],Leo.y[13]],[Leo.x[13],Vir.x[4]],[Leo.y[13],Vir.y[4]]]
    CB02n = [numpy.mean([Leo.x[2],Leo.x[5],Leo.x[12],Leo.x[13],Vir.x[4]]),\
             numpy.mean([Leo.y[2],Leo.y[5],Leo.y[12],Leo.y[13],Vir.y[4]])-labelxy]
    #謁者#
    C_B03 = []
    CB03n = [Vir.x[30],Vir.y[30]-labelxy]
    #三公#
    C_B04 = []
    CB04n = [Vir.x[64],Vir.y[64]-labelxy]
    #九卿#
    C_B05 = [[Vir.x[27],Vir.x[41]],[Vir.y[27],Vir.y[41]]]
    CB05n = [numpy.mean([Vir.x[27],Vir.x[41]])+labelxy,\
             numpy.mean([Vir.y[27],Vir.y[41]])]
    #五諸侯#
    C_B06 = [[Com.x[3],Com.x[16]],[Com.y[3],Com.y[16]],[Com.x[3],Com.x[38]],[Com.y[3],Com.y[38]],\
             [Com.x[15],Com.x[16]],[Com.y[15],Com.y[16]]]
    CB06n = [numpy.mean([Com.x[3],Com.x[16],Com.x[38]])+2*labelxy,\
             numpy.mean([Com.y[3],Com.y[16],Com.y[38]])+labelxy]
    #內屏#
    C_B07 = [[Vir.x[10],Vir.x[18]],[Vir.y[10],Vir.y[18]],[Vir.x[10],Vir.x[26]],[Vir.y[10],Vir.y[26]],\
             [Vir.x[12],Vir.x[18]],[Vir.y[12],Vir.y[18]]]
    CB07n = [numpy.mean([Vir.x[10],Vir.x[12],Vir.x[18],Vir.x[26]]),\
             numpy.mean([Vir.y[10],Vir.y[12],Vir.y[18],Vir.y[26]])+labelxy]
    #五帝座#
    C_B08 = [[Leo.x[1],Leo.x[52]],[Leo.y[1],Leo.y[52]],[Leo.x[1],Leo.x[87]],[Leo.y[1],Leo.y[87]]]
    CB08n = [numpy.mean([Leo.x[1],Leo.x[52],Leo.x[87]]),\
             numpy.mean([Leo.y[1],Leo.y[52],Leo.y[87]])-2*labelxy]
    #幸臣#
    C_B09 = []
    CB09n = [] # ???
    #太子#
    C_B10 = []
    CB10n = [Leo.x[21],Leo.y[21]-labelxy]
    #從官#
    C_B11 = []
    CB11n = [Leo.x[37]+labelxy,Leo.y[37]-labelxy]
    #郎將#
    C_B12 = []
    CB12n = [Com.x[9],Com.y[9]-labelxy]
    #虎賁#
    C_B13 = []
    CB13n = [Leo.x[23],Leo.y[23]-labelxy]
    #常陳#
    C_B14 = [[CVn.x[0],CVn.x[31]],[CVn.y[0],CVn.y[31]],[CVn.x[1],CVn.x[10]],[CVn.y[1],CVn.y[10]],\
             [CVn.x[1],CVn.x[31]],[CVn.y[1],CVn.y[31]],[CVn.x[10],CVn.x[20]],[CVn.y[10],CVn.y[20]],\
             [CVn.x[20],UMa.x[52]],[CVn.y[20],UMa.y[52]]]
    CB14n = [numpy.mean([CVn.x[0],CVn.x[1],CVn.x[10],CVn.x[20],CVn.x[31]]),\
             numpy.mean([CVn.y[0],CVn.y[1],CVn.y[10],CVn.y[20],CVn.y[31]])]
    #郎位#
    C_B15 = [[Com.x[1],Com.x[11]],[Com.y[1],Com.y[11]],[Com.x[5],Com.x[17]],[Com.y[5],Com.y[17]],\
             [Com.x[5],Com.x[21]],[Com.y[5],Com.y[21]],[Com.x[6],Com.x[10]],[Com.y[6],Com.y[10]],\
             [Com.x[6],Com.x[22]],[Com.y[6],Com.y[22]],[Com.x[10],Com.x[23]],[Com.y[10],Com.y[23]],\
             [Com.x[11],Com.x[13]],[Com.y[11],Com.y[13]],[Com.x[13],Com.x[20]],[Com.y[13],Com.y[20]],\
             [Com.x[17],Com.x[20]],[Com.y[17],Com.y[20]],[Com.x[21],Com.x[23]],[Com.y[21],Com.y[23]],\
             [Com.x[22],Com.x[29]],[Com.y[22],Com.y[29]],[Com.x[25],Com.x[29]],[Com.y[25],Com.y[29]],\
             [Com.x[25],Com.x[35]],[Com.y[25],Com.y[35]]]
    CB15n = [numpy.mean([Com.x[1],Com.x[5],Com.x[6],Com.x[10],Com.x[11],Com.x[13],Com.x[17],Com.x[20],\
                         Com.x[21],Com.x[22],Com.x[23],Com.x[25],Com.x[29],Com.x[35]])+labelxy,\
             numpy.mean([Com.y[1],Com.y[5],Com.y[6],Com.y[10],Com.y[11],Com.y[13],Com.y[17],Com.y[20],\
                         Com.y[21],Com.y[22],Com.y[23],Com.y[25],Com.y[29],Com.y[35]])-2*labelxy]
    #明堂#
    C_B16 = [[Leo.x[14],Leo.x[26]],[Leo.y[14],Leo.y[26]],[Leo.x[14],Leo.x[29]],[Leo.y[14],Leo.y[29]]]
    CB16n = [numpy.mean([Leo.x[14],Leo.x[26],Leo.x[29]])+labelxy,\
             numpy.mean([Leo.y[14],Leo.y[26],Leo.y[29]])]
    #靈台#
    C_B17 = [[Leo.x[22],Leo.x[31]],[Leo.y[22],Leo.y[31]],[Leo.x[28],Leo.x[31]],[Leo.y[28],Leo.y[31]]]
    CB17n = [numpy.mean([Leo.x[22],Leo.x[28],Leo.x[31]])-labelxy,\
             numpy.mean([Leo.y[22],Leo.y[28],Leo.y[31]])]
    #少微#
    C_B18 = [[Leo.x[20],LMi.x[6]],[Leo.y[20],LMi.y[6]],[Leo.x[49],LMi.x[6]],[Leo.y[49],LMi.y[6]]]
    CB18n = [numpy.mean([Leo.x[20],Leo.x[49],LMi.x[6]])-labelxy,\
             numpy.mean([Leo.y[20],Leo.y[49],LMi.y[6]])]
    #長垣#
    C_B19 = [[Leo.x[34],Leo.x[40]],[Leo.y[34],Leo.y[40]],[Leo.x[40],Leo.x[48]],[Leo.y[40],Leo.y[48]],\
             [Leo.x[47],Leo.x[48]],[Leo.y[47],Leo.y[48]]]
    CB19n = [numpy.mean([Leo.x[34],Leo.x[40],Leo.x[47],Leo.x[48]]),\
             numpy.mean([Leo.y[34],Leo.y[40],Leo.y[47],Leo.y[48]])]
    #三台#
    C_B20 = [[UMa.x[7],UMa.x[12]],[UMa.y[7],UMa.y[12]],[UMa.x[7],UMa.x[13]],[UMa.y[7],UMa.y[13]],\
             [UMa.x[8],UMa.x[14]],[UMa.y[8],UMa.y[14]],[UMa.x[12],UMa.x[14]],[UMa.y[12],UMa.y[14]],\
             [UMa.x[13],UMa.x[20]],[UMa.y[13],UMa.y[20]]]
    CB20n = [numpy.mean([UMa.x[7],UMa.x[8],UMa.x[12],UMa.x[13],UMa.x[14],UMa.x[20]])+labelxy,\
             numpy.mean([UMa.y[7],UMa.y[8],UMa.y[12],UMa.y[13],UMa.y[14],UMa.y[20]])-labelxy]

    C_B_list = [C_B01,C_B02,C_B03,C_B04,C_B05,C_B06,C_B07,C_B08,C_B09,C_B10,\
                C_B11,C_B12,C_B13,C_B14,C_B15,C_B16,C_B17,C_B18,C_B19,C_B20]

    # 太微垣 linecollection
    C_B_line_xy1 = []
    C_B_line_xy2 = []        
    for i in range(len(C_B_list)):
        for j in range(len(C_B_list[i]))[0::2]:
            if math.hypot(C_B_list[i][j][0]-C_B_list[i][j][1],C_B_list[i][j+1][0]-C_B_list[i][j+1][1]) < hori_border:
                C_B_line_xy1.append((C_B_list[i][j][0],C_B_list[i][j+1][0]))
                C_B_line_xy2.append((C_B_list[i][j][1],C_B_list[i][j+1][1]))

    C_B_line_list = []
    for i in range(len(C_B_line_xy1)):            
        C_B_line_list.append([C_B_line_xy1[i],C_B_line_xy2[i]])
    
    lc_C_B = mc.LineCollection(C_B_line_list, colors='white', zorder=2+2.5)
    lc_C_B.set_alpha(plot_alpha)
    lc_C_B.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_B)
    
    CBn_list = [[CB01n,'太微左垣'],[CB02n,'太微右垣'],[CB03n,'謁者'],[CB04n,'三公'],[CB05n,'九卿'],\
                [CB06n,'五諸侯'],[CB07n,'內屏'],[CB08n,'五帝座'],[CB09n,'幸臣'],[CB10n,'太子'],\
                [CB11n,'從官'],[CB12n,'郎將'],[CB13n,'虎賁'],[CB14n,'常陳'],[CB15n,'郎位'],\
                [CB16n,'明堂'],[CB17n,'靈台'],[CB18n,'少微'],[CB19n,'長垣'],[CB20n,'三台']]
  
##    for i in range(len(CBn_list)):
##        if len(CBn_list[i][0]) != 0:
##            if (CBn_list[i][0][0])**2 < (hori_border/2)**2-(CBn_list[i][0][1])**2 \
##               and max(CBn_list[i][0])-min(CBn_list[i][0]) < hori_border:
##                ax0.annotate(str(CBn_list[i][1]),(CBn_list[i][0][0],CBn_list[i][0][1]),color='w',\
##                                  fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ########
    #天市垣#
    ########
    #天市左垣#
    C_C01 = [[Aql.x[2],Her.x[75]],[Aql.y[2],Her.y[75]],[Aql.x[2],Ser.x[15]],[Aql.y[2],Ser.y[15]],\
             [Her.x[2],Her.x[20]],[Her.y[2],Her.y[20]],[Her.x[4],Her.x[10]],[Her.y[4],Her.y[10]],\
             [Her.x[4],Her.x[20]],[Her.y[4],Her.y[20]],[Her.x[10],Her.x[75]],[Her.y[10],Her.y[75]],\
             [Oph.x[1],Ser.x[3]],[Oph.y[1],Ser.y[3]],[Oph.x[8],Ser.x[1]],[Oph.y[8],Ser.y[1]],\
             [Oph.x[8],Ser.x[3]],[Oph.y[8],Ser.y[3]],[Ser.x[1],Ser.x[15]],[Ser.y[1],Ser.y[15]]]
    CC01n = [numpy.mean([Aql.x[2],Ser.x[15]]),\
             numpy.mean([Aql.y[2],Ser.y[15]])]
    #天市右垣#
    C_C02 = [[Her.x[0],Her.x[8]],[Her.y[0],Her.y[8]],[Her.x[8],Her.x[38]],[Her.y[8],Her.y[38]],\
             [Her.x[38],Ser.x[8]],[Her.y[38],Ser.y[8]],[Oph.x[2],Oph.x[6]],[Oph.y[2],Oph.y[6]],\
             [Oph.x[3],Ser.x[5]],[Oph.y[3],Ser.y[5]],[Oph.x[3],Oph.x[6]],[Oph.y[3],Oph.y[6]],\
             [Ser.x[0],Ser.x[5]],[Ser.y[0],Ser.y[5]],[Ser.x[0],Ser.x[7]],[Ser.y[0],Ser.y[7]],\
             [Ser.x[4],Ser.x[7]],[Ser.y[4],Ser.y[7]],[Ser.x[4],Ser.x[8]],[Ser.y[4],Ser.y[8]]]
    CC02n = [numpy.mean([Her.x[0],Her.x[8],Her.x[38],Oph.x[2],Oph.x[3],Oph.x[6],Ser.x[0],Ser.x[4],\
                         Ser.x[5],Ser.x[7],Ser.x[8]]),\
             numpy.mean([Her.y[0],Her.y[8],Her.y[38],Oph.y[2],Oph.y[3],Oph.y[6],Ser.y[0],Ser.y[4],\
                         Ser.y[5],Ser.y[7],Ser.y[8]])]
    #市樓#
    C_C03 = [[Oph.x[25],Ser.x[10]],[Oph.y[25],Ser.y[10]],[Oph.x[42],Ser.x[11]],[Oph.y[42],Ser.y[11]]]
    CC03n = [numpy.mean([Oph.x[25],Oph.x[42],Ser.x[10],Ser.x[11]])+labelxy,\
             numpy.mean([Oph.y[25],Oph.y[42],Ser.y[10],Ser.y[11]])]
    #車肆#
    C_C04 = [[Oph.x[26],Oph.x[29]],[Oph.y[26],Oph.y[29]]]
    CC04n = [numpy.mean([Oph.x[26],Oph.x[29]]),\
             numpy.mean([Oph.y[26],Oph.y[29]])+labelxy]
    #宗正#
    C_C05 = [[Oph.x[4],Oph.x[10]],[Oph.y[4],Oph.y[10]]]
    CC05n = [numpy.mean([Oph.x[4],Oph.x[10]])+labelxy,\
             numpy.mean([Oph.y[4],Oph.y[10]])]
    #宗人#
    C_C06 = [[Oph.x[12],Oph.x[22]],[Oph.y[12],Oph.y[22]],[Oph.x[12],Oph.x[27]],[Oph.y[12],Oph.y[27]],\
             [Oph.x[13],Oph.x[22]],[Oph.y[13],Oph.y[22]]]
    CC06n = [numpy.mean([Oph.x[12],Oph.x[13],Oph.x[22]]),\
             numpy.mean([Oph.y[12],Oph.y[13],Oph.y[22]])-2*labelxy]
    #宗#
    C_C07 = [[Her.x[15],Her.x[19]],[Her.y[15],Her.y[19]]]
    CC07n = [numpy.mean([Her.x[15],Her.x[19]])+labelxy,\
             numpy.mean([Her.y[15],Her.y[19]])]
    #帛度#
    C_C08 = [[Her.x[18],Her.x[35]],[Her.y[18],Her.y[35]]]
    CC08n = [numpy.mean([Her.x[18],Her.x[35]]),\
             numpy.mean([Her.y[18],Her.y[35]])-labelxy]
    #屠肆#
    C_C09 = [[Her.x[11],Her.x[44]],[Her.y[11],Her.y[44]]]
    CC09n = [numpy.mean([Her.x[11],Her.x[44]]),\
             numpy.mean([Her.y[11],Her.y[44]])-labelxy]
    #侯#
    C_C10 = []
    CC10n = [Oph.x[0],Oph.y[0]-labelxy]
    #帝座#
    C_C11 = []
    CC11n = [Her.x[5],Her.y[5]-labelxy]
    #宦者#
    C_C12 = [[Her.x[33],Oph.x[45]],[Her.y[33],Oph.y[45]],[Her.x[33],Her.x[132]],[Her.y[33],Her.y[132]],\
             [Her.x[37],Her.x[132]],[Her.y[37],Her.y[132]]]
    CC12n = [numpy.mean([Her.x[33],Oph.x[45],Her.x[132]]),\
             numpy.mean([Her.y[33],Oph.y[45],Her.y[132]])]
    #列肆#
    C_C13 = [[Oph.x[11],Ser.x[17]],[Oph.y[11],Ser.y[17]]]
    CC13n = [numpy.mean([Oph.x[11],Ser.x[17]]),\
             numpy.mean([Oph.y[11],Ser.y[17]])-labelxy]
    #斗#
    C_C14 = [[Her.x[23],Her.x[31]],[Her.y[23],Her.y[31]]]
    CC14n = [numpy.mean([Her.x[23],Her.x[31]])+labelxy,\
             numpy.mean([Her.y[23],Her.y[31]])]
    #斛#
    C_C15 = [[Her.x[51],Her.x[76]],[Her.y[51],Her.y[76]],[Her.x[76],Oph.x[5]],[Her.y[76],Oph.y[5]],\
             [Oph.x[5],Oph.x[18]],[Oph.y[5],Oph.y[18]]]
    CC15n = [numpy.mean([Her.x[51],Her.x[76],Oph.x[5],Oph.x[18]]),\
             numpy.mean([Her.y[51],Her.y[76],Oph.y[5],Oph.y[18]])]
    #貫索#
    C_C16 = [[CrB.x[1],CrB.x[2]],[CrB.y[1],CrB.y[2]],[CrB.x[1],CrB.x[3]],[CrB.y[1],CrB.y[3]],\
             [CrB.x[2],CrB.x[4]],[CrB.y[2],CrB.y[4]],[CrB.x[3],CrB.x[6]],[CrB.y[3],CrB.y[6]],\
             [CrB.x[4],CrB.x[18]],[CrB.y[4],CrB.y[18]],[CrB.x[5],CrB.x[6]],[CrB.y[5],CrB.y[6]],\
             [CrB.x[5],CrB.x[10]],[CrB.y[5],CrB.y[10]],[CrB.x[10],CrB.x[15]],[CrB.y[10],CrB.y[15]]]
    CC16n = [numpy.mean([CrB.x[1],CrB.x[2],CrB.x[3],CrB.x[4],CrB.x[5],CrB.x[6],CrB.x[10],CrB.x[15],\
                         CrB.x[18]]),\
             numpy.mean([CrB.y[1],CrB.y[2],CrB.y[3],CrB.y[4],CrB.y[5],CrB.y[6],CrB.y[10],CrB.y[15],\
                         CrB.y[18]])]
    #七公#
    C_C17 = [[Boo.x[4],Boo.x[10]],[Boo.y[4],Boo.y[10]],[Boo.x[10],Boo.x[31]],[Boo.y[10],Boo.y[31]],\
             [Her.x[13],Her.x[17]],[Her.y[13],Her.y[17]],[Boo.x[31],Her.x[25]],[Boo.y[31],Her.y[25]],\
             [Her.x[13],Her.x[32]],[Her.y[13],Her.y[32]],[Her.x[17],Her.x[25]],[Her.y[17],Her.y[25]]]
    CC17n = [numpy.mean([Boo.x[4],Boo.x[10],Boo.x[31],Her.x[13],Her.x[17],Her.x[25],Her.x[32]]),\
             numpy.mean([Boo.y[4],Boo.y[10],Boo.y[31],Her.y[13],Her.y[17],Her.y[25],Her.y[32]])-labelxy]
    #天紀#
    C_C18 = [[CrB.x[9],Her.x[1]],[CrB.y[9],Her.y[1]],[Her.x[1],Her.x[14]],[Her.y[1],Her.y[14]],\
             [Her.x[12],Her.x[88]],[Her.y[12],Her.y[88]],[Her.x[14],Her.x[56]],[Her.y[14],Her.y[56]],\
             [Her.x[30],Her.x[56]],[Her.y[30],Her.y[56]],[Her.x[30],Her.x[88]],[Her.y[30],Her.y[88]]]
    CC18n = [numpy.mean([CrB.x[9],Her.x[1],Her.x[12],Her.x[14],Her.x[30],Her.x[56],Her.x[88]]),\
             numpy.mean([CrB.y[9],Her.y[1],Her.y[12],Her.y[14],Her.y[30],Her.y[56],Her.y[88]])-labelxy]
    #女床#
    C_C19 = [[Her.x[3],Her.x[26]],[Her.y[3],Her.y[26]],[Her.x[22],Her.x[26]],[Her.y[22],Her.y[26]]]
    CC19n = [numpy.mean([Her.x[3],Her.x[22],Her.x[26]])-labelxy,\
             numpy.mean([Her.y[3],Her.y[22],Her.y[26]])]

    C_C_list = [C_C01,C_C02,C_C03,C_C04,C_C05,C_C06,C_C07,C_C08,C_C09,C_C10,\
                C_C11,C_C12,C_C13,C_C14,C_C15,C_C16,C_C17,C_C18,C_C19]

    # 天市垣 linecollection
    C_C_line_xy1 = []
    C_C_line_xy2 = []        
    for i in range(len(C_C_list)):
        for j in range(len(C_C_list[i]))[0::2]:
            if math.hypot(C_C_list[i][j][0]-C_C_list[i][j][1],C_C_list[i][j+1][0]-C_C_list[i][j+1][1]) < hori_border:
                C_C_line_xy1.append((C_C_list[i][j][0],C_C_list[i][j+1][0]))
                C_C_line_xy2.append((C_C_list[i][j][1],C_C_list[i][j+1][1]))

    C_C_line_list = []
    for i in range(len(C_C_line_xy1)):            
        C_C_line_list.append([C_C_line_xy1[i],C_C_line_xy2[i]])
    
    lc_C_C = mc.LineCollection(C_C_line_list, colors='white', zorder=2+2.5)
    lc_C_C.set_alpha(plot_alpha)
    lc_C_C.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_C)

    CCn_list = [[CC01n,'天市左垣'],[CC02n,'天市右垣'],[CC03n,'市樓'],[CC04n,'車肆'],[CC05n,'宗正'],\
                [CC06n,'宗人'],[CC07n,'宗'],[CC08n,'帛度'],[CC09n,'屠肆'],[CC10n,'侯'],\
                [CC11n,'帝座'],[CC12n,'宦者'],[CC13n,'列肆'],[CC14n,'斗'],[CC15n,'斛'],\
                [CC16n,'貫索'],[CC17n,'七公'],[CC18n,'天紀'],[CC19n,'女床']]
  
##    for i in range(len(CCn_list)):
##        if len(CCn_list[i][0]) != 0:
##            if (CCn_list[i][0][0])**2 < (hori_border/2)**2-(CCn_list[i][0][1])**2 \
##               and max(CCn_list[i][0])-min(CCn_list[i][0]) < hori_border:
##                ax0.annotate(str(CCn_list[i][1]),(CCn_list[i][0][0],CCn_list[i][0][1]),color='w',\
##                                  fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ##########
    #東宮蒼龍#
    ##########
    #角宿#
    C_D01 = [[Vir.x[0],Vir.x[2]],[Vir.y[0],Vir.y[2]]]
    CD01n = [numpy.mean([Vir.x[0],Vir.x[2]])-labelxy,\
             numpy.mean([Vir.y[0],Vir.y[2]])]
    #平道#
    C_D02 = [[Vir.x[15],Vir.x[33]],[Vir.y[15],Vir.y[33]]]
    CD02n = [numpy.mean([Vir.x[15],Vir.x[33]])+labelxy,\
             numpy.mean([Vir.y[15],Vir.y[33]])]
    #天田#
    C_D03 = [[Vir.x[14],Vir.x[29]],[Vir.y[14],Vir.y[29]]]
    CD03n = [numpy.mean([Vir.x[14],Vir.x[29]]),\
             numpy.mean([Vir.y[14],Vir.y[29]])-labelxy]
    #進賢#
    C_D04 = []
    CD04n = [] # ???
    #周鼎#
    C_D05 = [[Com.x[0],Com.x[8]],[Com.y[0],Com.y[8]],[Com.x[4],Com.x[8]],[Com.y[4],Com.y[8]]]
    CD05n = [numpy.mean([Com.x[0],Com.x[4],Com.x[8]])+2*labelxy,\
             numpy.mean([Com.y[0],Com.y[4],Com.y[8]])]
    #天門#
    C_D06 = [[Vir.x[22],Vir.x[35]],[Vir.y[22],Vir.y[35]]]
    CD06n = [numpy.mean([Vir.x[22],Vir.x[35]]),\
             numpy.mean([Vir.y[22],Vir.y[35]])-labelxy]
    #平#
    C_D07 = [[Hya.x[1],Hya.x[4]],[Hya.y[1],Hya.y[4]]]
    CD07n = [numpy.mean([Hya.x[1],Hya.x[4]]),\
             numpy.mean([Hya.y[1],Hya.y[4]])-labelxy]
    #庫樓#
    C_D08 = [[Cen.x[6],Cen.x[7]],[Cen.y[6],Cen.y[7]],[Cen.x[3],Cen.x[6]],[Cen.y[3],Cen.y[6]],\
             [Cen.x[3],Cen.x[25]],[Cen.y[3],Cen.y[25]],[Cen.x[17],Cen.x[25]],[Cen.y[17],Cen.y[25]],\
             [Cen.x[4],Cen.x[17]],[Cen.y[4],Cen.y[17]],[Cen.x[4],Cen.x[15]],[Cen.y[4],Cen.y[15]],\
             [Cen.x[15],Cen.x[19]],[Cen.y[15],Cen.y[19]]]
    CD08n = [numpy.mean([Cen.x[3],Cen.x[4],Cen.x[6],Cen.x[7],Cen.x[15],Cen.x[17],Cen.x[19],Cen.x[25]]),\
             numpy.mean([Cen.y[3],Cen.y[4],Cen.y[6],Cen.y[7],Cen.y[15],Cen.y[17],Cen.y[19],Cen.y[25]])+2*labelxy]
    #柱#
    C_D09 = [[Cen.x[16],Cen.x[32]],[Cen.y[16],Cen.y[32]],[Cen.x[22],Cen.x[34]],[Cen.y[22],Cen.y[34]],\
             [Cen.x[26],Cen.x[39]],[Cen.y[26],Cen.y[39]],[Cen.x[39],Cen.x[47]],[Cen.y[39],Cen.y[47]],\
             [Lup.x[7],Lup.x[18]],[Lup.y[7],Lup.y[18]]]
    CD09an = [numpy.mean([Cen.x[16],Cen.x[32]])+labelxy,\
              numpy.mean([Cen.y[16],Cen.y[32]])-labelxy]
    CD09bn = [numpy.mean([Cen.x[22],Cen.x[34]])-labelxy,\
              numpy.mean([Cen.y[22],Cen.y[34]])+labelxy]
    CD09cn = [numpy.mean([Cen.x[26],Cen.x[39],Cen.x[47]])+labelxy,\
              numpy.mean([Cen.y[26],Cen.y[39],Cen.y[47]])+2*labelxy]
    CD09dn = [numpy.mean([Lup.x[7],Lup.x[18]]),\
              numpy.mean([Lup.y[7],Lup.y[18]])-labelxy]
    #衡#
    C_D10 = [[Cen.x[10],Cen.x[13]],[Cen.y[10],Cen.y[13]],[Cen.x[10],Cen.x[14]],[Cen.y[10],Cen.y[14]],\
             [Cen.x[14],Cen.x[33]],[Cen.y[14],Cen.y[33]]]
    CD10n = [numpy.mean([Cen.x[10],Cen.x[13],Cen.x[14],Cen.x[33]]),\
             numpy.mean([Cen.y[10],Cen.y[13],Cen.y[14],Cen.y[33]])-labelxy]
    #南門#
    C_D11 = [[Cen.x[0],Cen.x[5]],[Cen.y[0],Cen.y[5]]]
    CD11n = [numpy.mean([Cen.x[0],Cen.x[5]]),\
             numpy.mean([Cen.y[0],Cen.y[5]])-labelxy]
    #亢宿#
    C_D12 = [[Vir.x[11],Vir.x[13]],[Vir.y[11],Vir.y[13]],[Vir.x[11],Vir.x[25]],[Vir.y[11],Vir.y[25]],\
             [Vir.x[13],Vir.x[17]],[Vir.y[13],Vir.y[17]]]
    CD12n = [numpy.mean([Vir.x[11],Vir.x[13],Vir.x[25],Vir.x[17]]),\
             numpy.mean([Vir.y[11],Vir.y[13],Vir.y[25],Vir.y[17]])]
    #大角#
    C_D13 = []
    CD13n = [Boo.x[0],Boo.y[0]-labelxy]
    #右攝提#
    C_D14 = [[Boo.x[1],Boo.x[13]],[Boo.y[1],Boo.y[13]],[Boo.x[8],Boo.x[13]],[Boo.y[8],Boo.y[13]]]
    CD14n = [numpy.mean([Boo.x[1],Boo.x[8],Boo.x[13]])-labelxy,\
             numpy.mean([Boo.y[1],Boo.y[8],Boo.y[13]])]
    #左攝提#
    C_D15 = [[Boo.x[11],Boo.x[29]],[Boo.y[11],Boo.y[29]],[Boo.x[17],Boo.x[29]],[Boo.y[17],Boo.y[29]]]
    CD15n = [numpy.mean([Boo.x[11],Boo.x[17],Boo.x[29]])-labelxy,\
             numpy.mean([Boo.y[11],Boo.y[17],Boo.y[29]])]
    #頓頑#
    C_D16 = [[Lup.x[8],Lup.x[32]],[Lup.y[8],Lup.y[32]]]
    CD16n = [numpy.mean([Lup.x[8],Lup.x[32]])+labelxy,\
             numpy.mean([Lup.y[8],Lup.y[32]])]
    #陽門#
    C_D17 = [[Cen.x[21],Cen.x[23]],[Cen.y[21],Cen.y[23]]]
    CD17n = [numpy.mean([Cen.x[21],Cen.x[23]])+2*labelxy,\
             numpy.mean([Cen.y[21],Cen.y[23]])+labelxy]
    #折威#
    C_D18 = [[Lib.x[2],Lib.x[21]],[Lib.y[2],Lib.y[21]],[Lib.x[21],Lib.x[38]],[Lib.y[21],Lib.y[38]]]
    CD18n = [numpy.mean([Lib.x[2],Lib.x[21],Lib.x[38]]),\
             numpy.mean([Lib.y[2],Lib.y[21],Lib.y[38]])-labelxy]
    #氐宿#
    C_D19 = [[Lib.x[0],Lib.x[5]],[Lib.y[0],Lib.y[5]],[Lib.x[1],Lib.x[8]],[Lib.y[1],Lib.y[8]],\
             [Lib.x[5],Lib.x[8]],[Lib.y[5],Lib.y[8]]]
    CD19n = [numpy.mean([Lib.x[0],Lib.x[1],Lib.x[5],Lib.x[8]]),\
             numpy.mean([Lib.y[0],Lib.y[1],Lib.y[5],Lib.y[8]])]
    #天乳#
    C_D20 = []
    CD20n = [Ser.x[2],Ser.y[2]-labelxy]
    #招搖#
    C_D21 = []
    CD21n = [Boo.x[3],Boo.y[3]-labelxy]
    #梗河#
    C_D22 = [[Boo.x[2],Boo.x[12]],[Boo.y[2],Boo.y[12]],[Boo.x[6],Boo.x[12]],[Boo.y[6],Boo.y[12]]]
    CD22n = [numpy.mean([Boo.x[2],Boo.x[6],Boo.x[12]]),\
             numpy.mean([Boo.y[2],Boo.y[6],Boo.y[12]])-labelxy]
    #帝席#
    C_D23 = [[Boo.x[23],Boo.x[115]],[Boo.y[23],Boo.y[115]],[Boo.x[30],Boo.x[115]],[Boo.y[30],Boo.y[115]]]
    CD23n = [numpy.mean([Boo.x[23],Boo.x[30],Boo.x[115]]),\
             numpy.mean([Boo.y[23],Boo.y[30],Boo.y[115]])]
    #亢池#
    C_D24 = [[Boo.x[25],Boo.x[50]],[Boo.y[25],Boo.y[50]],[Boo.x[44],Boo.x[50]],[Boo.y[44],Boo.y[50]]]
    CD24n = [numpy.mean([Boo.x[25],Boo.x[44],Boo.x[50]])-labelxy,\
             numpy.mean([Boo.y[25],Boo.y[44],Boo.y[50]])]
    #陣車#
    C_D25 = [[Hya.x[18],Hya.x[111]],[Hya.y[18],Hya.y[111]],[Hya.x[111],Lup.x[17]],[Hya.y[111],Lup.y[17]]]
    CD25n = [numpy.mean([Hya.x[18],Hya.x[111],Lup.x[17]]),\
             numpy.mean([Hya.y[18],Hya.y[111],Lup.y[17]])]
    #騎官#
    C_D26 = [[Cen.x[12],Lup.x[1]],[Cen.y[12],Lup.y[1]],[Cen.x[12],Lup.x[3]],[Cen.y[12],Lup.y[3]],\
             [Lup.x[0],Lup.x[15]],[Lup.y[0],Lup.y[15]],[Lup.x[1],Lup.x[12]],[Lup.y[1],Lup.y[12]],\
             [Lup.x[2],Lup.x[3]],[Lup.y[2],Lup.y[3]],[Lup.x[4],Lup.x[12]],[Lup.y[4],Lup.y[12]],\
             [Lup.x[4],Lup.x[14]],[Lup.y[4],Lup.y[14]],[Lup.x[14],Lup.x[29]],[Lup.y[14],Lup.y[29]],\
             [Lup.x[15],Lup.x[29]],[Lup.y[15],Lup.y[29]]]
    CD26n = [numpy.mean([Cen.x[12],Lup.x[0],Lup.x[1],Lup.x[2],Lup.x[3],Lup.x[4],Lup.x[12],Lup.x[14],\
                         Lup.x[15],Lup.x[29]]),\
             numpy.mean([Cen.y[12],Lup.y[0],Lup.y[1],Lup.y[2],Lup.y[3],Lup.y[4],Lup.y[12],Lup.y[14],\
                         Lup.y[15],Lup.y[29]])+labelxy]
    #車騎#
    C_D27 = [[Lup.x[5],Lup.x[11]],[Lup.y[5],Lup.y[11]],[Lup.x[11],Lup.x[19]],[Lup.y[11],Lup.y[19]]]
    CD27n = [numpy.mean([Lup.x[5],Lup.x[11],Lup.x[19]]),\
             numpy.mean([Lup.y[5],Lup.y[11],Lup.y[19]])]
    #天輻#
    C_D28 = [[Lib.x[3],Lib.x[4]],[Lib.y[3],Lib.y[4]]]
    CD28n = [numpy.mean([Lib.x[3],Lib.x[4]])+2*labelxy,\
             numpy.mean([Lib.y[3],Lib.y[4]])]
    #騎陣將軍#
    C_D29 = []
    CD29n = [Lup.x[9],Lup.y[9]-labelxy]
    #房宿#
    C_D30 = [[Sco.x[4],Sco.x[6]],[Sco.y[4],Sco.y[6]],[Sco.x[4],Sco.x[9]],[Sco.y[4],Sco.y[9]],\
             [Sco.x[9],Sco.x[17]],[Sco.y[9],Sco.y[17]]]
    CD30n = [numpy.mean([Sco.x[4],Sco.x[6],Sco.x[9],Sco.x[17]]),\
             numpy.mean([Sco.y[4],Sco.y[6],Sco.y[9],Sco.y[17]])]
    #鉤鈐#
    C_D31 = []
    CD31n = [Sco.x[18],Sco.y[18]-labelxy]
    #鍵閉#
    C_D32 = []
    CD32n = [Sco.x[19],Sco.y[19]-labelxy]
    #罰#
    C_D33 = [[Lib.x[27],Sco.x[73]],[Lib.y[27],Sco.y[73]],[Sco.x[60],Sco.x[73]],[Sco.y[60],Sco.y[73]]]
    CD33n = [numpy.mean([Lib.x[27],Sco.x[60],Sco.x[73]])-labelxy,\
             numpy.mean([Lib.y[27],Sco.y[60],Sco.y[73]])]
    #東咸#
    C_D34 = [[Oph.x[15],Oph.x[20]],[Oph.y[15],Oph.y[20]],[Oph.x[20],Oph.x[23]],[Oph.y[20],Oph.y[23]],\
             [Oph.x[21],Oph.x[23]],[Oph.y[21],Oph.y[23]]]
    CD34n = [numpy.mean([Oph.x[15],Oph.x[20],Oph.x[21],Oph.x[23]])-labelxy,\
             numpy.mean([Oph.y[15],Oph.y[20],Oph.y[21],Oph.y[23]])]
    #西咸#
    C_D35 = [[Lib.x[6],Lib.x[11]],[Lib.y[6],Lib.y[11]],[Lib.x[6],Lib.x[25]],[Lib.y[6],Lib.y[25]],\
             [Lib.x[11],Sco.x[29]],[Lib.y[11],Sco.y[29]]]
    CD35n = [numpy.mean([Lib.x[6],Lib.x[11],Lib.x[25],Sco.x[29]])+labelxy,\
             numpy.mean([Lib.y[6],Lib.y[11],Lib.y[25],Sco.y[29]])]
    #日#
    C_D36 = []
    CD36n = [Lib.x[10],Lib.y[10]-labelxy]
    #從官#
    C_D37 = [[Lup.x[10],Lup.x[27]],[Lup.y[10],Lup.y[27]]]
    CD37n = [numpy.mean([Lup.x[10],Lup.x[27]]),\
             numpy.mean([Lup.y[10],Lup.y[27]])-labelxy]
    #心宿#
    C_D38 = [[Sco.x[0],Sco.x[8]],[Sco.y[0],Sco.y[8]],[Sco.x[0],Sco.x[10]],[Sco.y[0],Sco.y[10]]]
    CD38n = [numpy.mean([Sco.x[0],Sco.x[8],Sco.x[10]]),\
             numpy.mean([Sco.y[0],Sco.y[8],Sco.y[10]])-labelxy]
    #積卒#
    C_D39 = [[Lup.x[6],Lup.x[13]],[Lup.y[6],Lup.y[13]]]
    CD39n = [numpy.mean([Lup.x[6],Lup.x[13]])-labelxy,\
             numpy.mean([Lup.y[6],Lup.y[13]])]
    #尾宿#
    C_D40 = [[Sco.x[1],Sco.x[5]],[Sco.y[1],Sco.y[5]],[Sco.x[2],Sco.x[11]],[Sco.y[2],Sco.y[11]],\
             [Sco.x[2],Sco.x[14]],[Sco.y[2],Sco.y[14]],[Sco.x[3],Sco.x[12]],[Sco.y[3],Sco.y[12]],\
             [Sco.x[5],Sco.x[7]],[Sco.y[5],Sco.y[7]],[Sco.x[5],Sco.x[11]],[Sco.y[5],Sco.y[11]],\
             [Sco.x[12],Sco.x[16]],[Sco.y[12],Sco.y[16]],[Sco.x[14],Sco.x[16]],[Sco.y[14],Sco.y[16]]]
    CD40n = [numpy.mean([Sco.x[1],Sco.x[2],Sco.x[3],Sco.x[5],Sco.x[7],Sco.x[11],Sco.x[12],Sco.x[14],Sco.x[16]]),\
             numpy.mean([Sco.y[1],Sco.y[2],Sco.y[3],Sco.y[5],Sco.y[7],Sco.y[11],Sco.y[12],Sco.y[14],Sco.y[16]])]
    #神宮#
    C_D41 = []
    CD41n = [Sco.x[28],Sco.y[28]-labelxy]
    #龜#
    C_D42 = [[Ara.x[2],Ara.x[6]],[Ara.y[2],Ara.y[6]],[Ara.x[2],Ara.x[7]],[Ara.y[2],Ara.y[7]],\
             [Ara.x[3],Ara.x[4]],[Ara.y[3],Ara.y[4]],[Ara.x[3],Ara.x[7]],[Ara.y[3],Ara.y[7]],\
             [Ara.x[4],Ara.x[6]],[Ara.y[4],Ara.y[6]]]
    CD42n = [numpy.mean([Ara.x[2],Ara.x[3],Ara.x[4],Ara.x[6],Ara.x[7]]),\
             numpy.mean([Ara.y[2],Ara.y[3],Ara.y[4],Ara.y[6],Ara.y[7]])]
    #天江#
    C_D43 = [[Oph.x[7],Oph.x[14]],[Oph.y[7],Oph.y[14]],[Oph.x[7],Oph.x[39]],[Oph.y[7],Oph.y[39]]]
    CD43n = [numpy.mean([Oph.x[7],Oph.x[14],Oph.x[39]]),\
             numpy.mean([Oph.y[7],Oph.y[14],Oph.y[39]])-labelxy]
    #傅說#
    C_D44 = []
    CD44n = [Sco.x[13],Sco.y[13]-labelxy]
    #魚#
    C_D45 = []
    CD45n = [numpy.mean([Sco.x[65],Sco.x[78],Sco.x[86],Sco.x[97],Sco.x[98],Sco.x[109],Sco.x[124],Sco.x[144],\
                         Sco.x[150],Sco.x[155]]),\
             numpy.mean([Sco.y[65],Sco.y[78],Sco.y[86],Sco.y[97],Sco.y[98],Sco.y[109],Sco.y[124],Sco.y[144],\
                         Sco.y[150],Sco.y[155]])-labelxy]
    #箕宿#
    C_D46 = [[Sgr.x[0],Sgr.x[3]],[Sgr.y[0],Sgr.y[3]],[Sgr.x[0],Sgr.x[7]],[Sgr.y[0],Sgr.y[7]],\
             [Sgr.x[3],Sgr.x[6]],[Sgr.y[3],Sgr.y[6]]]
    CD46n = [numpy.mean([Sgr.x[0],Sgr.x[3],Sgr.x[6],Sgr.x[7]]),\
             numpy.mean([Sgr.y[0],Sgr.y[3],Sgr.y[6],Sgr.y[7]])]
    #糠#
    C_D47 = []
    CD47n = [Oph.x[16],Oph.y[16]-labelxy]
    #杵#
    C_D48 = [[Ara.x[0],Ara.x[1]],[Ara.y[0],Ara.y[1]],[Ara.x[1],Ara.x[8]],[Ara.y[1],Ara.y[8]]]
    CD48n = [numpy.mean([Ara.x[0],Ara.x[1],Ara.x[8]]),\
             numpy.mean([Ara.y[0],Ara.y[1],Ara.y[8]])-labelxy]

    C_D_list = [C_D01,C_D02,C_D03,C_D04,C_D05,C_D06,C_D07,C_D08,C_D09,C_D10,\
                C_D11,C_D12,C_D13,C_D14,C_D15,C_D16,C_D17,C_D18,C_D19,C_D20,\
                C_D21,C_D22,C_D23,C_D24,C_D25,C_D26,C_D27,C_D28,C_D29,C_D30,\
                C_D31,C_D32,C_D33,C_D34,C_D35,C_D36,C_D37,C_D38,C_D39,C_D40,\
                C_D41,C_D42,C_D43,C_D44,C_D45,C_D46,C_D47,C_D48]

    # 東宮蒼龍 linecollection
    C_D_line_z_xy1 = []
    C_D_line_z_xy2 = [] 
    C_D_line_xy1 = []
    C_D_line_xy2 = []        
    for i in range(len(C_D_list)):
        for j in range(len(C_D_list[i]))[0::2]:
            if math.hypot(C_D_list[i][j][0]-C_D_list[i][j][1],C_D_list[i][j+1][0]-C_D_list[i][j+1][1]) < hori_border:
                if i in set([0,11,18,29,37,39,45]):
                    C_D_line_z_xy1.append((C_D_list[i][j][0],C_D_list[i][j+1][0]))
                    C_D_line_z_xy2.append((C_D_list[i][j][1],C_D_list[i][j+1][1]))
                else:
                    C_D_line_xy1.append((C_D_list[i][j][0],C_D_list[i][j+1][0]))
                    C_D_line_xy2.append((C_D_list[i][j][1],C_D_list[i][j+1][1]))

    C_D_line_z_list = []
    for i in range(len(C_D_line_z_xy1)):            
        C_D_line_z_list.append([C_D_line_z_xy1[i],C_D_line_z_xy2[i]])
    
    C_D_line_list = []
    for i in range(len(C_D_line_xy1)):            
        C_D_line_list.append([C_D_line_xy1[i],C_D_line_xy2[i]])
    
    lc_C_D_z = mc.LineCollection(C_D_line_z_list, colors='yellow', zorder=2+2.5)
    lc_C_D = mc.LineCollection(C_D_line_list, colors='white', zorder=2+2.5)
    lc_C_D_z.set_alpha(plot_alpha)
    lc_C_D_z.set_clip_path(twlight_line)
    lc_C_D.set_alpha(plot_alpha)
    lc_C_D.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_D_z)
    ax0.add_collection(lc_C_D)

    CDn_list = [[CD01n,'角宿'],[CD02n,'平道'],[CD03n,'天田'],[CD04n,'進賢'],[CD05n,'周鼎'],\
                [CD06n,'天門'],[CD07n,'平'],[CD08n,'庫樓'],[CD09an,'柱'],[CD09bn,'柱'],\
                [CD09cn,'柱'],[CD09dn,'柱'],[CD10n,'衡'],[CD11n,'南門'],[CD12n,'亢宿'],\
                [CD13n,'大角'],[CD14n,'右攝提'],[CD15n,'左攝提'],[CD16n,'頓頑'],[CD17n,'陽門'],\
                [CD18n,'折威'],[CD19n,'氐宿'],[CD20n,'天乳'],[CD21n,'招搖'],[CD22n,'梗河'],\
                [CD23n,'帝席'],[CD24n,'亢池'],[CD25n,'陣車'],[CD26n,'騎官'],[CD27n,'車騎'],\
                [CD28n,'天輻'],[CD29n,'騎陣將軍'],[CD30n,'房宿'],[CD31n,'鉤鈐'],[CD32n,'鍵閉'],\
                [CD33n,'罰'],[CD34n,'東咸'],[CD35n,'西咸'],[CD36n,'日'],[CD37n,'從官'],\
                [CD38n,'心宿'],[CD39n,'積卒'],[CD40n,'尾宿'],[CD41n,'神宮'],[CD42n,'龜'],\
                [CD43n,'天江'],[CD44n,'傅說'],[CD45n,'魚'],[CD46n,'箕宿'],[CD47n,'糠'],\
                [CD48n,'杵']]

    for i in range(len(CDn_list)):
        if len(CDn_list[i][0]) != 0:
            if (CDn_list[i][0][0])**2 < (hori_border/2)**2-((CDn_list[i][0][1]))**2 \
               and max(CDn_list[i][0])-min(CDn_list[i][0]) < hori_border:
                if i in set([0,14,21,32,40,42,48]):
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0],CDn_list[i][0][1]),color='y',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=9+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]+olw,CDn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]+olw,CDn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]+olw,CDn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0],CDn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0],CDn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]-olw,CDn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]-olw,CDn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0]-olw,CDn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
##                else:
##                    ax0.annotate(str(CDn_list[i][1]),(CDn_list[i][0][0],CDn_list[i][0][1]),color='w',\
##                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ##########
    #北宮玄武#
    ##########
    #斗宿#
    C_E01 = [[Sgr.x[1],Sgr.x[8]],[Sgr.y[1],Sgr.y[8]],[Sgr.x[1],Sgr.x[9]],[Sgr.y[1],Sgr.y[9]],\
             [Sgr.x[2],Sgr.x[9]],[Sgr.y[2],Sgr.y[9]],[Sgr.x[4],Sgr.x[8]],[Sgr.y[4],Sgr.y[8]],\
             [Sgr.x[4],Sgr.x[12]],[Sgr.y[4],Sgr.y[12]]]
    CE01n = [numpy.mean([Sgr.x[1],Sgr.x[2],Sgr.x[4],Sgr.x[8],Sgr.x[9],Sgr.x[12]]),\
             numpy.mean([Sgr.y[1],Sgr.y[2],Sgr.y[4],Sgr.y[8],Sgr.y[9],Sgr.y[12]])]
    #建#
    C_E02 = [[Sgr.x[5],Sgr.x[36]],[Sgr.y[5],Sgr.y[36]],[Sgr.x[5],Sgr.x[11]],[Sgr.y[5],Sgr.y[11]],\
             [Sgr.x[10],Sgr.x[11]],[Sgr.y[10],Sgr.y[11]],[Sgr.x[13],Sgr.x[24]],[Sgr.y[13],Sgr.y[24]],\
             [Sgr.x[13],Sgr.x[36]],[Sgr.y[13],Sgr.y[36]]]
    CE02n = [numpy.mean([Sgr.x[5],Sgr.x[10],Sgr.x[11],Sgr.x[13],Sgr.x[24],Sgr.x[36]]),\
             numpy.mean([Sgr.y[5],Sgr.y[10],Sgr.y[11],Sgr.y[13],Sgr.y[24],Sgr.y[36]])]
    #天弁#
    C_E03 = [[Aql.x[5],Aql.x[9]],[Aql.y[5],Aql.y[9]],[Aql.x[5],Aql.x[38]],[Aql.y[5],Aql.y[38]],\
             [Aql.x[9],Sct.x[5]],[Aql.y[9],Sct.y[5]],[Aql.x[37],Aql.x[38]],[Aql.y[37],Aql.y[38]],\
             [Sct.x[0],Sct.x[4]],[Sct.y[0],Sct.y[4]],[Sct.x[1],Sct.x[5]],[Sct.y[1],Sct.y[5]],\
             [Sct.x[1],Sct.x[6]],[Sct.y[1],Sct.y[6]],[Sct.x[4],Sct.x[6]],[Sct.y[4],Sct.y[6]],]
    CE03n = [numpy.mean([Aql.x[5],Aql.x[9],Aql.x[37],Aql.x[38],Sct.x[0],Sct.x[1],Sct.x[4],Sct.x[5],\
                         Sct.x[6]]),\
             numpy.mean([Aql.y[5],Aql.y[9],Aql.y[37],Aql.y[38],Sct.y[0],Sct.y[1],Sct.y[4],Sct.y[5],\
                         Sct.y[6]])]
    #鱉#
    C_E04 = [[CrA.x[0],CrA.x[1]],[CrA.y[0],CrA.y[1]],[CrA.x[0],CrA.x[7]],[CrA.y[0],CrA.y[7]],\
             [CrA.x[1],CrA.x[2]],[CrA.y[1],CrA.y[2]],[CrA.x[2],CrA.x[4]],[CrA.y[2],CrA.y[4]],\
             [CrA.x[3],CrA.x[8]],[CrA.y[3],CrA.y[8]],[CrA.x[3],Tel.x[0]],[CrA.y[3],Tel.y[0]],\
             [CrA.x[4],CrA.x[19]],[CrA.y[4],CrA.y[19]],[CrA.x[5],CrA.x[7]],[CrA.y[5],CrA.y[7]],\
             [CrA.x[5],CrA.x[15]],[CrA.y[5],CrA.y[15]],[CrA.x[8],CrA.x[15]],[CrA.y[8],CrA.y[15]],\
             [Tel.x[0],CrA.x[19]],[Tel.y[0],CrA.y[19]]]
    CE04n = [numpy.mean([CrA.x[0],CrA.x[1],CrA.x[2],CrA.x[3],CrA.x[4],CrA.x[5],CrA.x[7],CrA.x[8],\
                         CrA.x[15],CrA.x[19],Tel.x[0]]),\
             numpy.mean([CrA.y[0],CrA.y[1],CrA.y[2],CrA.y[3],CrA.y[4],CrA.y[5],CrA.y[7],CrA.y[8],\
                         CrA.y[15],CrA.y[19],Tel.y[0]])]
    #天雞#
    C_E05 = [[Sgr.x[34],Sgr.x[42]],[Sgr.y[34],Sgr.y[42]]]
    CE05n = [numpy.mean([Sgr.x[34],Sgr.x[42]]),\
             numpy.mean([Sgr.y[34],Sgr.y[42]])]
    #天籥#
    C_E06 = [[Oph.x[31],Oph.x[34]],[Oph.y[31],Oph.y[34]],[Oph.x[31],Oph.x[91]],[Oph.y[31],Oph.y[91]],\
             [Oph.x[34],Sgr.x[141]],[Oph.y[34],Sgr.y[141]],[Oph.x[91],Sgr.x[20]],[Oph.y[91],Sgr.y[20]]]
    CE06n = [numpy.mean([Oph.x[31],Oph.x[34],Oph.x[91],Sgr.x[20],Sgr.x[141]]),\
             numpy.mean([Oph.y[31],Oph.y[34],Oph.y[91],Sgr.y[20],Sgr.y[141]])]
    #狗國#
    C_E07 = [[Sgr.x[19],Sgr.x[22]],[Sgr.y[19],Sgr.y[22]],[Sgr.x[22],Sgr.x[32]],[Sgr.y[22],Sgr.y[32]],\
             [Sgr.x[27],Sgr.x[32]],[Sgr.y[27],Sgr.y[32]]]
    CE07n = [numpy.mean([Sgr.x[19],Sgr.x[22],Sgr.x[27],Sgr.x[32]]),\
             numpy.mean([Sgr.y[19],Sgr.y[22],Sgr.y[27],Sgr.y[32]])]
    #天淵#
    C_E08 = [[Sgr.x[14],Sgr.x[15]],[Sgr.y[14],Sgr.y[15]]]
    CE08n = [numpy.mean([Sgr.x[14],Sgr.x[15]]),\
             numpy.mean([Sgr.y[14],Sgr.y[15]])]
    #狗#
    C_E09 = [[Sgr.x[23],Sgr.x[41]],[Sgr.y[23],Sgr.y[41]]]
    CE09n = [numpy.mean([Sgr.x[23],Sgr.x[41]]),\
             numpy.mean([Sgr.y[23],Sgr.y[41]])]
    #農丈人#
    C_E10 = []
    CE10n = [Sgr.x[35],Sgr.y[35]]
    #牛宿#
    C_E11 = [[Cap.x[1],Cap.x[2]],[Cap.y[1],Cap.y[2]],[Cap.x[1],Cap.x[15]],[Cap.y[1],Cap.y[15]],\
             [Cap.x[1],Cap.x[24]],[Cap.y[1],Cap.y[24]],[Cap.x[1],Cap.x[39]],[Cap.y[1],Cap.y[39]],\
             [Cap.x[15],Cap.x[45]],[Cap.y[15],Cap.y[45]],[Cap.x[24],Cap.x[45]],[Cap.y[24],Cap.y[45]]]
    CE11n = [numpy.mean([Cap.x[1],Cap.x[2],Cap.x[15],Cap.x[24],Cap.x[39],Cap.x[45]]),\
             numpy.mean([Cap.y[1],Cap.y[2],Cap.y[15],Cap.y[24],Cap.y[39],Cap.y[45]])]
    #天田#
    C_E12 = [[Cap.x[6],Cap.x[7]],[Cap.y[6],Cap.y[7]],[Cap.x[7],Mic.x[10]],[Cap.y[7],Mic.y[10]],\
             [Cap.x[10],Mic.x[10]],[Cap.y[10],Mic.y[10]]]
    CE12n = [numpy.mean([Cap.x[6],Cap.x[7],Cap.x[10],Mic.x[10]]),\
             numpy.mean([Cap.y[6],Cap.y[7],Cap.y[10],Mic.y[10]])]
    #九坎#
    C_E13 = []
    CE13n = [] # ???
    #河鼓#
    C_E14 = [[Aql.x[0],Aql.x[1]],[Aql.y[0],Aql.y[1]],[Aql.x[0],Aql.x[6]],[Aql.y[0],Aql.y[6]]]
    CE14n = [numpy.mean([Aql.x[0],Aql.x[1],Aql.x[6]]),\
             numpy.mean([Aql.y[0],Aql.y[1],Aql.y[6]])]
    #織女#
    C_E15 = [[Lyr.x[0],Lyr.x[12]],[Lyr.y[0],Lyr.y[12]],[Lyr.x[6],Lyr.x[12]],[Lyr.y[6],Lyr.y[12]]]
    CE15n = [numpy.mean([Lyr.x[0],Lyr.x[6],Lyr.x[12]]),\
             numpy.mean([Lyr.y[0],Lyr.y[6],Lyr.y[12]])]
    #左旗#
    C_E16 = [[Aql.x[52],Del.x[6]],[Aql.y[52],Del.y[6]],[Aql.x[52],Sge.x[8]],[Aql.y[52],Sge.y[8]],\
             [Sge.x[0],Sge.x[4]],[Sge.y[0],Sge.y[4]],[Sge.x[0],Sge.x[7]],[Sge.y[0],Sge.y[7]],\
             [Sge.x[1],Sge.x[3]],[Sge.y[1],Sge.y[3]],[Sge.x[1],Sge.x[4]],[Sge.y[1],Sge.y[4]],\
             [Sge.x[2],Sge.x[3]],[Sge.y[2],Sge.y[3]],[Sge.x[7],Sge.x[8]],[Sge.y[7],Sge.y[8]]]
    CE16n = [numpy.mean([Aql.x[52],Del.x[6],Sge.x[0],Sge.x[1],Sge.x[2],Sge.x[3],Sge.x[4],Sge.x[7],\
                         Sge.x[8]]),\
             numpy.mean([Aql.y[52],Del.y[6],Sge.y[0],Sge.y[1],Sge.y[2],Sge.y[3],Sge.y[4],Sge.y[7],\
                         Sge.y[8]])]
    #右旗#
    C_E17 = [[Aql.x[4],Aql.x[13]],[Aql.y[4],Aql.y[13]],[Aql.x[4],Aql.x[27]],[Aql.y[4],Aql.y[27]],\
             [Aql.x[11],Aql.x[13]],[Aql.y[11],Aql.y[13]],[Aql.x[11],Aql.x[39]],[Aql.y[11],Aql.y[39]],\
             [Aql.x[12],Aql.x[27]],[Aql.y[12],Aql.y[27]],[Aql.x[17],Aql.x[39]],[Aql.y[17],Aql.y[39]],\
             [Aql.x[17],Aql.x[57]],[Aql.y[17],Aql.y[57]]]
    CE17n = [numpy.mean([Aql.x[4],Aql.x[11],Aql.x[12],Aql.x[13],Aql.x[17],Aql.x[27],Aql.x[39],Aql.x[57]]),\
             numpy.mean([Aql.y[4],Aql.y[11],Aql.y[12],Aql.y[13],Aql.y[17],Aql.y[27],Aql.y[39],Aql.y[57]])]
    #天桴#
    C_E18 = [[Aql.x[3],Aql.x[53]],[Aql.y[3],Aql.y[53]],[Aql.x[7],Aql.x[48]],[Aql.y[7],Aql.y[48]],\
             [Aql.x[48],Aql.x[53]],[Aql.y[48],Aql.y[53]]]
    CE18n = [numpy.mean([Aql.x[3],Aql.x[7],Aql.x[48],Aql.x[53]]),\
             numpy.mean([Aql.y[3],Aql.y[7],Aql.y[48],Aql.y[53]])]
    #羅堰#
    C_E19 = [[Cap.x[19],Cap.x[21]],[Cap.y[19],Cap.y[21]],[Cap.x[19],Cap.x[44]],[Cap.y[19],Cap.y[44]]]
    CE19n = [numpy.mean([Cap.x[19],Cap.x[21],Cap.x[44]]),\
             numpy.mean([Cap.y[19],Cap.y[21],Cap.y[44]])]
    #漸臺#
    C_E20 = [[Lyr.x[1],Lyr.x[2]],[Lyr.y[1],Lyr.y[2]],[Lyr.x[1],Lyr.x[19]],[Lyr.y[1],Lyr.y[19]],\
             [Lyr.x[2],Lyr.x[4]],[Lyr.y[2],Lyr.y[4]]]
    CE20n = [numpy.mean([Lyr.x[1],Lyr.x[2],Lyr.x[4],Lyr.x[19]]),\
             numpy.mean([Lyr.y[1],Lyr.y[2],Lyr.y[4],Lyr.y[19]])]
    #輦道#
    C_E21 = [[Cyg.x[46],Cyg.x[57]],[Cyg.y[46],Cyg.y[57]],[Cyg.x[57],Lyr.x[7]],[Cyg.y[57],Lyr.y[7]],\
             [Lyr.x[3],Lyr.x[8]],[Lyr.y[3],Lyr.y[8]],[Lyr.x[7],Lyr.x[8]],[Lyr.y[7],Lyr.y[8]]]
    CE21n = [numpy.mean([Cyg.x[46],Cyg.x[57],Lyr.x[3],Lyr.x[7],Lyr.x[8]]),\
             numpy.mean([Cyg.y[46],Cyg.y[57],Lyr.y[3],Lyr.y[7],Lyr.y[8]])]
    #女宿#
    C_E22 = [[Aqr.x[5],Aqr.x[28]],[Aqr.y[5],Aqr.y[28]],[Aqr.x[16],Aqr.x[94]],[Aqr.y[16],Aqr.y[94]],\
             [Aqr.x[28],Aqr.x[94]],[Aqr.y[28],Aqr.y[94]]]
    CE22n = [numpy.mean([Aqr.x[5],Aqr.x[16],Aqr.x[28],Aqr.x[94]]),\
             numpy.mean([Aqr.y[5],Aqr.y[16],Aqr.y[28],Aqr.y[94]])]
    #十二國#
    C_E23 = []
    CE23n = [numpy.mean([Cap.x[4],Cap.x[5],Cap.x[9],Cap.x[11],Cap.x[16],Cap.x[22],Cap.x[27],Cap.x[28],\
                         Cap.x[29],Cap.x[33],Cap.x[36],Cap.x[37],Cap.x[62],Cap.x[63]]),\
             numpy.mean([Cap.y[4],Cap.y[5],Cap.y[9],Cap.y[11],Cap.y[16],Cap.y[22],Cap.y[27],Cap.y[28],\
                         Cap.y[29],Cap.y[33],Cap.y[36],Cap.y[37],Cap.y[62],Cap.y[63]])]
    #燕#
    C_E23a = []
    CE23an = [Cap.x[4],Cap.y[4]]
    #周#
    C_E23b = []
    CE23bn = [Cap.x[16],Cap.y[16]]
    #晉#
    C_E23c = []
    CE23cn = [Cap.x[11],Cap.y[11]]
    #魏#
    C_E23d = []
    CE23dn = [Cap.x[28],Cap.y[28]]
    #楚#
    C_E23e = []
    CE23en = [Cap.x[22],Cap.y[22]]
    #齊#
    C_E23f = []
    CE23fn = [Cap.x[27],Cap.y[27]]
    #韓#
    C_E23g = []
    CE23gn = [Cap.x[37],Cap.y[37]]
    #越#
    C_E23h = []
    CE23hn = [Cap.x[36],Cap.y[36]]
    #鄭#
    C_E23i = []
    CE23in = [Cap.x[62],Cap.y[62]]
    #趙#
    C_E23j = []
    CE23jn = [Cap.x[63],Cap.y[63]]
    #代#
    C_E23k = [[Cap.x[9],Cap.x[33]],[Cap.y[9],Cap.y[33]]]
    CE23kn = [numpy.mean([Cap.x[9],Cap.x[33]]),\
              numpy.mean([Cap.y[9],Cap.y[33]])]
    #秦#
    C_E23l = [[Cap.x[5],Cap.x[29]],[Cap.y[5],Cap.y[29]]]
    CE23ln = [numpy.mean([Cap.x[5],Cap.x[29]]),\
              numpy.mean([Cap.y[5],Cap.y[29]])]
    #離珠#
    C_E24 = [[Aql.x[10],Aql.x[15]],[Aql.y[10],Aql.y[15]],[Aql.x[10],Aqr.x[38]],[Aql.y[10],Aqr.y[38]],\
             [Aql.x[15],Aql.x[16]],[Aql.y[15],Aql.y[16]]]
    CE24n = [numpy.mean([Aql.x[10],Aql.x[15],Aql.x[16],Aqr.x[38]]),\
             numpy.mean([Aql.y[10],Aql.y[15],Aql.y[16],Aqr.y[38]])]
    #敗瓜#
    C_E25 = [[Del.x[2],Del.x[10]],[Del.y[2],Del.y[10]],[Del.x[2],Del.x[11]],[Del.y[2],Del.y[11]],\
             [Del.x[7],Del.x[11]],[Del.y[7],Del.y[11]],[Del.x[10],Del.x[16]],[Del.y[10],Del.y[16]],\
             [Del.x[11],Del.x[16]],[Del.y[11],Del.y[16]]]
    CE25n = [numpy.mean([Del.x[2],Del.x[7],Del.x[10],Del.x[11],Del.x[16]]),\
             numpy.mean([Del.y[2],Del.y[7],Del.y[10],Del.y[11],Del.y[16]])]
    #瓠瓜#
    C_E26 = [[Del.x[0],Del.x[1]],[Del.y[0],Del.y[1]],[Del.x[0],Del.x[4]],[Del.y[0],Del.y[4]],\
             [Del.x[0],Del.x[5]],[Del.y[0],Del.y[5]],[Del.x[1],Del.x[3]],[Del.y[1],Del.y[3]],\
             [Del.x[3],Del.x[4]],[Del.y[3],Del.y[4]]]
    CE26n = [numpy.mean([Del.x[0],Del.x[1],Del.x[3],Del.x[4],Del.x[5]]),\
             numpy.mean([Del.y[0],Del.y[1],Del.y[3],Del.y[4],Del.y[5]])]
    #天津#
    C_E27 = [[Cyg.x[0],Cyg.x[10]],[Cyg.y[0],Cyg.y[10]],[Cyg.x[0],Cyg.x[12]],[Cyg.y[0],Cyg.y[12]],\
             [Cyg.x[1],Cyg.x[2]],[Cyg.y[1],Cyg.y[2]],[Cyg.x[1],Cyg.x[3]],[Cyg.y[1],Cyg.y[3]],\
             [Cyg.x[2],Cyg.x[5]],[Cyg.y[2],Cyg.y[5]],[Cyg.x[3],Cyg.x[10]],[Cyg.y[3],Cyg.y[10]],\
             [Cyg.x[5],Cyg.x[22]],[Cyg.y[5],Cyg.y[22]],[Cyg.x[7],Cyg.x[12]],[Cyg.y[7],Cyg.y[12]],\
             [Cyg.x[7],Cyg.x[22]],[Cyg.y[7],Cyg.y[22]]]
    CE27n = [numpy.mean([Cyg.x[0],Cyg.x[1],Cyg.x[2],Cyg.x[3],Cyg.x[5],Cyg.x[7],Cyg.x[10],Cyg.x[12],\
                         Cyg.x[22]]),\
             numpy.mean([Cyg.y[0],Cyg.y[1],Cyg.y[2],Cyg.y[3],Cyg.y[5],Cyg.y[7],Cyg.y[10],Cyg.y[12],\
                         Cyg.y[22]])]
    #奚仲#
    C_E28 = [[Cyg.x[8],Cyg.x[9]],[Cyg.y[8],Cyg.y[9]],[Cyg.x[9],Cyg.x[23]],[Cyg.y[9],Cyg.y[23]],\
             [Cyg.x[23],Cyg.x[135]],[Cyg.y[23],Cyg.y[135]]]
    CE28n = [numpy.mean([Cyg.x[8],Cyg.x[9],Cyg.x[23],Cyg.x[135]]),\
             numpy.mean([Cyg.y[8],Cyg.y[9],Cyg.y[23],Cyg.y[135]])]
    #扶筐#
    C_E29 = [[Dra.x[20],Dra.x[36]],[Dra.y[20],Dra.y[36]],[Dra.x[20],Dra.x[80]],[Dra.y[20],Dra.y[80]],\
             [Dra.x[22],Dra.x[36]],[Dra.y[22],Dra.y[36]],[Dra.x[22],Dra.x[42]],[Dra.y[22],Dra.y[42]],\
             [Dra.x[63],Dra.x[72]],[Dra.y[63],Dra.y[72]],[Dra.x[72],Dra.x[80]],[Dra.y[72],Dra.y[80]]]
    CE29n = [numpy.mean([Dra.x[20],Dra.x[22],Dra.x[36],Dra.x[42],Dra.x[63],Dra.x[72],Dra.x[80]]),\
             numpy.mean([Dra.y[20],Dra.y[22],Dra.y[36],Dra.y[42],Dra.y[63],Dra.y[72],Dra.y[80]])]
    #虛宿#
    C_E30 = [[Equ.x[0],Aqr.x[0]],[Equ.y[0],Aqr.y[0]]]
    CE30n = [numpy.mean([Equ.x[0],Aqr.x[0]]),\
             numpy.mean([Equ.y[0],Aqr.y[0]])]
    #司命#
    C_E31 = [[Aqr.x[65],Aqr.x[126]],[Aqr.y[65],Aqr.y[126]]]
    CE31n = [numpy.mean([Aqr.x[65],Aqr.x[126]]),\
             numpy.mean([Aqr.y[65],Aqr.y[126]])]
    #司祿#
    C_E32 = [[Aqr.x[36],Peg.x[63]],[Aqr.y[36],Peg.y[63]]]
    CE32n = [numpy.mean([Aqr.x[36],Peg.x[63]]),\
             numpy.mean([Aqr.y[36],Peg.y[63]])]
    #司危#
    C_E33 = [[Equ.x[3],Equ.x[6]],[Equ.y[3],Equ.y[6]]]
    CE33n = [numpy.mean([Equ.x[3],Equ.x[6]]),\
             numpy.mean([Equ.y[3],Equ.y[6]])]
    #司非#
    C_E34 = [[Equ.x[1],Equ.x[2]],[Equ.y[1],Equ.y[2]]]
    CE34n = [numpy.mean([Equ.x[1],Equ.x[2]]),\
             numpy.mean([Equ.y[1],Equ.y[2]])]
    #哭#
    C_E35 = [[Cap.x[17],Aqr.x[52]],[Cap.y[17],Aqr.y[52]]]
    CE35n = [numpy.mean([Cap.x[17],Aqr.x[52]]),\
             numpy.mean([Cap.y[17],Aqr.y[52]])]
    #泣#
    C_E36 = [[Aqr.x[10],Aqr.x[50]],[Aqr.y[10],Aqr.y[50]]]
    CE36n = [numpy.mean([Aqr.x[10],Aqr.x[50]]),\
             numpy.mean([Aqr.y[10],Aqr.y[50]])]
    #天壘城#
    C_E37 = [[Aqr.x[20],Cap.x[26]],[Aqr.y[20],Cap.y[26]],[Aqr.x[20],Aqr.x[95]],[Aqr.y[20],Aqr.y[95]],\
             [Aqr.x[23],Cap.x[18]],[Aqr.y[23],Cap.y[18]],[Aqr.x[53],Cap.x[26]],[Aqr.y[53],Cap.y[26]],\
             [Aqr.x[53],Cap.x[30]],[Aqr.y[53],Cap.y[30]],[Aqr.x[66],Aqr.x[95]],[Aqr.y[66],Aqr.y[95]],\
             [Cap.x[18],Cap.x[30]],[Cap.y[18],Cap.y[30]]]
    CE37n = [numpy.mean([Aqr.x[20],Aqr.x[23],Aqr.x[53],Aqr.x[66],Aqr.x[95],Cap.x[18],Cap.x[26],Cap.x[30]]),\
             numpy.mean([Aqr.y[20],Aqr.y[23],Aqr.y[53],Aqr.y[66],Aqr.y[95],Cap.y[18],Cap.y[26],Cap.y[30]])]
    #敗臼#
    C_E38 = [[Gru.x[2],Gru.x[9]],[Gru.y[2],Gru.y[9]],[Gru.x[9],PsA.x[5]],[Gru.y[9],PsA.y[5]],\
             [PsA.x[5],PsA.x[31]],[PsA.y[5],PsA.y[31]]]
    CE38n = [numpy.mean([Gru.x[2],Gru.x[9],PsA.x[5],PsA.x[31]]),\
             numpy.mean([Gru.y[2],Gru.y[9],PsA.y[5],PsA.y[31]])]
    #離瑜#
    C_E39 = []
    CE39n = [Mic.x[1],Mic.y[1]]
    #危宿#
    C_E40 = [[Aqr.x[1],Peg.x[7]],[Aqr.y[1],Peg.y[7]],[Peg.x[0],Peg.x[7]],[Peg.y[0],Peg.y[7]]]
    CE40n = [numpy.mean([Aqr.x[1],Peg.x[0],Peg.x[7]]),\
             numpy.mean([Aqr.y[1],Peg.y[0],Peg.y[7]])]
    #墳墓#
    C_E41 = [[Aqr.x[6],Aqr.x[17]],[Aqr.y[6],Aqr.y[17]],[Aqr.x[9],Aqr.x[17]],[Aqr.y[9],Aqr.y[17]],\
             [Aqr.x[17],Aqr.x[22]],[Aqr.y[17],Aqr.y[22]]]
    CE41n = [numpy.mean([Aqr.x[6],Aqr.x[9],Aqr.x[17],Aqr.x[22]]),\
             numpy.mean([Aqr.y[6],Aqr.y[9],Aqr.y[17],Aqr.y[22]])]
    #人#
    C_E42 = [[Peg.x[10],Peg.x[14]],[Peg.y[10],Peg.y[14]],[Peg.x[10],Peg.x[18]],[Peg.y[10],Peg.y[18]],\
             [Peg.x[14],Peg.x[39]],[Peg.y[14],Peg.y[39]]]
    CE42n = [numpy.mean([Peg.x[10],Peg.x[14],Peg.x[18],Peg.x[39]]),\
             numpy.mean([Peg.y[10],Peg.y[14],Peg.y[18],Peg.y[39]])]
    #杵#
    C_E43 = [[Lac.x[1],Peg.x[13]],[Lac.y[1],Peg.y[13]],[Peg.x[13],Peg.x[69]],[Peg.y[13],Peg.y[69]]]
    CE43n = [numpy.mean([Lac.x[1],Peg.x[13],Peg.x[69]]),\
             numpy.mean([Lac.y[1],Peg.y[13],Peg.y[69]])]
    #臼#
    C_E44 = [[Cyg.x[29],Peg.x[11]],[Cyg.y[29],Peg.y[11]],[Peg.x[8],Peg.x[11]],[Peg.y[8],Peg.y[11]],\
             [Peg.x[8],Peg.x[25]],[Peg.y[8],Peg.y[25]]]
    CE44n = [numpy.mean([Cyg.x[29],Peg.x[8],Peg.x[11],Peg.x[25]]),\
             numpy.mean([Cyg.y[29],Peg.y[8],Peg.y[11],Peg.y[25]])]
    #車府#
    C_E45 = [[Cyg.x[6],Cyg.x[31]],[Cyg.y[6],Cyg.y[31]],[Cyg.x[6],Cyg.x[48]],[Cyg.y[6],Cyg.y[48]],\
             [Cyg.x[15],Cyg.x[31]],[Cyg.y[15],Cyg.y[31]],[Cyg.x[15],Lac.x[7]],[Cyg.y[15],Lac.y[7]],\
             [Lac.x[4],Lac.x[7]],[Lac.y[4],Lac.y[7]],[Lac.x[4],Lac.x[11]],[Lac.y[4],Lac.y[11]]]
    CE45n = [numpy.mean([Cyg.x[6],Cyg.x[15],Cyg.x[31],Cyg.x[48],Lac.x[4],Lac.x[7],Lac.x[11]]),\
             numpy.mean([Cyg.y[6],Cyg.y[15],Cyg.y[31],Cyg.y[48],Lac.y[4],Lac.y[7],Lac.y[11]])]
    #天鉤#
    C_E46 = [[Cep.x[0],Cep.x[4]],[Cep.y[0],Cep.y[4]],[Cep.x[0],Cep.x[12]],[Cep.y[0],Cep.y[12]],\
             [Cep.x[4],Cep.x[9]],[Cep.y[4],Cep.y[9]],[Cep.x[5],Cep.x[35]],[Cep.y[5],Cep.y[35]],\
             [Cep.x[5],Cep.x[44]],[Cep.y[5],Cep.y[44]],[Cep.x[9],Cep.x[55]],[Cep.y[9],Cep.y[55]],\
             [Cep.x[12],Cep.x[44]],[Cep.y[12],Cep.y[44]],[Cep.x[20],Cep.x[35]],[Cep.y[20],Cep.y[35]]]
    CE46n = [numpy.mean([Cep.x[0],Cep.x[4],Cep.x[5],Cep.x[9],Cep.x[12],Cep.x[20],Cep.x[35],Cep.x[44],\
                         Cep.x[55]]),\
             numpy.mean([Cep.y[0],Cep.y[4],Cep.y[5],Cep.y[9],Cep.y[12],Cep.y[20],Cep.y[35],Cep.y[44],\
                         Cep.y[55]])]
    #造父#
    C_E47 = [[Cep.x[3],Cep.x[6]],[Cep.y[3],Cep.y[6]],[Cep.x[3],Cep.x[24]],[Cep.y[3],Cep.y[24]],\
             [Cep.x[7],Cep.x[11]],[Cep.y[7],Cep.y[11]],[Cep.x[7],Cep.x[24]],[Cep.y[7],Cep.y[24]]]
    CE47n = [numpy.mean([Cep.x[3],Cep.x[6],Cep.x[7],Cep.x[11],Cep.x[24]]),\
             numpy.mean([Cep.y[3],Cep.y[6],Cep.y[7],Cep.y[11],Cep.y[24]])]
    #蓋屋#
    C_E48 = [[Aqr.x[24],Aqr.x[46]],[Aqr.y[24],Aqr.y[46]]]
    CE48n = [numpy.mean([Aqr.x[24],Aqr.x[46]]),\
             numpy.mean([Aqr.y[24],Aqr.y[46]])]
    #虛梁#
    C_E49 = [[Aqr.x[33],Aqr.x[68]],[Aqr.y[33],Aqr.y[68]],[Aqr.x[33],Aqr.x[75]],[Aqr.y[33],Aqr.y[75]],\
             [Aqr.x[71],Aqr.x[75]],[Aqr.y[71],Aqr.y[75]]]
    CE49n = [numpy.mean([Aqr.x[33],Aqr.x[68],Aqr.x[71],Aqr.x[75]]),\
             numpy.mean([Aqr.y[33],Aqr.y[68],Aqr.y[71],Aqr.y[75]])]
    #天錢#
    C_E50 = [[PsA.x[4],PsA.x[6]],[PsA.y[4],PsA.y[6]],[PsA.x[4],PsA.x[9]],[PsA.y[4],PsA.y[9]],\
             [PsA.x[6],PsA.x[7]],[PsA.y[6],PsA.y[7]],[PsA.x[7],PsA.x[9]],[PsA.y[7],PsA.y[9]]]
    CE50n = [numpy.mean([PsA.x[4],PsA.x[6],PsA.x[7],PsA.x[9]]),\
             numpy.mean([PsA.y[4],PsA.y[6],PsA.y[7],PsA.y[9]])]
    #室宿#
    C_E51 = [[Peg.x[1],Peg.x[2]],[Peg.y[1],Peg.y[2]]]
    CE51n = [numpy.mean([Peg.x[1],Peg.x[2]]),\
             numpy.mean([Peg.y[1],Peg.y[2]])]
    #離宮#
    C_E52 = [[Peg.x[4],Peg.x[23]],[Peg.y[4],Peg.y[23]],[Peg.x[6],Peg.x[9]],[Peg.y[6],Peg.y[9]],\
             [Peg.x[15],Peg.x[19]],[Peg.y[15],Peg.y[19]]]
    CE52n = [numpy.mean([Peg.x[4],Peg.x[6],Peg.x[9],Peg.x[15],Peg.x[19],Peg.x[23]]),\
             numpy.mean([Peg.y[4],Peg.y[6],Peg.y[9],Peg.y[15],Peg.y[19],Peg.y[23]])]
    #雷電#
    C_E53 = [[Peg.x[5],Peg.x[12]],[Peg.y[5],Peg.y[12]],[Peg.x[12],Peg.x[37]],[Peg.y[12],Peg.y[37]],\
             [Peg.x[16],Peg.x[34]],[Peg.y[16],Peg.y[34]],[Peg.x[16],Peg.x[37]],[Peg.y[16],Peg.y[37]],\
             [Peg.x[17],Peg.x[34]],[Peg.y[17],Peg.y[34]]]
    CE53n = [numpy.mean([Peg.x[5],Peg.x[12],Peg.x[16],Peg.x[17],Peg.x[34],Peg.x[37]]),\
             numpy.mean([Peg.y[5],Peg.y[12],Peg.y[16],Peg.y[17],Peg.y[34],Peg.y[37]])]
    #壘壁陣#
    C_E54 = [[Aqr.x[4],Aqr.x[12]],[Aqr.y[4],Aqr.y[12]],[Aqr.x[4],Aqr.x[29]],[Aqr.y[4],Aqr.y[29]],\
             [Aqr.x[13],Aqr.x[29]],[Aqr.y[13],Aqr.y[29]],[Aqr.x[12],Psc.x[20]],[Aqr.y[12],Psc.y[20]],\
             [Cap.x[0],Aqr.x[13]],[Cap.y[0],Aqr.y[13]],[Cap.x[0],Cap.x[3]],[Cap.y[0],Cap.y[3]],\
             [Cap.x[0],Cap.x[13]],[Cap.y[0],Cap.y[13]],[Cap.x[3],Cap.x[12]],[Cap.y[3],Cap.y[12]],\
             [Cap.x[12],Cap.x[13]],[Cap.y[12],Cap.y[13]],[Psc.x[8],Psc.x[14]],[Psc.y[8],Psc.y[14]],\
             [Psc.x[8],Psc.x[20]],[Psc.y[8],Psc.y[20]],[Psc.x[14],Psc.x[26]],[Psc.y[14],Psc.y[26]],\
             [Psc.x[20],Psc.x[26]],[Psc.y[20],Psc.y[26]]]
    CE54n = [numpy.mean([Aqr.x[4],Aqr.x[12],Aqr.x[13],Aqr.x[29],Cap.x[0],Cap.x[3],Cap.x[12],Cap.x[13],\
                         Psc.x[8],Psc.x[14],Psc.x[20],Psc.x[26]]),\
             numpy.mean([Aqr.y[4],Aqr.y[12],Aqr.y[13],Aqr.y[29],Cap.y[0],Cap.y[3],Cap.y[12],Cap.y[13],\
                         Psc.y[8],Psc.y[14],Psc.y[20],Psc.y[26]])]
    #羽林軍#
    C_E55 = [[Aqr.x[2],Aqr.x[61]],[Aqr.y[2],Aqr.y[61]],[Aqr.x[2],Aqr.x[64]],[Aqr.y[2],Aqr.y[64]],\
             [Aqr.x[3],Aqr.x[26]],[Aqr.y[3],Aqr.y[26]],[Aqr.x[7],Aqr.x[41]],[Aqr.y[7],Aqr.y[41]],\
             [Aqr.x[8],Aqr.x[77]],[Aqr.y[8],Aqr.y[77]],[Aqr.x[11],Aqr.x[14]],[Aqr.y[11],Aqr.y[14]],\
             [Aqr.x[14],Aqr.x[31]],[Aqr.y[14],Aqr.y[31]],[Aqr.x[15],Aqr.x[134]],[Aqr.y[15],Aqr.y[134]],\
             [Aqr.x[18],Aqr.x[26]],[Aqr.y[18],Aqr.y[26]],[Aqr.x[19],Aqr.x[32]],[Aqr.y[19],Aqr.y[32]],\
             [Aqr.x[27],Aqr.x[134]],[Aqr.y[27],Aqr.y[134]],[Aqr.x[32],Aqr.x[34]],[Aqr.y[32],Aqr.y[34]],\
             [Aqr.x[35],Aqr.x[41]],[Aqr.y[35],Aqr.y[41]],[Aqr.x[37],Aqr.x[56]],[Aqr.y[37],Aqr.y[56]],\
             [Aqr.x[40],Aqr.x[43]],[Aqr.y[40],Aqr.y[43]],[Aqr.x[47],Aqr.x[78]],[Aqr.y[47],Aqr.y[78]],\
             [Aqr.x[56],PsA.x[13]],[Aqr.y[56],PsA.y[13]],[Aqr.x[73],Aqr.x[90]],[Aqr.y[73],Aqr.y[90]],\
             [Aqr.x[77],Aqr.x[114]],[Aqr.y[77],Aqr.y[114]],[PsA.x[1],PsA.x[25]],[PsA.y[1],PsA.y[25]]]
    CE55n = [numpy.mean([Aqr.x[2],Aqr.x[3],Aqr.x[7],Aqr.x[8],Aqr.x[11],Aqr.x[14],Aqr.x[15],Aqr.x[18],\
                         Aqr.x[19],Aqr.x[26],Aqr.x[27],Aqr.x[31],Aqr.x[32],Aqr.x[34],Aqr.x[35],Aqr.x[37],\
                         Aqr.x[40],Aqr.x[41],Aqr.x[43],Aqr.x[47],Aqr.x[56],Aqr.x[61],Aqr.x[64],Aqr.x[73],\
                         Aqr.x[77],Aqr.x[78],Aqr.x[90],Aqr.x[114],Aqr.x[134],PsA.x[1],PsA.x[13],PsA.x[25]]),\
             numpy.mean([Aqr.y[2],Aqr.y[3],Aqr.y[7],Aqr.y[8],Aqr.y[11],Aqr.y[14],Aqr.y[15],Aqr.y[18],\
                         Aqr.y[19],Aqr.y[26],Aqr.y[27],Aqr.y[31],Aqr.y[32],Aqr.y[34],Aqr.y[35],Aqr.y[37],\
                         Aqr.y[40],Aqr.y[41],Aqr.y[43],Aqr.y[47],Aqr.y[56],Aqr.y[61],Aqr.y[64],Aqr.y[73],\
                         Aqr.y[77],Aqr.y[78],Aqr.y[90],Aqr.y[114],Aqr.y[134],PsA.y[1],PsA.y[13],PsA.y[25]])]
    #鈇鉞#
    C_E56 = [[Aqr.x[39],Aqr.x[42]],[Aqr.y[39],Aqr.y[42]],[Aqr.x[42],Aqr.x[49]],[Aqr.y[42],Aqr.y[49]]]
    CE56n = [numpy.mean([Aqr.x[39],Aqr.x[42],Aqr.x[49]]),\
             numpy.mean([Aqr.y[39],Aqr.y[42],Aqr.y[49]])]
    #北落師門#
    C_E57 = []
    CE57n = [PsA.x[0],PsA.y[0]]
    #八魁#
    C_E58 = [[Cet.x[15],Cet.x[26]],[Cet.y[15],Cet.y[26]],[Cet.x[16],Cet.x[26]],[Cet.y[16],Cet.y[26]],\
             [Cet.x[26],Cet.x[29]],[Cet.y[26],Cet.y[29]]]
    CE58n = [numpy.mean([Cet.x[15],Cet.x[16],Cet.x[26],Cet.x[29]]),\
             numpy.mean([Cet.y[15],Cet.y[16],Cet.y[26],Cet.y[29]])]
    #天綱#
    C_E59 = []
    CE59n = [PsA.x[2],PsA.y[2]]
    #土公吏#
    C_E60 = [[Peg.x[30],Peg.x[59]],[Peg.y[30],Peg.y[59]]]
    CE60n = [numpy.mean([Peg.x[30],Peg.x[59]]),\
             numpy.mean([Peg.y[30],Peg.y[59]])]
    #螣蛇#
    C_E61 = [[And.x[6],And.x[26]],[And.y[6],And.y[26]],[And.x[6],And.x[30]],[And.y[6],And.y[30]],\
             [And.x[10],And.x[12]],[And.y[10],And.y[12]],[And.x[10],And.x[30]],[And.y[10],And.y[30]],\
             [And.x[17],And.x[20]],[And.y[17],And.y[20]],[And.x[17],And.x[26]],[And.y[17],And.y[26]],\
             [And.x[20],Lac.x[9]],[And.y[20],Lac.y[9]],[Cas.x[13],Cas.x[24]],[Cas.y[13],Cas.y[24]],\
             [Cas.x[13],Cas.x[25]],[Cas.y[13],Cas.y[25]],[Cas.x[24],Cas.x[27]],[Cas.y[24],Cas.y[27]],\
             [Cas.x[25],Lac.x[3]],[Cas.y[25],Lac.y[3]],[Cas.x[27],Lac.x[9]],[Cas.y[27],Lac.y[9]],\
             [Cep.x[8],Lac.x[3]],[Cep.y[8],Lac.y[3]],[Cep.x[8],Cep.x[61]],[Cep.y[8],Cep.y[61]],\
             [Cep.x[61],Cyg.x[27]],[Cep.y[61],Cyg.y[27]],[Cyg.x[19],Cyg.x[27]],[Cyg.y[19],Cyg.y[27]],\
             [Cyg.x[19],Lac.x[8]],[Cyg.y[19],Lac.y[8]],[Lac.x[0],Lac.x[8]],[Lac.y[0],Lac.y[8]]]
    CE61n = [numpy.mean([And.x[6],And.x[10],And.x[12],And.x[17],And.x[20],And.x[26],And.x[30],Cas.x[13],\
                         Cas.x[24],Cas.x[25],Cas.x[27],Cep.x[8],Cep.x[61],Cyg.x[19],Cyg.x[27],Lac.x[0],\
                         Lac.x[3],Lac.x[8],Lac.x[9]]),\
             numpy.mean([And.y[6],And.y[10],And.y[12],And.y[17],And.y[20],And.y[26],And.y[30],Cas.y[13],\
                         Cas.y[24],Cas.y[25],Cas.y[27],Cep.y[8],Cep.y[61],Cyg.y[19],Cyg.y[27],Lac.y[0],\
                         Lac.y[3],Lac.y[8],Lac.y[9]])]
    #壁宿#
    C_E62 = [[And.x[0],Peg.x[3]],[And.y[0],Peg.y[3]]]
    CE62n = [numpy.mean([And.x[0],Peg.x[3]]),\
             numpy.mean([And.y[0],Peg.y[3]])]
    #霹靂#
    C_E63 = [[Psc.x[1],Psc.x[6]],[Psc.y[1],Psc.y[6]],[Psc.x[1],Psc.x[13]],[Psc.y[1],Psc.y[13]],\
             [Psc.x[2],Psc.x[3]],[Psc.y[2],Psc.y[3]],[Psc.x[3],Psc.x[6]],[Psc.y[3],Psc.y[6]]]
    CE63n = [numpy.mean([Psc.x[1],Psc.x[2],Psc.x[3],Psc.x[6],Psc.x[13]]),\
             numpy.mean([Psc.y[1],Psc.y[2],Psc.y[3],Psc.y[6],Psc.y[13]])]
    #雲雨#
    C_E64 = [[Psc.x[11],Psc.x[61]],[Psc.y[11],Psc.y[61]],[Psc.x[21],Psc.x[61]],[Psc.y[21],Psc.y[61]]]
    CE64n = [numpy.mean([Psc.x[11],Psc.x[21],Psc.x[61]]),\
             numpy.mean([Psc.y[11],Psc.y[21],Psc.y[61]])]
    #天廄#
    C_E65 = [[And.x[16],And.x[37]],[And.y[16],And.y[37]],[And.x[19],And.x[37]],[And.y[19],And.y[37]]]
    CE65n = [numpy.mean([And.x[16],And.x[19],And.x[37]]),\
             numpy.mean([And.y[16],And.y[19],And.y[37]])]
    #鈇鑕#
    C_E66 = [[Cet.x[9],Cet.x[24]],[Cet.y[9],Cet.y[24]],[Cet.x[9],Cet.x[34]],[Cet.y[9],Cet.y[34]]]
    CE66n = [numpy.mean([Cet.x[9],Cet.x[24],Cet.x[34]]),\
             numpy.mean([Cet.y[9],Cet.y[24],Cet.y[34]])]
    #土公#
    C_E67 = []
    CE67n = [] # ???

    C_E_list = [C_E01,C_E02,C_E03,C_E04,C_E05,C_E06,C_E07,C_E08,C_E09,C_E10,\
                C_E11,C_E12,C_E13,C_E14,C_E15,C_E16,C_E17,C_E18,C_E19,C_E20,\
                C_E21,C_E22,C_E23,C_E23a,C_E23b,C_E23c,C_E23d,C_E23e,C_E23f,C_E23g,\
                C_E23h,C_E23i,C_E23j,C_E23k,C_E23l,C_E24,C_E25,C_E26,C_E27,C_E28,\
                C_E29,C_E30,C_E31,C_E32,C_E33,C_E34,C_E35,C_E36,C_E37,C_E38,\
                C_E39,C_E40,C_E41,C_E42,C_E43,C_E44,C_E45,C_E46,C_E47,C_E48,\
                C_E49,C_E50,C_E51,C_E52,C_E53,C_E54,C_E55,C_E56,C_E57,C_E58,\
                C_E59,C_E60,C_E61,C_E62,C_E63,C_E64,C_E65,C_E66,C_E67]

    # 北宮玄武 linecollection
    C_E_line_z_xy1 = []
    C_E_line_z_xy2 = [] 
    C_E_line_xy1 = []
    C_E_line_xy2 = []        
    for i in range(len(C_E_list)):
        for j in range(len(C_E_list[i]))[0::2]:
            if math.hypot(C_E_list[i][j][0]-C_E_list[i][j][1],C_E_list[i][j+1][0]-C_E_list[i][j+1][1]) < hori_border:
                if i in set([0,10,21,41,51,62,73]):
                    C_E_line_z_xy1.append((C_E_list[i][j][0],C_E_list[i][j+1][0]))
                    C_E_line_z_xy2.append((C_E_list[i][j][1],C_E_list[i][j+1][1]))
                else:
                    C_E_line_xy1.append((C_E_list[i][j][0],C_E_list[i][j+1][0]))
                    C_E_line_xy2.append((C_E_list[i][j][1],C_E_list[i][j+1][1]))

    C_E_line_z_list = []
    for i in range(len(C_E_line_z_xy1)):            
        C_E_line_z_list.append([C_E_line_z_xy1[i],C_E_line_z_xy2[i]])
    
    C_E_line_list = []
    for i in range(len(C_E_line_xy1)):            
        C_E_line_list.append([C_E_line_xy1[i],C_E_line_xy2[i]])
    
    lc_C_E_z = mc.LineCollection(C_E_line_z_list, colors='yellow', zorder=2+2.5)
    lc_C_E = mc.LineCollection(C_E_line_list, colors='white', zorder=2+2.5)
    lc_C_E_z.set_alpha(plot_alpha)
    lc_C_E_z.set_clip_path(twlight_line)
    lc_C_E.set_alpha(plot_alpha)
    lc_C_E.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_E_z)
    ax0.add_collection(lc_C_E)

    CEn_list = [[CE01n,'斗宿'],[CE02n,'建'],[CE03n,'天弁'],[CE04n,'鱉'],[CE05n,'天雞'],\
                [CE06n,'天籥'],[CE07n,'狗國'],[CE08n,'天淵'],[CE09n,'狗'],[CE10n,'農丈人'],\
                [CE11n,'牛宿'],[CE12n,'天田'],[CE13n,'九坎'],[CE14n,'河鼓'],[CE15n,'織女'],\
                [CE16n,'左旗'],[CE17n,'右旗'],[CE18n,'天桴'],[CE19n,'羅堰'],[CE20n,'漸臺'],\
                [CE21n,'輦道'],[CE22n,'女宿'],[CE23n,'十二國'],[CE23an,'燕'],[CE23bn,'周'],\
                [CE23cn,'晉'],[CE23dn,'魏'],[CE23en,'楚'],[CE23fn,'齊'],[CE23gn,'韓'],\
                [CE23hn,'越'],[CE23in,'鄭'],[CE23jn,'趙'],[CE23kn,'代'],[CE23ln,'秦'],\
                [CE24n,'離珠'],[CE25n,'敗瓜'],[CE26n,'瓠瓜'],[CE27n,'天津'],[CE28n,'奚仲'],\
                [CE29n,'扶筐'],[CE30n,'虛宿'],[CE31n,'司命'],[CE32n,'司祿'],[CE33n,'司危'],\
                [CE34n,'司非'],[CE35n,'哭'],[CE36n,'泣'],[CE37n,'天壘城'],[CE38n,'敗臼'],\
                [CE39n,'離瑜'],[CE40n,'危宿'],[CE41n,'墳墓'],[CE42n,'人'],[CE43n,'杵'],\
                [CE44n,'臼'],[CE45n,'車府'],[CE46n,'天鉤'],[CE47n,'造父'],[CE48n,'蓋屋'],\
                [CE49n,'虛梁'],[CE50n,'天錢'],[CE51n,'室宿'],[CE52n,'離宮'],[CE53n,'雷電'],\
                [CE54n,'壘壁陣'],[CE55n,'羽林軍'],[CE56n,'鈇鉞'],[CE57n,'北落師門'],[CE58n,'八魁'],\
                [CE59n,'天綱'],[CE60n,'土公吏'],[CE61n,'螣蛇'],[CE62n,'壁宿'],[CE63n,'霹靂'],\
                [CE64n,'雲雨'],[CE65n,'天廄'],[CE66n,'鈇鑕'],[CE67n,'土公']]

    for i in range(len(CEn_list)):
        if len(CEn_list[i][0]) != 0:
            if (CEn_list[i][0][0])**2 < (hori_border/2)**2-(CEn_list[i][0][1])**2 \
               and max(CEn_list[i][0])-min(CEn_list[i][0]) < hori_border:
                if i in set([0,10,21,41,51,62,73]):
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0],CEn_list[i][0][1]),color='y',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=9+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]+olw,CEn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]+olw,CEn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]+olw,CEn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0],CEn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0],CEn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]-olw,CEn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]-olw,CEn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0]-olw,CEn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
##                else:
##                    ax0.annotate(str(CEn_list[i][1]),(CEn_list[i][0][0],CEn_list[i][0][1]),color='w',\
##                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ##########
    #西宮白虎#
    ##########
    #奎宿#
    C_F01 = [[And.x[1],And.x[7]],[And.y[1],And.y[7]],[And.x[1],Psc.x[27]],[And.y[1],Psc.y[27]],\
             [And.x[3],And.x[13]],[And.y[3],And.y[13]],[And.x[3],And.x[14]],[And.y[3],And.y[14]],\
             [And.x[7],And.x[18]],[And.y[7],And.y[18]],[And.x[8],And.x[14]],[And.y[8],And.y[14]],\
             [And.x[8],And.x[15]],[And.y[8],And.y[15]],[And.x[13],And.x[18]],[And.y[13],And.y[18]],\
             [And.x[15],Psc.x[33]],[And.y[15],Psc.y[33]],[Psc.x[12],Psc.x[29]],[Psc.y[12],Psc.y[29]],\
             [Psc.x[12],Psc.x[27]],[Psc.y[12],Psc.y[27]],[Psc.x[16],Psc.x[17]],[Psc.y[16],Psc.y[17]],\
             [Psc.x[16],Psc.x[18]],[Psc.y[16],Psc.y[18]],[Psc.x[17],Psc.x[33]],[Psc.y[17],Psc.y[33]],\
             [Psc.x[18],Psc.x[29]],[Psc.y[18],Psc.y[29]]]
    CF01n = [numpy.mean([And.x[1],And.x[3],And.x[7],And.x[8],And.x[13],And.x[14],And.x[15],And.x[18],\
                         Psc.x[12],Psc.x[16],Psc.x[17],Psc.x[18],Psc.x[27],Psc.x[29],Psc.x[33]]),\
             numpy.mean([And.y[1],And.y[3],And.y[7],And.y[8],And.y[13],And.y[14],And.y[15],And.y[18],\
                         Psc.y[12],Psc.y[16],Psc.y[17],Psc.y[18],Psc.y[27],Psc.y[29],Psc.y[33]])]
    #外屏#
    C_F02 = [[Psc.x[5],Psc.x[9]],[Psc.y[5],Psc.y[9]],[Psc.x[5],Psc.x[31]],[Psc.y[5],Psc.y[31]],\
             [Psc.x[7],Psc.x[15]],[Psc.y[7],Psc.y[15]],[Psc.x[10],Psc.x[15]],[Psc.y[10],Psc.y[15]],\
             [Psc.x[10],Psc.x[19]],[Psc.y[10],Psc.y[19]],[Psc.x[19],Psc.x[31]],[Psc.y[19],Psc.y[31]]]
    CF02n = [numpy.mean([Psc.x[5],Psc.x[7],Psc.x[9],Psc.x[10],Psc.x[15],Psc.x[19],Psc.x[31]]),\
             numpy.mean([Psc.y[5],Psc.y[7],Psc.y[9],Psc.y[10],Psc.y[15],Psc.y[19],Psc.y[31]])]
    #天溷#
    C_F03 = [[Cet.x[20],Cet.x[130]],[Cet.y[20],Cet.y[130]],[Cet.x[43],Cet.x[130]],[Cet.y[43],Cet.y[130]],\
             [Cet.x[43],Cet.x[133]],[Cet.y[43],Cet.y[133]]]
    CF03n = [numpy.mean([Cet.x[20],Cet.x[43],Cet.x[130],Cet.x[133]]),\
             numpy.mean([Cet.y[20],Cet.y[43],Cet.y[130],Cet.y[133]])]
    #土司空#
    C_F04 = []
    CF04n = [Cet.x[0],Cet.y[0]]
    #軍南門#
    C_F05 = []
    CF05n = [And.x[11],And.y[11]]
    #閣道#
    C_F06 = [[Cas.x[3],Cas.x[4]],[Cas.y[3],Cas.y[4]],[Cas.x[3],Cas.x[9]],[Cas.y[3],Cas.y[9]],\
             [Cas.x[4],Cas.x[10]],[Cas.y[4],Cas.y[10]],[Cas.x[9],Cas.x[26]],[Cas.y[9],Cas.y[26]],\
             [Cas.x[11],Cas.x[26]],[Cas.y[11],Cas.y[26]]]
    CF06n = [numpy.mean([Cas.x[3],Cas.x[4],Cas.x[9],Cas.x[10],Cas.x[11],Cas.x[26]]),\
             numpy.mean([Cas.y[3],Cas.y[4],Cas.y[9],Cas.y[10],Cas.y[11],Cas.y[26]])]
    #附路#
    C_F07 = []
    CF07n = [Cas.x[6],Cas.y[6]]
    #王良#
    C_F08 = [[Cas.x[0],Cas.x[5]],[Cas.y[0],Cas.y[5]],[Cas.x[0],Cas.x[16]],[Cas.y[0],Cas.y[16]],\
             [Cas.x[1],Cas.x[8]],[Cas.y[1],Cas.y[8]],[Cas.x[5],Cas.x[8]],[Cas.y[5],Cas.y[8]]]
    CF08n = [numpy.mean([Cas.x[0],Cas.x[1],Cas.x[5],Cas.x[8],Cas.x[16]]),\
             numpy.mean([Cas.y[0],Cas.y[1],Cas.y[5],Cas.y[8],Cas.y[16]])]
    #策#
    C_F09 = []
    CF09n = [Cas.x[2],Cas.y[2]]
    #婁宿#
    C_F10 = [[Ari.x[0],Ari.x[1]],[Ari.y[0],Ari.y[1]],[Ari.x[1],Ari.x[9]],[Ari.y[1],Ari.y[9]]]
    CF10n = [numpy.mean([Ari.x[0],Ari.x[1],Ari.x[9]]),\
             numpy.mean([Ari.y[0],Ari.y[1],Ari.y[9]])]
    #左更#
    C_F11 = [[Ari.x[18],Ari.x[24]],[Ari.y[18],Ari.y[24]],[Ari.x[22],Ari.x[34]],[Ari.y[22],Ari.y[34]],\
             [Ari.x[24],Ari.x[39]],[Ari.y[24],Ari.y[39]],[Ari.x[34],Ari.x[39]],[Ari.y[34],Ari.y[39]]]
    CF11n = [numpy.mean([Ari.x[18],Ari.x[22],Ari.x[24],Ari.x[34],Ari.x[39]]),\
             numpy.mean([Ari.y[18],Ari.y[22],Ari.y[24],Ari.y[34],Ari.y[39]])]
    #右更#
    C_F12 = [[Psc.x[0],Psc.x[45]],[Psc.y[0],Psc.y[45]],[Psc.x[0],Psc.x[52]],[Psc.y[0],Psc.y[52]],\
             [Psc.x[4],Psc.x[52]],[Psc.y[4],Psc.y[52]]]
    CF12n = [numpy.mean([Psc.x[0],Psc.x[4],Psc.x[45],Psc.x[52]]),\
             numpy.mean([Psc.y[0],Psc.y[4],Psc.y[45],Psc.y[52]])]
    #天倉#
    C_F13 = [[Cet.x[3],Cet.x[6]],[Cet.y[3],Cet.y[6]],[Cet.x[3],Cet.x[7]],[Cet.y[3],Cet.y[7]],\
             [Cet.x[5],Cet.x[8]],[Cet.y[5],Cet.y[8]],[Cet.x[5],Cet.x[48]],[Cet.y[5],Cet.y[48]],\
             [Cet.x[7],Cet.x[8]],[Cet.y[7],Cet.y[8]]]
    CF13n = [numpy.mean([Cet.x[3],Cet.x[5],Cet.x[6],Cet.x[7],Cet.x[8],Cet.x[48]]),\
             numpy.mean([Cet.y[3],Cet.y[5],Cet.y[6],Cet.y[7],Cet.y[8],Cet.y[48]])]
    #天庾#
    C_F14 = []
    CF14n = [For.x[1],For.y[1]]
    #天大將軍#
    C_F15 = [[And.x[2],Per.x[15]],[And.y[2],Per.y[15]],[And.x[2],Tri.x[3]],[And.y[2],Tri.y[3]],\
             [And.x[4],And.x[41]],[And.y[4],And.y[41]],[And.x[4],Per.x[15]],[And.y[4],Per.y[15]],\
             [And.x[9],And.x[28]],[And.y[9],And.y[28]],[And.x[9],And.x[31]],[And.y[9],And.y[31]],\
             [And.x[28],And.x[57]],[And.y[28],And.y[57]],[And.x[31],And.x[41]],[And.y[31],And.y[41]],\
             [And.x[57],Tri.x[0]],[And.y[57],Tri.y[0]],[Tri.x[0],Tri.x[2]],[Tri.y[0],Tri.y[2]],\
             [Tri.x[2],Tri.x[3]],[Tri.y[2],Tri.y[3]]]
    CF15n = [numpy.mean([And.x[2],And.x[4],And.x[9],And.x[28],And.x[31],And.x[41],And.x[57],Per.x[15],\
                         Tri.x[0],Tri.x[2],Tri.x[3]]),\
             numpy.mean([And.y[2],And.y[4],And.y[9],And.y[28],And.y[31],And.y[41],And.y[57],Per.y[15],\
                         Tri.y[0],Tri.y[2],Tri.y[3]])]
    #胃宿#
    C_F16 = [[Ari.x[2],Ari.x[5]],[Ari.y[2],Ari.y[5]],[Ari.x[5],Ari.x[8]],[Ari.y[5],Ari.y[8]]]
    CF16n = [numpy.mean([Ari.x[2],Ari.x[5],Ari.x[8]]),\
             numpy.mean([Ari.y[2],Ari.y[5],Ari.y[8]])]
    #天廩#
    C_F17 = [[Tau.x[7],Tau.x[11]],[Tau.y[7],Tau.y[11]],[Tau.x[11],Tau.x[55]],[Tau.y[11],Tau.y[55]],\
             [Tau.x[16],Tau.x[55]],[Tau.y[16],Tau.y[55]]]
    CF17n = [numpy.mean([Tau.x[7],Tau.x[11],Tau.x[16],Tau.x[55]]),\
             numpy.mean([Tau.y[7],Tau.y[11],Tau.y[16],Tau.y[55]])]
    #天囷#
    C_F18 = [[Cet.x[1],Cet.x[74]],[Cet.y[1],Cet.y[74]],[Cet.x[4],Cet.x[10]],[Cet.y[4],Cet.y[10]],\
             [Cet.x[4],Cet.x[25]],[Cet.y[4],Cet.y[25]],[Cet.x[10],Cet.x[45]],[Cet.y[10],Cet.y[45]],\
             [Cet.x[12],Cet.x[14]],[Cet.y[12],Cet.y[14]],[Cet.x[12],Cet.x[18]],[Cet.y[12],Cet.y[18]],\
             [Cet.x[13],Cet.x[14]],[Cet.y[13],Cet.y[14]],[Cet.x[13],Cet.x[25]],[Cet.y[13],Cet.y[25]],\
             [Cet.x[18],Cet.x[74]],[Cet.y[18],Cet.y[74]],[Cet.x[45],Cet.x[50]],[Cet.y[45],Cet.y[50]],\
             [Cet.x[50],Cet.x[102]],[Cet.y[50],Cet.y[102]],[Cet.x[59],Cet.x[102]],[Cet.y[59],Cet.y[102]]]
    CF18n = [numpy.mean([Cet.x[1],Cet.x[4],Cet.x[10],Cet.x[12],Cet.x[13],Cet.x[14],Cet.x[18],Cet.x[25],\
                         Cet.x[45],Cet.x[50],Cet.x[59],Cet.x[74],Cet.x[102]]),\
             numpy.mean([Cet.y[1],Cet.y[4],Cet.y[10],Cet.y[12],Cet.y[13],Cet.y[14],Cet.y[18],Cet.y[25],\
                         Cet.y[45],Cet.y[50],Cet.y[59],Cet.y[74],Cet.y[102]])]
    #大陵#
    C_F19 = [[Per.x[1],Per.x[6]],[Per.y[1],Per.y[6]],[Per.x[1],Per.x[9]],[Per.y[1],Per.y[9]],\
             [Per.x[6],Per.x[18]],[Per.y[6],Per.y[18]],[Per.x[9],Per.x[14]],[Per.y[9],Per.y[14]],\
             [Per.x[11],Per.x[14]],[Per.y[11],Per.y[14]],[Per.x[11],Per.x[44]],[Per.y[11],Per.y[44]],\
             [Per.x[18],Per.x[32]],[Per.y[18],Per.y[32]]]
    CF19n = [numpy.mean([Per.x[1],Per.x[6],Per.x[9],Per.x[11],Per.x[14],Per.x[18],Per.x[32],Per.x[44]]),\
             numpy.mean([Per.y[1],Per.y[6],Per.y[9],Per.y[11],Per.y[14],Per.y[18],Per.y[32],Per.y[44]])]
    #天船#
    C_F20 = [[Cam.x[23],Per.x[24]],[Cam.y[23],Per.y[24]],[Per.x[0],Per.x[4]],[Per.y[0],Per.y[4]],\
             [Per.x[0],Per.x[19]],[Per.y[0],Per.y[19]],[Per.x[4],Per.x[7]],[Per.y[4],Per.y[7]],\
             [Per.x[5],Per.x[13]],[Per.y[5],Per.y[13]],[Per.x[5],Per.x[19]],[Per.y[5],Per.y[19]],\
             [Per.x[13],Per.x[17]],[Per.y[13],Per.y[17]],[Per.x[17],Per.x[24]],[Per.y[17],Per.y[24]]]
    CF20n = [numpy.mean([Cam.x[23],Per.x[0],Per.x[4],Per.x[5],Per.x[7],Per.x[13],Per.x[17],Per.x[19],\
                         Per.x[24]]),\
             numpy.mean([Cam.y[23],Per.y[0],Per.y[4],Per.y[5],Per.y[7],Per.y[13],Per.y[17],Per.y[19],\
                         Per.y[24]])]
    #積尸#
    C_F21 = []
    CF21n = [Per.x[27],Per.y[27]]
    #積水#
    C_F22 = []
    CF22n = [Per.x[21],Per.y[21]]
    #昴宿#
    C_F23 = []
    CF23n = [numpy.mean([Tau.x[2],Tau.x[8],Tau.x[10],Tau.x[14],Tau.x[17],Tau.x[26],Tau.x[52]]),\
             numpy.mean([Tau.y[2],Tau.y[8],Tau.y[10],Tau.y[14],Tau.y[17],Tau.y[26],Tau.y[52]])]
    #天阿#
    C_F24 = []
    CF24n = [Ari.x[27],Ari.y[27]]
    #月#
    C_F25 = []
    CF25n = [Tau.x[27],Tau.y[27]]
    #天陰#
    C_F26 = [[Ari.x[3],Ari.x[15]],[Ari.y[3],Ari.y[15]],[Ari.x[12],Ari.x[15]],[Ari.y[12],Ari.y[15]]]
    CF26n = [numpy.mean([Ari.x[3],Ari.x[12],Ari.x[15]]),\
             numpy.mean([Ari.y[3],Ari.y[12],Ari.y[15]])]
    #芻蒿#
    C_F27 = [[Cet.x[23],Cet.x[57]],[Cet.y[23],Cet.y[57]],[Cet.x[27],Cet.x[81]],[Cet.y[27],Cet.y[81]],\
             [Cet.x[57],Cet.x[81]],[Cet.y[57],Cet.y[81]]]
    CF27n = [numpy.mean([Cet.x[23],Cet.x[27],Cet.x[57],Cet.x[81]]),\
             numpy.mean([Cet.y[23],Cet.y[27],Cet.y[57],Cet.y[81]])]
    #天苑#
    C_F28 = [[Cet.x[11],Eri.x[12]],[Cet.y[11],Eri.y[12]],[Cet.x[11],Eri.x[30]],[Cet.y[11],Eri.y[30]],\
             [Eri.x[2],Eri.x[28]],[Eri.y[2],Eri.y[28]],[Eri.x[4],Eri.x[9]],[Eri.y[4],Eri.y[9]],\
             [Eri.x[4],Eri.x[28]],[Eri.y[4],Eri.y[28]],[Eri.x[7],Eri.x[17]],[Eri.y[7],Eri.y[17]],\
             [Eri.x[7],Eri.x[23]],[Eri.y[7],Eri.y[23]],[Eri.x[9],Eri.x[42]],[Eri.y[9],Eri.y[42]],\
             [Eri.x[12],Eri.x[42]],[Eri.y[12],Eri.y[42]],[Eri.x[17],Eri.x[39]],[Eri.y[17],Eri.y[39]],\
             [Eri.x[20],Eri.x[23]],[Eri.y[20],Eri.y[23]],[Eri.x[20],Eri.x[59]],[Eri.y[20],Eri.y[59]],\
             [Eri.x[30],Eri.x[39]],[Eri.y[30],Eri.y[39]],[Eri.x[34],Eri.x[35]],[Eri.y[34],Eri.y[35]],\
             [Eri.x[34],Eri.x[59]],[Eri.y[34],Eri.y[59]]]
    CF28n = [numpy.mean([Cet.x[11],Eri.x[2],Eri.x[4],Eri.x[7],Eri.x[9],Eri.x[12],Eri.x[17],Eri.x[20],\
                         Eri.x[23],Eri.x[28],Eri.x[30],Eri.x[34],Eri.x[35],Eri.x[39],Eri.x[42],Eri.x[59]]),\
             numpy.mean([Cet.y[11],Eri.y[2],Eri.y[4],Eri.y[7],Eri.y[9],Eri.y[12],Eri.y[17],Eri.y[20],\
                         Eri.y[23],Eri.y[28],Eri.y[30],Eri.y[34],Eri.y[35],Eri.y[39],Eri.y[42],Eri.y[59]])]
    #卷舌#
    C_F29 = [[Per.x[2],Per.x[10]],[Per.y[2],Per.y[10]],[Per.x[2],Per.x[12]],[Per.y[2],Per.y[12]],\
             [Per.x[3],Per.x[8]],[Per.y[3],Per.y[8]],[Per.x[3],Per.x[12]],[Per.y[3],Per.y[12]],\
             [Per.x[10],Per.x[36]],[Per.y[10],Per.y[36]]]
    CF29n = [numpy.mean([Per.x[2],Per.x[3],Per.x[8],Per.x[10],Per.x[12],Per.x[36]]),\
             numpy.mean([Per.y[2],Per.y[3],Per.y[8],Per.y[10],Per.y[12],Per.y[36]])]
    #天讒#
    C_F30 = []
    CF30n = [Per.x[42],Per.y[42]]
    #礪石#
    C_F31 = [[Tau.x[45],Tau.x[71]],[Tau.y[45],Tau.y[71]],[Tau.x[59],Tau.x[76]],[Tau.y[59],Tau.y[76]],\
             [Tau.x[71],Tau.x[76]],[Tau.y[71],Tau.y[76]]]
    CF31n = [numpy.mean([Tau.x[45],Tau.x[59],Tau.x[71],Tau.x[76]]),\
             numpy.mean([Tau.y[45],Tau.y[59],Tau.y[71],Tau.y[76]])]
    #畢宿#
    C_F32 = [[Tau.x[0],Tau.x[4]],[Tau.y[0],Tau.y[4]],[Tau.x[4],Tau.x[29]],[Tau.y[4],Tau.y[29]],\
             [Tau.x[5],Tau.x[9]],[Tau.y[5],Tau.y[9]],[Tau.x[6],Tau.x[25]],[Tau.y[6],Tau.y[25]],\
             [Tau.x[9],Tau.x[12]],[Tau.y[9],Tau.y[12]],[Tau.x[9],Tau.x[29]],[Tau.y[9],Tau.y[29]],\
             [Tau.x[12],Tau.x[25]],[Tau.y[12],Tau.y[25]]]
    CF32n = [numpy.mean([Tau.x[0],Tau.x[4],Tau.x[5],Tau.x[6],Tau.x[9],Tau.x[12],Tau.x[25],Tau.x[29]]),\
             numpy.mean([Tau.y[0],Tau.y[4],Tau.y[5],Tau.y[6],Tau.y[9],Tau.y[12],Tau.y[25],Tau.y[29]])]
    #附耳#
    C_F33 = []
    CF33n = [Tau.x[34],Tau.y[34]]
    #天街#
    C_F34 = [[Tau.x[18],Tau.x[43]],[Tau.y[18],Tau.y[43]]]
    CF34n = [numpy.mean([Tau.x[18],Tau.x[43]]),\
             numpy.mean([Tau.y[18],Tau.y[43]])]
    #天節#
    C_F35 = [[Tau.x[19],Tau.x[54]],[Tau.y[19],Tau.y[54]],[Tau.x[19],Tau.x[81]],[Tau.y[19],Tau.y[81]],\
             [Tau.x[20],Tau.x[49]],[Tau.y[20],Tau.y[49]],[Tau.x[20],Tau.x[81]],[Tau.y[20],Tau.y[81]],\
             [Tau.x[32],Tau.x[33]],[Tau.y[32],Tau.y[33]],[Tau.x[33],Tau.x[98]],[Tau.y[33],Tau.y[98]],\
             [Tau.x[49],Tau.x[98]],[Tau.y[49],Tau.y[98]]]
    CF35n = [numpy.mean([Tau.x[19],Tau.x[20],Tau.x[32],Tau.x[33],Tau.x[49],Tau.x[54],Tau.x[81],Tau.x[98]]),\
             numpy.mean([Tau.y[19],Tau.y[20],Tau.y[32],Tau.y[33],Tau.y[49],Tau.y[54],Tau.y[81],Tau.y[98]])]
    #諸王#
    C_F36 = [[Tau.x[23],Tau.x[120]],[Tau.y[23],Tau.y[120]],[Tau.x[30],Tau.x[56]],[Tau.y[30],Tau.y[56]],\
             [Tau.x[56],Tau.x[84]],[Tau.y[56],Tau.y[84]],[Tau.x[84],Tau.x[89]],[Tau.y[84],Tau.y[89]],\
             [Tau.x[89],Tau.x[120]],[Tau.y[89],Tau.y[120]]]
    CF36n = [numpy.mean([Tau.x[23],Tau.x[30],Tau.x[56],Tau.x[84],Tau.x[89],Tau.x[120]]),\
             numpy.mean([Tau.y[23],Tau.y[30],Tau.y[56],Tau.y[84],Tau.y[89],Tau.y[120]])]
    #天高#
    C_F37 = [[Tau.x[31],Tau.x[44]],[Tau.y[31],Tau.y[44]],[Tau.x[31],Tau.x[53]],[Tau.y[31],Tau.y[53]],\
             [Tau.x[44],Tau.x[53]],[Tau.y[44],Tau.y[53]]]
    CF37n = [numpy.mean([Tau.x[31],Tau.x[44],Tau.x[53]]),\
             numpy.mean([Tau.y[31],Tau.y[44],Tau.y[53]])]
    #九州殊口#
    C_F38 = [[Eri.x[13],Eri.x[55]],[Eri.y[13],Eri.y[55]],[Eri.x[13],Eri.x[118]],[Eri.y[13],Eri.y[118]],\
             [Eri.x[16],Eri.x[44]],[Eri.y[16],Eri.y[44]],[Eri.x[16],Eri.x[55]],[Eri.y[16],Eri.y[55]]]
    CF38n = [numpy.mean([Eri.x[13],Eri.x[16],Eri.x[44],Eri.x[55],Eri.x[118]]),\
             numpy.mean([Eri.y[13],Eri.y[16],Eri.y[44],Eri.y[55],Eri.y[118]])]
    #五車#
    C_F39 = [[Aur.x[0],Aur.x[1]],[Aur.y[0],Aur.y[1]],[Aur.x[0],Aur.x[3]],[Aur.y[0],Aur.y[3]],\
             [Aur.x[1],Aur.x[2]],[Aur.y[1],Aur.y[2]],[Aur.x[2],Tau.x[1]],[Aur.y[2],Tau.y[1]]]
    CF39n = [numpy.mean([Aur.x[0],Aur.x[1],Aur.x[2],Aur.x[3],Tau.x[1]]),\
             numpy.mean([Aur.y[0],Aur.y[1],Aur.y[2],Aur.y[3],Tau.y[1]])]
    #柱#
    C_F40 = [[Aur.x[4],Aur.x[5]],[Aur.y[4],Aur.y[5]],[Aur.x[4],Aur.x[7]],[Aur.y[4],Aur.y[7]],\
             [Aur.x[8],Aur.x[11]],[Aur.y[8],Aur.y[11]],[Aur.x[8],Aur.x[14]],[Aur.y[8],Aur.y[14]],\
             [Aur.x[15],Aur.x[41]],[Aur.y[15],Aur.y[41]]]
    CF40an = [numpy.mean([Aur.x[4],Aur.x[5],Aur.x[7]]),\
              numpy.mean([Aur.y[4],Aur.y[5],Aur.y[7]])]
    CF40bn = [numpy.mean([Aur.x[8],Aur.x[11],Aur.x[14]]),\
              numpy.mean([Aur.y[8],Aur.y[11],Aur.y[14]])]
    CF40cn = [numpy.mean([Aur.x[15],Aur.x[41]]),\
              numpy.mean([Aur.y[15],Aur.y[41]])]
    #天潢#
    C_F41 = [[Aur.x[18],Aur.x[29]],[Aur.y[18],Aur.y[29]],[Aur.x[23],Aur.x[29]],[Aur.y[23],Aur.y[29]],\
             [Aur.x[26],Aur.x[29]],[Aur.y[26],Aur.y[29]],[Aur.x[29],Aur.x[30]],[Aur.y[29],Aur.y[30]]]
    CF41n = [numpy.mean([Aur.x[18],Aur.x[23],Aur.x[26],Aur.x[29],Aur.x[30]]),\
             numpy.mean([Aur.y[18],Aur.y[23],Aur.y[26],Aur.y[29],Aur.y[30]])]
    #咸池#
    C_F42 = [[Aur.x[13],Aur.x[35]],[Aur.y[13],Aur.y[35]]]
    CF42n = [numpy.mean([Aur.x[13],Aur.x[35]]),\
             numpy.mean([Aur.y[13],Aur.y[35]])]
    #天關#
    C_F43 = []
    CF43n = [Tau.x[3],Tau.y[3]]
    #參旗#
    C_F44 = [[Ori.x[8],Ori.x[12]],[Ori.y[8],Ori.y[12]],[Ori.x[8],Ori.x[21]],[Ori.y[8],Ori.y[21]],\
             [Ori.x[12],Ori.x[13]],[Ori.y[12],Ori.y[13]],[Ori.x[13],Ori.x[26]],[Ori.y[13],Ori.y[26]],\
             [Ori.x[15],Ori.x[38]],[Ori.y[15],Ori.y[38]],[Ori.x[15],Ori.x[55]],[Ori.y[15],Ori.y[55]],\
             [Ori.x[21],Ori.x[34]],[Ori.y[21],Ori.y[34]],[Ori.x[34],Ori.x[55]],[Ori.y[34],Ori.y[55]]]
    CF44n = [numpy.mean([Ori.x[8],Ori.x[12],Ori.x[13],Ori.x[15],Ori.x[21],Ori.x[26],Ori.x[34],Ori.x[38],\
                         Ori.x[55]]),\
             numpy.mean([Ori.y[8],Ori.y[12],Ori.y[13],Ori.y[15],Ori.y[21],Ori.y[26],Ori.y[34],Ori.y[38],\
                         Ori.y[55]])]
    #九斿#
    C_F45 = [[Eri.x[15],Eri.x[27]],[Eri.y[15],Eri.y[27]],[Eri.x[15],Tau.x[66]],[Eri.y[15],Tau.y[66]],\
             [Eri.x[25],Eri.x[75]],[Eri.y[25],Eri.y[75]],[Eri.x[25],Lep.x[37]],[Eri.y[25],Lep.y[37]],\
             [Eri.x[27],Eri.x[69]],[Eri.y[27],Eri.y[69]],[Eri.x[41],Eri.x[48]],[Eri.y[41],Eri.y[48]],\
             [Eri.x[41],Eri.x[69]],[Eri.y[41],Eri.y[69]],[Eri.x[48],Eri.x[75]],[Eri.y[48],Eri.y[75]]]
    CF45n = [numpy.mean([Eri.x[15],Eri.x[25],Eri.x[27],Eri.x[41],Eri.x[48],Eri.x[69],Eri.x[75],Lep.x[37],\
                         Tau.x[66]]),\
             numpy.mean([Eri.y[15],Eri.y[25],Eri.y[27],Eri.y[41],Eri.y[48],Eri.y[69],Eri.y[75],Lep.y[37],\
                         Tau.y[66]])]
    #天園#
    C_F46 = [[Eri.x[3],Eri.x[33]],[Eri.y[3],Eri.y[33]],[Eri.x[3],Eri.x[38]],[Eri.y[3],Eri.y[38]],\
             [Eri.x[5],Eri.x[8]],[Eri.y[5],Eri.y[8]],[Eri.x[5],Eri.x[21]],[Eri.y[5],Eri.y[21]],\
             [Eri.x[6],Eri.x[14]],[Eri.y[6],Eri.y[14]],[Eri.x[6],Eri.x[19]],[Eri.y[6],Eri.y[19]],\
             [Eri.x[8],Phe.x[6]],[Eri.y[8],Phe.y[6]],[Eri.x[10],Eri.x[14]],[Eri.y[10],Eri.y[14]],\
             [Eri.x[10],Eri.x[31]],[Eri.y[10],Eri.y[31]],[Eri.x[19],Eri.x[37]],[Eri.y[19],Eri.y[37]],\
             [Eri.x[21],Eri.x[38]],[Eri.y[21],Eri.y[38]],[Eri.x[33],Eri.x[37]],[Eri.y[33],Eri.y[37]]]
    CF46n = [numpy.mean([Eri.x[3],Eri.x[5],Eri.x[6],Eri.x[8],Eri.x[10],Eri.x[14],Eri.x[19],Eri.x[21],\
                         Eri.x[31],Eri.x[33],Eri.x[37],Eri.x[38],Phe.x[6]]),\
             numpy.mean([Eri.y[3],Eri.y[5],Eri.y[6],Eri.y[8],Eri.y[10],Eri.y[14],Eri.y[19],Eri.y[21],\
                         Eri.y[31],Eri.y[33],Eri.y[37],Eri.y[38],Phe.y[6]])]
    #觜宿#
    C_F47 = [[Ori.x[10],Ori.x[22]],[Ori.y[10],Ori.y[22]],[Ori.x[16],Ori.x[22]],[Ori.y[16],Ori.y[22]]]
    CF47n = [numpy.mean([Ori.x[10],Ori.x[16],Ori.x[22]]),\
             numpy.mean([Ori.y[10],Ori.y[16],Ori.y[22]])]
    #司怪#
    C_F48 = [[Gem.x[16],Ori.x[33]],[Gem.y[16],Ori.y[33]],[Gem.x[16],Tau.x[37]],[Gem.y[16],Tau.y[37]],\
             [Ori.x[23],Ori.x[33]],[Ori.y[23],Ori.y[33]]]
    CF48n = [numpy.mean([Gem.x[16],Ori.x[23],Ori.x[33],Tau.x[37]]),\
             numpy.mean([Gem.y[16],Ori.y[23],Ori.y[33],Tau.y[37]])]
    #座旗#
    C_F49 = [[Aur.x[17],Aur.x[28]],[Aur.y[17],Aur.y[28]],[Aur.x[17],Aur.x[36]],[Aur.y[17],Aur.y[36]],\
             [Aur.x[27],Aur.x[36]],[Aur.y[27],Aur.y[36]],[Aur.x[27],Lyn.x[11]],[Aur.y[27],Lyn.y[11]],\
             [Aur.x[28],Aur.x[33]],[Aur.y[28],Aur.y[33]],[Aur.x[33],Aur.x[51]],[Aur.y[33],Aur.y[51]],\
             [Aur.x[34],Lyn.x[11]],[Aur.y[34],Lyn.y[11]],[Aur.x[51],Aur.x[94]],[Aur.y[51],Aur.y[94]],]
    CF49n = [numpy.mean([Aur.x[17],Aur.x[27],Aur.x[28],Aur.x[33],Aur.x[34],Aur.x[36],Aur.x[51],Aur.x[94],\
                         Lyn.x[11]]),\
             numpy.mean([Aur.y[17],Aur.y[27],Aur.y[28],Aur.y[33],Aur.y[34],Aur.y[36],Aur.y[51],Aur.y[94],\
                         Lyn.y[11]])]
    #參宿#
    C_F50 = [[Ori.x[0],Ori.x[6]],[Ori.y[0],Ori.y[6]],[Ori.x[1],Ori.x[4]],[Ori.y[1],Ori.y[4]],\
             [Ori.x[2],Ori.x[6]],[Ori.y[2],Ori.y[6]],[Ori.x[3],Ori.x[4]],[Ori.y[3],Ori.y[4]],\
             [Ori.x[3],Ori.x[6]],[Ori.y[3],Ori.y[6]],[Ori.x[4],Ori.x[5]],[Ori.y[4],Ori.y[5]],]
    CF50n = [numpy.mean([Ori.x[0],Ori.x[1],Ori.x[2],Ori.x[3],Ori.x[4],Ori.x[5],Ori.x[6]]),\
             numpy.mean([Ori.y[0],Ori.y[1],Ori.y[2],Ori.y[3],Ori.y[4],Ori.y[5],Ori.y[6]])]
    #伐#
    C_F51 = [[Ori.x[7],Ori.x[51]],[Ori.y[7],Ori.y[51]],[Ori.x[31],Ori.x[51]],[Ori.y[31],Ori.y[51]]]
    CF51n = [numpy.mean([Ori.x[7],Ori.x[31],Ori.x[51]]),\
             numpy.mean([Ori.y[7],Ori.y[31],Ori.y[51]])]
    #玉井#
    C_F52 = [[Eri.x[1],Eri.x[43]],[Eri.y[1],Eri.y[43]],[Eri.x[1],Ori.x[11]],[Eri.y[1],Ori.y[11]],\
             [Eri.x[24],Eri.x[43]],[Eri.y[24],Eri.y[43]]]
    CF52n = [numpy.mean([Eri.x[1],Eri.x[24],Eri.x[43],Ori.x[11]]),\
             numpy.mean([Eri.y[1],Eri.y[24],Eri.y[43],Ori.y[11]])]
    #屏#
    C_F53 = [[Lep.x[2],Lep.x[3]],[Lep.y[2],Lep.y[3]]]
    CF53n = [numpy.mean([Lep.x[2],Lep.x[3]]),\
             numpy.mean([Lep.y[2],Lep.y[3]])]
    #軍井#
    C_F54 = [[Lep.x[8],Lep.x[9]],[Lep.y[8],Lep.y[9]],[Lep.x[8],Lep.x[20]],[Lep.y[8],Lep.y[20]],\
             [Lep.x[9],Lep.x[10]],[Lep.y[9],Lep.y[10]]]
    CF54n = [numpy.mean([Lep.x[8],Lep.x[9],Lep.x[10],Lep.x[20]]),\
             numpy.mean([Lep.y[8],Lep.y[9],Lep.y[10],Lep.y[20]])]
    #厠#
    C_F55 = [[Lep.x[0],Lep.x[1]],[Lep.y[0],Lep.y[1]],[Lep.x[1],Lep.x[5]],[Lep.y[1],Lep.y[5]],\
             [Lep.x[5],Lep.x[7]],[Lep.y[5],Lep.y[7]]]
    CF55n = [numpy.mean([Lep.x[0],Lep.x[1],Lep.x[5],Lep.x[7]]),\
             numpy.mean([Lep.y[0],Lep.y[1],Lep.y[5],Lep.y[7]])]
    #屎#
    C_F56 = []
    CF56n = [Col.x[11],Col.y[11]]

    C_F_list = [C_F01,C_F02,C_F03,C_F04,C_F05,C_F06,C_F07,C_F08,C_F09,C_F10,\
                C_F11,C_F12,C_F13,C_F14,C_F15,C_F16,C_F17,C_F18,C_F19,C_F20,\
                C_F21,C_F22,C_F23,C_F24,C_F25,C_F26,C_F27,C_F28,C_F29,C_F30,\
                C_F31,C_F32,C_F33,C_F34,C_F35,C_F36,C_F37,C_F38,C_F39,C_F40,\
                C_F41,C_F42,C_F43,C_F44,C_F45,C_F46,C_F47,C_F48,C_F49,C_F50,\
                C_F51,C_F52,C_F53,C_F54,C_F55,C_F56]

    # 西宮白虎 linecollection
    C_F_line_z_xy1 = []
    C_F_line_z_xy2 = [] 
    C_F_line_xy1 = []
    C_F_line_xy2 = []        
    for i in range(len(C_F_list)):
        for j in range(len(C_F_list[i]))[0::2]:
            if math.hypot(C_F_list[i][j][0]-C_F_list[i][j][1],C_F_list[i][j+1][0]-C_F_list[i][j+1][1]) < hori_border:
                if i in set([0,9,15,22,31,46,49]):
                    C_F_line_z_xy1.append((C_F_list[i][j][0],C_F_list[i][j+1][0]))
                    C_F_line_z_xy2.append((C_F_list[i][j][1],C_F_list[i][j+1][1]))
                else:
                    C_F_line_xy1.append((C_F_list[i][j][0],C_F_list[i][j+1][0]))
                    C_F_line_xy2.append((C_F_list[i][j][1],C_F_list[i][j+1][1]))

    C_F_line_z_list = []
    for i in range(len(C_F_line_z_xy1)):            
        C_F_line_z_list.append([C_F_line_z_xy1[i],C_F_line_z_xy2[i]])
    
    C_F_line_list = []
    for i in range(len(C_F_line_xy1)):            
        C_F_line_list.append([C_F_line_xy1[i],C_F_line_xy2[i]])
    
    lc_C_F_z = mc.LineCollection(C_F_line_z_list, colors='yellow', zorder=2+2.5)
    lc_C_F = mc.LineCollection(C_F_line_list, colors='white', zorder=2+2.5)
    lc_C_F_z.set_alpha(plot_alpha)
    lc_C_F_z.set_clip_path(twlight_line)
    lc_C_F.set_alpha(plot_alpha)
    lc_C_F.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_F_z)
    ax0.add_collection(lc_C_F)

    CFn_list = [[CF01n,'奎宿'],[CF02n,'外屏'],[CF03n,'天溷'],[CF04n,'土司空'],[CF05n,'軍南門'],\
                [CF06n,'閣道'],[CF07n,'附路'],[CF08n,'王良'],[CF09n,'策'],[CF10n,'婁宿'],\
                [CF11n,'左更'],[CF12n,'右更'],[CF13n,'天倉'],[CF14n,'天庾'],[CF15n,'天大將軍'],\
                [CF16n,'胃宿'],[CF17n,'天廩'],[CF18n,'天囷'],[CF19n,'大陵'],[CF20n,'天船'],\
                [CF21n,'積尸'],[CF22n,'積水'],[CF23n,'昴宿'],[CF24n,'天阿'],[CF25n,'月'],\
                [CF26n,'天陰'],[CF27n,'芻蒿'],[CF28n,'天苑'],[CF29n,'卷舌'],[CF30n,'天讒'],\
                [CF31n,'礪石'],[CF32n,'畢宿'],[CF33n,'附耳'],[CF34n,'天街'],[CF35n,'天節'],\
                [CF36n,'諸王'],[CF37n,'天高'],[CF38n,'九州殊口'],[CF39n,'五車'],[CF40an,'柱'],\
                [CF40bn,'柱'],[CF40cn,'柱'],[CF41n,'天潢'],[CF42n,'咸池'],[CF43n,'天關'],\
                [CF44n,'參旗'],[CF45n,'九斿'],[CF46n,'天園'],[CF47n,'觜宿'],[CF48n,'司怪'],\
                [CF49n,'座旗'],[CF50n,'參宿'],[CF51n,'伐'],[CF52n,'玉井'],[CF53n,'屏'],\
                [CF54n,'軍井'],[CF55n,'厠'],[CF56n,'屎']]

    for i in range(len(CFn_list)):
        if len(CFn_list[i][0]) != 0:
            if (CFn_list[i][0][0])**2 < (hori_border/2)**2-(CFn_list[i][0][1])**2 \
               and max(CFn_list[i][0])-min(CFn_list[i][0]) < hori_border:
                if i in set([0,9,15,22,31,48,51]):
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0],CFn_list[i][0][1]),color='y',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=9+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]+olw,CFn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]+olw,CFn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]+olw,CFn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0],CFn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0],CFn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]-olw,CFn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]-olw,CFn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0]-olw,CFn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
##                else:
##                    ax0.annotate(str(CFn_list[i][1]),(CFn_list[i][0][0],CFn_list[i][0][1]),color='w',\
##                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ##########
    #南宮朱雀#
    ##########
    #井宿#
    C_G01 = [[Gem.x[1],Gem.x[7]],[Gem.y[1],Gem.y[7]],[Gem.x[1],Gem.x[12]],[Gem.y[1],Gem.y[12]],\
             [Gem.x[1],Gem.x[15]],[Gem.y[1],Gem.y[15]],[Gem.x[3],Gem.x[15]],[Gem.y[3],Gem.y[15]],\
             [Gem.x[5],Gem.x[38]],[Gem.y[5],Gem.y[38]],[Gem.x[10],Gem.x[12]],[Gem.y[10],Gem.y[12]],\
             [Gem.x[12],Gem.x[38]],[Gem.y[12],Gem.y[38]],[Gem.x[15],Gem.x[38]],[Gem.y[15],Gem.y[38]]]
    CG01n = [numpy.mean([Gem.x[1],Gem.x[3],Gem.x[5],Gem.x[7],Gem.x[10],Gem.x[12],Gem.x[15],Gem.x[38]]),\
             numpy.mean([Gem.y[1],Gem.y[3],Gem.y[5],Gem.y[7],Gem.y[10],Gem.y[12],Gem.y[15],Gem.y[38]])]
    #鉞#
    C_G02 = []
    CG02n = [Gem.x[6],Gem.y[6]]
    #南河#
    C_G03 = [[CMi.x[0],CMi.x[1]],[CMi.y[0],CMi.y[1]],[CMi.x[1],CMi.x[5]],[CMi.y[1],CMi.y[5]]]
    CG03n = [numpy.mean([CMi.x[0],CMi.x[1],CMi.x[5]]),\
             numpy.mean([CMi.y[0],CMi.y[1],CMi.y[5]])]
    #北河#
    C_G04 = [[Gem.x[0],Gem.x[4]],[Gem.y[0],Gem.y[4]],[Gem.x[4],Gem.x[17]],[Gem.y[4],Gem.y[17]]]
    CG04n = [numpy.mean([Gem.x[0],Gem.x[4],Gem.x[17]]),\
             numpy.mean([Gem.y[0],Gem.y[4],Gem.y[17]])]
    #天樽#
    C_G05 = [[Gem.x[8],Gem.x[28]],[Gem.y[8],Gem.y[28]],[Gem.x[8],Gem.x[34]],[Gem.y[8],Gem.y[34]]]
    CG05n = [numpy.mean([Gem.x[8],Gem.x[28],Gem.x[34]]),\
             numpy.mean([Gem.y[8],Gem.y[28],Gem.y[34]])]
    #五諸候#
    C_G06 = [[Gem.x[11],Gem.x[19]],[Gem.y[11],Gem.y[19]],[Gem.x[13],Gem.x[14]],[Gem.y[13],Gem.y[14]],\
             [Gem.x[13],Gem.x[19]],[Gem.y[13],Gem.y[19]],[Gem.x[14],Gem.x[25]],[Gem.y[14],Gem.y[25]]]
    CG06n = [numpy.mean([Gem.x[11],Gem.x[13],Gem.x[14],Gem.x[19],Gem.x[25]]),\
             numpy.mean([Gem.y[11],Gem.y[13],Gem.y[14],Gem.y[19],Gem.y[25]])]
    #積水#
    C_G07 = []
    CG07n = [Aur.x[31],Aur.y[31]]
    #積薪#
    C_G08 = []
    CG08n = [Gem.x[9],Gem.y[9]]
    #水府#
    C_G09 = [[Ori.x[24],Ori.x[27]],[Ori.y[24],Ori.y[27]],[Ori.x[27],Ori.x[60]],[Ori.y[27],Ori.y[60]],\
             [Ori.x[47],Ori.x[60]],[Ori.y[47],Ori.y[60]]]
    CG09n = [numpy.mean([Ori.x[24],Ori.x[27],Ori.x[47],Ori.x[60]]),\
             numpy.mean([Ori.y[24],Ori.y[27],Ori.y[47],Ori.y[60]])]
    #水位#
    C_G10 = [[Cnc.x[5],CMi.x[11]],[Cnc.y[5],CMi.y[11]],[Cnc.x[5],Cnc.x[25]],[Cnc.y[5],Cnc.y[25]],\
             [CMi.x[4],CMi.x[11]],[CMi.y[4],CMi.y[11]],]
    CG10n = [numpy.mean([Cnc.x[5],Cnc.x[25],CMi.x[4],CMi.x[11]]),\
             numpy.mean([Cnc.y[5],Cnc.y[25],CMi.y[4],CMi.y[11]])]
    #四瀆#
    C_G11 = [[Gem.x[32],Mon.x[10]],[Gem.y[32],Mon.y[10]],[Mon.x[4],Mon.x[6]],[Mon.y[4],Mon.y[6]],\
             [Mon.x[6],Mon.x[10]],[Mon.y[6],Mon.y[10]]]
    CG11n = [numpy.mean([Gem.x[32],Mon.x[4],Mon.x[6],Mon.x[10]]),\
             numpy.mean([Gem.y[32],Mon.y[4],Mon.y[6],Mon.y[10]])]
    #軍市#
    C_G12 = [[CMa.x[3],CMa.x[14]],[CMa.y[3],CMa.y[14]],[CMa.x[3],CMa.x[17]],[CMa.y[3],CMa.y[17]],\
             [CMa.x[9],CMa.x[14]],[CMa.y[9],CMa.y[14]],[CMa.x[9],CMa.x[22]],[CMa.y[9],CMa.y[22]],\
             [CMa.x[17],CMa.x[25]],[CMa.y[17],CMa.y[25]],[CMa.x[22],CMa.x[25]],[CMa.y[22],CMa.y[25]]]
    CG12n = [numpy.mean([CMa.x[3],CMa.x[9],CMa.x[14],CMa.x[17],CMa.x[22],CMa.x[25]]),\
             numpy.mean([CMa.y[3],CMa.y[9],CMa.y[14],CMa.y[17],CMa.y[22],CMa.y[25]])]
    #野雞#
    C_G13 = []
    CG13n = [CMa.x[10],CMa.y[10]]
    #丈人#
    C_G14 = [[Col.x[0],Col.x[3]],[Col.y[0],Col.y[3]]]
    CG14n = [numpy.mean([Col.x[0],Col.x[3]]),\
             numpy.mean([Col.y[0],Col.y[3]])]
    #子#
    C_G15 = [[Col.x[1],Col.x[8]],[Col.y[1],Col.y[8]]]
    CG15n = [numpy.mean([Col.x[1],Col.x[8]]),\
             numpy.mean([Col.y[1],Col.y[8]])]
    #孫#
    C_G16 = [[Col.x[6],Col.x[10]],[Col.y[6],Col.y[10]]]
    CG16n = [numpy.mean([Col.x[6],Col.x[10]]),\
             numpy.mean([Col.y[6],Col.y[10]])]
    #闕丘#
    C_G17 = [[Mon.x[2],Mon.x[5]],[Mon.y[2],Mon.y[5]]]
    CG17n = [numpy.mean([Mon.x[2],Mon.x[5]]),\
             numpy.mean([Mon.y[2],Mon.y[5]])]
    #天狼#
    C_G18 = []
    CG18n = [CMa.x[0],CMa.y[0]]
    #弧矢#
    C_G19 = [[CMa.x[1],CMa.x[4]],[CMa.y[1],CMa.y[4]],[CMa.x[1],CMa.x[11]],[CMa.y[1],CMa.y[11]],\
             [CMa.x[2],CMa.x[4]],[CMa.y[2],CMa.y[4]],[CMa.x[4],Pup.x[7]],[CMa.y[4],Pup.y[7]],\
             [CMa.x[4],Pup.x[21]],[CMa.y[4],Pup.y[21]],[CMa.x[11],Pup.x[1]],[CMa.y[11],Pup.y[1]],\
             [Pup.x[1],Pup.x[7]],[Pup.y[1],Pup.y[7]],[Pup.x[7],Pup.x[37]],[Pup.y[7],Pup.y[37]],\
             [Pup.x[21],Pup.x[22]],[Pup.y[21],Pup.y[22]],[Pup.x[22],Pup.x[37]],[Pup.y[22],Pup.y[37]]]
    CG19n = [numpy.mean([CMa.x[1],CMa.x[2],CMa.x[4],CMa.x[11],Pup.x[1],Pup.x[7],Pup.x[21],Pup.x[22],\
                         Pup.x[37]]),\
             numpy.mean([CMa.y[1],CMa.y[2],CMa.y[4],CMa.y[11],Pup.y[1],Pup.y[7],Pup.y[21],Pup.y[22],\
                         Pup.y[37]])]
    #老人#
    C_G20 = []
    CG20n = [Car.x[0],Car.y[0]]
    #鬼宿#
    C_G21 = [[Cnc.x[1],Cnc.x[4]],[Cnc.y[1],Cnc.y[4]],[Cnc.x[4],Cnc.x[14]],[Cnc.y[4],Cnc.y[14]],\
             [Cnc.x[14],Cnc.x[16]],[Cnc.y[14],Cnc.y[16]]]
    CG21n = [numpy.mean([Cnc.x[1],Cnc.x[4],Cnc.x[14],Cnc.x[16]]),\
             numpy.mean([Cnc.y[1],Cnc.y[4],Cnc.y[14],Cnc.y[16]])]
    #積尸#
    C_G22 = []
    CG22n = [Cnc.x[78],Cnc.y[78]]
    #爟#
    C_G23 = [[Cnc.x[24],Cnc.x[26]],[Cnc.y[24],Cnc.y[26]],[Cnc.x[24],Cnc.x[45]],[Cnc.y[24],Cnc.y[45]],\
             [Cnc.x[31],Cnc.x[45]],[Cnc.y[31],Cnc.y[45]]]
    CG23n = [numpy.mean([Cnc.x[24],Cnc.x[26],Cnc.x[31],Cnc.x[45]]),\
             numpy.mean([Cnc.y[24],Cnc.y[26],Cnc.y[31],Cnc.y[45]])]
    #天狗#
    C_G24 = [[Pyx.x[0],Pyx.x[1]],[Pyx.y[0],Pyx.y[1]],[Pyx.x[0],Pyx.x[2]],[Pyx.y[0],Pyx.y[2]],\
             [Pyx.x[0],Pyx.x[7]],[Pyx.y[0],Pyx.y[7]],[Pyx.x[1],Vel.x[14]],[Pyx.y[1],Vel.y[14]],\
             [Vel.x[14],Vel.x[15]],[Vel.y[14],Vel.y[15]]]
    CG24n = [numpy.mean([Pyx.x[0],Pyx.x[1],Pyx.x[2],Pyx.x[7],Vel.x[14],Vel.x[15]]),\
             numpy.mean([Pyx.y[0],Pyx.y[1],Pyx.y[2],Pyx.y[7],Vel.y[14],Vel.y[15]])]
    #外廚#
    C_G25 = [[Hya.x[10],Hya.x[23]],[Hya.y[10],Hya.y[23]],[Hya.x[23],Hya.x[58]],[Hya.y[23],Hya.y[58]]]
    CG25n = [numpy.mean([Hya.x[10],Hya.x[23],Hya.x[58]]),\
             numpy.mean([Hya.y[10],Hya.y[23],Hya.y[58]])]
    #天社#
    C_G26 = [[Vel.x[0],Vel.x[10]],[Vel.y[0],Vel.y[10]],[Vel.x[1],Vel.x[3]],[Vel.y[1],Vel.y[3]],\
             [Vel.x[1],Vel.x[10]],[Vel.y[1],Vel.y[10]],[Vel.x[3],Vel.x[5]],[Vel.y[3],Vel.y[5]]]
    CG26n = [numpy.mean([Vel.x[0],Vel.x[1],Vel.x[3],Vel.x[5],Vel.x[10]]),\
             numpy.mean([Vel.y[0],Vel.y[1],Vel.y[3],Vel.y[5],Vel.y[10]])]
    #天記#
    C_G27 = []
    CG27n = [Vel.x[2],Vel.y[2]]
    #柳宿#
    C_G28 = [[Hya.x[2],Hya.x[5]],[Hya.y[2],Hya.y[5]],[Hya.x[2],Hya.x[41]],[Hya.y[2],Hya.y[41]],\
             [Hya.x[5],Hya.x[13]],[Hya.y[5],Hya.y[13]],[Hya.x[9],Hya.x[41]],[Hya.y[9],Hya.y[41]],\
             [Hya.x[13],Hya.x[19]],[Hya.y[13],Hya.y[19]],[Hya.x[15],Hya.x[17]],[Hya.y[15],Hya.y[17]],\
             [Hya.x[15],Hya.x[19]],[Hya.y[15],Hya.y[19]]]
    CG28n = [numpy.mean([Hya.x[2],Hya.x[5],Hya.x[9],Hya.x[13],Hya.x[15],Hya.x[17],Hya.x[19],Hya.x[41]]),\
             numpy.mean([Hya.y[2],Hya.y[5],Hya.y[9],Hya.y[13],Hya.y[15],Hya.y[17],Hya.y[19],Hya.y[41]])]
    #酒旗#
    C_G29 = [[Leo.x[30],Leo.x[41]],[Leo.y[30],Leo.y[41]],[Leo.x[30],Leo.x[43]],[Leo.y[30],Leo.y[43]]]
    CG29n = [numpy.mean([Leo.x[30],Leo.x[41],Leo.x[43]]),\
             numpy.mean([Leo.y[30],Leo.y[41],Leo.y[43]])]
    #星宿#
    C_G30 = [[Hya.x[0],Hya.x[21]],[Hya.y[0],Hya.y[21]],[Hya.x[0],Hya.x[30]],[Hya.y[0],Hya.y[30]],\
             [Hya.x[0],Hya.x[152]],[Hya.y[0],Hya.y[152]],[Hya.x[11],Hya.x[20]],[Hya.y[11],Hya.y[20]],\
             [Hya.x[20],Hya.x[21]],[Hya.y[20],Hya.y[21]],[Hya.x[29],Hya.x[30]],[Hya.y[29],Hya.y[30]],\
             [Hya.x[29],Hya.x[152]],[Hya.y[29],Hya.y[152]]]
    CG30n = [numpy.mean([Hya.x[0],Hya.x[11],Hya.x[20],Hya.x[21],Hya.x[29],Hya.x[30],Hya.x[152]]),\
             numpy.mean([Hya.y[0],Hya.y[11],Hya.y[20],Hya.y[21],Hya.y[29],Hya.y[30],Hya.y[152]])]
    #天相#
    C_G31 = [[Sex.x[4],Sex.x[7]],[Sex.y[4],Sex.y[7]]]
    CG31n = [numpy.mean([Sex.x[4],Sex.x[7]]),\
             numpy.mean([Sex.y[4],Sex.y[7]])]
    #軒轅#
    C_G32 = [[Leo.x[0],Leo.x[7]],[Leo.y[0],Leo.y[7]],[Leo.x[0],Leo.x[8]],[Leo.y[0],Leo.y[8]],\
             [Leo.x[0],Leo.x[10]],[Leo.y[0],Leo.y[10]],[Leo.x[3],Leo.x[6]],[Leo.y[3],Leo.y[6]],\
             [Leo.x[3],Leo.x[8]],[Leo.y[3],Leo.y[8]],[Leo.x[4],Leo.x[11]],[Leo.y[4],Leo.y[11]],\
             [Leo.x[4],Leo.x[15]],[Leo.y[4],Leo.y[15]],[Leo.x[6],Leo.x[11]],[Leo.y[6],Leo.y[11]],\
             [Leo.x[15],Leo.x[18]],[Leo.y[15],Leo.y[18]],[Leo.x[18],Leo.x[57]],[Leo.y[18],Leo.y[57]],\
             [Leo.x[57],Lyn.x[0]],[Leo.y[57],Lyn.y[0]],[Lyn.x[0],Lyn.x[1]],[Lyn.y[0],Lyn.y[1]],\
             [Lyn.x[1],Lyn.x[6]],[Lyn.y[1],Lyn.y[6]],[Lyn.x[2],Lyn.x[6]],[Lyn.y[2],Lyn.y[6]]]
    CG32n = [numpy.mean([Leo.x[0],Leo.x[3],Leo.x[4],Leo.x[6],Leo.x[7],Leo.x[8],Leo.x[10],Leo.x[11],\
                         Leo.x[15],Leo.x[18],Leo.x[57],Lyn.x[0],Lyn.x[1],Lyn.x[2],Lyn.x[6]]),\
             numpy.mean([Leo.y[0],Leo.y[3],Leo.y[4],Leo.y[6],Leo.y[7],Leo.y[8],Leo.y[10],Leo.y[11],\
                         Leo.y[15],Leo.y[18],Leo.y[57],Lyn.y[0],Lyn.y[1],Lyn.y[2],Lyn.y[6]])]
    #御女#
    C_G33 = []
    CG33n = [Leo.x[16],Leo.y[16]]
    #內平#
    C_G34 = [[LMi.x[2],LMi.x[24]],[LMi.y[2],LMi.y[24]]]
    CG34n = [numpy.mean([LMi.x[2],LMi.x[24]]),\
             numpy.mean([LMi.y[2],LMi.y[24]])]
    #張宿#
    C_G35 = [[Hya.x[7],Hya.x[8]],[Hya.y[7],Hya.y[8]],[Hya.x[7],Hya.x[12]],[Hya.y[7],Hya.y[12]],\
             [Hya.x[8],Hya.x[35]],[Hya.y[8],Hya.y[35]],[Hya.x[8],Hya.x[37]],[Hya.y[8],Hya.y[37]],\
             [Hya.x[12],Hya.x[37]],[Hya.y[12],Hya.y[37]],[Hya.x[12],Hya.x[47]],[Hya.y[12],Hya.y[47]]]
    CG35n = [numpy.mean([Hya.x[7],Hya.x[8],Hya.x[12],Hya.x[35],Hya.x[37],Hya.x[47]]),\
             numpy.mean([Hya.y[7],Hya.y[8],Hya.y[12],Hya.y[35],Hya.y[37],Hya.y[47]])]
    #翼宿#
    C_G36 = [[Crt.x[0],Crt.x[2]],[Crt.y[0],Crt.y[2]],[Crt.x[0],Crt.x[9]],[Crt.y[0],Crt.y[9]],\
             [Crt.x[1],Crt.x[2]],[Crt.y[1],Crt.y[2]],[Crt.x[1],Crt.x[7]],[Crt.y[1],Crt.y[7]],\
             [Crt.x[2],Crt.x[5]],[Crt.y[2],Crt.y[5]],[Crt.x[3],Crt.x[7]],[Crt.y[3],Crt.y[7]],\
             [Crt.x[4],Crt.x[6]],[Crt.y[4],Crt.y[6]],[Crt.x[5],Crt.x[7]],[Crt.y[5],Crt.y[7]],\
             [Crt.x[5],Crt.x[8]],[Crt.y[5],Crt.y[8]],[Crt.x[6],Crt.x[15]],[Crt.y[6],Crt.y[15]],\
             [Crt.x[9],Crt.x[15]],[Crt.y[9],Crt.y[15]],[Crt.x[1],Hya.x[3]],[Crt.y[1],Hya.y[3]],\
             [Crt.x[3],Hya.x[38]],[Crt.y[3],Hya.y[38]]]
    CG36n = [numpy.mean([Crt.x[0],Crt.x[1],Crt.x[2],Crt.x[3],Crt.x[4],Crt.x[5],Crt.x[6],Crt.x[7],\
                         Crt.x[8],Crt.x[9],Crt.x[15],Hya.x[3],Hya.x[38]]),\
             numpy.mean([Crt.y[0],Crt.y[1],Crt.y[2],Crt.y[3],Crt.y[4],Crt.y[5],Crt.y[6],Crt.y[7],\
                         Crt.y[8],Crt.y[9],Crt.y[15],Hya.y[3],Hya.y[38]])]
    #軫宿#
    C_G37 = [[Crv.x[0],Crv.x[2]],[Crv.y[0],Crv.y[2]],[Crv.x[0],Crv.x[3]],[Crv.y[0],Crv.y[3]],\
             [Crv.x[1],Crv.x[2]],[Crv.y[1],Crv.y[2]]]
    CG37n = [numpy.mean([Crv.x[0],Crv.x[1],Crv.x[2],Crv.x[3]]),\
             numpy.mean([Crv.y[0],Crv.y[1],Crv.y[2],Crv.y[3]])]
    #長沙#
    C_G38 = []
    CG38n = [Crv.x[7],Crv.y[7]]
    #左轄#
    C_G39 = []
    CG39n = [Crv.x[5],Crv.y[5]]
    #右轄#
    C_G40 = []
    CG40n = [Crv.x[4],Crv.y[4]]
    #青丘#
    C_G41 = [[Hya.x[6],Hya.x[46]],[Hya.y[6],Hya.y[46]],[Hya.x[6],Hya.x[123]],[Hya.y[6],Hya.y[123]],\
             [Hya.x[14],Hya.x[119]],[Hya.y[14],Hya.y[119]],[Hya.x[26],Hya.x[96]],[Hya.y[26],Hya.y[96]],\
             [Hya.x[46],Hya.x[80]],[Hya.y[46],Hya.y[80]],[Hya.x[80],Hya.x[119]],[Hya.y[80],Hya.y[119]],\
             [Hya.x[96],Hya.x[123]],[Hya.y[96],Hya.y[123]]]
    CG41n = [numpy.mean([Hya.x[6],Hya.x[14],Hya.x[26],Hya.x[46],Hya.x[80],Hya.x[96],Hya.x[119],Hya.x[123]]),\
             numpy.mean([Hya.y[6],Hya.y[14],Hya.y[26],Hya.y[46],Hya.y[80],Hya.y[96],Hya.y[119],Hya.y[123]])]

    C_G_list = [C_G01,C_G02,C_G03,C_G04,C_G05,C_G06,C_G07,C_G08,C_G09,C_G10,\
                C_G11,C_G12,C_G13,C_G14,C_G15,C_G16,C_G17,C_G18,C_G19,C_G20,\
                C_G21,C_G22,C_G23,C_G24,C_G25,C_G26,C_G27,C_G28,C_G29,C_G30,\
                C_G31,C_G32,C_G33,C_G34,C_G35,C_G36,C_G37,C_G38,C_G39,C_G40,\
                C_G41]

    # 南宮朱雀 linecollection
    C_G_line_z_xy1 = []
    C_G_line_z_xy2 = [] 
    C_G_line_xy1 = []
    C_G_line_xy2 = []        
    for i in range(len(C_G_list)):
        for j in range(len(C_G_list[i]))[0::2]:
            if math.hypot(C_G_list[i][j][0]-C_G_list[i][j][1],C_G_list[i][j+1][0]-C_G_list[i][j+1][1]) < hori_border:
                if i in set([0,20,27,29,34,35,36]):
                    C_G_line_z_xy1.append((C_G_list[i][j][0],C_G_list[i][j+1][0]))
                    C_G_line_z_xy2.append((C_G_list[i][j][1],C_G_list[i][j+1][1]))
                else:
                    C_G_line_xy1.append((C_G_list[i][j][0],C_G_list[i][j+1][0]))
                    C_G_line_xy2.append((C_G_list[i][j][1],C_G_list[i][j+1][1]))

    C_G_line_z_list = []
    for i in range(len(C_G_line_z_xy1)):            
        C_G_line_z_list.append([C_G_line_z_xy1[i],C_G_line_z_xy2[i]])
    
    C_G_line_list = []
    for i in range(len(C_G_line_xy1)):            
        C_G_line_list.append([C_G_line_xy1[i],C_G_line_xy2[i]])
    
    lc_C_G_z = mc.LineCollection(C_G_line_z_list, colors='yellow', zorder=2+2.5)
    lc_C_G = mc.LineCollection(C_G_line_list, colors='white', zorder=2+2.5)
    lc_C_G_z.set_alpha(plot_alpha)
    lc_C_G_z.set_clip_path(twlight_line)
    lc_C_G.set_alpha(plot_alpha)
    lc_C_G.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_G_z)
    ax0.add_collection(lc_C_G)

    CGn_list = [[CG01n,'井宿'],[CG02n,'鉞'],[CG03n,'南河'],[CG04n,'北河'],[CG05n,'天樽'],\
                [CG06n,'五諸候'],[CG07n,'積水'],[CG08n,'積薪'],[CG09n,'水府'],[CG10n,'水位'],\
                [CG11n,'四瀆'],[CG12n,'軍市'],[CG13n,'野雞'],[CG14n,'丈人'],[CG15n,'子'],\
                [CG16n,'孫'],[CG17n,'闕丘'],[CG18n,'天狼'],[CG19n,'弧矢'],[CG20n,'老人'],\
                [CG21n,'鬼宿'],[CG22n,'積尸'],[CG23n,'爟'],[CG24n,'天狗'],[CG25n,'外廚'],\
                [CG26n,'天社'],[CG27n,'天記'],[CG28n,'柳宿'],[CG29n,'酒旗'],[CG30n,'星宿'],\
                [CG31n,'天相'],[CG32n,'軒轅'],[CG33n,'御女'],[CG34n,'內平'],[CG35n,'張宿'],\
                [CG36n,'翼宿'],[CG37n,'軫宿'],[CG38n,'長沙'],[CG39n,'左轄'],[CG40n,'右轄'],\
                [CG41n,'青丘']]

    for i in range(len(CGn_list)):
        if len(CGn_list[i][0]) != 0:
            if (CGn_list[i][0][0])**2 < (hori_border/2)**2-(CGn_list[i][0][1])**2 \
               and max(CGn_list[i][0])-min(CGn_list[i][0]) < hori_border:
                if i in set([0,20,27,29,34,35,36]):
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0],CGn_list[i][0][1]),color='y',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=9+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]+olw,CGn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]+olw,CGn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]+olw,CGn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0],CGn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0],CGn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]-olw,CGn_list[i][0][1]+olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]-olw,CGn_list[i][0][1]),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0]-olw,CGn_list[i][0][1]-olw),color='k',\
                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top',zorder=8+2.5)
##                else:
##                    ax0.annotate(str(CGn_list[i][1]),(CGn_list[i][0][0],CGn_list[i][0][1]),color='w',\
##                                      fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    ##########
    #南極星區#
    ##########
    #海山#
    C_H01 = [[Car.x[13],Cen.x[11]],[Car.y[13],Cen.y[11]],[Cen.x[11],Mus.x[3]],[Cen.y[11],Mus.y[3]]]
    CH01n = [numpy.mean([Car.x[13],Cen.x[11],Mus.x[3]]),\
             numpy.mean([Car.y[13],Cen.y[11],Mus.y[3]])]
    #十字架#
    C_H02 = [[Cru.x[0],Cru.x[4]],[Cru.y[0],Cru.y[4]],[Cru.x[2],Cru.x[3]],[Cru.y[2],Cru.y[3]]]
    CH02n = [numpy.mean([Cru.x[0],Cru.x[2],Cru.x[3],Cru.x[4]]),\
             numpy.mean([Cru.y[0],Cru.y[2],Cru.y[3],Cru.y[4]])]
    #馬尾#
    C_H03 = [[Cen.x[8],Cen.x[20]],[Cen.y[8],Cen.y[20]],[Cen.x[20],Cen.x[49]],[Cen.y[20],Cen.y[49]]]
    CH03n = [numpy.mean([Cen.x[8],Cen.x[20],Cen.x[49]]),\
             numpy.mean([Cen.y[8],Cen.y[20],Cen.y[49]])]
    #馬腹#
    C_H04 = []
    CH04n = [Cen.x[1],Cen.y[1]]
    #蜜蜂#
    C_H05 = [[Mus.x[0],Mus.x[1]],[Mus.y[0],Mus.y[1]]]
    CH05n = [numpy.mean([Mus.x[0],Mus.x[1]]),\
             numpy.mean([Mus.y[0],Mus.y[1]])]
    #三角形#
    C_H06 = [[TrA.x[0],TrA.x[1]],[TrA.y[0],TrA.y[1]],[TrA.x[0],TrA.x[2]],[TrA.y[0],TrA.y[2]],\
             [TrA.x[1],TrA.x[2]],[TrA.y[1],TrA.y[2]]]
    CH06n = [numpy.mean([TrA.x[0],TrA.x[1],TrA.x[2]]),\
             numpy.mean([TrA.y[0],TrA.y[1],TrA.y[2]])]
    #異雀#
    C_H07 = [[Aps.x[0],Aps.x[6]],[Aps.y[0],Aps.y[6]],[Aps.x[0],Aps.x[7]],[Aps.y[0],Aps.y[7]],\
             [Aps.x[1],Aps.x[2]],[Aps.y[1],Aps.y[2]],[Aps.x[1],Oct.x[20]],[Aps.y[1],Oct.y[20]],\
             [Aps.x[2],Aps.x[7]],[Aps.y[2],Aps.y[7]],[Aps.x[2],Aps.x[9]],[Aps.y[2],Aps.y[9]],\
             [Aps.x[4],Aps.x[9]],[Aps.y[4],Aps.y[9]],[Aps.x[5],Aps.x[7]],[Aps.y[5],Aps.y[7]]]
    CH07n = [numpy.mean([Aps.x[0],Aps.x[1],Aps.x[2],Aps.x[4],Aps.x[5],Aps.x[6],Aps.x[7],Aps.x[9],\
                         Oct.x[20]]),\
             numpy.mean([Aps.y[0],Aps.y[1],Aps.y[2],Aps.y[4],Aps.y[5],Aps.y[6],Aps.y[7],Aps.y[9],\
                         Oct.y[20]])]
    #孔雀#
    C_H08 = [[Pav.x[0],Pav.x[7]],[Pav.y[0],Pav.y[7]],[Pav.x[1],Pav.x[2]],[Pav.y[1],Pav.y[2]],\
             [Pav.x[2],Pav.x[10]],[Pav.y[2],Pav.y[10]],[Pav.x[3],Pav.x[5]],[Pav.y[3],Pav.y[5]],\
             [Pav.x[3],Pav.x[8]],[Pav.y[3],Pav.y[8]],[Pav.x[4],Pav.x[5]],[Pav.y[4],Pav.y[5]],\
             [Pav.x[4],Pav.x[7]],[Pav.y[4],Pav.y[7]],[Pav.x[6],Pav.x[10]],[Pav.y[6],Pav.y[10]],\
             [Pav.x[6],Pav.x[11]],[Pav.y[6],Pav.y[11]],[Pav.x[8],Pav.x[11]],[Pav.y[8],Pav.y[11]]]
    CH08n = [numpy.mean([Pav.x[0],Pav.x[1],Pav.x[2],Pav.x[3],Pav.x[4],Pav.x[5],Pav.x[6],Pav.x[7],\
                         Pav.x[8],Pav.x[10],Pav.x[11]]),\
             numpy.mean([Pav.y[0],Pav.y[1],Pav.y[2],Pav.y[3],Pav.y[4],Pav.y[5],Pav.y[6],Pav.y[7],\
                         Pav.y[8],Pav.y[10],Pav.y[11]])]
    #波斯#
    C_H09 = []
    CH09n = [Ind.x[0],Ind.y[0]]
    #蛇尾#
    C_H10 = [[Hyi.x[0],Oct.x[0]],[Hyi.y[0],Oct.y[0]],[Oct.x[0],Oct.x[6]],[Oct.y[0],Oct.y[6]]]
    CH10n = [numpy.mean([Hyi.x[0],Oct.x[0],Oct.x[6]]),\
             numpy.mean([Hyi.y[0],Oct.y[0],Oct.y[6]])]
    #蛇腹#
    C_H11 = [[Hyi.x[3],Hyi.x[4]],[Hyi.y[3],Hyi.y[4]],[Hyi.x[3],Hyi.x[5]],[Hyi.y[3],Hyi.y[5]],\
             [Hyi.x[4],Hyi.x[7]],[Hyi.y[4],Hyi.y[7]]]
    CH11n = [numpy.mean([Hyi.x[3],Hyi.x[4],Hyi.x[5],Hyi.x[7]]),\
             numpy.mean([Hyi.y[3],Hyi.y[4],Hyi.y[5],Hyi.y[7]])]
    #蛇首#
    C_H12 = [[Hyi.x[1],Ret.x[1]],[Hyi.y[1],Ret.y[1]]]
    CH12n = [numpy.mean([Hyi.x[1],Ret.x[1]]),\
             numpy.mean([Hyi.y[1],Ret.y[1]])]
    #鳥喙#
    C_H13 = [[Tuc.x[0],Tuc.x[4]],[Tuc.y[0],Tuc.y[4]],[Tuc.x[2],Tuc.x[5]],[Tuc.y[2],Tuc.y[5]],\
             [Tuc.x[2],Tuc.x[13]],[Tuc.y[2],Tuc.y[13]],[Tuc.x[3],Tuc.x[13]],[Tuc.y[3],Tuc.y[13]],\
             [Tuc.x[3],Tuc.x[25]],[Tuc.y[3],Tuc.y[25]],[Tuc.x[4],Tuc.x[25]],[Tuc.y[4],Tuc.y[25]]]
    CH13n = [numpy.mean([Tuc.x[0],Tuc.x[2],Tuc.x[3],Tuc.x[4],Tuc.x[5],Tuc.x[13],Tuc.x[25]]),\
             numpy.mean([Tuc.y[0],Tuc.y[2],Tuc.y[3],Tuc.y[4],Tuc.y[5],Tuc.y[13],Tuc.y[25]])]
    #鶴#
    C_H14 = [[Gru.x[0],Gru.x[1]],[Gru.y[0],Gru.y[1]],[Gru.x[1],Gru.x[3]],[Gru.y[1],Gru.y[3]],\
             [Gru.x[1],Gru.x[4]],[Gru.y[1],Gru.y[4]],[Gru.x[1],Gru.x[6]],[Gru.y[1],Gru.y[6]],\
             [Gru.x[1],Gru.x[7]],[Gru.y[1],Gru.y[7]],[Gru.x[1],Gru.x[8]],[Gru.y[1],Gru.y[8]],\
             [Gru.x[3],Tuc.x[1]],[Gru.y[3],Tuc.y[1]],[Gru.x[6],Gru.x[10]],[Gru.y[6],Gru.y[10]],\
             [Gru.x[7],Tuc.x[1]],[Gru.y[7],Tuc.y[1]]]
    CH14n = [numpy.mean([Gru.x[0],Gru.x[1],Gru.x[3],Gru.x[4],Gru.x[6],Gru.x[7],Gru.x[8],Gru.x[10],\
                         Tuc.x[1]]),\
             numpy.mean([Gru.y[0],Gru.y[1],Gru.y[3],Gru.y[4],Gru.y[6],Gru.y[7],Gru.y[8],Gru.y[10],\
                         Tuc.y[1]])]
    #火鳥#
    C_H15 = [[Phe.x[0],Phe.x[5]],[Phe.y[0],Phe.y[5]],[Phe.x[0],Phe.x[9]],[Phe.y[0],Phe.y[9]],\
             [Phe.x[1],Phe.x[2]],[Phe.y[1],Phe.y[2]],[Phe.x[1],Phe.x[12]],[Phe.y[1],Phe.y[12]],\
             [Phe.x[3],Phe.x[5]],[Phe.y[3],Phe.y[5]],[Phe.x[3],Phe.x[11]],[Phe.y[3],Phe.y[11]],\
             [Phe.x[9],Phe.x[12]],[Phe.y[9],Phe.y[12]],[Phe.x[10],Phe.x[11]],[Phe.y[10],Phe.y[11]],\
             [Phe.x[10],Scl.x[1]],[Phe.y[10],Scl.y[1]]]
    CH15n = [numpy.mean([Phe.x[0],Phe.x[1],Phe.x[2],Phe.x[3],Phe.x[5],Phe.x[9],Phe.x[10],Phe.x[11],\
                         Phe.x[12],Scl.x[1]]),\
             numpy.mean([Phe.y[0],Phe.y[1],Phe.y[2],Phe.y[3],Phe.y[5],Phe.y[9],Phe.y[10],Phe.y[11],\
                         Phe.y[12],Scl.y[1]])]
    #水委#
    C_H16 = [[Eri.x[0],Phe.x[4]],[Eri.y[0],Phe.y[4]],[Phe.x[4],Phe.x[7]],[Phe.y[4],Phe.y[7]]]
    CH16n = [numpy.mean([Eri.x[0],Phe.x[4],Phe.x[7]]),\
             numpy.mean([Eri.y[0],Phe.y[4],Phe.y[7]])]
    #附白#
    C_H17 = [[Hyi.x[2],Hyi.x[6]],[Hyi.y[2],Hyi.y[6]]]
    CH17n = [numpy.mean([Hyi.x[2],Hyi.x[6]]),\
             numpy.mean([Hyi.y[2],Hyi.y[6]])]
    #夾白#
    C_H18 = [[Dor.x[6],Ret.x[0]],[Dor.y[6],Ret.y[0]]]
    CH18n = [numpy.mean([Dor.x[6],Ret.x[0]]),\
             numpy.mean([Dor.y[6],Ret.y[0]])]
    #金魚#
    C_H19 = [[Dor.x[0],Dor.x[1]],[Dor.y[0],Dor.y[1]],[Dor.x[0],Dor.x[2]],[Dor.y[0],Dor.y[2]],\
             [Dor.x[1],Dor.x[3]],[Dor.y[1],Dor.y[3]],[Dor.x[3],Dor.x[8]],[Dor.y[3],Dor.y[8]]]
    CH19n = [numpy.mean([Dor.x[0],Dor.x[1],Dor.x[2],Dor.x[3],Dor.x[8]]),\
             numpy.mean([Dor.y[0],Dor.y[1],Dor.y[2],Dor.y[3],Dor.y[8]])]
    #海石#
    C_H20 = [[Car.x[2],Car.x[3]],[Car.y[2],Car.y[3]],[Car.x[3],Car.x[18]],[Car.y[3],Car.y[18]],\
             [Car.x[5],Car.x[11]],[Car.y[5],Car.y[11]],[Car.x[11],Car.x[18]],[Car.y[11],Car.y[18]]]
    CH20n = [numpy.mean([Car.x[2],Car.x[3],Car.x[5],Car.x[11],Car.x[18]]),\
             numpy.mean([Car.y[2],Car.y[3],Car.y[5],Car.y[11],Car.y[18]])]
    #飛魚#
    C_H21 = [[Vol.x[0],Vol.x[4]],[Vol.y[0],Vol.y[4]],[Vol.x[1],Vol.x[4]],[Vol.y[1],Vol.y[4]],\
             [Vol.x[2],Vol.x[4]],[Vol.y[2],Vol.y[4]],[Vol.x[3],Vol.x[4]],[Vol.y[3],Vol.y[4]],\
             [Vol.x[4],Vol.x[11]],[Vol.y[4],Vol.y[11]]]
    CH21n = [numpy.mean([Vol.x[0],Vol.x[1],Vol.x[2],Vol.x[3],Vol.x[4],Vol.x[11]]),\
             numpy.mean([Vol.y[0],Vol.y[1],Vol.y[2],Vol.y[3],Vol.y[4],Vol.y[11]])]
    #南船#
    C_H22 = [[Car.x[1],Car.x[6]],[Car.y[1],Car.y[6]],[Car.x[4],Car.x[6]],[Car.y[4],Car.y[6]],\
             [Car.x[4],Car.x[7]],[Car.y[4],Car.y[7]],[Car.x[7],Car.x[8]],[Car.y[7],Car.y[8]]]
    CH22n = [numpy.mean([Car.x[1],Car.x[4],Car.x[6],Car.x[7],Car.x[8]]),\
             numpy.mean([Car.y[1],Car.y[4],Car.y[6],Car.y[7],Car.y[8]])]
    #小斗#
    C_H23 = [[Cha.x[1],Cha.x[4]],[Cha.y[1],Cha.y[4]],[Cha.x[1],Cha.x[5]],[Cha.y[1],Cha.y[5]],\
             [Cha.x[2],Cha.x[5]],[Cha.y[2],Cha.y[5]],[Cha.x[3],Cha.x[8]],[Cha.y[3],Cha.y[8]],\
             [Cha.x[4],Cha.x[7]],[Cha.y[4],Cha.y[7]],[Cha.x[7],Cha.x[8]],[Cha.y[7],Cha.y[8]]]
    CH23n = [numpy.mean([Cha.x[1],Cha.x[2],Cha.x[3],Cha.x[4],Cha.x[5],Cha.x[7],Cha.x[8]]),\
             numpy.mean([Cha.y[1],Cha.y[2],Cha.y[3],Cha.y[4],Cha.y[5],Cha.y[7],Cha.y[8]])]

    C_H_list = [C_H01,C_H02,C_H03,C_H04,C_H05,C_H06,C_H07,C_H08,C_H09,C_H10,\
                C_H11,C_H12,C_H13,C_H14,C_H15,C_H16,C_H17,C_H18,C_H19,C_H20,\
                C_H21,C_H22,C_H23]

    # 南極星區 linecollection
    C_H_line_xy1 = []
    C_H_line_xy2 = []        
    for i in range(len(C_H_list)):
        for j in range(len(C_H_list[i]))[0::2]:
            if math.hypot(C_H_list[i][j][0]-C_H_list[i][j][1],C_H_list[i][j+1][0]-C_H_list[i][j+1][1]) < hori_border:
                C_H_line_xy1.append((C_H_list[i][j][0],C_H_list[i][j+1][0]))
                C_H_line_xy2.append((C_H_list[i][j][1],C_H_list[i][j+1][1]))

    C_H_line_list = []
    for i in range(len(C_H_line_xy1)):            
        C_H_line_list.append([C_H_line_xy1[i],C_H_line_xy2[i]])
    
    lc_C_H = mc.LineCollection(C_H_line_list, colors='white', zorder=2+2.5)
    lc_C_H.set_alpha(plot_alpha)
    lc_C_H.set_clip_path(twlight_line)
    ax0.add_collection(lc_C_H)

    CHn_list = [[CH01n,'海山'],[CH02n,'十字架'],[CH03n,'馬尾'],[CH04n,'馬腹'],[CH05n,'蜜蜂'],\
                [CH06n,'三角形'],[CH07n,'異雀'],[CH08n,'孔雀'],[CH09n,'波斯'],[CH10n,'蛇尾'],\
                [CH11n,'蛇腹'],[CH12n,'蛇首'],[CH13n,'鳥喙'],[CH14n,'鶴'],[CH15n,'火鳥'],\
                [CH16n,'水委'],[CH17n,'附白'],[CH18n,'夾白'],[CH19n,'金魚'],[CH20n,'海石'],\
                [CH21n,'飛魚'],[CH22n,'南船'],[CH23n,'小斗']]

##    for i in range(len(CHn_list)):
##        if len(CHn_list[i][0]) != 0:
##            if (CHn_list[i][0][0])**2 < (hori_border/2)**2-(CHn_list[i][0][1])**2 \
##               and max(CHn_list[i][0])-min(CHn_list[i][0]) < hori_border:
##                ax0.annotate(str(CHn_list[i][1]),(CHn_list[i][0][0],CHn_list[i][0][1]),color='w',\
##                                  fontproperties=chara_chi,horizontalalignment='center',verticalalignment='top')

    if debug_mode == 1:
        timelog('ref count constellation_list: '+str(sys.getrefcount(constellation_list)))
        timelog('ref count labelxy: '+str(sys.getrefcount(labelxy)))
        timelog('ref count And_line: '+str(sys.getrefcount(And_line)))
        timelog('ref count constellation_line: '+str(sys.getrefcount(constellation_line)))
        timelog('ref count constellation_line_z_xy1: '+str(sys.getrefcount(constellation_line_z_xy1)))
        timelog('ref count constellation_line_z_xy2: '+str(sys.getrefcount(constellation_line_z_xy2)))
        timelog('ref count constellation_line_xy1: '+str(sys.getrefcount(constellation_line_xy1)))
        timelog('ref count constellation_line_xy2: '+str(sys.getrefcount(constellation_line_xy2)))
        timelog('ref count constellation_line_z_list: '+str(sys.getrefcount(constellation_line_z_list)))
        timelog('ref count constellation_line_list: '+str(sys.getrefcount(constellation_line_list)))
        timelog('ref count lc_west_z: '+str(sys.getrefcount(lc_west_z)))
        timelog('ref count lc_west: '+str(sys.getrefcount(lc_west)))
        timelog('ref count constellation_dotted_line: '+str(sys.getrefcount(constellation_dotted_line)))
        timelog('ref count constellation_dotted_line_list: '+str(sys.getrefcount(constellation_dotted_line_list)))
        timelog('ref count lc_west_dotted: '+str(sys.getrefcount(lc_west_dotted)))
        
def plot_MW():
    timelog('weaving Milkyway')
    
    MW_list = [MW_southernedge,MW_MonPer,MW_CamCas,MW_Cep,MW_CygOph,MW_OphSco,MW_LupVel,MW_VelMon,\
               dark_PerCas,dark_CasCep,dark_betaCas,dark_CygCep,dark_CygOph,dark_thetaOph,dark_lambdaSco,dark_ScoNor,dark_Coalsack,dark_Vel,\
               MW_LMC1,MW_LMC2,MW_SMC]

    MW_line_list = []
    for df in MW_list:
        df.x = list(map(transform_x, df.RA, df.Dec))
        df.y = list(map(transform_y, df.RA, df.Dec))
        for i in range(len(df)-1):
            if (df.x[i])**2 < (hori_border/2)**2-(df.y[i])**2:
                MW_line_list.append([(df.x[i],df.y[i]),(df.x[i+1],df.y[i+1])])

    lc_MW = mc.LineCollection(MW_line_list, colors='c',alpha=plot_alpha, zorder=1+2.5)
    ax0.add_collection(lc_MW)

    if debug_mode == 1:
        timelog('ref count MW_list: '+str(sys.getrefcount(MW_list)))
        timelog('ref count MW_line_list: '+str(sys.getrefcount(MW_line_list)))
        timelog('ref count lc_MW: '+str(sys.getrefcount(lc_MW)))

def plot_boundary():
    timelog('drawing boundaries')
    
    boundary.x = list(map(transform_x, boundary.RA*15, boundary.Dec)) #convert RA to degrees
    boundary.y = list(map(transform_y, boundary.RA*15, boundary.Dec))
    
    boundary_line_list = []
    for i in range(len(boundary)-1):
        if boundary.Constellation[i] == boundary.Constellation[i+1]:
            boundary_line_list.append([(boundary.x[i],boundary.y[i]),(boundary.x[i+1],boundary.y[i+1])])

    lc_boundary = mc.LineCollection(boundary_line_list, colors=[1,0.5,0,0.15],alpha=plot_alpha/3, zorder=1+2.5)
    lc_boundary.set_clip_path(horizon_line)
    ax0.add_collection(lc_boundary)

    if debug_mode == 1:
        timelog('ref count boundary.x: '+str(sys.getrefcount(boundary.x)))
        timelog('ref count boundary.y: '+str(sys.getrefcount(boundary.y)))
        timelog('ref count boundary_line_list: '+str(sys.getrefcount(boundary_line_list)))
        timelog('ref count lc_boundary: '+str(sys.getrefcount(lc_boundary)))
 
def write_label(x,y,z,c1,c2,c3): # (x,y) are text offset, z is zorder, (c1,c2,c3) are text colors
    if (x,y,z) == (0,0,0):
        timelog('timestamp')
    #print('label:'+str(date_local))
    ax0.annotate(Obs[4]+'\n'+Obs[6],(hori_xmin+x,hori_ymax+y),ha='left',va='top',color=c1,zorder=12+2.5+z)
    ax0.annotate(Obs[3]+'\n'+Obs[5],(hori_xmin+x+60,hori_ymax+y),ha='right',va='top',color=c1,zorder=12+2.5+z)
    ax0.annotate('Ho Koon Nature Education cum\nAstronomical Centre',(hori_xmax+x,hori_ymax+y),ha='right',va='top',color=c1,zorder=12+2.5+z)
    ax0.annotate('HKT\n\n',(hori_xmax+x,hori_ymin+y),ha='right',color=c1,zorder=12+2.5+z)
    ax0.annotate(str(date_local.strftime('%H:%M:%S\n')),(hori_xmax+x,hori_ymin+y),ha='right',color=c1,zorder=12+2.5+z)
    ax0.annotate(str(date_local.strftime('%d/%m/%Y')),(hori_xmax+x,hori_ymin+y),ha='right',color=c1,zorder=12+2.5+z)
    ax0.annotate('ephemeris by Skyfield',(360+x,hori_ymin+y),rotation=90,ha='right',va='bottom',color=c2,zorder=12+2.5+z)

    txt_offset = 7
    mark_offset = 5
    ax0.annotate('N',(0+x,hori_ymax+y+txt_offset),ha='center',va='bottom',color=c1,zorder=12+2.5+z)
    ax0.plot([0,0],[hori_ymax+mark_offset,hori_ymax],color='green',zorder=12+2.5+z)
    ax0.annotate('S',(0+x,hori_ymin+y-txt_offset),ha='center',va='top',color=c1,zorder=12+2.5+z)
    ax0.plot([0,0],[hori_ymin-mark_offset,hori_ymin],color='green',zorder=12+2.5+z)
    ax0.annotate('E',(hori_xmin+x-txt_offset,0+y),ha='right',va='center',color=c1,zorder=12+2.5+z)
    ax0.plot([hori_xmin-mark_offset,hori_xmin],[0,0],color='green',zorder=12+2.5+z)
    ax0.annotate('W',(hori_xmax+x+txt_offset,0+y),ha='left',va='center',color=c1,zorder=12+2.5+z)
    ax0.plot([hori_xmax+mark_offset,hori_xmax],[0,0],color='green',zorder=12+2.5+z)
    
def write_weather():
    Tw0 = time.time()
    
    timelog('weather report')
    
    socket.setdefaulttimeout(5)

    # BesutifulSoup, for sunspot
    try:
        link_ss = 'http://sidc.oma.be/silso/home'
        html_ss = requests.get(link_ss).text
        soup_ss = BeautifulSoup(html_ss, 'html.parser')
        SW_ss = soup_ss.find_all('table')[1].get_text().split()[-1]
    except:
        print('silso fail')
        try:
            link_ss = 'http://spaceweather.com/'
            html_ss = requests.get(link_ss).text
            soup_ss = BeautifulSoup(html_ss, 'html.parser')
            SW_ss = soup_ss.find_all(class_='solarWindText')[4].get_text().split()[2]
        except:
            print('spaceweather fail')
        pass
    
    #sunspot
    try:
        ax5.annotate('Sunspot no.',(1320,49),ha='center',va='center',fontproperties=DjV_S_10,color='darkgrey')
        ax5.annotate(SW_ss,(1320,19),ha='center',va='center',fontproperties=DjV_S_10,color='w')
    except:
        print('no sun la')
        pass
    
def update_para():
    global transform_x, transform_y, ra0, dec0, plot_scale, sidereal_time
    #print('transform:'+str(date_UTC))
    sidereal_time = date_UTC.gmst+Obs[2]/15
    ra0 = 15*sidereal_time
    dec0 = Obs[1]

    # projection formula (Lambert Azimuthal Equal-Area)
    transform_x = lambda x,y: plot_scale\
                   *(-math.cos(math.radians(y))*math.sin(math.radians(x-ra0)))\
                   *math.sqrt(2/(1+math.sin(math.radians(dec0))*math.sin(math.radians(y))+math.cos(math.radians(dec0))*math.cos(math.radians(y))*math.cos(math.radians(x-ra0))))
    transform_y = lambda x,y: plot_scale\
                   *(math.cos(math.radians(dec0))*math.sin(math.radians(y))-math.sin(math.radians(dec0))*math.cos(math.radians(y))*math.cos(math.radians(x-ra0)))\
                   *math.sqrt(2/(1+math.sin(math.radians(dec0))*math.sin(math.radians(y))+math.cos(math.radians(dec0))*math.cos(math.radians(y))*math.cos(math.radians(x-ra0))))

    if debug_mode == 1:
        timelog('ref count ra0: '+str(sys.getrefcount(ra0)))
        timelog('ref count dec0: '+str(sys.getrefcount(dec0)))
        timelog('ref count transform_x: '+str(sys.getrefcount(transform_x)))
        timelog('ref count transform_y: '+str(sys.getrefcount(transform_y)))

def plot_ASC():
    # show image
    #ax0.imshow(asc, extent=[-360, 360, -240, 240])
    ax0.set_xlim((-300,300))
    ax0.set_ylim((-300,300))
    ax0.axis('off')
    ax0.add_patch(patches.Rectangle((-300,-300),600,600,fc='none',ec=(1,1,0,0.75),lw=2))
    
    plot_solar()
    plot_constellation()
    plot_MW()
    plot_boundary()
    write_label(0,0,0,'w','dimgrey','y')
    write_weather()

def side_panel():   
    moon_phase()
    jovian_moons()
    mercury_venus()
    ephemeris()
    
def moon_phase(): #ax1
    Tmp0 = time.time()
    global ax1_moon

    timelog('drawing Moon')
    
    ax1.set_xlim((-90,90))
    ax1.set_ylim((-90,90))
    ax1.axis('off')
    ax1.add_patch(patches.Rectangle((-90,-90),180,180,fc='none',ec=(1,1,0,0.75),lw=2))
    
    # Moon phase
    ax1.annotate('Moon Phase',(0,85),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')

    moon_size = math.degrees(3474.2/moon_vector.radec()[2].km)*3600

    M_d  = moon_size/2100*110
    ph_r = 50*moon_size/2100 # line inner radius
    ph_R = 60*moon_size/2100 # line outer radius
    ph_l = 68*moon_size/2100 # text radius
    
    # illuminated percentage
    Moon_percent = almanac.fraction_illuminated(ephem, 'moon', date_UTC)
    
    # rotate for position angle of the Moon's bright limb
    rot_pa_limb_moon = moon_chi-90

    # rotation angle from zenith to equatorial north clockwise
    Moon_parallactic_angle = math.atan2(math.sin(math.radians(sidereal_time*15)-moon_vector.radec()[0].radians),
                                        math.tan(Obs[1])*math.cos(moon_vector.radec()[1].radians)-math.sin(moon_vector.radec()[1].radians)*math.cos(math.radians(sidereal_time*15)-moon_vector.radec()[0].radians))

    ##brightLimbAngle = (moon_chi - math.degrees(Moon_parallactic_angle))%360
    
    moondisc0 = patches.Circle((0,0), M_d/2, color='#F0F0F0')
    if Moon_percent == 0:
        moondisc1 = patches.Circle((0,0), M_d/2, color='#94908D')
        moondisc2 = patches.Wedge((0,0), 0, 0, 0, color='#94908D') #dummy
        moondisc3 = patches.Ellipse((0,0), 0, 0, 0, color='#94908D') #dummy
    elif 0 < Moon_percent < 0.5:
        moondisc1 = patches.Circle((0,0), M_d/2, color='#F0F0F0')
        moondisc2 = patches.Wedge((0,0), M_d/2, 270+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), 90+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), color='#94908D')
        moondisc3 = patches.Ellipse((0,0), M_d*(1-Moon_percent/0.5), M_d, angle=rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), color='#94908D')
    elif Moon_percent == 0.5:
        moondisc1 = patches.Circle((0,0), M_d/2, color='#94908D')
        moondisc2 = patches.Wedge((0,0), M_d/2, 90+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), 270+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), color='#F0F0F0')
        moondisc3 = patches.Ellipse((0,0), 0, 0, 0, color='#F0F0F0') #dummy
    elif 0.5 < Moon_percent < 1:
        moondisc1 = patches.Circle((0,0), M_d/2, color='#94908D')
        moondisc2 = patches.Wedge((0,0), M_d/2, 90+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), 270+rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), color='#F0F0F0')
        moondisc3 = patches.Ellipse((0,0), M_d*(1-Moon_percent/0.5), M_d, angle=rot_pa_limb_moon-math.degrees(Moon_parallactic_angle), color='#F0F0F0')
    elif Moon_percent == 1:
        moondisc1 = patches.Circle((0,0), M_d/2, color='#F0F0F0')
        moondisc2 = patches.Wedge((0,0), 0, 0, 0,color='#F0F0F0') #dummy
        moondisc3 = patches.Ellipse((0,0), 0, 0, 0, color='#F0F0F0') #dummy
    
    ax1.add_patch(moondisc0)
    ax1.add_patch(moondisc1)
    ax1.add_patch(moondisc2)
    ax1.add_patch(moondisc3)
    
    #libration
    Mlat, Mlon, distance = (earth - moon).at(date_UTC).frame_latlon(frame)

    T               = (date_UTC.tdb-2451545)/36525 # should use Julian Emphemeris Date instead
    asc_node        = 125.04452-1934.136261*T\
                      +0.0020708*T*T\
                      +T*T*T/450000 # longitude of ascending node of Moon mean orbit
    L_s             = 280.4665+36000.7698*T # mean longitude of Sun
    L_m             = 218.3165+481267.8813*T # mean longitude of Moon
    nu_lon          = -17.2/3600*math.sin(math.radians(asc_node))\
                      -1.32/3600*math.sin(math.radians(2*L_s))\
                      -0.23/3600*math.sin(math.radians(2*L_m))\
                      +0.21/3600*math.sin(math.radians(2*asc_node)) # nutation in longitude
    Inc             = 1.54242 # inclination of mean lunar equator to ecliptic
    M_s             = 357.5291092\
                      +35999.0502909*T\
                      -0.0001536*T*T\
                      +T*T*T/24490000 # Sun mean anomaly
    M_m             = 134.9634114\
                      +477198.8676313*T\
                      +0.008997*T*T\
                      +T*T*T/69699\
                      -T*T*T*T/14712000 # Moon mean anomaly
    D_m             = 297.8502042\
                      +445267.1115168*T\
                      -0.00163*T*T\
                      +T*T*T/545868\
                      -T*T*T*T/113065000 # mean elongation of Moon
    F_m             = 93.2720993\
                      +483202.0175273*T\
                      -0.0034029*T*T\
                      -T*T*T/3526000\
                      +T*T*T*T/863310000 # Moon argument of latitude
    rho             = -0.02752*math.cos(math.radians(M_m))\
                      -0.02245*math.sin(math.radians(F_m))\
                      +0.00684*math.cos(math.radians(M_m-2*F_m))\
                      -0.00293*math.cos(math.radians(2*F_m))\
                      -0.00085*math.cos(math.radians(2*F_m-2*D_m))\
                      -0.00054*math.cos(math.radians(M_m-2*D_m))\
                      -0.0002*math.sin(math.radians(M_m+F_m))\
                      -0.0002*math.cos(math.radians(M_m+2*F_m))\
                      -0.0002*math.cos(math.radians(M_m-F_m))\
                      +0.00014*math.cos(math.radians(M_m+2*F_m-2*D_m))
    sigma           = -0.02816*math.sin(math.radians(M_m))\
                      +0.02244*math.cos(math.radians(F_m))\
                      -0.00682*math.sin(math.radians(M_m-2*F_m))\
                      -0.00279*math.sin(math.radians(2*F_m))\
                      -0.00083*math.sin(math.radians(2*F_m-2*D_m))\
                      +0.00069*math.sin(math.radians(M_m-2*D_m))\
                      +0.0004*math.cos(math.radians(M_m+F_m))\
                      -0.00025*math.sin(math.radians(2*M_m))\
                      -0.00023*math.sin(math.radians(M_m+2*F_m))\
                      +0.0002*math.cos(math.radians(M_m-F_m))\
                      +0.00019*math.sin(math.radians(M_m-F_m))\
                      +0.00013*math.sin(math.radians(M_m+2*F_m-2*D_m))\
                      -0.0001*math.cos(math.radians(M_m-3*F_m))
    V_m             = asc_node + nu_lon + sigma/math.sin(math.radians(Inc))
    epsilion        = 23.4355636928 #(IAU 2000B nutation series)
    X_m             = math.sin(math.radians(Inc)+rho)*math.sin(math.radians(V_m))
    Y_m             = math.sin(math.radians(Inc)+rho)*math.cos(math.radians(V_m))*math.cos(math.radians(epsilion))\
                      -math.cos(math.radians(Inc)+rho)*math.sin(math.radians(epsilion))
    omega           = math.atan2(X_m,Y_m)

    PA_axis_moon_N  = math.asin(math.sqrt(X_m*X_m+Y_m*Y_m)*math.cos(moon_vector.radec()[0].radians-omega)/math.cos(Mlon.radians))
            
    PA_axis_moon_z  = Moon_parallactic_angle-PA_axis_moon_N # clockwise, radians
    
    moon_rot = -math.degrees(PA_axis_moon_z) # anti-clockwise
    
    # Mare in Orthographic projection with rotation shown on ax1_moon
    lon0 = Mlon.degrees
    lat0 = Mlat.degrees
    
    if count != 1:
        ax1_moon.remove()
        
    fig0 = plt.figure(0)
    ax_moon_img = plt.axes(projection=ccrs.Orthographic(central_longitude=lon0,central_latitude=lat0))
    ax_moon_img.set_facecolor('none')
    ax_moon_img.axis('off')
    ax_moon_img.imshow(plt.imread('moonmap.png'), extent=(-180,180,-90,90), transform=ccrs.PlateCarree())
    #ax_moon_img.gridlines(crs=ccrs.PlateCarree(), color='c')
    #ax_moon_img.set_global()
    #ax_moon_img.background_patch.set_fill(False)
    #ax_moon_img.outline_patch.set_alpha(0)
    fig0.tight_layout(pad=0)
    fig0.savefig('moon_proj.png', bbox_inches='tight', transparent=True)
    plt.close(fig0)
    
#     src = cv2.imread('moon_proj.png',1)
#     tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
#     _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
#     b,g,r = cv2.split(src)
#     rgba = [b,g,r,alpha]
#     dst = cv2.merge(rgba,4)
#     cv2.imwrite('moon_proj_proj.png',dst)
    
    ax1_moon = fig.add_axes([ax1.get_position().x0,ax1.get_position().y0,
                              ax1.get_position().width,ax1.get_position().height], projection=ccrs.Orthographic(central_longitude=lon0,central_latitude=lat0))
    ax1_moon.set_facecolor('none')
    ax1_moon.set_xlim((-90,90))
    ax1_moon.set_ylim((-90,90))
    ax1_moon.axis('off')
    
#     rgba = numpy.array(Image.open(pathlib.Path.cwd().joinpath('moon_proj.png')))
#     rgba[rgba[255,255,255,...]==1] = [0,0,0,0]
#     #print(rgba[rgba[255,255,255,...]==1])
#     print(rgba)
#     Image.fromarray(rgba).save('moon_proj_proj.png')

    moon_proj = Image.open(pathlib.Path.cwd().joinpath('moon_proj.png')).rotate(moon_rot)
    mscale = 1.045
    ax1_moon.imshow(moon_proj, extent=[-M_d/2*mscale,M_d/2*mscale,-M_d/2*mscale,M_d/2*mscale])

    # eq. coord.
    if moon_vector.altaz()[0].degrees > 0:
        ax1.annotate('N',(ph_l*math.sin(Moon_parallactic_angle),ph_l*math.cos(Moon_parallactic_angle)),\
                     xycoords=('data'),rotation=-math.degrees(Moon_parallactic_angle),ha='center',va='center',color='red')
        ax1.plot([ph_r*math.sin(Moon_parallactic_angle),ph_R*math.sin(Moon_parallactic_angle)],\
                 [ph_r*math.cos(Moon_parallactic_angle),ph_R*math.cos(Moon_parallactic_angle)],color='red',zorder=10)
        
        ax1.annotate('E',(ph_l*math.sin(Moon_parallactic_angle+3*math.pi/2),ph_l*math.cos(Moon_parallactic_angle+3*math.pi/2)),\
                     xycoords=('data'),rotation=-math.degrees(Moon_parallactic_angle),ha='center',va='center',color='red')
        ax1.plot([ph_r*math.sin(Moon_parallactic_angle+3*math.pi/2),ph_R*math.sin(Moon_parallactic_angle+3*math.pi/2)],\
                 [ph_r*math.cos(Moon_parallactic_angle+3*math.pi/2),ph_R*math.cos(Moon_parallactic_angle+3*math.pi/2)],color='red',zorder=10)
        
        ax1.annotate('S',(ph_l*math.sin(Moon_parallactic_angle+math.pi),ph_l*math.cos(Moon_parallactic_angle+math.pi)),\
                     xycoords=('data'),rotation=-math.degrees(Moon_parallactic_angle),ha='center',va='center',color='red')
        ax1.plot([ph_r*math.sin(Moon_parallactic_angle+math.pi),ph_R*math.sin(Moon_parallactic_angle+math.pi)],\
                 [ph_r*math.cos(Moon_parallactic_angle+math.pi),ph_R*math.cos(Moon_parallactic_angle+math.pi)],color='red',zorder=10)
        
        ax1.annotate('W',(ph_l*math.sin(Moon_parallactic_angle+math.pi/2),ph_l*math.cos(Moon_parallactic_angle+math.pi/2)),\
                     xycoords=('data'),rotation=-math.degrees(Moon_parallactic_angle),ha='center',va='center',color='red')
        ax1.plot([ph_r*math.sin(Moon_parallactic_angle+math.pi/2),ph_R*math.sin(Moon_parallactic_angle+math.pi/2)],\
                 [ph_r*math.cos(Moon_parallactic_angle+math.pi/2),ph_R*math.cos(Moon_parallactic_angle+math.pi/2)],color='red',zorder=10)

    ax1.annotate('equatorial\ncoordinate',(-88,-70),xycoords=('data'),ha='left',va='bottom',fontproperties=DjV_S_9,color='red')

    # selenographic
    ax1.annotate('selenographic\ncoordinate',(88,-70),xycoords=('data'),ha='right',va='bottom',fontproperties=DjV_S_9,color='cyan')

    ax1.annotate('N',(ph_l*math.sin(PA_axis_moon_z),ph_l*math.cos(PA_axis_moon_z)),\
                 xycoords=('data'),rotation=-math.degrees(PA_axis_moon_z),ha='center',va='center',color='cyan')
    ax1.plot([ph_r*math.sin(PA_axis_moon_z),ph_R*math.sin(PA_axis_moon_z)],\
             [ph_r*math.cos(PA_axis_moon_z),ph_R*math.cos(PA_axis_moon_z)],color='cyan',zorder=10)
    
    ax1.annotate('E',(ph_l*math.sin(PA_axis_moon_z+math.pi/2),ph_l*math.cos(PA_axis_moon_z+math.pi/2)),\
                 xycoords=('data'),rotation=-math.degrees(PA_axis_moon_z),ha='center',va='center',color='cyan')
    ax1.plot([ph_r*math.sin(PA_axis_moon_z+math.pi/2),ph_R*math.sin(PA_axis_moon_z+math.pi/2)],\
             [ph_r*math.cos(PA_axis_moon_z+math.pi/2),ph_R*math.cos(PA_axis_moon_z+math.pi/2)],color='cyan',zorder=10)
    
    ax1.annotate('S',(ph_l*math.sin(PA_axis_moon_z+math.pi),ph_l*math.cos(PA_axis_moon_z+math.pi)),\
                 xycoords=('data'),rotation=-math.degrees(PA_axis_moon_z),ha='center',va='center',color='cyan')
    ax1.plot([ph_r*math.sin(PA_axis_moon_z+math.pi),ph_R*math.sin(PA_axis_moon_z+math.pi)],\
             [ph_r*math.cos(PA_axis_moon_z+math.pi),ph_R*math.cos(PA_axis_moon_z+math.pi)],color='cyan',zorder=10)
    
    ax1.annotate('W',(ph_l*math.sin(PA_axis_moon_z+3*math.pi/2),ph_l*math.cos(PA_axis_moon_z+3*math.pi/2)),\
                 xycoords=('data'),rotation=-math.degrees(PA_axis_moon_z),ha='center',va='center',color='cyan')
    ax1.plot([ph_r*math.sin(PA_axis_moon_z+3*math.pi/2),ph_R*math.sin(PA_axis_moon_z+3*math.pi/2)],\
             [ph_r*math.cos(PA_axis_moon_z+3*math.pi/2),ph_R*math.cos(PA_axis_moon_z+3*math.pi/2)],color='cyan',zorder=10)
    
    # zenith
    if moon_vector.altaz()[0].degrees > 0:
        ax1.arrow(0,M_d/2,0,10,color='green',head_width=5, head_length=5)
        ax1.annotate('dia = '+str(round(moon_size/60,1))+"'\nele = "+str(round(moon_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',
                     (88,70),xycoords=('data'),ha='right',va='top',fontproperties=DjV_S_12,color='orange')
    else:
        ax1.annotate('below horizon',(88,70),xycoords=('data'),ha='right',va='top',fontproperties=DjV_S_12,color='orange')
    ax1.annotate('zenith',(0,68),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_12,color='green')
    
    phase_moon = 'illuminated '+str(round(Moon_percent*100,2))+'%' # projected 2D apparent area
    if Moon_percent >= 0:
        ax1.annotate(phase_moon,(0,-85),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_10,color='#F0F0F0')
    else:
        ax1.annotate(phase_moon,(0,-85),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_10,color='#94908D')

    Tmp1 = time.time()
    #print(Tmp1-Tmp0)

def jovian_moons(): #ax2
    Tj0 = time.time()

    timelog('drawing Jupiter')

    ax2.set_xlim((-90,90))
    ax2.set_ylim((-45,45))
    ax2.axis('off')
    ax2.add_patch(patches.Rectangle((-90,-45),180,90,fc='none',ec=(1,1,0,0.75),lw=2))

    ax2.annotate('Jovian Moons',(0,40),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')

    ra_J, dec_J, dis_J = Obs[0].at(date_UTC).observe(jupiterJ).apparent().radec()

    ra_io, dec_io, dis_io = Obs[0].at(date_UTC).observe(io).apparent().radec()
    ra_eu, dec_eu, dis_eu = Obs[0].at(date_UTC).observe(europa).apparent().radec()
    ra_ga, dec_ga, dis_ga = Obs[0].at(date_UTC).observe(ganymede).apparent().radec()
    ra_ca, dec_ca, dis_ca = Obs[0].at(date_UTC).observe(callisto).apparent().radec()
    
    Io_x        = (ra_io.radians - ra_J.radians)*math.cos(dec_J.radians)*dis_J.km/71492
    Io_y        = (dec_io.radians - dec_J.radians)*dis_J.km/71492
    Europa_x    = (ra_eu.radians - ra_J.radians)*math.cos(dec_J.radians)*dis_J.km/71492
    Europa_y    = (dec_eu.radians - dec_J.radians)*dis_J.km/71492
    Ganymede_x  = (ra_ga.radians - ra_J.radians)*math.cos(dec_J.radians)*dis_J.km/71492
    Ganymede_y  = (dec_ga.radians - dec_J.radians)*dis_J.km/71492
    Callisto_x  = (ra_ca.radians - ra_J.radians)*math.cos(dec_J.radians)*dis_J.km/71492
    Callisto_y  = (dec_ca.radians - dec_J.radians)*dis_J.km/71492
        
    Io_radius = 1821.6/71492
    Europa_radius = 1560.8/71492
    Ganymede_radius = 2410.3/71492
    Callisto_radius = 2634.1/71492
    jov_radius = 88/(1+max(abs(Io_x-Io_radius),abs(Io_x+Io_radius),
                           abs(Europa_x-Europa_radius),abs(Europa_x+Europa_radius),
                           abs(Ganymede_x-Ganymede_radius),abs(Ganymede_x+Ganymede_radius),
                           abs(Callisto_x-Callisto_radius),abs(Callisto_x+Callisto_radius)))
    
    Io_r = 5*Io_radius*jov_radius
    Eu_r = 5*Europa_radius*jov_radius
    Ga_r = 5*Ganymede_radius*jov_radius
    Ca_r = 5*Callisto_radius*jov_radius
    
    Jupdisc = patches.Circle((0,0), jov_radius, color='#C88B3A', zorder=-dis_J.km)
    Iodisc = patches.Circle((-Io_x*jov_radius,Io_y*jov_radius), Io_r, color='#9f9538', zorder=-dis_io.km)
    Europadisc = patches.Circle((-Europa_x*jov_radius,Europa_y*jov_radius), Eu_r, color='#6c5d40', zorder=-dis_eu.km)
    Ganymededisc = patches.Circle((-Ganymede_x*jov_radius,Ganymede_y*jov_radius), Ga_r, color='#544a45', zorder=-dis_ga.km)
    Callistodisc = patches.Circle((-Callisto_x*jov_radius,Callisto_y*jov_radius), Ca_r, color='#766b5d', zorder=-dis_ca.km)
    
    ax2.annotate('I',(-Io_x*jov_radius,-30),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_12,color='#9f9538')
    ax2.annotate('E',(-Europa_x*jov_radius,-30),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_12,color='#6c5d40')
    ax2.annotate('G',(-Ganymede_x*jov_radius,-30),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_12,color='#544a45')
    ax2.annotate('C',(-Callisto_x*jov_radius,-30),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_12,color='#766b5d')
    
    ax2.add_patch(Jupdisc)
    ax2.add_patch(Iodisc)
    ax2.add_patch(Europadisc)
    ax2.add_patch(Ganymededisc)
    ax2.add_patch(Callistodisc)
    
    ax2.annotate('\u2190 E',(-88,-40),xycoords=('data'),ha='left',va='bottom',fontproperties=DjV_S_10,color='red')
    ax2.annotate('W \u2192',(88,-40),xycoords=('data'),ha='right',va='bottom',fontproperties=DjV_S_10,color='red')
    
    #FOV 5 arcmin
    for i in range(5):
        ax2.add_patch(patches.Circle((0,0),i*5*math.pi/180/60/2*dis_J.km/71492*jov_radius,
                                     fc='none',ec=(1,0,0,0.35),ls='--',zorder=-dis_J.km*2))
        ax2.annotate(str(5*i)+"'",(i*5*math.pi/180/60/2*dis_J.km/71492*jov_radius*math.cos(math.radians(25)),
                                   i*5*math.pi/180/60/2*dis_J.km/71492*jov_radius*math.sin(math.radians(25))),
                     rotation=-65,ha='center',va='center',color=(1,0,0,0.75), backgroundcolor= 'black', zorder=-dis_J.km*2+1)

    Tj1 = time.time()
    #print(Tj1-Tj0)

def mercury_venus(): #ax3
    Tmv0 = time.time()

    timelog('drawing Mercury and Venus')
    
    ax3.set_xlim((-90,90))
    ax3.set_ylim((-45,45))
    ax3.axis('off')
    ax3.add_patch(patches.Rectangle((-90,-45),180,90,fc='none',ec=(1,1,0,0.75),lw=2))

    mercury_chi = math.degrees(math.atan2(math.cos(sun_vector.radec()[1].radians)*math.sin(sun_vector.radec()[0].radians-mercury_vector.radec()[0].radians),
                                          math.sin(sun_vector.radec()[1].radians)*math.cos(mercury_vector.radec()[1].radians)
                                          -math.cos(sun_vector.radec()[1].radians)*math.sin(mercury_vector.radec()[1].radians)*math.cos(sun_vector.radec()[0].radians-mercury_vector.radec()[0].radians))) % 360

    venus_chi = math.degrees(math.atan2(math.cos(sun_vector.radec()[1].radians)*math.sin(sun_vector.radec()[0].radians-venus_vector.radec()[0].radians),
                                        math.sin(sun_vector.radec()[1].radians)*math.cos(venus_vector.radec()[1].radians)
                                        -math.cos(sun_vector.radec()[1].radians)*math.sin(venus_vector.radec()[1].radians)*math.cos(sun_vector.radec()[0].radians-venus_vector.radec()[0].radians))) % 360

    Mercury_offsetx = -45
    Venus_offsetx = 45
    MV_d = 30
    rot_pa_limb_mercury = mercury_chi-90
    rot_pa_limb_venus = venus_chi-90

    ax3.annotate('Mercury',(Mercury_offsetx,40),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')
    ax3.annotate('Venus',(Venus_offsetx,40),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')

    Mercury_precent = almanac.fraction_illuminated(ephem, 'mercury', date_UTC)
    Venus_percent = almanac.fraction_illuminated(ephem, 'venus', date_UTC)

    if Mercury_precent == 0:
        Merdisc0 = patches.Circle((Mercury_offsetx,0), MV_d/2, color='black')
        Merdisc1 = patches.Wedge((Mercury_offsetx,0), 0, 0, 0, color='black') #dummy
        Merdisc2 = patches.Ellipse((Mercury_offsetx,0), 0, 0, 0, color='black') #dummy
    elif 0 < Mercury_precent < 0.5:
        Merdisc0 = patches.Circle((Mercury_offsetx,0), MV_d/2, color='#97979F')
        Merdisc1 = patches.Wedge((Mercury_offsetx,0), MV_d/2, 270+rot_pa_limb_mercury, 90+rot_pa_limb_mercury, color='black')
        Merdisc2 = patches.Ellipse((Mercury_offsetx,0), MV_d*(1-Mercury_precent/0.5), MV_d, angle=rot_pa_limb_mercury, color='black')
    elif Mercury_precent == 0.5:
        Merdisc0 = patches.Circle((Mercury_offsetx,0), MV_d/2, color='black')
        Merdisc1 = patches.Wedge((Mercury_offsetx,0), MV_d/2, 90+rot_pa_limb_mercury, 270+rot_pa_limb_mercury, color='#97979F')
        Merdisc2 = patches.Ellipse((Mercury_offsetx,0), 0, 0, 0, color='#97979F') #dummy
    elif 0.5 < Mercury_precent < 1:
        Merdisc0 = patches.Circle((Mercury_offsetx,0), MV_d/2, color='black')
        Merdisc1 = patches.Wedge((Mercury_offsetx,0), MV_d/2, 90+rot_pa_limb_mercury, 270+rot_pa_limb_mercury, color='#97979F')
        Merdisc2 = patches.Ellipse((Mercury_offsetx,0), MV_d*(1-Mercury_precent/0.5), MV_d, angle=rot_pa_limb_mercury, color='#97979F')
    elif Mercury_precent == 1:
        Merdisc0 = patches.Circle((Mercury_offsetx,0), MV_d/2, color='#97979F')
        Merdisc1 = patches.Wedge((Mercury_offsetx,0), 0, 0, 0,color='#97979F') #dummy
        Merdisc2 = patches.Ellipse((Mercury_offsetx,0), 0, 0, 0, color='#97979F') #dummy

    ax3.add_patch(Merdisc0)
    ax3.add_patch(Merdisc1)
    ax3.add_patch(Merdisc2)

    if Venus_percent == 0:
        Vendisc0 = patches.Circle((Venus_offsetx,0), MV_d/2, color='black')
        Vendisc1 = patches.Wedge((Venus_offsetx,0), 0, 0, 0, color='black') #dummy
        Vendisc2 = patches.Ellipse((Venus_offsetx,0), 0, 0, 0, color='black') #dummy
    elif 0 < Venus_percent < 0.5:
        Vendisc0 = patches.Circle((Venus_offsetx,0), MV_d/2, color='#C18F17')
        Vendisc1 = patches.Wedge((Venus_offsetx,0), MV_d/2, 270+rot_pa_limb_venus, 90+rot_pa_limb_venus, color='black')
        Vendisc2 = patches.Ellipse((Venus_offsetx,0), MV_d*(1-Venus_percent/0.5), MV_d, angle=rot_pa_limb_venus, color='black')
    elif Venus_percent == 0.5:
        Vendisc0 = patches.Circle((Venus_offsetx,0), MV_d/2, color='black')
        Vendisc1 = patches.Wedge((Venus_offsetx,0), MV_d/2, 90+rot_pa_limb_venus, 270+rot_pa_limb_venus, color='#C18F17')
        Vendisc2 = patches.Ellipse((Venus_offsetx,0), 0, 0, 0, color='#C18F17') #dummy
    elif 0.5 < Venus_percent < 1:
        Vendisc0 = patches.Circle((Venus_offsetx,0), MV_d/2, color='black')
        Vendisc1 = patches.Wedge((Venus_offsetx,0), MV_d/2, 90+rot_pa_limb_venus, 270+rot_pa_limb_venus, color='#C18F17')
        Vendisc2 = patches.Ellipse((Venus_offsetx,0), MV_d*(1-Venus_percent/0.5), MV_d, angle=rot_pa_limb_venus, color='#C18F17')
    elif Venus_percent == 1:
        Vendisc0 = patches.Circle((Venus_offsetx,0), MV_d/2, color='#C18F17')
        Vendisc1 = patches.Wedge((Venus_offsetx,0), 0, 0, 0,color='#C18F17') #dummy
        Vendisc2 = patches.Ellipse((Venus_offsetx,0), 0, 0, 0, color='#C18F17') #dummy

    ax3.add_patch(Vendisc0)
    ax3.add_patch(Vendisc1)
    ax3.add_patch(Vendisc2)

    dist_SM = math.degrees(math.acos(math.sin(sun_vector.radec()[1].radians)*math.sin(mercury_vector.radec()[1].radians)+math.cos(sun_vector.radec()[1].radians)*math.cos(mercury_vector.radec()[1].radians)*math.cos(sun_vector.radec()[0].radians-mercury_vector.radec()[0].radians)))
    ax3.annotate(str(round(dist_SM,1))+u'\N{DEGREE SIGN}\nfrom Sun',(Mercury_offsetx,-25),xycoords=('data'),
                 ha='center',va='center',fontproperties=DjV_S_8,color='#FFCC33')
    if rot_pa_limb_mercury != 0:
        ax3.arrow((MV_d/2-2)*math.sin(math.radians(270-rot_pa_limb_mercury))+Mercury_offsetx,(MV_d/2-2)*math.cos(math.radians(270-rot_pa_limb_mercury)),\
                  (dist_SM/3+2)*math.sin(math.radians(270-rot_pa_limb_mercury)),(dist_SM/3+2)*math.cos(math.radians(270-rot_pa_limb_mercury)),
                  shape='full',length_includes_head=True,head_width=1,color='#FFCC33')
    
    dist_SV = math.degrees(math.acos(math.sin(sun_vector.radec()[1].radians)*math.sin(venus_vector.radec()[1].radians)+math.cos(sun_vector.radec()[1].radians)*math.cos(venus_vector.radec()[1].radians)*math.cos(sun_vector.radec()[0].radians-venus_vector.radec()[0].radians)))
    ax3.annotate(str(round(dist_SV,1))+u'\N{DEGREE SIGN}\nfrom Sun',(Venus_offsetx,-25),xycoords=('data'),
                 ha='center',va='center',fontproperties=DjV_S_8,color='#FFCC33')
    if rot_pa_limb_venus != 0:
        ax3.arrow((MV_d/2-2)*math.sin(math.radians(270-rot_pa_limb_venus))+Venus_offsetx,(MV_d/2-2)*math.cos(math.radians(270-rot_pa_limb_venus)),\
                  (dist_SV/3+2)*math.sin(math.radians(270-rot_pa_limb_venus)),(dist_SV/3+2)*math.cos(math.radians(270-rot_pa_limb_venus)),
                  shape='full',length_includes_head=True,head_width=1,color='#FFCC33')
    
    ax3.annotate('illuminated '+str(round(Mercury_precent*100,2))+'%',(Mercury_offsetx,-35),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_10,color='#F0F0F0')
    ax3.annotate('illuminated '+str(round(Venus_percent*100,2))+'%',(Venus_offsetx,-35),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_10,color='#F0F0F0')
    
    ax3.annotate('\u2190 E',(-88,-40),xycoords=('data'),ha='left',va='bottom',fontproperties=DjV_S_10,color='red')
    #ax3.annotate('dist. from Sun',(0,-40),xycoords=('data'),ha='center',va='bottom',fontproperties=DjV_S_8,color='#FFCC33')
    ax3.annotate('W \u2192',(88,-40),xycoords=('data'),ha='right',va='bottom',fontproperties=DjV_S_10,color='red')

    Tmv1 = time.time()
    #print(Tmv1-Tmv0)

def ephemeris(): #ax5
    Tep0 = time.time()
    
    # PyEphem, as skyfield cant compute all mag
    import ephem as PyEphem
    PyEphem.Observer().lon = str(114+6/60+29/3600)
    PyEphem.Observer().lat = str(22+23/60+1/3600)
    PyEphem.Observer().date = datetime.utcnow().replace(second=0,microsecond=0)

    timelog('Ephemeris')

    ax5.set_xlim((0,1440))
    ax5.set_ylim((0,210))
    ax5.axis('off')
    ax5.add_patch(patches.Rectangle((0,0),1440,210,fc='none',ec=(1,1,0,0.75),lw=2))
    
    ax5.annotate('Ephemeris',(720,195),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')
    
    sym_y = 171-24
    rise_y = 133-18-6
    set_y = 95-12-4
    mag_y = 57-6-2
    ele_y = 19
    ax5.annotate('next rise',(120,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='white')
    ax5.annotate('next set',(120,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='white')
    ax5.annotate('magnitude',(120,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='white')
    ax5.annotate('elevation',(120,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='white')
    
    # Moon
    moon_x = 300
    if moon_chi>180:
        ax5.annotate('\u263D\nMoon',(moon_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#DAD9D7')
    else:
        ax5.annotate('\u263E\nMoon',(moon_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#DAD9D7')

    t_moon, updown_moon = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, moon, Obs[0]-earth, radius_degrees=0.25))
    for ti, udi in list(zip(t_moon, updown_moon))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(moon_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(moon_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
    
    moon_PE = PyEphem.Moon()
    moon_PE.compute(PyEphem.Observer())  
    ax5.annotate(str(round(moon_PE.mag,1)),(moon_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(moon_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(moon_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')
    
    # Mercury
    mercury_x = 420
    ax5.annotate('\u263F\nMercury',(mercury_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#97979F')
    
    t_mercury, updown_mercury = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, mercury, Obs[0]-earth))
    for ti, udi in list(zip(t_mercury, updown_mercury))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(mercury_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(mercury_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    ax5.annotate(str(round(planetary_magnitude(mercury_vector),1)),(mercury_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(mercury_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(mercury_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')
    
    # Venus
    venus_x = 540
    ax5.annotate('\u2640\nVenus',(venus_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#C18F17')
    
    t_venus, updown_venus = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, venus, Obs[0]-earth))
    for ti, udi in list(zip(t_venus, updown_venus))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(venus_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(venus_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    ax5.annotate(str(round(planetary_magnitude(venus_vector),1)),(venus_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(venus_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(venus_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')
    
    # Mars
    mars_x = 660
    ax5.annotate('\u2642\nMars',(mars_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#E27B58')
    
    t_mars, updown_mars = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, mars, Obs[0]-earth))
    for ti, udi in list(zip(t_mars, updown_mars))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(mars_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(mars_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    mars_PE = PyEphem.Mars()
    mars_PE.compute(PyEphem.Observer())  
    ax5.annotate(str(round(mars_PE.mag,1)),(mars_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(mars_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(mars_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')

    # Jupiter
    jupiter_x = 780
    ax5.annotate('\u2643\nJupiter',(jupiter_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#C88B3A')
    
    t_jupiter, updown_jupiter = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, jupiter, Obs[0]-earth))
    for ti, udi in list(zip(t_jupiter, updown_jupiter))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(jupiter_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(jupiter_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    ax5.annotate(str(round(planetary_magnitude(jupiter_vector),1)),(jupiter_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(jupiter_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(jupiter_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')

    # Saturn
    saturn_x = 900
    ax5.annotate('\u2644\nSaturn',(saturn_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#A49B72')
    
    t_saturn, updown_saturn = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, saturn, Obs[0]-earth))
    for ti, udi in list(zip(t_saturn, updown_saturn))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(saturn_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(saturn_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    saturn_PE = PyEphem.Saturn()
    saturn_PE.compute(PyEphem.Observer())  
    ax5.annotate(str(round(saturn_PE.mag,1)),(saturn_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(saturn_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(saturn_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')

    # Uranus
    uranus_x = 1020
    ax5.annotate('\u2645\nUranus',(uranus_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#D5FBFC')
    
    t_uranus, updown_uranus = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, uranus, Obs[0]-earth))
    for ti, udi in list(zip(t_uranus, updown_uranus))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(uranus_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(uranus_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))

    ax5.annotate(str(round(planetary_magnitude(uranus_vector),1)),(uranus_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(uranus_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(uranus_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')

    # Neptune
    neptune_x = 1140
    ax5.annotate('\u2646\nNeptune',(neptune_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#3E66F9')
    
    t_neptune, updown_neptune = find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),risings_and_settings(ephem, neptune, Obs[0]-earth))
    for ti, udi in list(zip(t_neptune, updown_neptune))[:2]:
        if udi == 1:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(neptune_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
        elif udi == 0:
            ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(neptune_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
    
    neptune_PE = PyEphem.Neptune()
    neptune_PE.compute(PyEphem.Observer())  
    ax5.annotate(str(round((neptune_PE.mag),1)),(neptune_x,mag_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='yellow')
    ax5.annotate(str(round(neptune_vector.altaz()[0].degrees,1))+u'\N{DEGREE SIGN}',(neptune_x,ele_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='grey')

    ###################################################################################################################################################
    
    # astronomical twilight

    #ax5.annotate('Astronomical Twilight',(0,-75),xycoords=('data'),ha='center',va='top',fontproperties=DjV_S_12,color='white')

    sun_x = 1320
    ax5.annotate('Astronomical\nTwilight',(sun_x,sym_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color='#FFCC33')

    t_twilight, updown_twilight = almanac.find_discrete(ts.utc(ts.now().utc_datetime()),ts.utc(ts.now().utc_datetime()+timedelta(days=1.5)),
                                                        almanac.dark_twilight_day(ephem, Obs[0]-earth))

    for ti, udi in list(zip(t_twilight, updown_twilight))[:8]:
        if udi == 1:
            if ti.astimezone(tz).hour <12:
                ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(sun_x,rise_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
            else:
                ax5.annotate(str(ti.astimezone(tz).strftime('%X')),(sun_x,set_y),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_10,color=('green' if ti.astimezone(tz).date() > date_local.date() else 'orange'))
                
    ax5.annotate('orange: today',(120,155),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_8,color='orange')
    ax5.annotate('green: tomorrow',(120,135),xycoords=('data'),ha='center',va='center',fontproperties=DjV_S_8,color='green')

    Tep1 = time.time()
    #print(Tep1-Tep0)

def refresh_sky(i):
    global fig, count, date_UTC, date_local

#     #################################
#     # read record and put timestamp #
#     #################################       
#     CC_hokoon = pandas.read_csv(pathlib.Path.cwd().joinpath('ASC','CC_hokoon.csv'), index_col=0)
#     #print(CC_hokoon.memory_usage(deep=True))
#     CC_hokoon = CC_hokoon.append({'HKT':str(date_local.strftime('%Y/%m/%d %H:%M:%S'))}, ignore_index=True) # can't use datetime in dict
#     CC_hokoon['HKT'] = pandas.to_datetime(CC_hokoon['HKT'],yearfirst=True) # convert to datetime object

    ###########
    # removal #
    ###########
    start = time.time()
    count = count + 1

    # clear the world
    gc.collect()
    try:
        ax0.clear()
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax5.clear()
        timelog('Armageddon')
    except:
        timelog('survivor')

    ##########
    # update #
    ##########

    # update time
    date_UTC    = ts.utc(ts.now().utc_datetime().replace(second=0,microsecond=0))
    date_local  = date_UTC.astimezone(tz)
        
    # update transformation
    update_para()

    plot_ASC()
        
    side_panel()

    # plot
    fig.canvas.draw() 
    fig.canvas.flush_events()
    #fig.savefig('Hokoon_ASIM_'+str("{:%Y_%m_%d-%H_%M_%S}".format(datetime.now()))+'.png')
    #plt.savefig('Hokoon_ASIM_'+str("{:%Y_%m_%d-%H_%M_%S}".format(datetime.now()))+'.png')
    plt.savefig('Hokoon_skymap_C.png')
    #plt.close(fig)

    ########################
    # save and trim record #
    ########################
#     CC_hokoon.drop(CC_hokoon[CC_hokoon['HKT'] <= datetime.now()-timedelta(hours=24)].index, inplace=True) # keep only last 24h data
#     CC_hokoon.reset_index(drop=True,inplace=True)
# 
#     CC_hokoon.to_csv(pathlib.Path.cwd().joinpath('ASC','CC_hokoon.csv'))

    end = time.time()
    timelog(str(round(end-start,2))+'s wasted')
    
    if count == 1:
        timelog('This is the begining of this section')
    else:
        timelog(str(count)+' snapshots in this section')
    timelog('runtime: '+str(timedelta(seconds=end-T0)).split('.')[0])
    if platform == 'linux':
        timelog(str(os.popen('vcgencmd measure_temp').readline().splitlines()[0]).replace('temp=','core_temp: '))
    timelog('memory usage:')
    print('')
    objgraph.show_growth()
    print('')

def refresh_refresh_sky(i):
    try:
        refresh_sky(i)
    except Exception as e:
        print(e)
        pass
    
    
if platform == 'win32':
    #ani = matplotlib.animation.FuncAnimation(fig, refresh_sky, repeat=False, interval=45000, save_count=0)
    ani = matplotlib.animation.FuncAnimation(fig, refresh_refresh_sky, repeat=False, interval=10000, save_count=0)
else:
    ani = matplotlib.animation.FuncAnimation(fig, refresh_refresh_sky, repeat=False, interval=44000, save_count=0)

timelog('backend is '+str(matplotlib.get_backend()))

plt.get_current_fig_manager().window.wm_geometry('-5-25')

plt.show()

#objgraph.show_most_common_types(objects=objgraph.get_leaking_objects())
#objgraph.show_refs(objgraph.get_leaking_objects()[:3], refcounts=True)
