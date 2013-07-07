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

	$("#SaveZentries").on('click', function() {
		$.jGrowl('Does Nothing yet');
	});
});
