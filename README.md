# skymap_homepage
![Screenshot](Hokoon_skymap_W.png?raw=true "Western Constellations")
![Screenshot](Hokoon_skymap_C.png?raw=true "Chinese Constellations")

## **Overview**
This project shows realtime skymap, including Western and Chinese constellations, and astronomical info for Hong Kong. The panel is updated every 30s by **matplotlib** and uploaded to specific Dropbox directory (external **rclone** setting would be required). 

Most of the astronomical calculations are done with help of [Skyfield](http://rhodesmill.org/skyfield/).

## **Features**
- realtime constellations, planets, sun and moon positions overlaid on allsky images monitoring cloud coverage over Ho Koon sky
- moonphase, with equatorial and selenographic cardinal points marked, is always shown with zenith upwards, matching the orientation when you look up in the sky
- jovian moons configuration along celestial equator
- mercury and venus phases, of which orientation is along celestial equator, and their cooresponding distance from the sun; **AVOID looking at mersury and venus when they are too close to the sun**
- rough estimation of cloud coverage, tile color indicating transparency of the no cloud area, if any
- ephemeris showing rise & set times of the celestial objects, astronomical twlight moments are also included
- 24hr-plot showing the change of air temperature and cloud coverage over past 24hrs
- temperature, relative humidity, UV intensity and weather condition from [Hong Kong Observatory](https://www.hko.gov.hk/en/index.html)
- sunspot no. from [SILSO](https://wwwbis.sidc.be/silso/home)

## **Update**
20211012 - text outline updated

