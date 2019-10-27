var ENDPOINT_URL = "https://100.98.2.198:8080/";

function initMap() {
    var location = {latitude: 47.497913, longitude: 19.040236};
    var infoWindow = new google.maps.InfoWindow;
    window.googleMap = new google.maps.Map(document.getElementById('map'), {
        zoom: 2,
        mapTypeId: 'terrain',
        zoom: 15,
          center: new google.maps.LatLng(location.latitude, location.longitude)
    });
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function (position) {
        initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
          infoWindow.setPosition(initialLocation);
          infoWindow.setContent('You are here');
          infoWindow.open(googleMap);
          googleMap.setCenter(initialLocation);
    });} 
}
function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
}

function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

$(document).ready(function() {
    // then to call it, plus stitch in '4' in the third group
    var guid = readCookie('fakeUserId');
    if (!guid) {
        guid = (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
        createCookie('fakeUserId', guid, 30);
    }
    $('#option-1').click(function(){
        $('#withdraw_input').val('1000');
    });
    $('#option-2').click(function(){
        $('#withdraw_input').val('2000');
    });
    $('#option-3').click(function(){
        $('#withdraw_input').val('5000');
    });
    $('#option-4').click(function(){
        $('#withdraw_input').val('10000');
    });
    var gps_location = {}; 
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
        //initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        gps_location.latitude = position.coords.latitude;
        gps_location.longitude = position.coords.longitude;
            });
    }

    function showQRCode(results){
        var qrcode = new QRCode(document.getElementById("qrcode"), {
            text: results.data._id,
            width: 256,
            height: 256,
            colorDark : "#000000",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H
        });
        $('#near_atm_list').find('button').css("display", "none");
        //$('#near_atm_list').html($('#qrcode').html());
    }

    function showATMButton(i, data) {
        var html_string = $("<input value=" + data._id + " type='hidden' id='atm_id_" + i + "'/>" +
            "<button id='button_address_" + i + "'>" + data.address + "<p>" + data.time_approx + " minutes</p></button>");
        $("#near_atm_list").append(html_string);
    }

    function displayATMList(results) {
        console.log(results);
        for (var i = 0; i < results.data.length; i++) {
            var coords = results.data[i];
            var latLng = new google.maps.LatLng(coords.location.coordinates[1], coords.location.coordinates[0]);

            if (i<=4) {
                var marker = new google.maps.Marker({
                    position: latLng,
                    map: googleMap,
                    icon: { url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" }
                });
            } else {
                var marker = new google.maps.Marker({
                    position: latLng,
                    map: googleMap
                });
            }

            if (results.data[i].time_approx) {
                showATMButton(i, results.data[i]);
            }
        }

        $("#near_atm_list").find('button').click(function() {
            var atm_id = $(this).prev('input').val();
            //var atm_id = $("#atm_id_0").val();
            $.ajax({
              url: "https://100.98.2.198:8080/qr/" + guid + "/",
              data: {atm_id: atm_id},
              type: "GET",
              dataType: "json"
            }).done(showQRCode);
        });

        $('#map').css("height","550px");
        $('#main_container').css("display","none");
    }

    $( "#find_nearest_atm" ).bind( "click", function() {
       var data = {
               "amount": document.getElementById('withdraw_input').value,
               "latitude": gps_location.latitude,
               "longitude": gps_location.longitude};
       $.ajax({
          url: "https://100.98.2.198:8080/atms/" + guid + "/",
          data: gps_location,
          type: "GET",
          dataType: "json"
        }).done(displayATMList);

       return false;
    });
    $( "#deposit_button" ).bind( "click", function() {
       var data = {
               "amount": 0,
               "latitude": gps_location.latitude,
               "longitude": gps_location.longitude,
               "deposit":true
           };
       $.ajax({
          url: "https://100.98.2.198:8080/atms/" + guid + "/",
          data: gps_location,
          type: "GET",
          dataType: "json"
        }).done(displayATMList);

       return false;
    });
});

jQuery(".toggle").on("click", function() {
  jQuery(".container")
    .stop()
    .addClass("active");
});

jQuery(".close").on("click", function() {
  jQuery(".container")
    .stop()
    .removeClass("active");
});