log = function(arg1) {
	console.log(arg1);
}
$(function () {
	$("a.comments, a.score").bind("mouseover", function() {
		$(this).closest("td").siblings("td").find("a.comments, a.score").addClass("onhover");
	}).bind("mouseout", function() {
		$(this).closest("td").siblings("td").find("a.comments, a.score").removeClass("onhover");
	});
});