module.exports = function(grunt) {

    var SCRIPTS = {
        'mathjax': [ 'src/js/mathjax.js' ],
        'edit': [ 'src/js/editor.js',
                  'bower_components/codemirror/lib/codemirror.js',
                  'bower_components/codemirror/mode/markdown/markdown.js' ],
        'main': [ 'bower_components/jquery/dist/jquery.js' ],
    }

    var CSS = {
        'main': [ 'build/css/style.css' ],
        'edit': [ 'bower_components/codemirror/lib/codemirror.css' ],
    }

    var STYLUS = {
        'main': [ 'src/css/reset.styl', 'src/css/style.styl' ],
    }

    grunt.initConfig({
        clean: {
            static: ['bknet/static/js', 'bknet/static/css']
        },
        uglify: {
            scripts: {
                files: {
                    'bknet/static/js/main.min.js': SCRIPTS.main,
                    'bknet/static/js/mathjax.min.js': SCRIPTS.mathjax,
                    'bknet/static/js/edit.min.js': SCRIPTS.edit,
                }
            }
        },
        cssmin: {
            styles: {
                files: {
                    'bknet/static/css/main.min.css': CSS.main,
                    'bknet/static/css/edit.min.css': CSS.edit,
                }
            }
        },
        stylus: {
            compile: {
                files: {
                    'build/css/style.css': STYLUS.main,
                }
            }
        },
        watch: {
            scripts: {
                files: 'src/js/*.js',
                tasks: ['uglify'],
            },
            css: {
                files: 'build/css/*.css',
                tasks: ['cssmin'],
            },
            stylus: {
                files: 'src/css/*.styl',
                tasks: ['stylus'],
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-stylus');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('all', ['clean', 'uglify', 'cssmin']);
};
