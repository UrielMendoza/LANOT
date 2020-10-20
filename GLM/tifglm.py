#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset
from osgeo import gdal,osr
import sys
import os
import load_cpt
from dateutil.parser import parse
from PIL import Image
import aggdraw
from pyproj import Proj,transform
from time import strftime,strptime 

#  Define colores de rayos
group_color = (255, 253, 199, 12)
event_color = (255, 251, 138, 20)
flash_color = (255, 247, 0, 25)

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            #print x,y
        yarr.reverse()
    return ext

def varDatos(ds,variable):
    if variable == 'event':
        lat = ds.variables[variable+'_lat'][:]
        lon = ds.variables[variable+'_lon'][:]   
        event_time = ds.variables[variable+'_time_offset'][:]
        #area = ds.variables[variable+'_area'][:]
        energy = ds.variables[variable+'_energy'][:]
        #quality = ds.variables[variable+'_quality_flag'][:]
        id_var = ds.variables[variable+'_id'][:]    
        return lat,lon,event_time,energy,id_var
    else :
        lat = ds.variables[variable+'_lat'][:]
        lon = ds.variables[variable+'_lon'][:]    
        area = ds.variables[variable+'_area'][:]
        energy = ds.variables[variable+'_energy'][:]
        quality = ds.variables[variable+'_quality_flag'][:]
        id_var = ds.variables[variable+'_id'][:]    
        return lat,lon,area,energy,quality,id_var
    
def fecha(archivo):
    fechaStr = archivo[archivo.find('_s')+2:archivo.find('_e')-1]
    fechaStr = strptime(fechaStr,"%Y%j%H%M%S")
    fechaG16 = strftime("%Y-%m-%dT%H:%M:%SZ",fechaStr)
    return fechaG16

if len(sys.argv) < 3:
    print("Usanza: ", sys.argv[0], " <archivo geotiff> <archivo GLM>")
    exit(1)

patht = sys.argv[1]
pathg = sys.argv[2]

if not os.path.isfile(patht):
    print("No existe ", patht)
    exit(1)

if not os.path.isfile(pathg):
    print("No existe ", pathg)
    exit(1)

colortablesdir='/usr/local/share/lanot/colortables'

ds = gdal.Open(patht)
projection = ds.GetProjection()
srs = osr.SpatialReference()
srs.ImportFromWkt(ds.GetProjection())
projection = srs.ExportToProj4()
print(projection)
gt=ds.GetGeoTransform()
cols = ds.RasterXSize
rows = ds.RasterYSize
ext=GetExtent(gt,cols,rows)
# close dataset
ds = None

xmin = ext[0][0]
ymax = ext[0][1]
xmax = ext[2][0]
ymin = ext[2][1]
dx = xmax - xmin
dy = ymax - ymin
print(xmin, xmax, ymin, ymax)

im = Image.open(patht).convert("RGBA")
w = im.width
h = im.height
glm = Dataset(pathg, 'r')
draw = aggdraw.Draw(im)


def coord2xy(u, v):
    x = w*(u - xmin)/dx
    y = h*(ymax - v)/dy
    return x, y

def draw_dots(sx, sy):
    dots = [[-430869.538452436,3164698.2839364],
            [-34633.7028816183,3281767.96262778],
            [-788082.147792794,3154192.03072051],
            [-487903.484481569,2938063.39313643],
            [-514919.564179579,3454370.69403174],
            [-192227.501120012,3245746.52303043]]
    red = (255, 0, 0, 255)
    b = aggdraw.Brush(red)
    p = aggdraw.Pen(red)
    for d in dots:
        x, y = coord2xy(d[0], d[1])
        draw.ellipse((x - sx, y -sy, x+sx, y+sy), p, b)

print("W H ", w, h)
sx = 2
sy = 2

lat,lon,area,energy,quality,id_var = varDatos(glm,'group')
p1 = Proj(projection)
p2 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
xx,yy = transform(p2,p1,lon,lat)
b = aggdraw.Brush(group_color)
p = aggdraw.Pen(group_color)
for i in range(len(xx)):
    if xx[i] > xmin and xx[i] < xmax and yy[i] > ymin and yy[i] < ymax:
        x, y = coord2xy(xx[i], yy[i])
        draw.ellipse((x - sx, y -sy, x+sx, y+sy), p, b)

lat,lon,event_time,energy,id_var = varDatos(glm,'event')
xx,yy = transform(p2,p1,lon,lat)
b = aggdraw.Brush(event_color)
p = aggdraw.Pen(event_color)
for i in range(len(xx)):
    if xx[i] > xmin and xx[i] < xmax and yy[i] > ymin and yy[i] < ymax:
        x, y = coord2xy(xx[i], yy[i])
        draw.ellipse((x - sx, y -sy, x+sx, y+sy), p, b)
                           
lat,lon,area,energy,quality,id_var = varDatos(glm,'flash')
xx,yy = transform(p2,p1,lon,lat)
b = aggdraw.Brush(group_color)
p = aggdraw.Pen(group_color)
for i in range(len(xx)):
    if xx[i] > xmin and xx[i] < xmax and yy[i] > ymin and yy[i] < ymax:
        x, y = coord2xy(xx[i], yy[i])
        draw.ellipse((x - sx, y -sy, x+sx, y+sy), p, b)

fechag = fecha(pathg)
fechat = fecha(patht)
print("Fecha ", fechag)
white = (255, 255, 255)
font = aggdraw.Font(white, "/usr/share/fonts/truetype/ttf-bitstream-vera/VeraMono.ttf", 32)
draw.text((1856, 1408), "GOES-16/ABI  "+fechat, font)
draw.text((1856, 1464), "GOES-16/GLM "+fechag, font)

draw.flush()
im.save('out.png')

