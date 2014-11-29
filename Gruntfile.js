module.exports = function(grunt) {

    var SCRIPTS = {
        'post': [ 'bower_components/MathJax/MathJax.js' ],
        'edit': [ 'bower_components/codemirror/lib/codemirror.js',
                  'bower_components/codemirror/mode/markdown/markdown.js' ],
        'main': [ 'bower_components/jquery/dist/jquery.js' ],
    }

    var CSS = {
        'main': [ 'src/css/style.css' ],
        'edit': [ 'bower_components/codemirror/lib/codemirror.css' ],
    }

    grunt.initConfig({
        clean: {
            static: ['bknet/static/js', 'bknet/static/css']
        },
        uglify: {
            scripts: {
                files: {
                    'bknet/static/js/main.min.js': [ 'bower_components/jquery/dist/jquery.js' ],
                    'bknet/static/js/edit.min.js': [
                        'src/js/editor.js',
                        'bower_components/codemirror/lib/codemirror.js',
                        'bower_components/codemirror/mode/markdown/markdown.js'
                    ],
                }
            }
        },
        cssmin: {
            styles: {
                files: {
                    'bknet/static/css/main.min.css': [ 'src/css/style.css' ],
                    'bknet/static/css/edit.min.css': [ 'bower_components/codemirror/lib/codemirror.css' ],
                }
            }
        },
        watch: {
            scripts: {
                files: 'src/js/*.js',
                tasks: ['uglify'],
            },
            css: {
                files: 'src/css/*.css',
                tasks: ['cssmin'],
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('all', ['clean', 'uglify', 'cssmin']);
};
