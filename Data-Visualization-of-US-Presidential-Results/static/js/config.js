// API key
const API_KEY = "pk.eyJ1IjoiYW5hbmRzaGFyYW4iLCJhIjoiY2tpaTgwYnI4MDAxbTJybnhzYmZ6MTFhdyJ9.JKuvMt8-5CqkxlBOWtZr7g";

// https://github.com/d3/d3/issues/1693#issuecomment-35556356
require.config({
    paths: {
        "d3": "http://d3js.org/d3.v4",
        "d3scalechoromatic": "http://d3js.org/d3-scale-chromatic.v1.min",
        "topojson": "http://d3js.org/topojson.v1.min",
        "d3legend":"https://cdnjs.cloudflare.com/ajax/libs/d3-legend/2.11.0/d3-legend.min"
  },
    shim: {
        "d3scalechoromatic": ["d3.global"],
        "d3-interpolate":["d3.global"]
  }
});

define("d3.global", ["d3"], function(_) {
  this.d3 = _;
});
