# skymap_homepage
![Screenshot](Hokoon_skymap_W.png?raw=true "Western Constellations")
![Screenshot](Hokoon_skymap_C.png?raw=true "Chinese Constellations")

## **Overview**
This project shows realtime skymap, including Western and Chinese constellations, and astronomical info for Hong Kong. The panel is updated roughly every 30s by **matplotlib** and uploaded to specific Dropbox directory (external **rclone** setting would be required). 

Most of the astronomical calculations are done with help of [Skyfield](http://rhodesmill.org/skyfield/).

## **Features**
- starmap with realtime constellations, planets, sun and moon positions
- moon symbol flips according to its relative positve with sun
- -18° horizon indicates the moment of astronomical twlight when the sun touch it
- moonphase, with equatorial cardinal points and selenographic grids marked, is always shown with libration and zenith upwards, matching the orientation when you look up in the sky
- jovian moons configuration along celestial equator with field of view indicated
- mercury and venus phases, of which orientation is along celestial equator, and their cooresponding distance from the sun; **AVOID looking at mersury and venus when they are too close to the sun**
- ephemeris showing rise & set times of the celestial objects, astronomical twlight moments are also included
- sunspot no. from [SILSO](https://wwwbis.sidc.be/silso/home)

## **Update**
20211012 - text outline updated

