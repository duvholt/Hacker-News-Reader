module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            sass: {
                files: ['reader/static/sass/**/*.{scss,sass}', 'reader/static/sass/_partials/**/*.{scss,sass}'],
                tasks: ['sass:dist']
            },
            livereload: {
                files: ['*.html', '*.php', 'js/**/*.{js,json}', 'css/*.css','img/**/*.{png,jpg,jpeg,gif,webp,svg}'],
                options: {
                    livereload: true
                }
            }
        },
        sass: {
            dist: {
                files: {
                    'reader/static/css/styles.css': 'reader/static/sass/styles.scss'
                },
                options: {
                    sourcemap: 'true'
                }
            }
        }
    });
    grunt.registerTask('default', ['sass:dist', 'watch']);
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
};