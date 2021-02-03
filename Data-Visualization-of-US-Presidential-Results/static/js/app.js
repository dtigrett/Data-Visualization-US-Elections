"use strict";

// Array of year
let year2016 = 2016;
let year2020 = 2020;

let year = new Array(year2016, year2020);

var selector = d3.select("#selDataset");

selector
.append("option")
.text(year2016)
.property("value", year2016);

selector
.append("option")
.text(year2020)
.property("value", year2020);

globalThis.selectedYear = 2016;

var demCandidate = new Array("Hillary D. R. Clinton", "Joseph R. Biden");
var gopCandidate = new Array("Donald J. Trump", "Donald J. Trump");

globalThis.selectedDemCandidate = demCandidate[0];
globalThis.selectedGopCandidate = gopCandidate[0];

// If SVG Area is not Empty When Browser Loads, Remove & Replace with a Resized Version of Chart
var svgArea = d3.select("body").select("scaling-svg-container");

// Clear SVG is Not Empty
//if (!svgArea.empty()) {
svgArea.remove();
//}

console.log(selectedYear);
function optionChanged(newYear) {
    // If SVG Area is not Empty When Browser Loads, Remove & Replace with a Resized Version of Chart
    var svgArea = d3.select("body").select("scaling-svg-container");

    // Clear SVG is Not Empty
    //if (!svgArea.empty()) {
    svgArea.remove();
    //}
    
    selectedYear = parseInt(newYear);
    console.log(selectedYear);

    if ( selectedYear == year2016 ) {
        console.log(demCandidate[0]);
        console.log(gopCandidate[0]);
    
        buildElection(selectedYear, demCandidate[0], gopCandidate[0]);
    }
    else {
        console.log(demCandidate[1]);
        console.log(gopCandidate[1]);
        
        buildElection(selectedYear, demCandidate[1], gopCandidate[1]);
    }
}

function buildElection(selectedYear, demCandidate, gopCandidate) {
/*// For each sampe append the value to the dropdown option
year.forEach((sample) => {
    selector
    .append("option")
    .text(year)
    .property("value", year);
})?.catch(function(error) {
    console.log(error);
});*/


const measure = 'countywinrate';

// define data and its attributes
const cols = {
    "countywinrate": {
        "label": "County Win Rate",
        "type": "percentage",
        "format": ".1%",
        "title": `${selectedYear} Presidential Election Results`,
        "latestyear": `${selectedYear}`,
        "url": "townhall.com",
        "source": "Web Scraping",
        "description": `Results of the ${selectedYear} Presidential General Election.`
    },
};

// spinner loader settings
const opts = {
    lines: 9, // The number of lines to draw
    length: 9, // The length of each line
    width: 5, // The line thickness
    radius: 14, // The radius of the inner circle
    color: '#c10e19', // #rgb or #rrggbb or array of colors
    speed: 1.9, // Rounds per second
    trail: 40, // Afterglow percentage
    className: 'spinner', // The CSS class to assign to the spinner
};

// create spinner
const target = d3.select("body").node();

// trigger loader
const spinner = new Spinner(opts).spin(target);

// create tooltip
const tooltip = d3.select("body").append("div").style("position", "absolute").style("z-index", "10").style("visibility", "hidden").attr("class", "tooltip");

// create reset button
const fab = d3.select("body")
    .append("div")
    .attr("class", "fab")
    .style("opacity", 0)
    .text(' ↺ ')
    .on('click', resetZoom)

// define dimensions
const width = 960;
const height = 720;

// set the domain for all scales from -1 to 1
const domain = [-1, 1]

// define color scale
const color = d3.scaleSequential().interpolator(d3.interpolateRgb("pink","blue")).domain(domain);

// define geo path function
const path = d3.geoPath()
    .projection(null);        

// define detail bar scale
const wScale = d3.scaleLinear()
    .domain(domain)
    .range([-width / 3, width / 3]);

// define legend
// use Susie Lu's d3-legend plugin
// http://d3-legend.susielu.com/
const legendWidth = width / 10;
const susieLegend = d3.legendColor()
    .shapeWidth(legendWidth)
    .cells(9)
    .orient("horizontal")
    .labelOffset(2)
    .ascending(true)
    .labelAlign("middle")
    .shapePadding(2);

// define zoom function
const zoom = d3.zoom()
    .scaleExtent([1, 15])
    .on("zoom", zoomed);

// define the county paths
let countyPath            
// object to hold data
let districtObj = {};
// counter for missing counties
let countMissing = 0;
// array for FIPS codes
let geoids = [];
// define useful metrics
let gop_votes;
let dem_votes;
let gop_share;
let dem_share;
// default view for map
// If SVG Area is not Empty When Browser Loads, Remove & Replace with a Resized Version of Chart
//var svgArea = d3.select("body").select("scaling-svg-container").select("svg");
// If SVG Area is not Empty When Browser Loads, Remove & Replace with a Resized Version of Chart select("body").select("scaling-svg-container").
var gArea = d3.select("g");
//select("col-md-12 col-xs-12")
// Clear SVG is Not Empty
//if (!svgArea.empty()) {
gArea.remove();
//}

// start DOM manipulation
// create svg element
const svg = d3.select("svg")
    .attr("viewBox", [0, 0, width, height]);

//svg.remove();

const g = svg.append("g");

// create background box for zoom
g.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height);

