//Execute when initializing the page
$(document).ready(function () {
    var defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(51.58666, -9.70264),
    new google.maps.LatLng(55.13333, -6.04944));

    var input = document.getElementById('omg');
    var searchBox = new google.maps.places.SearchBox(input,{bounds: defaultBounds});

    searchBox.addListener('places_changed', function(){
        var places = searchBox.getPlaces();
        $("#lat").val(places[0].geometry.location.lat());
        $("#lng").val(places[0].geometry.location.lng());
        if (places.length == 0){
            return;
        }
    })
});



var selectedData = [];
var totalData = [];
var totalPage = 1;
var currentPage = 1;
var pageSize = 6;

var loadlistCount = 0;
var domain = window.location.host;
console.log(domain);

var school_ids = [];
var currentCity = "Cork";

var cityList = ['dublin', 'cork','galway', 'wicklow','limerick','antrim', 'armagh',
                'carlow', 'cavan', 'clare', 'derry', 'donegal', 'down',
                'fermanagh', 'kerry', 'kildare', 'kilkenny', 'laois', 'leitrim',
                'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly', 'Roscommon',
                'sligo', 'tipperary', 'tyrone', 'waterford', 'westmeath', 'wexford'];


function ajax_getSchoolDataByLatlng(pos){

    var c_place = {};


    navigator.geolocation.getCurrentPosition(function (position){
        pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

        $.getJSON("https://extreme-ip-lookup.com/json/",
              function(json) {
                   if (!json.city){
                       json.city = 'Dublin';
                   }

                   if (json.city == ""){
                       json.city = 'Dublin';
                   }

                   if (json.city) {
                       //console.log("current ip: " + json.query + "  current city: " + json.city);
                       ajax_distanceComputing(pos, json.city);
                   }

                   currentCity = json.city;
              }
         );

    } , function () {
        //handleLocationError(true, infoWindow, map.getCenter());
        $.getJSON("https://extreme-ip-lookup.com/json/",
              function(json) {

                   if (!json.city){
                       json.city = 'Dublin';
                   }

                   if (json.city == ""){
                       json.city = 'Dublin';
                   }

                   if (json.city) {
                       //console.log("current ip: " + json.query + "  current city: " + json.city);
                       ajax_distanceComputing(pos, json.city);
                   }

                   currentCity = json.city;
              }
         );

    });

}


function ajax_clickMapGetSchoolsByLatlng(pos){

    var city = "Ireland";

    var geocoder = new google.maps.Geocoder;
    geocoder.geocode({'location': pos}, function (results, status) {
        if (status === 'OK') {

            if (results[0]) {
                var addr = results[0].formatted_address;

                //console.log("ajax_clickMapGetSchoolsByLatlng geocoder.geocode addr:");
                //console.log(addr);

                $("#address").html(addr);

                for(var i=0; i < cityList.length; i++){
                    if(addr.toLowerCase().indexOf(cityList[i].toLowerCase()) >= 0){
                        city = cityList[i];
                        break;
                    }
                }
                //Note: The google map method is asynchronous,
                // so you must place the method inside, which will cause the execution order to be uncontrollable.
                ajax_distanceComputing(pos, city);

            } else {
                //console.log('geocoder.geocode No results found');
                ajax_distanceComputing(pos, city);

            }
        } else {
            //console.log('Geocoder failed due to: ' + status);
            ajax_distanceComputing(pos, city);

        }
    });


}


function ajax_distanceComputing(position, c_place){
    var city = 'Cork';
    if(c_place != ''){
        city = c_place;
    }


    $.ajax({
        type: 'POST',
        url: "http://" +  domain + '/distance_computing/'+ position.lat + ','+ position.lng + '/' + city,
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {

            totalData = data.result;
            //console.log("ajax_distanceComputing totalData:");
            //console.log(totalData);

            if(data.page_count > 0){
                totalPage = data.page_count;
            }

            $('#pagination').twbsPagination({
                totalPages: totalPage,
                visiblePages: 5,
                onPageClick: function (event, page) {
                    $("#loadgif").hide();
                    drawSchoolCardsByPage(page);
                }
            });

        }
    });
}



