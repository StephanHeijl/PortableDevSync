/* JSLint settings */
/*jslint browser: true*/
/*global $, jQuery*/

$(function () {
	"use strict";
	
	/* Toggles the classes of menu options that require a selection */
	$("#content").on("change", "input:checkbox", function () {
		if ($("#content input:checkbox:checked").length > 0) {
			var selectionRequired = $("li.requires-selection");
			selectionRequired.removeClass("requires-selection");
			selectionRequired.addClass("selection-available");
		} else {
			var selectionAvailable = $("li.selection-available");
			selectionAvailable.removeClass("selection-available");
			selectionAvailable.addClass("requires-selection");
		}
	});
	
	/* Toggle checkbox when clicking on the parent row */
	$("#content").on("click", "tr", function () {
		var checkBoxes = $(this).find("input:checkbox");
		checkBoxes.prop("checked", !checkBoxes.prop("checked"));
		checkBoxes.change(); // Triggers checkbox change event
	});
	
	/* Load all the monitors */
	$.getJSON("monitors.config", function (monitors) {
		monitors.each(function() {
			row = $("<tr>")
			this.
		});
	});
	
});