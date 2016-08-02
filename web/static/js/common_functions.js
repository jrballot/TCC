var map;
var rectangle;
var infoWindow;

// navbar
$(".nav a").on("click", function(){
   $(".nav").find(".active").removeClass("active");
   $(this).parent().addClass("active");
});


// Datepicker
$(function() {
    $("#datepicker").datepicker({
        changeMonth: true,
        changeYear: true
    });
});

function initMap() {

    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: -22.8449, lng: -45.2308},
        zoom: 4,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        disableDefaultUI: true
    });


    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
              var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
              };

              infoWindow.setPosition(pos);
              infoWindow.setContent('Location found.');
              map.setCenter(pos);
              map.setZoom(10);
        }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
    }

    var center = {
        lat: map.getCenter().lat(),
        lng: map.getCenter().lng()
    }

    var bounds = {
        north: -22.80,
        south: -22.90,
        east:  -45.10,
        west:  -45.38
    };


    //console.log(bounds);



  // Define a rectangle and set its editable property to true.
    rectangle = new google.maps.Rectangle({
        bounds: bounds,
        editable: true,
        draggable: true
    });

    rectangle.setMap(map);

    rectangle.addListener('bounds_changed', showNewCoor);

    infoWindow = new google.maps.InfoWindow();


}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
}



function showNewCoor(event) {
    var ne = rectangle.getBounds().getNorthEast();
    var sw = rectangle.getBounds().getSouthWest();

    var x1;
    var x2;
    var y1;
    var y2;


    // Coord X for center of rectangle
    if ( ne.lat() > sw.lat() ) {
        x1 = sw.lat();
        x2 = ne.lat();
    } else {
        x1 = ne.lat();
        x2 = sw.lat();
    }

    // Coord Y for center of rectangle
    if ( ne.lng() > sw.lng() ) {
        y1 = sw.lng();
        y2 = ne.lng();
    } else {
        y1 = ne.lng();
        y2 = sw.lng();
    }

    var clat = x1+((x2-x1)/2);
    var clng = y1+((y2-y1)/2);

    var center = {
        lat: clat,
        lng: clng,
    };

    // Distance from center to X and Y bounds.
    //var distance = calcDistance(center, ne);

    document.getElementById("centlat").value = center.lat;
    document.getElementById("centlon").value = center.lng;

    var contentString = '<b>Coor:</b><br>'
        + 'North-West: ' + ne.lat() + ', ' + sw.lng() + '<br>'
        + 'North-East: ' + ne.lat() + ', ' + ne.lng() + '<br>'
        + 'South-West: ' + sw.lat() + ', ' + sw.lng() + '<br>'
        + 'South-East: ' + sw.lat() + ', ' + ne.lng() + '<br>'
        + 'Center: ' + center.lat + ', ' + center.lng + '<br>';
        //+ 'ctobY: ' + distance.Y + ', ' + 'ctobX: ' + distance.X;


    infoWindow.setContent(contentString);
    infoWindow.setPosition(ne);

    infoWindow.open(map)
}


/*
function calcDistance(center, ne) {
    var R = 6371e3; // metres
    var Dlat = deg2rad(center.lat - ne.lat());
    var Dlng = deg2rad(center.lng - ne.lng());

    var aY = Math.sin(Dlat/2) * Math.sin(Dlat/2) +
                Math.cos(center.lat) * Math.cos(ne.lat()) *
                Math.sin(0/2) * Math.sin(0/2);

    var aX = Math.sin(0/2) * Math.sin(0/2) +
            Math.cos(center.lat) * Math.cos(center.lat) *
            Math.sin(Dlng/2) * Math.sin(Dlng/2);

    var cY = 2 * Math.atan2(Math.sqrt(aY), Math.sqrt(1-aY));
    var cX = 2 * Math.atan2(Math.sqrt(aX), Math.sqrt(1-aX));

    var distY = R * cY;
    var distX = R * cX;

    var dist = { Y: distY, X: distX,};

    return dist;
}

function deg2rad(deg) {
    return deg * (Math.PI/180)
}
*/