// create group for county paths
const group = g.append("g").attr('id', 'map').attr("transform", "translate(0, 60)");

// create legend
const legend = g.append("g")
    .attr("id", "legend")
    .attr("transform", `translate(${(width / 24)},${(height * 11 / 12)})`);

legend.append("rect")
    .attr("class", "background")
    .attr("transform", `translate(-${(width / 24)},0)`)
    .attr("width", width)
    .attr("height", 60);

// create details bar
// use John Alexis Guerra Gómez dynamic details bar
// https://johnguerra.co/
const guerraLayer = g.append("g")
    .attr("id", "details")
    .attr("transform", "translate(" + (width / 2 - 100) + ", 30)");

guerraLayer.append("rect")
    .attr("class", "background")
    .attr("transform", "translate(" + (-wScale.range()[1] + 100) + ", -20)")
    .attr("width", wScale.range()[1] * 2 + 70)
    .attr("rx", 5)
    .attr("ry", 5)
    .attr("height", 60);

guerraLayer.append("text")
    .attr("id", "county-legend")
    .html("Percentage Share of the Two-party Vote")
    .attr("transform", "translate(100, 0)");

svg.call(zoom);

function createViz(us, data) {

    // define Albers USA projection
    // const projection = d3.geoAlbersUsa()
    //     .scale(1285)
    //     .translate([width / 2, height / 2])

    // stop spin.js loader
    spinner.stop();

    // parse data
    data.forEach(function(d) {
        d.per_gop = +d.per_gop;
        d.per_dem = +d.per_dem;
        d.result = +d.per_point_diff * -1;
        d.gop_votes = +d.votes_gop;
        d.dem_votes = +d.votes_dem;
        d.votes_total = +d.total_votes;
        d.geoid = d.county_fips;
        districtObj[d.geoid] = d;
    });

    // array of FIPS code for easier re-use
    geoids = Object.keys(districtObj)

    // calculate metrics
    calculateMetrics();

    // create county, state, and national paths (borders)
    createPaths(us);

    // create detail bars
    createBars();

    // bind election results to county paths
    renderData(data);
    bindHover();
    // setResponsiveSVG();
}

// calculate metrics
function calculateMetrics() {
    gop_votes = d3.sum(geoids, r => districtObj[r].gop_votes)
    dem_votes = d3.sum(geoids, r => districtObj[r].dem_votes)
    gop_share =  gop_votes / (gop_votes + dem_votes)
    dem_share =  dem_votes / (gop_votes + dem_votes)
}

