$(document).ready(function () {
    var defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(51.58666, -9.70264),
    new google.maps.LatLng(55.13333, -6.04944));

    var input = document.getElementById('search');
    var searchBox = new google.maps.places.SearchBox(input,{bounds: defaultBounds});

    searchBox.addListener('places_changed', function(){
        var places = searchBox.getPlaces();
    })

    var windowWidth = $(window).width();
    if(windowWidth < 640){
        $('#options-panel').collapse('hide')
    }

    if(windowWidth >= 640){
        var listholderHeight = $("#listholder").height();
        var optionHeight = $('#options-panel').height();
        if(optionHeight < listholderHeight){
            $('#options-panel').height(listholderHeight);
        }

    }

});



// GoogleMap intinazing elements
var markers = [];
var latlng ; // current user latlng
var userMark;
var map ;
var service ;
var domain = window.location.host;
var cityList = ['dublin', 'cork','galway', 'wicklow','limerick','antrim', 'armagh',
                'carlow', 'cavan', 'clare', 'derry', 'donegal', 'down',
                'fermanagh', 'kerry', 'kildare', 'kilkenny', 'laois', 'leitrim',
                'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly', 'Roscommon',
                'sligo', 'tipperary', 'tyrone', 'waterford', 'westmeath', 'wexford'];


