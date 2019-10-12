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

let baseCount = 10000;
let nonLinearity = 2;

window.addEventListener('resize', function () {
  map.getViewPort().resize();
});

const colorScale = d3.scaleLinear().range([
          'rgba(255, 255, 255, 0)',
	  'yellow',
          'rgba(34, 139, 34, 0.9)',
      ]).domain([0, 0.5, 1]);

$('#submitform').submit(function(e){
  e.preventDefault();
  $.ajax({
    url: '/filter',
    type: 'post',
    response: $('#submitform').serialize(),
    success: function(response) {
      csvFile = response.filename;
      // maybe need to remove layer here
      let provider = new H.datalens.RawDataProvider({
          dataUrl: csvBase + csvFile,
          dataToFeatures: (data, helpers) => {
              let parsed = helpers.parseCSV(data);
              let features = [];
              for (let i = 1; i < parsed.length; i++) {
                  let row = parsed[i];
                  let feature = {
                      "type": "Feature",
                      "geometry": {
                          "type": "Point",
                          "coordinates": [Number(row[2]), Number(row[1])]
                      },
                      "properties": {
                          "co2_emission": Number(row[3])
                      }
                  };
                  features.push(feature);
              }
              return features;
          },
          featuresToRows: (features, x, y, z, tileSize, helpers) => {
              let counts = {};
              for (let i = 0; i < features.length; i++) {
                  let feature = features[i];
                  let coordinates = feature.geometry.coordinates;
                  let lng = coordinates[0];
                  let lat = coordinates[1];

                  let p = helpers.latLngToPixel(lat, lng, z, tileSize);
                  let px = p[0];
                  let py = p[1];
                  let tx = px % tileSize;
                  let ty = py % tileSize;
                  let key = tx + '-' + ty;

                  if (counts[key]) {
                      counts[key] += feature.properties.co2_emission;
                  } else {
                      counts[key] = feature.properties.co2_emission;
                  }
              }

              let rows = [];
              for (let key in counts) {
                  let t = key.split('-');
                  let tx = Number(t[0]);
                  let ty = Number(t[1]);
                  let count = counts[key];
                  if (count != 0) {
                      rows.push({tx, ty, count, value: count});
                  }
              }
              return rows;
          }
      });
      let heatmap = new H.datalens.HeatmapLayer(provider, {
          rowToTilePoint: row => {
              return {
                  x: row.tx,
                  y: row.ty,
                  count: Math.abs(row.count),
                  value: Math.abs(row.count)
              };
          },
          bandwidth: [{
              value: 1,
              zoom: 9
          }, {
              value: 10,
              zoom: 16
          }],
          valueRange: z => [0, baseCount / Math.pow(z, 2 * nonLinearity)],
          countRange: [0, 0],
          opacity: 1,
          colorScale: colorScale,
          aggregation: H.datalens.HeatmapLayer.Aggregation.SUM,
          inputScale: H.datalens.HeatmapLayer.InputScale.LINEAR
      });
      map.addLayer(heatmap);
    }
  });
});