function drawSchoolCardsByPage(page){
    $("#loadgif").hide();
    var holder = $("#school-holder");
    if(holder){
        holder.empty();
    }

    //Here must be initialized to empty before each loop
    school_ids = [];
    selectedData = [];

    currentPage = page;

    for (var i = (currentPage-1)*pageSize; i < currentPage*pageSize; i++){
        if(i < totalData.length){
            selectedData.push(totalData[i]);
        }
    }

    //console.log("ajax_getSchoolDataByLatlng -- selectedData: ");
    //console.log(selectedData);

    $.each(selectedData, function(i,school){
        var img_src = "";
        img_src = 'https://s3-eu-west-1.amazonaws.com/bestchoiceimage/home/'+school.official_school_name+'.jpeg'

        var currentSchool = {}
        currentSchool.placeId = school.place_id;
        currentSchool.imgSrc = img_src;
        school_ids.push(currentSchool);

        holder.append(
            '<div class="product-item col-xs-6 col-md-4">' +
                '<a target="_blank" href=\"http:///school/'+ school.official_school_name+'/'+school.place_id+'\">' +
                    '<img style="height: 150px;"' +
                         'src="' + img_src + '" alt="sample school"/>' +
                '</a>'+

                '<h2 style="font-weight:bold"><a target="_blank" href=\"http://localhost:5000/school/'+ school.official_school_name+'/'+school.place_id+'\">' +
                                                 school.official_school_name+'</a><br>' +

                                                '<a class="'+ school.place_id + '" href="javascript:void(0)" name="'+school.official_school_name+'"' +
                                                'onclick="showLocation(this)"> <span style="color: black;font-size: 14px; font-style: italic">☞ Show Location </span> </a>' +
                '</h2>' +

                '<p><span style="font-weight:bold;color: black">Address : </span>' + school.address +
                '</p>' +
                '<p><span style="font-weight:bold;color: black">  distance from you : </span>' +
                    school.distance.toFixed(2) + ' km;' +
                '</p>' +

            '</div>'
        );
    });// end -- each

    try{
        addCustomMarkers(school_ids);
    }catch(err){
        if(loadlistCount == 0){
            window.location.reload();
        }else{
            //console.log("drawSchoolCardsByPage err: ");
            //console.log(err);
        }

    }

}


//Gets the province and city of the current location and sends it to the server side
function geocodeLocation(position) {
    var geocoder = new google.maps.Geocoder;
    geocoder.geocode({'location': position}, function (results, status) {
        if (status === 'OK') {
            if (results[0]) {
                var addr = results[0].formatted_address;
                var value = addr.split(",");

                count = value.length;
                country = value[count - 1];
                city = value[count - 2];
                area = value[count - 3];

                position['country'] = country;
                position['city'] = city;
                position['area'] = area;

                //console.log(position);


            } else {
                //console.log('No results found');
            }

        } else {
            //console.log('Geocoder failed due to: ' + status);
        }
    });
}



// GoogleMap intinazing elements
var markerlist = [];
var userMark;
var latlng ;
var map ;
var service ;

var school_ids = [];

function initMap() {
    try{
        latlng = new google.maps.LatLng(53.3498118, -6.2711979);
        map = new google.maps.Map(document.getElementById('mapholder'), {
            center: latlng,
            zoom: 12,
            gestureHandling: 'greedy'
        });
        service = new google.maps.places.PlacesService(map);

        // Try HTML5 geolocation.
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {

                latlng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            map.setCenter(latlng);

            userMark = new google.maps.Marker({
                position: latlng,
                map: map,
                title:"You are here!"
            });

            map.addListener('click', function(e){

                userMark.setMap(null);
                userMark = null;

                latlng.lat = e.latLng.lat();
                latlng.lng = e.latLng.lng();

                //map.setCenter(e.latLng);

                userMark = new google.maps.Marker({
                      position: latlng,
                      map: map
                });

                //console.log("initMap map.addListener latLng:")
                //console.log(latlng);

                $('#pagination').empty();
                $('#pagination').removeData("twbs-pagination");
                $('#pagination').unbind('page');

                var holder = $("#school-holder");
                holder.empty();
                $("#loadgif").show();

                //function here
                ajax_clickMapGetSchoolsByLatlng(latlng);


            });

            }, function () {
                //console.log("Error: The Geolocation service failed.");
            });

        } else {
            //if get user location failed

            // Browser doesn't support Geolocation
            //console.log("Error: Your browser doesn't support geolocation.");
        }
    }catch(err){
        //console.log(err);
        window.location.reload();
    }

}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
}

function addCustomMarkers(placeIds){
    /*if (markers.length == 6){
         for(var j=0; j < markers.length; j++){
            markers[j].setMap(null);
        }
    }*/
    for(var j=0; j < markerlist.length; j++){
        if (markerlist[j]){
            markerlist[j].setMap(null);
        }
    }
    markerlist = [];
    //console.log('placeIds: ');
    //console.log(placeIds);

    placeIds.map(function (school, i) {
        service.getDetails({
            placeId: school.placeId
        }, function (place, status) {
            //console.log(school.placeId);
            var marker;
            var infowindow = new google.maps.InfoWindow();
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                    //console.log("addMarkers: placeID "+i+"  "+school.placeId);
                    /*if (typeof(place.photos) == "undefined") {*/

                    var icon = {
                        url: school.imgSrc, // url
                        scaledSize: new google.maps.Size(30, 25), // scaled size
                        origin: new google.maps.Point(0,0), // origin
                        anchor: new google.maps.Point(0, 0) // anchor
                    };

                    marker = new google.maps.Marker({
                        map: map,
                        position: place.geometry.location,
                        title: place.name,
                        // label: labels[i % labels.length],
                        //icon: "../../static/img/search/not_found-small.png"
                        icon: icon
                    });

                    google.maps.event.addListener(marker, 'click', function () {
                        infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'><img class= 'img' src='" +
                            school.imgSrc + "' alt='Smiley face' width='80' height='60'><br><strong>" + place.name + '</strong><br>' +
                            '<strong>Place ID: </strong>' + place.place_id + '<br>' +
                            '<strong>Address: </strong>' + place.formatted_address + '</div>');
                        infowindow.open(map, this);
                    });

                    /*}*/
                   /* else {
                        marker = new google.maps.Marker({
                            map: map,
                            position: place.geometry.location,
                            title: place.name,
                            //label: labels[i % labels.length],
                            icon: place.photos[0].getUrl({
                                'maxWidth': 30,
                                'maxHeight': 30
                            })
                        });

                        google.maps.event.addListener(marker, 'click', function () {
                            infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'><img class= 'img' src='" + place.photos[0].getUrl({
                                    'maxWidth': 350,
                                    'maxHeight': 350
                                }) + "' alt='Smiley face' width='80'><br><strong>" + place.name + '</strong><br>' +
                                '<strong>Place ID: </strong>' + place.place_id + '<br>' +
                                '<strong>Address: </strong>' + place.formatted_address + '</div>');
                            infowindow.open(map, this);
                        });

                    }*/
            }

            markerlist.push(marker);

        });//--function (place, status) end


    });

    loadlistCount = loadlistCount + 1;
}


