#!/usr/bin/env python3
"""Regenerate the route map from the web layout and terrain grid. Requires Pillow."""
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORLD = Path(__file__).resolve().parents[1]
layout = json.loads((WORLD / 'layout.json').read_text())
nav = json.loads((WORLD / 'navigation.json').read_text())
places = {place['id']: place for place in layout['places']}
palette = ['#a64f2e', '#405a8d', '#367655', '#84487c', '#ad7327', '#4c727a',
           '#596937', '#635080', '#876a42', '#327d86', '#586733',
           '#934b58', '#647a97']
paper, ink, muted, rule = '#efe9d8', '#263b37', '#5a6356', '#ad9570'
font_path = os.environ.get(
    'HOGWARTS_PLAN_FONT', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
)

def font(size):
    return ImageFont.truetype(font_path, size)

def world_point(point):
    return places[point]['at'] if isinstance(point, str) else point

left, top, scale = 65, 177, 4.58
west, north = -120, -104
map_width, map_height = 1116, 826

def xy(x, z):
    return left + (x - west) * scale, top + (z - north) * scale

out = Image.new('RGB', (1790, 1040 + 35*math.ceil(len(layout['routes'])/3) + 78), paper)
draw = ImageDraw.Draw(out)
draw.text((left, 34), '霍格沃茨与周边高地', font=font(49), fill=ink)
draw.text((left + 2, 107), 'HOGWARTS & THE HIGHLANDS', font=font(20), fill=muted)
draw.text((1722, 72), f'校园漫游 · {len(places)} 处地标', font=font(26), fill=ink, anchor='ra')
draw.line((left, 143, 1725, 143), fill=rule, width=2)

def map_color(x, z):
    i = int((x - nav['x0']) / nav['step'])
    j = int((z - nav['z0']) / nav['step'])
    heights = nav['heights']
    h = heights[j][i]
    slope = max(-10, min(10, (heights[j + 1][i] - heights[j][i + 1]) * 6))
    if h < .15:
        return (133, 163, 157)
    t = min(1, max(0, h / 13))
    contour = -9 if int(h/1.35) != int(heights[j + 1][i] / 1.35) else 0
    return tuple(int(a*(1-t) + b*t + slope + contour)
                 for a,b in zip((207,211,174), (193,176,139)))

for dy in range(0, map_height, 2):
    for dx in range(0, map_width, 2):
        color = map_color(west + dx / scale, north + dy / scale)
        draw.rectangle((left+dx, top+dy, left+dx+1, top+dy+1), fill=color)

draw.ellipse((*xy(-104.6,-52.8),*xy(-79.4,-15.2)), fill='#aabf87', outline='#75845d', width=2)
for x,z,tx,tz,half,_ in nav.get('standRails',[]):
    draw.line((xy(x-tx*half,z-tz*half),xy(x+tx*half,z+tz*half)),fill='#968466',width=5)
for x1,z1,x2,z2 in [*nav['blocks'], *nav.get('detailBlocks', []), *nav['atlasBlocks'], *nav['landmarkBlocks']]:
    a,b=xy(x1,z1),xy(x2,z2)
    if not (left <= a[0] <= left+map_width and top <= a[1] <= top+map_height):
        continue
    if x2-x1 < 1.65 and z2-z1 < 1.65:
        draw.ellipse((a[0]-1,a[1]-1,b[0]+1,b[1]+1),fill='#6e8870')
    else:
        draw.rectangle((*a,*b),fill='#9d8d72',outline='#8c8068')
for path in layout['trails']:
    points=[xy(*world_point(p)) for p in path]
    draw.line(points,fill='#9a8667',width=8,joint='curve')
    draw.line(points,fill='#fbefd2',width=5,joint='curve')

segments={}
for route,color in zip(layout['routes'],palette):
    points=[tuple(world_point(p)) for p in [route['start'],*route['stops']]]
    for a,b in zip(points,points[1:]):
        key=tuple(sorted((a,b)))
        segments.setdefault(key,[]).append(color)

# Parallel strokes retain the identities of routes that share a footpath.
for (a,b),colors in segments.items():
    x1,y1=xy(*a)
    x2,y2=xy(*b)
    dist=math.hypot(x2-x1,y2-y1)
    if not dist:
        continue
    nx,ny=(y1-y2)/dist,(x2-x1)/dist
    colors=list(dict.fromkeys(colors))
    for index,color in enumerate(colors):
        offset=(index-(len(colors)-1)/2)*3.4
        draw.line((x1+nx*offset,y1+ny*offset,x2+nx*offset,y2+ny*offset),fill=color,width=3)

marker_offsets = {'honeydukes': (14, -28), 'observatory': (-24, -21), 'broomsticks': (-4, 26)}
for n,place in enumerate(places.values(),1):
    px,py=xy(*place['at'])
    dx,dy=marker_offsets.get(place['id'], (0,0))
    x,y=px+dx,py+dy
    if dx or dy:
        draw.line((px,py,x,y), fill=ink, width=2)
        draw.ellipse((px-3,py-3,px+3,py+3),fill=ink)
    draw.ellipse((x-14,y-14,x+14,y+14),fill=ink,outline='#f6e3a9',width=2)
    draw.text((x,y-1),str(n),font=font(16),fill='white',anchor='mm')
draw.text(xy(-89,63),'黑    湖',font=font(25),fill='#315754')
draw.rectangle((left,top,left+map_width,top+map_height),outline=rule,width=2)

x,y=left+43, top+59
draw.polygon([(x,y-14),(x-8,y+12),(x,y+7),(x+8,y+12)],fill=ink)
draw.text((x,y-27),'N',font=font(17),fill=ink,anchor='mm')
x,y=left+41, top+map_height-34
draw.line((x,y,x+20*scale,y),fill=ink,width=3)
draw.text((x,y-9),'20 m',font=font(17),fill=ink,anchor='ls')

draw.text((1220,181),'地点与室内入口',font=font(30),fill=ink)
for n,place in enumerate(places.values(),1):
    y=228+(n-1)*26
    draw.text((1222,y),str(n).zfill(2),font=font(18),fill=muted,anchor='lm')
    draw.text((1271,y),place['name'],font=font(24),fill=ink,anchor='lm')
    rooms=' · '.join(layout['rooms'][i] for i in place.get('rooms', []))
    if rooms:
        draw.text((1440,y),rooms,font=font(14),fill=muted,anchor='lm')
    draw.line((1220,y+12,1724,y+12),fill='#d5c8b0')

draw.line((left,1037,1725,1037),fill=rule,width=2)
for i,(route,color) in enumerate(zip(layout['routes'],palette)):
    x=left+(i%3)*330
    y=1068+(i//3)*35
    draw.line((x,y,x+35,y),fill=color,width=5)
    draw.text((x+48,y),route['name'],font=font(21),fill=ink,anchor='lm')
draw.text((left,out.height-40),'地形、尺度与入口按本版游览路线布置。底图与网页使用同一套地图坐标。',font=font(17),fill=muted)
out.save(WORLD/'ground-plan.png', optimize=True)
