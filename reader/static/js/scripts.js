/*jshint jquery:true, devel:true, browser:true*/

$(function () {
	'use strict';
	// Hover hack for frontpage
	$('a.comments, a.score').bind('mouseover', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').addClass('onhover');
	}).bind('mouseout', function() {
		$(this).closest('td').siblings('td').find('a.comments, a.score').removeClass('onhover');
	});
	// Shorten time format on frontpage for smaller screens
	$(window).resize($.debounce(100, resized));
	time_format();
	function resized() {
		time_format();
		var width = $(window).width();
		if(width > 767) {
			if($('.sidebar-collapse.collapse').length > 0) {
				var sidebar = $('.sidebar-collapse');
				sidebar.removeAttr('style');
				sidebar.removeClass('collapse in');
			}
			if($('.poll-collapse.collapse').length > 0) {
				var poll = $('.poll-collapse');
				poll.removeAttr('style');
				poll.removeClass('collapse in');
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

	function vote(id, dir) {
		$.get('/vote/' + id + '.json', {'dir': dir}, function(data) {
			data['alerts'].forEach(function(alert) {
				showAlert(alert['message'], alert['level'])
			});
		}, 'json');
	}

	var showAlert = function(message, level, delay) {
		/* Allowed levels: error, success, info and default (empty) */
		if(level) {
			level = 'alert-' + level;
		}
		else {
			level = 'alert-info';
		}
		var alert = $(
			'<div class="alert ' + level + ' fade in">' +
			'	<button type="button" class="close" data-dismiss="alert">&times;</button>' +
			'	' + message +
			'</div>');
		alert.appendTo($('.alerts'));
		if(delay) {
			setTimeout(function() {
				alert.alert('close');
			}, delay);
		}
	};
	// Toggle show for comments
	$('.comments .hidetoggle').click(function (e) {
		var toggler = $(this);
		var content = $(this).siblings('.content');
		var children = $(this).parent().siblings('.children');
		var hiddencontent = content.siblings('.hiddencontent');
		if(toggler.data("state") === 'hidden') {
			toggler.html('[-]');
			toggler.data("state", 'visible');
			content.show();
			if (hiddencontent) {
				hiddencontent.hide();
			}
			children.show();
		}
		else {
			toggler.html('[+]');
			toggler.data("state", 'hidden');
			content.hide();
			if (hiddencontent.length > 0) {
				hiddencontent.show();
			}
			else {
				hiddencontent = content.after(
					'<div class="hiddencontent">' +
					'<i>' + $('.comment', content.closest('li')).length + ' comment(s) hidden</i>' +
					'</div>');
			}
			children.hide();
		}
		e.preventDefault();
	});
	// Replace news.ycombinator links with internal
	$('.comments .content a[href*="item?id="]').each(function () {
		$(this).attr('href', $(this).attr('href').replace(/https?:\/\/news.ycombinator.com\/item\?id=(\d+)/, '/comments/$1'));
	});
	// Selectable comments
	$(".comments .comment").click(function () {
		$(".comments .comment").removeClass("selected");
		$(this).addClass("selected");
	});
	$(".vote a").click(function(e) {
		e.preventDefault();
		var found = $(this).attr('href').match(/\/vote\/(\d+)\?dir=(up|down)/);
		vote(found[1], found[2]);
	});
});
