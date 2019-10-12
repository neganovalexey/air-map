var mapContainer = document.getElementById('map-container');

var mapOptions = {
  zoom: 12,
  center: {lat:41.3851, lng:2.1734},
  height: 600,
  width: 900,
  noWrap: true
};

var defaultLayers = platform.createDefaultLayers();

var map = new H.Map(
  mapContainer,
  defaultLayers.normal.map,
  mapOptions);

var circles = []

var mapTileService = platform.getMapTileService({
    type: 'base'
  }),
  mapLayer = mapTileService.createTileLayer(
    'maptile',
    'normal.day',
    256,
    'png8'
  );
map.setBaseLayer(mapLayer);


var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers, 'en-US');

function prettyScaling(size, zoom) {
  threshold = 32
  base = 2 ** 10.5
  if (size < threshold) {
    radius = (size) / zoom;
  } else {
    radius = (threshold + Math.pow(size - threshold + 1, 0.25)) / zoom;
  }
  return base + radius * (2 ** 20 / threshold);
}

setInterval(function() {
  for (var i = 0; i < circles.length; ++i) {
    var lat = circles[i].geom.getCenter().lat;
    circles[i].geom.setRadius(prettyScaling(circles[i].size, 2 << map.getZoom())*Math.cos((180 / Math.PI)*lat));
  }
}, 500);


window.addEventListener('resize', function () {
  map.getViewPort().resize();
});
    

$('#submitform').submit(function(e){
  e.preventDefault();
  $.ajax({
    url: '/filter',
    type: 'post',
    data: $('#submitform').serialize(),
    success: function(data) {
      for (var i = 0; i < circles.length; ++i) {
        map.removeObject(circles[i].geom);
      }

      var points = data['points'];
      circles = [];

      for (var i = 0; i < points.length; ++i) {
        var circle = new H.map.Circle(
          { lat: points[i].lat, lng: points[i].lng },
          prettyScaling(points[i].count, 2 << map.getZoom())*Math.cos((180 / Math.PI)*points[i].lat),
          {style: {fillColor: points[i].fill_color, strokeColor: 'black', lineWidth: 0}})

        circle.setData(points[i].lat.toString() + ' ' + points[i].lng.toString());

        circle.addEventListener('tap', function (evt) {
          var bubble =  new H.ui.InfoBubble(evt.target.getCenter(), {
            content: evt.target.getData()
          });
          ui.addBubble(bubble);
        }, false);

        circles.push({size: points[i].count, geom: circle});

        map.addObject(circle);
      }

      for (var i = 0; i < points.length; ++i) {
        var circle = new H.map.Circle(
          { lat: points[i].lat, lng: points[i].lng },
          prettyScaling(points[i].count, 2 << map.getZoom())*Math.cos((180 / Math.PI)*points[i].lat),
          {style: {fillColor: 'rgba(0, 0, 0, 0)', strokeColor: 'black', lineWidth: 2.0}})
        
        circles.push({size: points[i].count, geom: circle});

        map.addObject(circle);
      }

      for (var i = 0; i < points.length; ++i) {
        var circle = new H.map.Circle(
          { lat: points[i].lat, lng: points[i].lng },
          prettyScaling(points[i].count, 2 << map.getZoom())*Math.cos((180 / Math.PI)*points[i].lat),
          {style: {fillColor: 'rgba(0, 0, 0, 0)', strokeColor: points[i].fill_color, lineWidth: 1.0}})

        circles.push({size: points[i].count, geom: circle});

        map.addObject(circle);
      }
    }
  });
});
