function init(){
    var canvas = document.getElementById('myCanvas');
    var canvas1 = document.getElementById('myCanvas_1');
    var canvas2 = document.getElementById('myCanvas_2');
    var canvas3 = document.getElementById('myCanvas_3');
    $('#treesuccess').hide()
    $('#treefail').hide()
    $('#nopanoramas').hide()


    fitToContainer(canvas);
    fitToContainer(canvas1);
    fitToContainer(canvas2);
    fitToContainer(canvas3);


    try {
        var tarp = [data[0]['x'],data[0]['y']]
        var tarp1 = [data[1]['x'],data[1]['y']]
        var tarp2 = [data[2]['x'],data[2]['y']]
        var tarp3 =[data[3]['x'],data[3]['y']]

        var pano = data[0]
        var pano1 = data[1]
        var pano2 = data[2]
        var pano3 = data[3]
    }
    catch(err) {

        $('#nopanoramas').show()
        document.getElementById("savingbutton").disabled = true;

    }



    var num_x, num_y, tile_width, tile_height;
    var c_width = canvas.scrollWidth;
    var c_height = canvas.scrollHeight;
    context = canvas.getContext('2d');
    context1 = canvas1.getContext('2d');
    context2 = canvas2.getContext('2d');
    context3 = canvas3.getContext('2d');

    vals = get_tiles_num(pano['pano'], 2)
    num_x = vals[0];
    num_y = vals[1];
    tile_width = vals[2];
    tile_height = vals[3];

    var imgs = [];
    var imgs1 = [];
    var imgs2 = [];
    var imgs3 = [];


    /////////////////////////////////
    // Draw
    ////////////////////////////////


    var totwidth = (c_width / (Math.ceil(num_x * tile_width)));
    var totheight = (c_height / Math.ceil(num_y * tile_height));
    var res_tile_width = parseInt(totwidth * tile_width);
    var res_tile_height = parseInt(totheight * tile_height);

    var totwidth = (c_width / (Math.ceil(num_x * tile_width)));
    var totheight = (c_height / Math.ceil(num_y * tile_height));
    var res_tile_width = parseInt(totwidth * tile_width);
    var res_tile_height = parseInt(totheight * tile_height);
            
    var max_zoom = parseInt(pano['pano']['Location']['zoomLevels']);
    var down = parseInt(Math.pow(2, max_zoom - 2));
    var image_width = parseInt(pano['pano']['Data']['image_width']);
    var image_height = parseInt(pano['pano']['Data']['image_height']);
    var mau_x = c_width/(image_width);
    var mau_y = c_height/(image_height+192);
    var zoom = "2";



    var max_zoom = parseInt(pano['pano']['Location']['zoomLevels']);
    var down = parseInt(Math.pow(2, max_zoom - 2));
    var image_width = parseInt(pano['pano']['Data']['image_width']);
    var image_height = parseInt(pano['pano']['Data']['image_height']);

    var mau_x = c_width/(image_width);
    var mau_y = c_height/(image_height+192);
    var zoom = "2";

    var currentbbox = -1;

}
document.getElementById("treeid").innerHTML = "<span class='badge badge-success'>Object ID:</span> " + treeid[0]["id"]

function initcanvases(num_x,num_y){
    loaddrawimagebg(num_x, num_y, imgs, context, pano['pano']);
    loaddrawimagebg(num_x, num_y, imgs1, context1, pano1['pano']);
    loaddrawimagebg(num_x, num_y, imgs2, context2, pano2['pano']);
    loaddrawimagebg(num_x, num_y, imgs3, context3, pano3['pano']);
}

function fitToContainer(canvas) {
    // Make it visually fill the positioned parent
    canvas.style.width = '100%';
    canvas.style.height = '350px';
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

function remove_array_element(array, n) {
    var index = array.indexOf(n);
    if (index > -1) {
        array.splice(index, 1);
    }
    return array;
}

function get_tiles_num(pano, zoom) {
    var max_zoom = parseInt(pano['Location']['zoomLevels']);
    var down = parseInt(Math.pow(2, max_zoom - zoom));
    var image_width = parseInt(pano['Data']['image_width']) / down;
    var image_height = parseInt(pano['Data']['image_height']) / down;
    var tile_width = parseInt(pano['Data']['tile_width']);
    var tile_height = parseInt(pano['Data']['tile_height']);
    var num_x = parseInt(Math.ceil(image_width / parseFloat(tile_width)));
    var num_y = parseInt(Math.ceil(image_height / parseFloat(tile_height)));

    return [num_x, num_y, tile_width, tile_height];
}


function loaddrawimagebg(num_x, num_y, imgsarr, cont,panoinst) {
    var i = 0;
    var j = 0;
    var imgIndex = 0;
    // console.log(res_tile_width)
    // console.log(res_tile_height)
    // console.log(num_x)
    // console.log(num_y)
    for (var i = 0; i < num_x; i++) {
        for (var j = 0; j < num_y; j++) {
            link = "http://cbk0.google.com/cbk?output=tile&panoid=" + panoinst['Location']['panoId'] + "&zoom=" + zoom + "&x=" + i + "&y=" + j;
            imgsarr[imgIndex] = new Image();
            imgsarr[imgIndex].src = link;
            imgsarr[imgIndex].onload = (function() {
                cont.drawImage(imgsarr[imgIndex], parseInt(Math.ceil(i * res_tile_width)), parseInt(Math.ceil(j * res_tile_height)), parseInt(Math.ceil(res_tile_width)), parseInt(Math.ceil(res_tile_height)));
            }());
            imgIndex += 1;
        }
    }

}

function redrawall()
{
    initcanvases(num_x,num_y)

}

function main()
{
    initcanvases(num_x,num_y)

} 
$(window).load(function() {
    initcanvases(num_x,num_y)
    main();
})
init();
redrawall();

