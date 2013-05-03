/*jshint jquery:true, devel:true, browser:true*/

var log = function(arg1) {
	'use strict';
	console.log(arg1);
};
$(function () {
	'use strict';
	$('a.comments, a.score').bind('mouseover', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').addClass('onhover');
	}).bind('mouseout', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').removeClass('onhover');
	});
	$(window).resize($.debounce(100, resized));
	time_format();
	function resized() {
		time_format();
		var width = $(window).width();
		if(width > 767) {
			if($('.sidebar-collapse.collapse').length > 0) {
				$('.sidebar-collapse').removeAttr('style');
				$('.sidebar-collapse').removeClass('collapse in');
			}
			if($('.poll-collapse.collapse').length > 0) {
				$('.poll-collapse').removeAttr('style');
				$('.poll-collapse').removeClass('collapse in');
			}
		}
	}
	function time_format() {
		$('table#stories').find('tr').find('td:last').find('time').each(function() {
			var width = $(window).width();
			if(width > 767) {
				if($(this).data('time_old')) {
					$(this).html($(this).data('time_old'));
					$(this).data('time_old', null);
				}
			}
			else {
				if(!$(this).data('time_old')) {
					$(this).data('time_old', $(this).html());
					$(this).html($(this).html().replace(/(\d+) minutes?/g, '$1m'));
					$(this).html($(this).html().replace(/(\d+) hours?/g, '$1h'));
					$(this).html($(this).html().replace(/(\d+) days?/g, '$1d'));
					$(this).html($(this).html().replace(/(\d+) weeks?/g, '$1w'));
				}
			}
		});
	}
	$('.comments .hidetoggle').click(function (e) {
		var toggler = $(this);
		var content = $(this).siblings('.content');
		var children = $(this).parent().siblings('.children');
		if(toggler.data("state") === 'hidden') {
			toggler.html('[-]');
			toggler.data("state", 'visible');
			content.show();
			children.show();
		}
		else {
			toggler.html('[+]');
			toggler.data("state", 'hidden');
			content.hide();
			children.hide();
		}
		e.preventDefault();
	});
	$('.comments .content a[href*="item?id="]').each(function () {
		$(this).attr('href', $(this).attr('href').replace(/https?:\/\/news.ycombinator.com\/item\?id=(\d+)/, '/comments/$1'));
	});
	$(".comments .comment").click(function () {
		$(".comments .comment").removeClass("selected");
		$(this).addClass("selected");
	});
});
