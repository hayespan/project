
module.exports = (grunt) ->

    coffeeify = require "coffeeify"
    stringify = require "stringify"

    src =
        coffee: "src/pc/src/coffee/*.coffee"
        less: "src/pc/src/less/*.less"

    dest =
        js: "static/pc/js"
        css: "static/pc/css"

    grunt.initConfig
        clean:
            bin:
                src: ["static/pc/css/*.css", "static/pc/js/*.js"]

        watch:
            compile:
                options:
                    livereload: true
                files: [src.coffee, src.less, "template/pc/*.html"]
                tasks: ["browserify", "less"]

        browserify:
            dev:
                options:
                  preBundleCB: (b)->
                    b.transform(coffeeify)
                    b.transform(stringify({extensions: [".hbs", ".html", ".tpl", ".txt"]}))
                expand: true
                flatten: true
                src: [src.coffee]
                dest: dest.js
                ext: ".js"

        less:
            compile:
                files: [{
                    expand: true,
                    cwd: "src/pc/src/less",
                    src: ["*.less", "!_*.less"],
                    dest: dest.css,
                    ext: ".css"
                }]


        uglify:
            build:
                files: [{
                    expand: true
                    cwd: dest.js
                    src: ["*.js"]
                    dest: dest.js
                    ext: ".js"
                }]

        cssmin:
            build:
                files: [{
                    expand: true
                    cwd: dest.css
                    src: ["*.css"]
                    dest: dest.css
                    ext: ".css"
                }]

        # copy:
            # assets:
                # src: "static/images"
                # dest: "dist/images"
            # css:
            #     options:
            #         process: (content, srcpath)->
            #             return content.replace /\/assets/g, "../assets"
            #     files:
            #         "dist/css/style.css": ["bin/css/style.css"]
            # html:
            #     options:
            #         process: (content, srcpath)->
            #             return content.replace(/\/assets/g, "./assets") \
            #                     .replace(/\/bin/g, ".").replace(/main.js/g, "main.min.js")
            #     files:
            #         "dist/index.html": ["src/index.html"]

        # imagemin:
            # dev:
                # files: [
                    # expand: true
                    # cwd: 'notminimgs'
                    # src: ['*.{png, jpg, gif}']
                    # dest: 'static/images/'
                # ]

    grunt.loadNpmTasks "grunt-contrib-copy"
    grunt.loadNpmTasks "grunt-contrib-clean"
    grunt.loadNpmTasks 'grunt-browserify'
    grunt.loadNpmTasks "grunt-contrib-less"
    grunt.loadNpmTasks "grunt-contrib-watch"
    grunt.loadNpmTasks "grunt-contrib-uglify"
    grunt.loadNpmTasks "grunt-contrib-cssmin"
    # grunt.loadNpmTasks "grunt-contrib-imagemin"

    grunt.registerTask "default",  ->
        grunt.task.run [
            "clean:bin"
            "browserify"
            "less"
            "watch"
        ]

    grunt.registerTask "build", ->
        grunt.task.run [
            "clean:bin"
            "browserify"
            "less"
            "uglify"
            "cssmin"
        ]

