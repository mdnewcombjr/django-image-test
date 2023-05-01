var imageUploadPage = (function() {

	function imgUpload() {
		var $uploadCrop;

		var crOptions = {
			enableExif: true,
			viewport: {
				width: 400,
				height: 400,
				type: 'circle'
			},
			boundary: {
				width: 500,
				height: 500
			}
		};

		function readFile(input) {
			if (input.files && input.files[0]) {
				var reader = new FileReader();

				reader.onload = function(e) {
					$('.upload-image').addClass('ready');
					$uploadCrop.croppie('bind', {
						url: e.target.result
					}).then(function() {console.log('Croppie jQuery bind complete');});
				}

				reader.readAsDataURL(input.files[0]);
			} else {
				swal("Sorry, this website doesn't currently support your browser.");
			}
		}


		$uploadCrop = $('#upload-image').croppie(crOptions);
		
		$('#upload').on('change', function() {readFile(this); });
		$('#img-form').submit(function(ev) {
			var hparams = $uploadCrop.croppie('get');
			//Put the Croppie params on our hidden image element to upload
				var top_left_x = document.getElementById("top_left_x");
				var top_left_y = document.getElementById("top_left_y");
				var bottom_right_x = document.getElementById("bottom_right_x");
				var bottom_right_y = document.getElementById("bottom_right_y");

				var zoom = document.getElementById("zoom");
				
				top_left_x.value = hparams.points[0];
				top_left_y.value = hparams.points[1];
				bottom_right_x.value = hparams.points[2];
				bottom_right_y.value = hparams.points[3];

				zoom.value = hparams.zoom;

		})
	}

	function init() {
		imgUpload();
	}

	return {
		init: init
	};

})();


