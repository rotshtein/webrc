$(document).ready(function () {
	$('#form-recorder').submit(function (e) {
		e.preventDefault();
	});

	$('#form-play').submit(function (e) {
		e.preventDefault();
	});

	this.getFileList = function () {
		$.ajax('/file_list').done(function (d) {
			filesBox = document.getElementById('files');
			$(d).each(function () {
				opt = document.createElement('option');
				opt.value = this;
				opt.innerHTML = this;
				filesBox.add(opt);
			});
		});
	};

	this.myOnSubmit = function (formId, validityCallback, extras) {
		console.log('my_submit');
		console.log(extras);
		console.log(data);
		if (!document.getElementById(formId).checkValidity()) {
			return;
		}
		var data = Object.assign({}, extras);
		$.each($('#' + formId).serializeArray(), function() {
			data[this.name] = this.value;
		});
		if (validityCallback && !validityCallback(data)) {
			return;
		}
		console.log(data);
		req = $.ajax({
			url: '/work',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify(data),
			processData: false,
			dataType: 'text',
			xhrFields: {
				// Copied from https://gist.github.com/sohelrana820/63f029d3aa12936afbc50eb785c496c0
				onprogress: function(e) {
					var lines = e.currentTarget.response.split(/\n/);
					$('#statusbar').html(lines[lines.length - 2]);
				},
			},
		});
		return;
	};

	this.submit1 = function (mode) {
		document.myOnSubmit('form-recorder',
			function (d) {
				return true;
			},
			{
				freq_center: $('#center').hasClass('active'),
				agc_auto: $('#automac_agc').hasClass('active'),
				mode: mode,
				play: false
			}
		);
	};

	this.submit2 = function () {
		document.myOnSubmit('form-play',
		function (d) {
				return true;
			},
			{
				freq_center: $('#play_center').hasClass('active'),
				play: true,
			});
	};

	this.select_center = function() {
		document.getElementById('center_freq').setAttribute('required',1);
		document.getElementById('bandwidth').setAttribute('required',1);
		document.getElementById('low_freq').removeAttribute('required');
		document.getElementById('high_freq').removeAttribute('required');
	};

	this.select_high_low = function()  {
		document.getElementById('center_freq').removeAttribute('required');
		document.getElementById('bandwidth').removeAttribute('required');
		document.getElementById('low_freq').setAttribute('required',1);
		document.getElementById('high_freq').setAttribute('required',1);
	};
	
	this.play_select_center = function() {
		document.getElementById('play_center_freq').setAttribute('required',1);
		document.getElementById('play_bandwidth').setAttribute('required',1);
		document.getElementById('play_low_freq').removeAttribute('required');
		document.getElementById('play_high_freq').removeAttribute('required');
	};

	this.play_select_high_low = function()  {
		document.getElementById('play_center_freq').removeAttribute('required');
		document.getElementById('play_bandwidth').removeAttribute('required');
		document.getElementById('play_low_freq').setAttribute('required',1);
		document.getElementById('play_high_freq').setAttribute('required',1);
	};
	
	this.select_agc = function() {
		if (!$('#automac_agc').hasClass('active')) {
			document.getElementById('agc').removeAttribute('required');
		}else{
			document.getElementById('agc').setAttribute('required',1);
		}
	}

	this.getFileList();

});