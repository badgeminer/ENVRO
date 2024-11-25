import './style.css';
import Feature from 'ol/Feature.js';
import {Map, View} from 'ol';
import {Vector,TileWMS} from 'ol/source.js';
import {Icon,Style,Stroke} from 'ol/style.js';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer.js';
import OSM from 'ol/source/OSM';
import {Point,LineString} from 'ol/geom';
import {fromLonLat,useGeographic} from 'ol/proj.js';
import VectorImageLayer from 'ol/layer/VectorImage.js';
//import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import Fill from 'ol/style/Fill.js';


async function getRadarStartEndTime() {
  let response = await fetch('https://geo.weather.gc.ca/geomet/?lang=en&service=WMS&request=GetCapabilities&version=1.3.0&LAYERS=RADAR_1KM_RRAI&t=' + new Date().getTime())
  let data = await response.text().then(
    data => {
      let xml = parser.parseFromString(data, 'text/xml');
      let [start, end] = xml.getElementsByTagName('Dimension')[0].innerHTML.split('/');
      let default_ = xml.getElementsByTagName('Dimension')[0].getAttribute('default');
      return [start, end, default_];
    }
  )
  return [new Date(data[0]), new Date(data[1]), new Date(data[2])];
}

const vectorLayer = new VectorImageLayer({
  background: '#00000000',
  imageRatio: 2,
  source: new VectorSource({
    url: 'https://api.weather.gc.ca/collections/public-standard-forecast-zones/items?f=json',
    format: new GeoJSON(),
  }),
  style: {
    'stroke-color': "#000000",
    'stroke-width': 0.5,
  }
});

const alerts_layer = new VectorImageLayer({
  background: '#00000000',
  imageRatio: 2,
  source: new VectorSource({
    url: '/api/geojson/merged',
    format: new GeoJSON(),
  }),
  style: [
    {
      filter: ['==', ['get', 'warn'],"snowfall"],
      style: {
        "fill-color":"#03c2fc55",
        'stroke-color': "#000000",
        'stroke-width': 0.1,
      }
    },
    {
      filter: ['==', ['get', 'warn'],"blizzard"],
      style: {
        "fill-color":"#00007755",
        'stroke-color': "#000000",
        'stroke-width': 0.1,
      }
    },
    {
      else:true,
      style: {
        "fill-color":"#11111155",
        'stroke-color': "#00000077",
        'stroke-width': 1,
      }
    }
  ],
});

const alertsO_layer = new TileLayer({
  opacity: 0.4,
  source: new TileWMS({
    url: 'https://geo.weather.gc.ca/geomet/',
    params: {'LAYERS': 'ALERTS', 'TILED': true},
    transition: 0
  })
})
const radar_layer = new TileLayer({
  opacity: 0.4,
  source: new TileWMS({
    url: 'https://geo.weather.gc.ca/geomet/',
    params: {'LAYERS': 'RADAR_1KM_RRAI', 'TILED': true},
    transition: 0
  })
})

radar_layer.getSource().on("imageloaderror", () => {
  getRadarStartEndTime().then(data => {
    currentTime = startTime = data[0];
    endTime = data[1];
    defaultTime = data[2];
    updateLayers();
    updateInfo();
    updateButtons();
  })
});




function updateLayers() {
  radar_layer.getSource().updateParams({'TIME': currentTime.toISOString().split('.')[0]+"Z"});
  //radar_layer.getSource().updateParams({'TIME': currentTime.toISOString().split('.')[0]+"Z"});
}


var lpings = document.getElementById("locPing");
//useGeographic()
const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM()
    }),
    vectorLayer,
    alerts_layer,
    radar_layer,
    
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

var checks = document.getElementById('checks_map')
function makeBind(name,o) {
    var data = document.createElement("p");
    var check = document.createElement("input");
    check.type = "checkbox";
    data.innerText = name;
    //data.appendChild(check);
    check.checked = o.getVisible()
    data.insertAdjacentElement("afterbegin",check)
    checks.appendChild(data)
    

    check.addEventListener('change', (event) => {
        o.setVisible(check.checked);
      })
}
makeBind("Alerts",alerts_layer)
makeBind("Bounds",vectorLayer)
makeBind("Radar",radar_layer)