log = function(arg1) {
	console.log(arg1);
}
$(function () {
	$('a.comments, a.score').bind('mouseover', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').addClass('onhover');
	}).bind('mouseout', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').removeClass('onhover');
	});
	$(window).resize($.debounce(300, time_format));
	time_format();
	function time_format() {
		width = $(window).width();
		$('table#stories').find('tr').find('td:last').find('time').each(function() {
			if(width > 767) {
				if($(this).data('time_old')) {
					$(this).html($(this).data('time_old'))
					$(this).data('time_old', null)
				}
			}
			else {
				if(!$(this).data('time_old')) {	
					$(this).data('time_old', $(this).html())
					$(this).html($(this).html().replace(/(\d+) minutes?/g, '$1m'));
					$(this).html($(this).html().replace(/(\d+) hours?/g, '$1h'));
					$(this).html($(this).html().replace(/(\d+) days?/g, '$1d'));
					$(this).html($(this).html().replace(/(\d+) weeks?/g, '$1w'));
				}
			}
		});
	}
});