// create county, state, and national paths (borders)
function createPaths(us) {
    // enter data and update county paths
    countyPath = group.selectAll(".counties")
        .data(topojson.feature(us, us.objects.counties).features)
        .enter()
        .append('path')
        .attr("class", "county")
        .on("click", clicked)
        .attr("d", path);
        
    group.append("path")
        .datum(topojson.mesh(us, us.objects.states, function(a, b) {
            return a !== b;
        }))
        .attr("class", "state")
        .attr("d", path);

    group.append("path")
        .datum(topojson.feature(us, us.objects.nation))
        .attr("class", "nation")
        .attr("d", path);
}

// render visualization based on data
function renderData(data) {
    updateLegend(data);
    updatePaths();
}

// create detail bars
function createBars() {
    const guerraBars = guerraLayer.selectAll("bar")
        .data([dem_share, -gop_share])
        .enter()
        .append("g")
        .attr("class", "bar");
    guerraBars
        .append("rect")
        .attr("width", 0)
        .attr("height", width > 767 ? 20 : 10)
        .attr("x", 100)
        .attr("y", 10)
        .style("fill", color)
        .transition()
        .duration(500)
        .attr("x", function(d) {
            return d > 0 ? 100 : 100 - wScale(-d);
        })
        .attr("width", function(d) {
            return d > 0 ? wScale(d) : wScale(-d);
        });
    guerraBars.append("text")
        .text(showDiffLabel)
        .attr("dx", function(d) {
            return d > 0 ? 5 : -5;
        })
        .attr("dy", 24)
        .attr("x", 100)
        .style("text-anchor", function(d) {
            return d > 0 ? "start" : "end";
        })
        .transition()
        .duration(500)
        .attr("x", function(d) {
            return d > 0 ? 100 + wScale(d) : 100 - wScale(-d);
        });
}

function updateLegend(data) {
    susieLegend
        .labelFormat(function(d) {
            return d3.format('.0%')(Math.abs(d));
        })
        .on("cellclick", function(d) { 
            const selectedBar = d3.select(d.target);
            const selectedCell = d3.select(d.target.parentNode);
            const selectedClass = selectedCell.attr('class').split(' ')[1];
            const selectedTick = selectedBar.data()[0];

            // set the opacity for the selected cell and all other cells
            d3.selectAll('.cell')._groups[0].forEach(c => {
                const isSelected = c.classList.contains(selectedClass)
                let opacity = 0.3;
                // if the selection is the middle one, then reset all cell opacity
                if (isSelected || selectedTick === 0) opacity = 1
                d3.select(c).style('opacity', opacity)
            })

            districtObj = {}
            data.forEach((r,i) => {
                if (selectedTick === 0) {
                    districtObj[r.geoid] = r;
                }else if (r.result > 0 && r.result < selectedTick) {
                    districtObj[r.geoid] = r;
                } else if (r.result < 0 && r.result > selectedTick) {
                    districtObj[r.geoid] = r;
                }
            })

            updatePaths();
        })
        .title('Percentage Point Difference')
        .scale(color);

    legend.call(susieLegend);

    // add special classes to each cell of the legend
    d3.selectAll('.cell').each((d, i, nodes) => { nodes[i].classList.add(`cell-${i}`); })
}

// adjust data bar on hover
function updateBars(d) {
    let share = [dem_share, -gop_share];
    let label = `<tspan x="0" y="0">Percentage Point Difference: ${formatValue(Math.abs(share[0] + share[1]), 'percent')}</tspan>`;

    if (d) {
        const county = districtObj[d.id];
        // county = districtObj[d.properties.geoid];
        if (county) {
            share = [county.per_dem, -county.per_gop];
            label = `<tspan x="0" y="0">Percentage Point Difference: ${formatValue(Math.abs(county.result), 'percent')}</tspan>`;
        }
    }

    const guerraBars = guerraLayer
        .selectAll(".bar")
        .data(share);

    guerraBars.select("rect")
        .transition()
        .duration(500)
        .attr("x", function(d) {
            return d > 0 ? 100 : 100 - wScale(-d);
        })
        .attr("width", function(d) {
            return d > 0 ? wScale(d) : wScale(-d);
        })
        .style("fill", color);

    guerraBars.select("text")
        .text(showDiffLabel)
        .transition()
        .duration(500)
        .attr("x", function(d) {
            return d > 0 ? 100 + wScale(d) : 100 - wScale(-d);
        })


    guerraLayer.select("#county-legend").html(label);

}

