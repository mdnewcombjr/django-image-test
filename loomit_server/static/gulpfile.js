var gulp = require('gulp');
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');
var pump = require('pump');
var cleanCSS = require('gulp-clean-css');
var concat = require('gulp-concat');
var inject = require('gulp-inject');
var argv = require('yargs').argv;
var del = require('del');
var flatmap = require('gulp-flatmap');
const path = require('path');

var production = !!argv.production;

//A helpful URL for integrating front-end with django:
//https://lincolnloop.com/blog/integrating-front-end-tools-your-django-project/

//DIRECTORY STRUCTURE
// 	- src
	// - js
	// - css
	// - html
	// - assets
	// - scss
	// - vendor
	//		- bootstrap
	//			...
	//
//	- dist
	// - js
	// - css
	// - templates (django/jinja templates)
	// - html (static html)
	// - assets
	//
//	- build (temporary build files)
	
var tasks = {
	clean: function() {
	    return del(
            [
                './build/**',
                './dist/**'
            ]);
	},

	//***********************************************
	//************* Javascript **********************
	//***********************************************
	
	finalize_js: function() 
	{
		return gulp.src('./build/js/{*,}/', {base: './build/js'})
		.pipe(flatmap(function(stream, dir) {
			return gulp.src(dir.path + '/*.js')
			.pipe(concat('app.js'))
			.pipe(gulp.dest('./dist/js/' + path.relative(dir.base, dir.path)))
		}));
	},
	
	move_js: function() 
	{
		gulp.src('./src/js/**/*.js', {base: './src/js'})
		.pipe(gulp.dest('./build/js'));
	},
	
	compress_js: function(cb) 
	{
		pump([
			gulp.src('./src/js/**/*.js', {base:'./src/js'}),
			uglify(),
			gulp.dest('./build/js')
			], cb);
	},
	
	vendor_js: function()
	{
		return gulp.src(
			['./src/vendor/jquery/jquery-3.0.0.min.js',
			'./src/vendor/bootstrap/dist/js/bootstrap.bundle.min.js',
			'./src/vendor/dropzone/min/dropzone.min.js',
			'./src/vendor/croppie/js/croppie.min.js'
			])
		.pipe(concat('vendors.js'))
		.pipe(gulp.dest('./dist/js/vendor'));
	},

	vendor_head_js: function()
	{
		return gulp.src(
			[
				'./src/vendor/fontawesome/svg-with-js/js/fontawesome.min.js',
				'./src/vendor/fontawesome/svg-with-js/js/fa-regular.min.js'
			])
		.pipe(concat('vendors-head.js'))
		.pipe(gulp.dest('./dist/js/vendor'));
	},
	
	//******************************************************
	//************** SASS and CSS Compilation **************
	//******************************************************
	compile_vendor_sass: function()
	{
		return gulp.src([
			'./src/vendor/bootstrap/scss/**/*.scss',
		], {base:'./src/vendor/bootstrap/scss'})
		.pipe(sass().on('error', sass.logError))
		.pipe(gulp.dest('./build/css/vendor'));
	},

	compile_sass: function()
	{
		return gulp.src([
			'./src/scss/**/*.scss'
		], {base:'./src/scss'})
		.pipe(sass().on('error', sass.logError))
		.pipe(gulp.dest('./build/css'));
	},

	move_vendor_css: function()
	{
		return gulp.src([
			'./src/vendor/dropzone/min/dropzone.min.css',
			'./src/vendor/croppie/css/croppie.css'
		])
		.pipe(concat('vendor-css.css'))
		.pipe(gulp.dest('./build/css'));
	},
	
	concat_css: function(cb)
	{
		return gulp.src('./build/css/{*,}/',{base:'./build/css'})
		.pipe(flatmap(function(stream, dir) {
			return gulp.src(dir.path + '/*.css')
			.pipe(cleanCSS({compatibility: '*'}))
			.pipe(concat('style.css'))
			.pipe(gulp.dest('./dist/css/' + path.relative(dir.base, dir.path)))
		}));
	},
	
	//************************************************
	//********** Assets Handling *********************
	//************************************************

	move_assets: function()
	{
		gulp.src('./src/assets/**.*')
		.pipe(gulp.dest('./dist/assets'));
	},
	
	//*********************************************
	//************* HTML **************************
	//*********************************************
	move_html: function()
	{

	    return gulp.src('./src/html/**/*.html', {base:'./src/html'})
        .pipe(gulp.dest('./dist/html'));

		////This will need changing to be compatible with different files being injected into various html files
		//var targets = gulp.src('./src/html/**/*.html');
		//var sources = gulp.src(['./dist/**/*.js', './dist/**/*.css'], {read: false});
		//var opts = {
		//	ignorePath: 'dist',
		//	addRootSlash: false
		//};

		//return targets.pipe(inject(sources, opts))
		//.pipe(gulp.dest('./dist/html'));
	}
	
};

//Custom Tasks
gulp.task('clean', tasks.clean);

gulp.task('move_js', tasks.move_js);
gulp.task('compress_js', tasks.compress_js);
gulp.task('prep_javascript', [ (production ? 'compress_js':'move_js') ])
gulp.task('js', ['prep_javascript'], tasks.finalize_js);

gulp.task('vendorjs', tasks.vendor_js);
gulp.task('vendor_headjs', tasks.vendor_head_js);

gulp.task('compile_sass', tasks.compile_sass);
gulp.task('compile_vendor_sass', tasks.compile_vendor_sass);
gulp.task('move_vendor_css', tasks.move_vendor_css);
gulp.task('concat_css',['compile_sass', 'compile_vendor_sass', 'move_vendor_css'], tasks.concat_css);

gulp.task('move_assets', tasks.move_assets);
gulp.task('move_html', tasks.move_html);



gulp.task('sass:watch', function() {
	gulp.watch([
		'./src/vendors/bootstrap/scss/**/*.scss',
		'./src/scss/**/*.scss'
		], ['concat_css']);
});

gulp.task('js:watch', function() {
	gulp.watch([
		'./src/js/**/*.js'
		], ['js']);
});

gulp.task('html:watch', function(){
	gulp.watch([
		'./src/html/**/*.html'
		], ['move_html']);
});


gulp.task('build', [
	'concat_css',
	'js',
    'vendorjs',
    'vendor_headjs',
	'move_assets',
    'move_html'
	]);

	
gulp.task('default', ['build']);
