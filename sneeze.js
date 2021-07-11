document.addEventListener("DOMContentLoaded", function(){
    var svg_container = document.getElementByClass("svg-container");
    var main_svg = document.getElementByClass("main-svg");
    parent = svg_container.parentNode;
    svg_container.style.width= parent.style.width;
    main_svg.style.width = parent.style.width;
    console.log("farts");
});
alert('farts')