module.exports = function(grunt) {
  var config = {};

 config.svgstore = {
    options: {
      cleanup:true,
      cleanupdefs:true
    },
    min: {
      // Target-specific file lists and/or options go here. 
      src:['img/svgs/**/*.svg'],
      dest:'img/base-sprite.svg'
    },
  };

  grunt.initConfig(config);

  grunt.loadNpmTasks('grunt-svgstore');
  var defaultTasks = [];
  defaultTasks.push('svgstore');

  grunt.registerTask('default', defaultTasks);
};
