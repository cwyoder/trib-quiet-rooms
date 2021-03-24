const pym = require('pym.js');
  
export function loadElement(el){
    // Function we use for loading graphics and lazyloading images.
    if (el.classList.contains('chart--lazy')){
        // if we're dealing with a graphic
        const   chartContainer = el.querySelector('.graphic-embed'),
                pymId = chartContainer.id,
                pymUrl = chartContainer.dataset.iframeUrl;
                new pym.Parent(pymId, pymUrl, {});
    } else if (el.classList.contains('audio--lazy')){
        const src = el.dataset.src;
        el.setAttribute('src', src);
    } else {
        // If we're dealing with an image
        const   elBox = el.getBoundingClientRect(),
                newDimension = elBox.width > elBox.height ? Math.round(elBox.width) : Math.round(elBox.height),
                fullResSrc = el.querySelector('img').getAttribute("src").replace("/10", `/${newDimension}`).replace(/’/g, ""); // Damn smart quotes are appearing again
        // console.log('lazy loading ', fullResSrc);
        el.querySelector('img').setAttribute('src', fullResSrc);
    }
}