function initMap(mylatlng) {

    latlng = new google.maps.LatLng(53.3498118, -6.2711979);
    map = new google.maps.Map(document.getElementById('map'), {
        center: latlng,
        zoom: 12,
        gestureHandling: 'greedy'
    });
    service = new google.maps.places.PlacesService(map);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {

            latlng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            if(mylatlng.lat){
                latlng = mylatlng;
            }

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

                //console.log("initMap map.addListener e.latLng:");
                //console.log(latlng);

                //function here
                geocodeProcessCityAndGetSchools(latlng);


            });

        }, function () {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    } else {
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

function geocodeProcessCityAndGetSchools(pos){
    var schools = {};
    var city = "Ireland";

    var geocoder = new google.maps.Geocoder;
    geocoder.geocode({'location': pos}, function (results, status) {
        if (status === 'OK') {

            if (results[0]) {
                var addr = results[0].formatted_address;

                //console.log("ajax_clickMapGetSchoolsByLatlng geocoder.geocode addr:");
                //console.log(addr);

                $("#keywords").html(addr);

                for(var i=0; i < cityList.length; i++){
                    if(addr.toLowerCase().indexOf(cityList[i].toLowerCase()) >= 0){
                        city = cityList[i];
                        break;
                    }
                }
                //Note: The google map method is asynchronous,
                // so you must place the method inside, which will cause the execution order to be uncontrollable.
                ajax_getSchoolsByLatLng(pos, city);
                //return schools;

            } else {
                //console.log('geocoder.geocode No results found');
                schools = ajax_getSchoolsByLatLng(pos, city);
                return schools;
            }
        } else {
            //console.log('Geocoder failed due to: ' + status);
            schools = ajax_getSchoolsByLatLng(pos, city);
            return schools;
        }
    });
}



function ajax_getSchoolsByLatLng(latlng,city){
    //console.log('your current hostname',window.location.hostname)

    $.ajax({
        type: 'POST',
        url: "http://" + domain + '/click_on_map/'+ latlng.lat + ','+ latlng.lng + '/' + city,
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {


            totalSchools = afterClickMap_initdata(data.result[0]);

            //console.log("ajax_getSchoolsByLatLng totalSchools:");
            //console.log(totalSchools);

            currentPage = 1;
            superLinkLocked(false);
            loadSchools(totalSchools, filters);

        }
    });

}


function afterClickMap_initdata(array) {
        var schools = [];

        for(var i=0; i < array.length; i++){

                var school = {};
                school.name = array[i].official_school_name ;
                school.img ="https://s3-eu-west-1.amazonaws.com/bestchoiceimage/home/"+ array[i].official_school_name +".jpeg";
                school.id =  array[i].official_school_name.replace(/[\ |\~|\`|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=|\||\\|\[|\]|\{|\}|\;|\:|\"|\'|\,|\<|\.|\>|\/|\?|\、|\，|\；|\。|\？|\！|\“|\”|\‘|\’|\：|\（|\）|\─|\…|\—|\·|\《|\》]/g, "");
                school.url = "http://" + domain + '/school/'+ array[i].official_school_name +'/' + array[i].place_id;
                school.address = array[i].address ;
                school.religion = array[i].religion;
                school.sex = array[i].school_gender;
                school.rank = array[i].rank;
                school.fee = array[i].fee;
                school.rate = array[i].Total_progression;
                school.boys = array[i].total_boy ;
                school.girls = array[i].total_girl;
                school.distance = array[i].distance;

                if (array[i].at_third_level){
                    school.third_level = array[i].at_third_level; // school.third_level
                }else{
                    school.third_level = -1;
                }

                if (array[i].at_university){
                    school.university_rate = array[i].at_university;// school.university_rate
                } else {
                    school.university_rate = -1;
                }

                school.placeid = array[i].place_id;

                schools.push(school);
        }

        //console.log("function afterClickMap_initdata totalSchools: ");
        //console.log(schools);
        return schools;
}


function ajax_getSchoolsByLatLng(latlng,city){

    $.ajax({
        type: 'POST',
        url: "http://" + domain + '/click_on_map/'+ latlng.lat + ','+ latlng.lng + '/' + city,
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {

            totalSchools = afterClickMap_initdata(data.result);

            //console.log("ajax_getSchoolsByLatLng totalSchools:");
            //console.log(totalSchools);

            loadSchools(totalSchools, filters);

        }
    });

}



function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
}

var documentHeight = 0;
function scrolling(jQueryObj,offsetTop) {

    var topPadding = 15;

    documentHeight = $(document).height();
    $(window).scroll(function () {
        var sideBarHeight = jQueryObj.height();
        if ($(window).scrollTop() > offsetTop) {
            var newPosition = ($(window).scrollTop() - offsetTop) + topPadding;
            var maxPosition = documentHeight - (sideBarHeight + 368);
            if (newPosition > maxPosition) {
                newPosition = maxPosition;
            }
            jQueryObj.stop().animate({
                marginTop: newPosition
            });
        } else {
            jQueryObj.stop().animate({
                marginTop: 0
            });
        }
        ;
        ////console.log("documentHeight: " + documentHeight + " ObjOffset.top: " + offsetTop + " window.scrollTop: " + $(window).scrollTop());
        ////console.log("sideBarHeight: " + sideBarHeight + " newPosition: " + newPosition + " maxPosition: " + maxPosition);
    });// window.scroll end

}

var currentMarker = null;
function showSelectedLocation(obj) {

    var infowindow = new google.maps.InfoWindow();

    if (currentMarker != null) {
        currentMarker.setMap(null);
        currentMarker = null;
    }

    service.getDetails({
        placeId: obj.getAttributeNode("name").value
    }, function (place, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            //console.log("placeID: " + obj.getAttributeNode("name").value);
            //console.log("Google return: place "+ place + "status "+ status);
            map.setCenter(place.geometry.location);
            map.setZoom(12);
            var marker;

            if (typeof(place.photos) == "undefined") {
                marker = new google.maps.Marker({
                    map: map,
                    position: place.geometry.location,
                    title: place.name,
                    //This controls the display size of the marker on the map.
                    icon: "../../static/img/search/not_found-big.png"
                });

                google.maps.event.addListener(marker, 'click', function () {
                    infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'>" +
                                                "<img class='img' src='../../static/img/search/not_found.jpg' alt='marker' width='80'><br>" +
                                                "<strong>" + place.name + '</strong><br>' +
                                                "<strong>Place ID: </strong>" + place.place_id + "<br>" +
                                                "<strong>Address: </strong>" + place.formatted_address +
                                          "</div>");
                    infowindow.open(map, this);
                });

            } else {
                marker = new google.maps.Marker({
                    map: map,
                    position: place.geometry.location,
                    title: place.name,
                    //This controls the display size of the marker on the map.
                    icon: place.photos[0].getUrl({
                        'maxWidth': 40,
                        'maxHeight': 40
                    })
                });

                google.maps.event.addListener(marker, 'click', function () {
                    infowindow.setContent(
                        "<div id='" + place.place_id + "' style='width: 220px'>" +
                            "<img class='img' src='" + place.photos[0].getUrl({ 'maxWidth': 350, 'maxHeight': 350 }) + "' alt='marker' width='80'><br>" +
                            "<strong>" + place.name + '</strong><br>' +
                            "<strong>Place ID: </strong>" + place.place_id + "<br>" +
                            "<strong>Address: </strong>" + place.formatted_address +
                        "</div>");
                    infowindow.open(map, this);
                });
            }

            currentMarker = marker;
        }
    });

}

/*function drawMarkersByplaceIds(){
    for(var i=0; i<markers.length; i++){
        markers[i].setMap(null);
    }
    markers = [];

    $(".placeId").each(function(i,e){
        //console.log(e);
        drawSingleMarker(e.name);
    });
}*/

function drawSingleMarker(placeid){
    service.getDetails(
        {
            placeId: placeid
        },
        function (place, status) {
            //console.log("current draw placeid: " + placeid);

            var marker;
            var infowindow = new google.maps.InfoWindow();

            if (status === google.maps.places.PlacesServiceStatus.OK) {

                if (typeof(place.photos) == "undefined") {
                    marker = new google.maps.Marker({
                        map: map,
                        position: place.geometry.location,
                        title: place.name,
                        //This controls the display size of the marker on the map.
                        icon: "../../static/img/search/not_found-small.png"
                    });

                    google.maps.event.addListener(marker, 'click', function () {
                        infowindow.setContent("<div id='" + place.place_id + "' style='width: 220px'>" +
                                                    "<img class='img' src='../../static/img/search/not_found.jpg' alt='marker' width='80'><br>" +
                                                    "<strong>" + place.name + '</strong><br>' +
                                                    "<strong>Place ID: </strong>" + place.place_id + "<br>" +
                                                    "<strong>Address: </strong>" + place.formatted_address +
                                              "</div>");
                        infowindow.open(map, this);
                    });

                } else {
                    marker = new google.maps.Marker({
                        map: map,
                        position: place.geometry.location,
                        title: place.name,
                        //This controls the display size of the marker on the map.
                        icon: place.photos[0].getUrl({
                            'maxWidth': 30,
                            'maxHeight': 30
                        })
                    });

                    google.maps.event.addListener(marker, 'click', function () {
                        infowindow.setContent(
                        "<div id='" + place.place_id + "' style='width: 220px'>" +
                            "<img class='img' src='" + place.photos[0].getUrl({ 'maxWidth': 350, 'maxHeight': 350 }) + "' alt='marker' width='80'><br>" +
                            "<strong>" + place.name + '</strong><br>' +
                            "<strong>Place ID: </strong>" + place.place_id + "<br>" +
                            "<strong>Address: </strong>" + place.formatted_address +
                        "</div>");
                    infowindow.open(map, this);
                    });

                }

                markers.push(marker);
            }else{
                //console.log("google Map failed: "+ placeid);
            }
        });
}

/*
* Quicksort, sort by a property, or by "get the function on which the sorting is based".
* @method Sort
* @static
* @param {array} arr Unsorted array
* @param {string | function}  Sorting based on prop
* @param {boolean} desc
* @return {array} Returns a new sorted array
*/
function Sort(arr, prop, desc){
    var props=[],
    ret=[],
    i=0,
    len=arr.length;
    if(typeof prop=='string') {
        for(; i<len; i++){
            var oI = arr[i];
            if(typeof(oI[prop]) == 'number'){
                (props[i] = new Number(oI && oI[prop] || ''))._obj = oI;
            } else if(typeof(oI[prop]) == 'string'){
                (props[i] = new String(oI && oI[prop] || ''))._obj = oI;
            } else{
                throw 'can only compare string or numeric attribute values';
            }
        }

        //console.log("quickSort Step1 props :");
        //console.log(props[i]);
    }
    else if(typeof prop=='function') {
        for(; i<len; i++){
            var oI = arr[i];
            if(typeof(oI[prop]) == 'number'){
                (props[i] = new Number(oI && oI[prop] || ''))._obj = oI;
            } else if(typeof(oI[prop]) == 'string'){
                (props[i] = new String(oI && oI[prop] || ''))._obj = oI;
            } else{
                throw 'can only compare string or numeric attribute values';
            }
        }
    }
    else {
        throw 'selected prop Parameter type error';
    }

    //props.sort();
    quickSort(props,0, props.length-1);
    //console.log("quickSort Step2 props  :");
    //console.log(props);

    for(i=0; i<len; i++) {
        ret[i] = props[i]._obj;
    }
    //console.log("quickSort Step3 ret  :");
    //console.log(ret);

    if(desc) ret.reverse();
    return ret;
};



function quickSort(arr, left, right){
   var len = arr.length,
   pivot,
   partitionIndex;


  if(left < right){
    pivot = right;
    partitionIndex = partition(arr, pivot, left, right);

   //sort left and right
   quickSort(arr, left, partitionIndex - 1);
   quickSort(arr, partitionIndex + 1, right);
  }
  return arr;
}

function partition(arr, pivot, left, right){
   var pivotValue = arr[pivot],
       partitionIndex = left;

   for(var i = left; i < right; i++){
    if(arr[i] < pivotValue){
      swap(arr, i, partitionIndex);
      partitionIndex++;
    }
  }
  swap(arr, right, partitionIndex);
  return partitionIndex;
}

function swap(arr, i, j){
   var temp = arr[i];
   arr[i] = arr[j];
   arr[j] = temp;
}