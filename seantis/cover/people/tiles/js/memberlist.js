load_libraries(['jQuery'], function($) {
    "use strict";
    
    var handle_after_post = function(return_value, data_parent) {
        var tile_id = '#' + data_parent.find('#form-widgets-tile').val();
        if (tile_id == '#') { return; }

        $(tile_id).replaceWith(return_value.find(tile_id));

        setup_overlays();
    };

    var setup_overlays = function() {
        $('a.seantis-memberlist-edit').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: 'form',
            closeselector: '[name="form.buttons.cancel"]',
            noform: 'close',
            afterpost: handle_after_post
        });
    };

    $(document).ready(setup_overlays);
});