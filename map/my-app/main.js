import './style.css';
import Feature from 'ol/Feature.js';
import {Map, View} from 'ol';
import {Vector} from 'ol/source.js';
import {Icon,Style,Stroke} from 'ol/style.js';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer.js';
import OSM from 'ol/source/OSM';
import {Point,LineString} from 'ol/geom';
import {fromLonLat,useGeographic,} from 'ol/proj.js';


var lpings = document.getElementById("locPing");
//useGeographic()
const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM()
    })
  ],
  view: new View({
    center: fromLonLat([-114, 51]),
    zoom: 12
  })
});

var markers = new VectorLayer({
  source: new Vector(),
  style: new Style({
    image: new Icon({
      anchor: [0.5, 0.5],
      src: 'location.svg'
    })
  })
});
map.addLayer(markers);

var chasers = new VectorLayer({
  source: new Vector(),
  style: new Style({
    image: new Icon({
      anchor: [0.5, 0.5],
      src: 'chaser.svg'
    })
  })
});
map.addLayer(chasers);


var route = new VectorLayer({
  source: new Vector(),
  style: new Style({
    stroke: new Stroke({
      width: 3,
      color: [255, 50, 0, 0.8]
    }),
  })
});

map.addLayer(route);
var locations = [[51.1435, -114.257], [51.1441, -114.2583], [51.1451, -114.2606],[51.1463, -114.2639]];

function regenLine(locations) {
  locations.map(function(l) {
    return l.reverse();
  });
  
  var polyline = new LineString(locations);
  polyline.transform('EPSG:4326', 'EPSG:3857');
  var feature = new Feature(polyline);
  var src =  new Vector()
  src.addFeature(feature)
  route.setSource(src)
}
regenLine(locations);

var marker = new Feature(new Point(fromLonLat([-114, 51])));
  chasers.getSource().addFeature(marker);

var location = new Feature(new Point(fromLonLat([-114, 51])));
    markers.getSource().addFeature(location);

const watchID = navigator.geolocation.watchPosition((position) => {
  location.latitude =position.coords.latitude
  location.longitude =position.coords.longitude
  location.setGeometry(new Point(fromLonLat([position.coords.longitude, position.coords.latitude])))
  console.log(position.coords.latitude, position.coords.longitude);
  if (lpings.checked)  {
    fetch("/api/chsr", {
      method: "POST",
      body: JSON.stringify([
        position.coords.latitude,
        position.coords.longitude
      ]),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    })
      .then((response) => response.json())
      .then((json) => {
        regenLine(json.route)
        marker.setGeometry(new Point(fromLonLat(json.chsr)))
      });
  } else {
    
  }
  
});