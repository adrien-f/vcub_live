
class Vcub
    constructor: () ->
        Handlebars.registerHelper 'lowercase', (str) ->
            str.toLowerCase()
        @stations = window.stations
        @create_map()
        @populate_map()
        $('div#stations_list').html(Handlebars.templates['stations_list_template.hbs']({stations: @stations}))
        $(document).on('keyup', 'input[name=search]', @filter)
        $(document).on('click', 'a.station', @to_map)

    create_map: () ->
        @map = L.map('map').setView([44.837856, -0.578842], 13)
        @map.locate({setView: true, maxZoom: 16})
        @map.on 'locationfound', (e) =>
            radius = e.accuracy / 2
            L.marker(e.latlng).addTo(@map).bindPopup("Vous vous trouvez à" + radius + " metres de ce point");
            L.circle(e.latlng, radius).addTo(@map);
        @osm = L.tileLayer 'http://{s}.tile.cloudmade.com/d4eab6cbbfa24ccf98980fb8b04ca7a8/1930/256/{z}/{x}/{y}.png', 
            {
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
                maxZoom: 18
            }
        @map.addLayer @osm

    populate_map: () ->
        for station in @stations
            popup = Handlebars.templates['popup_template.hbs']({nom: station.data.NOM, nbvelos: station.data.nbvelos, nbplaces: station.data.nbplaces})
            marker = new L.marker(station.coordinates, {
                icon: new L.DivIcon {
                    className: 'leaflet-div-icon ' + station.data['class']
                    iconSize: new L.Point 20, 20
                }
            }).bindPopup(popup)
            marker['_leaflet_id'] = station.data['GID']
            marker.addTo(@map)

    filter: (e) ->
        $el = $('input[name=search]')
        $list = $('div#stations_list')
        filter = $el.val().toLowerCase()
        if filter == ''
            $('div#stations_list div').show()
        else
            $('div#stations_list div').hide()
            $('div#stations_list').find('div[data-name*="' + filter + '"]').each((i, e) ->
                $(e).css('display', 'block')
            )

    to_map: (e) =>
        gid = $(e.currentTarget).data('gid')
        @map.panTo(@map._layers[gid]._latlng)
        @map._layers[gid].openPopup()

$(document).on 'ready', (e) ->
    window.vcub = new Vcub()