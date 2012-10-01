log = function(arg1) {
	console.log(arg1);
}
$(function () {
	$("a.comments, a.score").bind("mouseover", function() {
		$(this).closest("td").siblings("td").find("a.comments, a.score").addClass("onhover");
	}).bind("mouseout", function() {
		$(this).closest("td").siblings("td").find("a.comments, a.score").removeClass("onhover");
	});
	
	// $("a.score").each(function() {
	// 	var color = $.Color($(this).css("color")).saturation("0.5");
	// 	log(color);
	// 	$(this).css("color", color)
	// });
});