var currentMarker = null;

function showLocation(obj) {
    //var removeObj = document.getElementById(obj.getAttributeNode("class").value)
    //removeObj.parentNode.removeChild(removeObj);

    var infowindow = new google.maps.InfoWindow();
    var service = new google.maps.places.PlacesService(map);

    if (currentMarker != null) {
        currentMarker.setMap(null);
        currentMarker = null;
    }

    service.getDetails({
        placeId: obj.getAttributeNode("class").value
    }, function (place, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            map.setCenter(place.geometry.location);

            var marker;
            var imgsrc = 'https://s3-eu-west-1.amazonaws.com/bestchoiceimage/home/'+obj.getAttributeNode("name").value+'.jpeg';
            //if (typeof(place.photos) == "undefined") {
            var icon = {
                url: imgsrc, // url
                scaledSize: new google.maps.Size(40, 32), // scaled size
                origin: new google.maps.Point(0,0), // origin
                anchor: new google.maps.Point(0, 0) // anchor
            };

            marker = new google.maps.Marker({
                map: map,
                position: place.geometry.location,
                title: place.name,
                // label: labels[i % labels.length],
                //icon: "../../static/img/search/not_found-small.png"
                icon: icon
            });

            google.maps.event.addListener(marker, 'click', function () {
                infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'><img class= 'img' src='" +
                    imgsrc + "' alt='Smiley face' width='80' height='60'><br><strong>" + place.name + '</strong><br>' +
                    '<strong>Place ID: </strong>' + place.place_id + '<br>' +
                    '<strong>Address: </strong>' + place.formatted_address + '</div>');
                infowindow.open(map, this);
            });

            //}
            /*else {
                marker = new google.maps.Marker({
                    map: map,
                    position: place.geometry.location,
                    title: place.name,
                    //label: labels[i % labels.length],
                    icon: place.photos[0].getUrl({
                        'maxWidth': 40,
                        'maxHeight': 40
                    })
                });

                google.maps.event.addListener(marker, 'click', function () {
                    infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'><img class= 'img' src='" + place.photos[0].getUrl({
                            'maxWidth': 350,
                            'maxHeight': 350
                        }) + "' alt='Smiley face' width='80'><br><strong>" + place.name + '</strong><br>' +
                        '<strong>Place ID: </strong>' + place.place_id + '<br>' +
                        '<strong>Address: </strong>' + place.formatted_address + '</div>');
                    infowindow.open(map, this);
                });
            }*/


            currentMarker = marker;
        }
    });

}


// Automatically refresh once. If you have not logged in, create a new cookie: views are set to 1.
// Judge whether the views are the first browsing based on whether there is a value or not.
function autoRefresh() {
    if (getCookie("views") != 1) {
        document.cookie = "views = 1";
        if (getCookie("view") != 1)
            location.reload()
        else
            refresh();// If the browser does not allow cookies to be written, the url refresh method is used.
    } else {
        delCookie("views");
    }

}

function getCookie(name) {
    //Gets the value of the cookie with the specified name
    var arrStr = document.cookie.split("; ");
    for (var i = 0; i < arrStr.length; i++) {
        var temp = arrStr[i].split("=");
        if (temp[0] == name)
            return unescape(temp[1]);
    }
    return null;
}

function delCookie(name) {
    //To remove the cookie with the specified name, set its expiration time to a past time
    var date = new Date();
    date.setTime(date.getTime() - 10000);
    document.cookie = name + "=a; expires=" + date.toGMTString();
}

function refresh() {
    url = location.href; // Assign the address of the current page to the variable url
    // The split variable url delimiter is "#"
    if (url.indexOf("#") == -1) { // If there's no # after the url
        url += "#"; // add #
        self.location.replace(url); // refresh the page
    }
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
    setMapOnAll(null);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
    clearMarkers();
    markers = [];
}


// map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);