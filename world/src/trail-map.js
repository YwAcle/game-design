function routePoint(point, places) {
  return typeof point === 'string' ? places.get(point) : point;
}

export function drawTrailMap(canvas, layout, nav, position, route, stop, yaw) {
  const context = canvas.getContext('2d');
  const {width, height} = canvas;
  const left = -122, top = -106, meters = 250;
  const scale = width / meters;
  const screen = ([x, z]) => [(x - left) * scale, (z - top) * scale];
  const places = new Map(layout.places.map(({id, at}) => [id, at]));
  context.fillStyle = '#e1d4ad';
  context.fillRect(0, 0, width, height);

  const swatches = ['#8ca6a0', '#d8d9b0', '#c9cda0', '#c0bf91', '#bca980', '#a69474'];
  const cell = nav.step * scale;
  for (const [row, heights] of nav.heights.entries()) {
    for (const [column, elevation] of heights.entries()) {
      const x = (nav.x0 + column * nav.step - left) * scale;
      const y = (nav.z0 + row * nav.step - top) * scale;
      const shade = elevation < .15 ? 0 : Math.min(5, 1 + Math.floor(elevation / 3.5));
      context.fillStyle = swatches[shade];
      context.fillRect(Math.floor(x), Math.floor(y), Math.ceil(cell) + 1, Math.ceil(cell) + 1);
    }
  }

  context.fillStyle = '#9c8b6d';
  for (const [x1, z1, x2, z2] of [...nav.blocks, ...nav.detailBlocks, ...nav.atlasBlocks, ...nav.landmarkBlocks]) {
    context.fillRect(...screen([x1, z1]), (x2 - x1) * scale, (z2 - z1) * scale);
  }
  function line(points, color, width) {
    context.beginPath();
    context.moveTo(...screen(points[0]));
    for (const point of points.slice(1)) context.lineTo(...screen(point));
    context.lineWidth = width;
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.strokeStyle = color;
    context.stroke();
  }
  for (const path of layout.trails) line(path.map(point => routePoint(point, places)), '#f6edd4', 5);

  if (route) {
    const remaining = route.stops.slice(stop).map(point => routePoint(point, places));
    if (remaining.length) {
      line([position, ...remaining], '#996146', 6);
      const [x, y] = screen(remaining[0]);
      context.fillStyle = '#996146';
      context.beginPath();context.arc(x, y, 8, 0, Math.PI * 2);context.fill();
    }
  }

  context.fillStyle = '#43534b';
  for (const {at} of layout.places) {
    const [x, y] = screen(at);
    context.beginPath();context.arc(x, y, 4.5, 0, Math.PI * 2);context.fill();
  }
  const names = ['霍格沃茨', '黑湖', '魁地奇球场', '温室', '禁林', '霍格莫德', '车站'];
  const anchors = [[-1, -13], [-10, 58], [-90, -55], [48, -37], [96, -89], [-43, -83], [10, -98]];
  context.font = '23px "Noto Serif CJK SC", "Songti SC", serif';
  context.textAlign = 'center';
  names.forEach((name, index) => context.fillText(name, ...screen(anchors[index])));
  context.fillText('北 ↑', 53, 47);

  context.save();
  context.translate(...screen(position));
  if (yaw !== null) context.rotate(-yaw);
  context.fillStyle = '#284941';
  context.beginPath();
  if (yaw === null) context.arc(0, 0, 9, 0, Math.PI * 2);
  else {
    context.moveTo(0, -15);context.lineTo(10, 11);context.lineTo(0, 6);context.lineTo(-10, 11);
    context.closePath();
  }
  context.strokeStyle = '#fff3cd';context.lineWidth = 3;
  context.fill();context.stroke();context.restore();
}
