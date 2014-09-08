// Function to run at page load
$(document).ready(function() {
  function initialize_map() {
    // Initialize map inside #map div element
    var map = new GMap2(document.getElementById('map'));
    map.setUIToDefault();

    // Set up points for Seattle nodes
    var markers = [];
    $("ul#coords li").each(function(i) {
      var latitude = $(this).children(".latitude").text();
      var longitude = $(this).children(".longitude").text();
      if(!latitude && !longitude){
        var point = new GLatLng(85,0);
        marker = new GMarker(point);
        map.addOverlay(marker);
        marker.setImage("map_marker_icon_blue.png");
        map.setCenter(point, 2);
        markers[i] = marker;
      }else{
        var point = new GLatLng(latitude, longitude);
        marker = new GMarker(point);
        map.addOverlay(marker);
        marker.setImage("map_marker_icon.png");
        map.setCenter(point, 2);
        markers[i] = marker;
      }
    });

    // Pan to point when clicked
    $(markers).each(function(i, marker) {
      GEvent.addListener(marker, "click", function(){
        displayPoint(marker, i);
      });
    });
    return map;
  }

  // Whenever a marker is clicked, pan to it and move/populate the tooltip div
  function displayPoint(marker, i) {
    map.panTo(marker.getPoint());
    var markerOffset = map.fromLatLngToDivPixel(marker.getPoint());

    // Get node information from adjacency table
    var nodeip = $("#node" + i).children(".nodeip").text();
    var nodelocation = $("#node" + i).children(".locationname").text();
    var nodelat = $("#node" + i).children(".latitude").text();
    var nodelong = $("#node" + i).children(".longitude").text();

    // Populate #message div with node information
    $("#message").empty().append("<strong>Node IP:</strong> " + nodeip + "<br /><strong>Location:</strong> " + nodelocation + "<br /><strong>Lat/Long:</strong> " + nodelat + "/" + nodelong + "<br /><a href='#'>Select this node</a>");

    // If a node bas been selected to base latencies on...
    if (typeof(selected_node) != "undefined") {
      // Remove any existing lines
      if (typeof(line) != "undefined") {
        map.removeOverlay(line);        
      }

      // Draw new line between selected node and clicked node
      line = new GPolyline([selected_marker.getLatLng(), marker.getLatLng()]);
      map.addOverlay(line);

      // Populate #message div with latency info
      var latency = $("td." + selected_node + "_" + i).text();
      $("#message a").before("<strong>Latency to " + selected_location + ":</strong> " + latency + ((latency != 'N/A') ? " s" : "") + "<br />");
    }
    
    // Function to select node as latency hub on click
    $("#message").children("a").click(function() {
      if (typeof(selected_marker) != "undefined") {
          selected_marker.setImage("map_marker_icon.png");
      }
      selected_marker = marker;
      selected_node = i;
      selected_location = nodelocation.split(",")[0];
      marker.setImage("map_marker_sel_icon.png");
    });

    // Finally, display the #message div tooltip
    $("#message").show().css({ top:markerOffset.y, left:markerOffset.x });
  }


  var map = initialize_map();
  $("#message").appendTo(map.getPane(G_MAP_FLOAT_SHADOW_PANE));
  var selected_node;
  var selected_marker;
  var selected_location;
  var line;
});
