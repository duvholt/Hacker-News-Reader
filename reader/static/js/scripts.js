/*jshint jquery:true, browser:true*/

$(function () {
	HNReader.bindEvents();
	Comments.bindEvents();
});


var Alert = {
	alerts: $('.alerts'),
	levels: {
		PREFIX: 'alert-',
		DANGER: 'danger',
		SUCCESS: 'success',
		INFO: 'info'
	},
	show: function(message, level, delay) {
		level = this.levels.PREFIX + (level || this.levels.INFO);
		var alert = this.html(level, message);
		alert.appendTo(this.alerts);
		// Closing alert after "delay" ms
		if(delay) {
			setTimeout(function() {
				alert.alert('close');
			}, delay);
		}
	},
	html: function(alertLevel, message) {
		return $(
			'<div class="alert ' + alertLevel + ' fade in">' +
			'	<button type="button" class="close" data-dismiss="alert">&times;</button>' +
			'	' + message +
			'</div>');
	}
};


var Comments = {
	comments: $('.comments'),
	vote: function(id, dir) {
		$.get('/vote/' + id + '.json', {'dir': dir},
			function(data) {
				data.alerts.forEach(function(alert) {
					Alert.show(alert.message, alert.level);
				});
		}, 'json');
	},
	bindEvents: function() {
		// jQuery overwrites 'this' inside events
		var self = this;
		if(this.comments) {
			// Replace news.ycombinator links with internal
			this.comments.find('.content a[href*="item?id="]').each(function () {
				$(this).attr('href', $(this).attr('href').replace(/https?:\/\/news.ycombinator.com\/item\?id=(\d+)/, '/comments/$1/'));
			});
			// Selectable comments
			this.comments.find(".comment").click(function () {
				self.comments.find(".comment.selected").removeClass("selected");
				$(this).addClass("selected");
			});
			// Toggle show for comments
			this.comments.find('.hidetoggle').click(function(e) {
				e.preventDefault();
				var toggler = $(this);
				var comment = toggler.closest('.comment');
				var content = comment.find('.content');
				var children =	comment.siblings('.children');
				var hiddencontent = comment.find('.hiddencontent');
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
			});
		}
	}
};


var HNReader = {
	settings: {
		pollWidth: 767
	},
	bindEvents: function() {
		// Resize window checks
		$(window).resize($.debounce(100, this.resize));
		// Voting
		$(".vote a").click(function(e) {
			e.preventDefault();
			var found = $(this).attr('href').match(/\/vote\/(\d+)\?dir=(up|down)/);
			if(found) {
				Comments.vote(found[1], found[2]);
			}
		});
	},
	resize: function() {
		var width = $(window).width();
		if(width > this.pollWidth) {
			if($('.poll-collapse.collapse').length > 0) {
				var poll = $('.poll-collapse');
				poll.removeAttr('style');
				poll.removeClass('collapse in');
			}
		}
	}
};