// update fill property of county paths
function updatePaths() {
                
    // update map with new data
    countyPath
        .transition()
        .duration(1000)
        .style("fill", function(d) {
            const county = districtObj[d.id];
            // const county = districtObj[d.properties.geoid];
            if (county)
                return color(county.result);
            else {
                // countMissing++;
                // console.log("geoid: " + d.id + " not found. Error #" + countMissing);
                // console.log("geoid: " + d.properties.geoid + " not found. Error #" + countMissing);
                return '#ccc';
            }
        });
}

function resetZoom() {
    svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity,
        d3.zoomTransform(svg.node()).invert([width / 2, height / 2])
    );
}        

// define click function
function clicked(event, d) {
    const [[x0, y0], [x1, y1]] = path.bounds(d);
    event.stopPropagation();
    svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity
            .translate(width / 2, height / 2)
            .scale(Math.min(8, 0.9 / Math.max((x1 - x0) / width, (y1 - y0) / height)))
            .translate(-(x0 + x1) / 2, -(y0 + y1) / 2),
        d3.pointer(event, svg.node())
    );
}

// define zoom event
function zoomed(event) {
    const {transform} = event;
    group.attr("transform", transform);
    group.attr("stroke-width", 1 / transform.k);
    // hide button if zoomed out
    if (transform.k > 1 && (transform.x || transform.y !== 0)) {
        fab
            .transition()
            .duration(500)
            .style("opacity", 1)
    } else {
        fab
            .transition()
            .duration(500)
            .style("opacity", 0)
    }
}

// define mouseover and mouseout events to ensure mouseover events work on IE
function bindHover() {
    document.body.addEventListener('mousemove', function(e) {

        if (e.target.nodeName == 'path' && e.target.className.animVal !== 'state') {
            const d = d3.select(e.target).data()[0];
            const county = districtObj[d.id]
            // const county = districtObj[d.properties.geoid]
            const value = formatValue(county.result);
            const dem_votes = (county.dem_votes)
            const gop_votes = (county.gop_votes)
            const votes_total = (county.votes_total)

            const report_level = '<div class="e-title">' + county.county_name + ', ' + county.state_name + '</div>';

            const startTable = '<table>'
            // const tbody = `<tbody><tr><td><svg height="20" width="150"><rect height="20" width="4" style="fill:${color(0.75)}"></rect><text x="10" y="15">Joseph R. Biden</text></svg></td><td>Dem.</td><td style="text-align:right">${formatValue(dem_votes)}</td><td style="text-align:right; font-weight:700">${formatValue(dem_votes / votes_total, "percent")}</td></tr><tr><td><svg height="20" width="150"><rect height="20" width="4" style="fill:${color(-0.75)}"></rect><text x="10" y="15">Donald J. Trump</text></svg></td><td>Rep.</td><td style="text-align:right">${formatValue(gop_votes)}</td><td style="text-align:right; font-weight:700">${formatValue(gop_votes / votes_total, "percent")}</td></tr><tr style="font-size:13px"><td><span><strong>All Votes</strong></span></td><td></td><td style="text-align:right"><span><strong>${formatValue(votes_total)}</strong></span></td><td style="text-align:right"></td></tr></tbody>`;
            const tbody = `<table><tbody><tr><td></td><th>Candidate</th><th>Party</th><th style="text-align:right">Votes</th><th style="text-align:right">Pct.</th></tr><tr><td style="background-color:${color(0.75)}"></td><td>${demCandidate}</td><td>Dem.</td><td style="text-align:right">${formatValue(dem_votes)}</td><td style="text-align:right; font-weight:700">${formatValue(dem_votes / votes_total, "percent")}</td></tr><tr><td style="background-color:${color(-0.75)}"></td><td>${gopCandidate}</td><td>Rep.</td><td style="text-align:right">${formatValue(gop_votes)}</td><td style="text-align:right; font-weight:700">${formatValue(gop_votes / votes_total, "percent")}</td></tr><tr style="font-size:13px"><td></td><td><span><strong>All Votes</strong></span></td><td></td><td style="text-align:right"><span><strong>${formatValue(votes_total)}</strong></span></td><td style="text-align:right"></td></tr></tbody></table>`
            const endTable = '</table>';

            // show tooltip with information from the __data__ property of the element
            const content = report_level + startTable + tbody + endTable;

            showDetail(e, content);
            updateBars(d);
        }
    });

    document.body.addEventListener('mouseout', function(e) {
        if (e.target.nodeName == 'path') hideDetail();
    });
}

