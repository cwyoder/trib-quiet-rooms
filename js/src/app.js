import {loadElement} from './load-element.js';
import Drift from 'drift-zoom';
//Copyright (c) 2015-2018, Zebrafish Labs All rights reserved.
//https://github.com/imgix/drift


  
const   scrollMonitor = require('scrollmonitor'),
        pym = require('pym.js'),
        throttle = require('lodash.throttle');
  
function isMobile(){
    return window.innerWidth < 850 ? true : false;
}

var thumbs = document.querySelectorAll('.doc-thmb');
var details = document.querySelectorAll('.doc-detail');
  
// #########################################
// ######### DOMCONTENT LOADED #############
// #########################################
  
window.addEventListener('DOMContentLoaded', function(e){

    // First, start by loading the non-lazy charts/graphics by looking 
    // for the charts WITHOUT the lazy class.
    const nonLazyItems = [].slice.call(document.querySelectorAll('.chart:not(.chart--lazy)'));
    nonLazyItems.forEach(i => loadElement(i));

    // Also, let's lazyload the images and charts
    const lazyItems = [].slice.call(document.querySelectorAll('.image--lazy, .chart--lazy, .audio--lazy'));
    const lazyWatchers = lazyItems.map(el => {
  
        const lazyWatcher = scrollMonitor.create(el, {
            top: 500,
            bottom: 500
        });
  
        // This will let us load pictures/graphics/etc. without overwhelming 
        // the client. Loads are limited to one every 100ms.
        const throttledLazyLoad = throttle(function(){ loadElement(el) }, 100);
  
        lazyWatcher.enterViewport(function(){
            // First bring on the lazy content, but only once every 1/10 second
            throttledLazyLoad();
  
            // Now that the image is loaded, we can kill the watcher.
            lazyWatcher.destroy();
        });
        return lazyWatcher;
    });

    // Implementing document drift-zoom function
    for (var i = 0, len = thumbs.length; i < len; i++) {
        var thumb = thumbs[i];
        var detail = details[i];

        new Drift(thumb, {
            paneContainer: detail,
            inlinePane: true,
            inlineOffsetY: -75,
            containInline: false,
            hoverBoundingBox: true,
            injectBaseStyles: true,
            zoomFactor: 1.75
        });
    }

    //animating the lede
    animateLede();

    //Lazyloading videos

    var lazyVideos = [].slice.call(document.querySelectorAll("video.lazyvideo"));

    if ("IntersectionObserver" in window) {
        var lazyVideoObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(video) {
                if (video.isIntersecting) {
                    for (var source in video.target.children) {
                        var videoSource = video.target.children[source];
                        if (typeof videoSource.tagName === "string" && videoSource.tagName === "SOURCE") {
                            videoSource.src = videoSource.dataset.src;
                        }
                    }

                    video.target.load();
                    console.log("video loaded");
                    video.target.play();
                    video.target.classList.remove("lazyvideo");
                    lazyVideoObserver.unobserve(video.target);
                }
            });
        });

        lazyVideos.forEach(function(lazyVideo) {
            lazyVideoObserver.observe(lazyVideo);
        });
    }

});


// #########################################
// ########### DOCUMENT LOADED #############
// #########################################
  
window.addEventListener('load', function() {  
    // Now that the css is parsed and rendered, let's recalc all our waypoints
    scrollMonitor.recalculateLocations();
});


// #########################################
// ########### ANIMATING LEDE  #############
// #########################################

const pp = {
    // via @ashaw
    isMobile: ('ontouchstart' in document.documentElement && window.innerWidth <= 600),
    scrolledOnce: false
};


let getRandomInt = function(min, max, step) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random()*((max-min)/step))*step + min;
};
function animateLede() {
    let q = [
      {
        "log": "Why am I even in here? Let me go. Let me go.\”",
        "school": "Braun Educational Center",
        "date": "Nov. 2, 2017"
      },
      {
        "log": "I want my mom and dad. I love them.\”",
        "school": "Mattoon Community Unit School District",
        "date": "Dec. 11, 2017"
      },
      {
        "log": "You lock kids in here.\”",
        "school": "Bridges Learning Center",
        "date": "Nov. 29, 2017"
      },
      {
        "log": "I'm scared.\”",
        "school": "Chester-East Lincoln Elementary School",
        "date": "Sept. 22, 2017"
      },
      {
        "log": "Help, help, help me!\”",
        "school": "Wabash and Ohio Valley Special Education District",
        "date": "Sept. 19, 2018"
      },
      {
        "log": "\“Why? Why are you doing this to me?\”",
        "school": "Bridges Learning Center",
        "date": "Nov. 21, 2017"
      }
    ];
    let p = document.querySelector('#lede-quote'); // parent container
    let t = document.querySelector('header.full-bleed .titles'); // hed/dek
    let d = 2000; // delay in ms
    let r = 'show'; // reveal class
    var s = 0; // running count

    let setshowhide = function(i, s) {
        if (!pp.scrolledOnce) { // do nothing if user has already scrolled
            p.querySelector('.date').textContent = q[i].date;
            p.querySelector('.school').textContent = q[i].school;
            if (i < q.length-1) {
                p.querySelector('.log').textContent = q[i].log.substr(0);
                p.style.marginLeft = (pp.isMobile ? getRandomInt(2,10,4) : getRandomInt(6,26,4)) + 'rem';
                p.style.marginTop = (pp.isMobile ? getRandomInt(0,16,4) : getRandomInt(0,16,4)) + 'rem';
            } else {
                p.querySelector('.log').textContent = q[i].log;
                p.style.marginLeft = 'auto';
                p.style.marginTop = (pp.isMobile ? '8rem' : '7vw');
                p.classList.add('final');
            }
            p.classList.add(r);
            setTimeout(function(){
                if (i < q.length-1) {
                    // hide the quote
                    p.classList.remove(r);
                } else {
                    // show hed/dek
                    t.classList.add(r);
                    // then hide last quote
                    setTimeout(function(){p.classList.remove(r);}, d/3);
                }
            }, d);
        }
    };


    // load lede img asset in a dummy img elem, which caches in browser memory;
    var dummy = document.createElement('img');
    // bind animations to start on load callback
    dummy.onload = function() {
        dummy.remove(); // prevent memory leaks
        // start img animation
        document.querySelector('#lede-art').classList.add('panning');
        // start quotes animation
        var i;
        for (i = 0; i < q.length; i++) {
            setTimeout(setshowhide.bind(null, i, s), s);
            s += d*2;
        }
    };
    // use whichever responsive img was defined in css
    dummy.src = window.getComputedStyle(document.getElementById('lede-art'))
                      .backgroundImage
                      .slice(4, -1).replace(/['"]/g, "");


    // on scroll (once), show lede if it isn't already
    setTimeout(() => {
        window.addEventListener('scroll', (e) => {
            pp.scrolledOnce = true;
            t.classList.add(r);
        }, {once: true});
    }, 100);
}
