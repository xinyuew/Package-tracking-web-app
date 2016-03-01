function add_addr2map(map, address, index) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': address}, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            var new_loc = {
                lat: latitude,
                lon: longitude,
                html: address,
            };
            map.AddLocation(new_loc, index, true);
            //console.log('loc ' + index + ' ' + address + ' loaded');
        } else {
            console.log("GeoCode request failed.")
        }
    });
}

function get_locations() {
    var locations = [];
    $('table tr td:nth-child(3)').each(function () {
        var val = $(this).html();
        if ((val != '') && (val != 'None, None') && (val != 'United States')) {
            locations.push(val);
        }
    });

    $.unique(locations)
    locations.reverse();
    return locations;
}

$(document).ready(function () {
    var locs = get_locations();
    //console.log(locs);

    var maplace = new Maplace({
        locations: [],
        controls_type: 'list',
        controls_on_map: false,
        view_all_text: 'Start',
        type: 'polyline'
    });

    var len = locs.length;
    for (i = 0; i < len; i++) {
        add_addr2map(maplace, locs[i], i);
    }
});
