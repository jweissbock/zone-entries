$(document).ready(function() {
	// add new row to the zone entry table
	$(document).on("click", "#NewRow", function(e) {
		// clone bottom row
		var newRow = $("#zentries tr:last").html();
		newRow = '<tr>'+newRow+'</tr>';
		// remove all buttons
		$("#NewRow").remove();
		// append clone
		$("#zentries").append(newRow);
	});

	// remove a table row
	$(document).on("click", ".DeleteCell", function(e) {
		// clone last row just in case
		var newRow = $("#zentries tr:last").html();
		newRow = '<tr>'+newRow+'</tr>';
		// delete this row
		newDelete = $("#NewRow").parent().html();
		$(this).parent().remove();
		// adds 'new button' to last row
		$("#zentries tr:last .NewCell").html(newDelete);
		// count rows, if zero, add
		if ($("#zentries tr").length <= 1) {
			$("#zentries").append(newRow);
		}
	});

	(function($) {
	    $.extend({
	        toDictionary: function(query) {
	            var parms = {};
	            var items = query.split("&"); // split
	            for (var i = 0; i < items.length; i++) {
	                var values = items[i].split("=");
	                var key = decodeURIComponent(values.shift());
	                var value = values.join("=")
	                parms[key] = decodeURIComponent(value);
	            }
	            return (parms);
	        }
	    })
	})(jQuery);
    
	(function($) {
	    $.fn.serializeFormJSON = function() {
	        var o = [];
	        $(this).find('tr').each(function() {
	            var elements = $(this).find('input, textarea, select')
	            if (elements.size() > 0) {
	                var serialized = $(this).find('input, textarea, select').serialize();
	                var item = $.toDictionary(serialized );
	                o.push(item);
	            }
	        });
	        return o;
	    };
	})(jQuery);

	$("#SaveZentries").on('click', function() {
		$.jGrowl('Trying to save...');

		// save gameid
		gameidyear = $("#gameidyear").val();
		gameid = $("#gameid").val();
		team = $("#team").val();

		// get table
		var rawData = $('#addZE').serializeFormJSON();
    	var formData = JSON.stringify(rawData);

    	// send by ajax, see what the response is
    	$.post("/saveze", {
    		gameidyear: gameidyear,
    		gameid: gameid,
    		team: team,
    		table: formData
    	}, function(data) {
    		if (data.success == false) {
    			$.jGrowl(data.message);
    			// clear all backgrounds
    			$('#zentries tr').css('background-color', '');
    			if (data.row > -1) {
    				// set this one
    				data.row += 1;
    				$('#zentries tr:nth-child('+data.row+')').css('background-color', '#f0d6d6');
    			}
    		} else {
    			$.jGrowl(data.message);
    		}
    	}, "json");
	});
});
