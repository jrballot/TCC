

// Get current possition
function initMap() {
    if (navigator.geolocation) {
        // if have support to geolocation, getCurrentPosition and pass to showPosition
        navigator.geolocation.getCurrentPosition(openCurrentPosition);
    } else {
        alert("Geolocation not suported")
    }
}

// With current possition open a map
function openCurrentPosition(position) {

    var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
    }

    document.getElementById('centlat').value = pos.lat;
    document.getElementById('centlon').value = pos.lng;

    // Create a object LatLng with current possition
    var location = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

    var mapCanvas = document.getElementById('map');
    var mapOptions = {
        center: location,
        zoom: 10,
        panControl: false,
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
    }

    var map = new google.maps.Map(mapCanvas, mapOptions);

    // Define a marker
    var pin = new google.maps.Marker({
        position: pos,
        map: map,
        title: 'Central Point'
    });



    // Get new center lat lng at marker's possition change
    map.addListener('click', function(event){
        pin.setPosition(event.latLng);
        var new_pos = pin.getPosition();
        document.getElementById('centlat').value = new_pos.lat();
        document.getElementById('centlon').value = new_pos.lng();
        map.panTo(event.latLng);
    });

}