// return percentage point labels for details bars
function showDiffLabel(d) {
    return d > 0 ? `Dem. ${formatValue(d, 'percent')}` : `Rep. ${formatValue(-d, 'percent')}`
}

// Show tooltip on hover
function showDetail(event, content) {

    // show tooltip with information from the __data__ property of the element
    let x_hover = 0;
    let y_hover = 0;

    const tooltipWidth = parseInt(tooltip.style('width'));
    const tooltipHeight = parseInt(tooltip.style('height'));
    let classed, notClassed;

    if (event.pageX > document.body.clientWidth / 2) {
        x_hover = tooltipWidth + 30;
        classed = 'right';
        notClassed = 'left';
    }
    else {
        x_hover = -30;
        classed = 'left';
        notClassed = 'right';
    }

    y_hover = (document.body.clientHeight - event.pageY < (tooltipHeight + 4)) ? event.pageY - (tooltipHeight + 4) : event.pageY - tooltipHeight / 2;

    return tooltip
        .classed(classed, true)
        .classed(notClassed, false)
        .style("visibility", "visible")
        .style("top", y_hover + "px")
        .style("left", (event.pageX - x_hover) + "px")
        .html(content);
}

// Hide tooltip on hover
function hideDetail() {

    // hide tooltip
    return tooltip.style("visibility", "hidden");
}

// set SVG to respond to changes in clientWidth and clientHeight
function setResponsiveSVG() {
    // Many browsers -- IE particularly -- will not auto-size inline SVG
    // IE applies default width and height sizing
    // padding-bottom hack on a container solves IE inconsistencies in size
    // https://css-tricks.com/scale-svg/#article-header-id-10
    const width = +d3.select('svg').attr('width');
    const height = +d3.select('svg').attr('height');
    const calcString = +(height / width) * 100 + "%";

    const svgElement = d3.select('svg');
    const svgParent = d3.select(d3.select('svg').node().parentNode);

    svgElement
        .attr('class', 'scaling-svg')
        .attr('preserveAspectRatio', 'xMinYMin')
        .attr('viewBox', '0 0 ' + width + ' ' + height)
        .attr('width', null)
        .attr('height', null);

    svgParent.style('padding-bottom', calcString);
}

// format values
function formatValue(value, type) {
    return type === 'percent' ? d3.format('.2%')(value) : d3.format(',.0f')(value)
}

// get county paths and election data
Promise.all([
    d3.json("https://unpkg.com/us-atlas@1/us/10m.json"),
    d3.csv(`/static/Resources/${selectedYear}_US_County_Level_Presidential_Results.csv`)
]).then(resp => {
    createViz(resp[0], resp[1])
}).catch(e => {
    console.log(e)
})
}

buildElection(selectedYear, selectedDemCandidate, selectedGopCandidate);