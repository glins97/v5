const COLOR_PRIMARY = '#9c27b066';
const COLOR_INFO = '#00bcd466';
const COLOR_SUCCESS = '#4caf5066';
const COLOR_DANGER = '#f48b3666';
const COLOR_WARNING = '#ffee0066';
const COLOR_GREY = '#33333366';
var color = "#00000000";

var objects = [];

var mode = "";
var pushes = [];
var pops = [];
var drawables = [];
var comments = [];
var images = [];
var competencies = {
    'comments': {},
    'grades': {},
};

var lastImage = undefined;
var canvas = undefined;

var canvasWidth = 0;
var canvasHeight = 0;
var rect_x0 = 0;
var rect_x1 = 0;
var rect_y0 = 0;
var rect_y1 = 0;
var countErrorsC1 = 0;
var countErrorsC2 = 0;
var countErrorsC3 = 0;
var countErrorsC4 = 0;
var countErrorsC5 = 0;
var PEN_SIZE = 34;
var RECT_PEN_CORRECTION = 8;
var savedImagePos = undefined;
var nullified = false;
var username = '';
var modalVisible = false;

function setUsername(val) {
    username = val;
}

function openNav() {
    document.getElementById("mySidebar").style.width = "500px";
    document.getElementById("src").style.marginLeft = "250px";
    document.getElementById("canvas").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("src").style.marginLeft= "0";
    document.getElementById("canvas").style.marginLeft= "0";
}

function getScroll() {
    if (window.pageYOffset != undefined) {
        return [pageXOffset, pageYOffset];
    } else {
        var sx, sy, d = document,
        r = d.documentElement,
        b = d.body;
        sx = r.scrollLeft || b.scrollLeft || 0;
        sy = r.scrollTop || b.scrollTop || 0;
        return [sx, sy];
    }
}

function updateCanvas() {
    var img = document.getElementById("src");
    canvas = document.getElementById("canvas");
    canvas.style.position = "absolute";
    canvas.style.left = img.offsetLeft + "px";
    canvas.style.top = img.offsetTop + "px";
    canvas.width = img.width;
    canvas.height = img.height;
    canvasWidth = canvas.width;
    canvasHeight = canvas.height;
    PEN_SIZE = img.height * 30 / 2000
}

function setColor(newColor) {
    color = newColor;
}

function setMode(newMode) {
    mode = newMode;
}

function drawMarker(x0, y0, x1, y1, color, mode) {
    console.log('drawing marker', x0, y0, x1, y1, color, mode);
    var ctx = canvas.getContext("2d");
    ctx.beginPath();
    if (mode == "LINE") {
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.moveTo(x0 * canvasWidth, y0 * canvasHeight);
        ctx.lineTo(x1 * canvasWidth, y1 * canvasHeight);
    }
    else if (mode == "RECT"){
        ctx.lineWidth = PEN_SIZE / RECT_PEN_CORRECTION;
        ctx.rect(x0 * canvasWidth, y0 * canvasHeight, x1 * canvasWidth - x0 * canvasWidth, y1 * canvasHeight - y0 * canvasHeight);
        ctx.fillStyle = "#00000000";
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.stroke();
    }
    ctx.stroke();
}
   
function drawMarkers() {
    for (var i = 0; i < objects.length; i++) {
        var obj = objects[i];
        if (obj['mode'] != 'LINE' && obj['mode'] != 'RECT') continue;
        drawMarker(obj['attributes']['x0'], obj['attributes']['y0'], obj['attributes']['x1'], obj['attributes']['y1'], obj['attributes']['color'], obj['mode']);
    }
}

function getImageSrc(color) {
    var src = '/static/essay_manager/img/comments/';
    switch (color){
        case COLOR_PRIMARY: src += 'primary.png'; break;
        case COLOR_INFO: src += 'info.png'; break;
        case COLOR_SUCCESS: src += 'success.png'; break;
        case COLOR_DANGER: src += 'danger.png'; break;
        case COLOR_WARNING: src += 'warning.png'; break;
        case COLOR_GREY: src += 'light.png'; break;
    }
    return src;
}

function addMarker(x0, y0, x1, y1, color, mode) {
    objects.push({
        'mode': mode,
        'attributes': {
            'x0': x0,
            'y0': y0,
            'x1': x1,
            'y1': y1,
            'color': color,
        },
    })
    drawMarker(x0, y0, x1, y1, color, mode);
}

function drawImage(src, x0, y0) {
    console.log('drawing image', src, x0, y0);
    var ctx = canvas.getContext("2d");
    var image = new Image();
    image.src = src;
    image.onload = function(){
        ctx.drawImage(image, x0 * canvasWidth, y0 * canvasHeight);
    }
}

function drawImages() {
    for (var i = 0; i < objects.length; i++) {
        var object = objects[i];
        if (object['mode'] != 'COMM' && object['mode'] != 'AUDIO') continue;
        drawImage(object['attributes']['src'], object['attributes']['x0'], object['attributes']['y0'])
    }
}

function addImage(x0, y0, src, comment) {
    objects.push({
        'mode': 'COMM',
        'attributes': {
            'comment': comment,
            'x0': x0,
            'y0': y0,
            'src': src,
        }
    })
    drawImage(src, x0, y0);
}

function importCorrectionData(data) {
    if (data['objects'] == undefined) return;
    objects = data['objects'];
    nullified = data['nullified'];
    grades = data['competencies']['grades'];
    textfieldComments = data['competencies']['comments'];
    
    competencies['comments'] = textfieldComments;
    competencies['grades'] = grades;

    for (var key in grades){
        var el = document.getElementById('slider-' + key);
        if (el)
            el.noUiSlider.set(grades[key]);
    }

    for (var key in textfieldComments){
        var el = document.getElementById('formtextarea-' + key);
        if (el)
            el.value = textfieldComments[key];
    }
    
    loadModule();
}

function loadModule() {
    var img = document.getElementById("src");
    img.onload = function() {
        loadModule();
    }

    canvas = document.getElementById("canvas");
    canvas.addEventListener('mousedown', mouseDownEvent);
    canvas.addEventListener('mousemove', mouseMoveEvent);

    updateCanvas();
    drawImages();
    drawMarkers();
}

const b64toBlob = (b64Data, contentType='', sliceSize=512) => {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];
  
    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }
  
    const blob = new Blob(byteArrays, {type: contentType});
    return blob;
}

function mouseDownEvent(e) {
    if (hoveringObjectIndex >= 0) {
        var object = objects[hoveringObjectIndex];
        if (object['mode'] == 'COMM'){
            document.getElementById('comment-text').value = object['attributes']['comment'];
            document.getElementById("openModal").click();
        }
        else if (object['mode'] == 'AUDIO')
        {
            document.getElementById("openAudioModal").click();
            document.getElementById("recordedAudio").src = URL.createObjectURL(b64toBlob(object['attributes']['b64']))
            document.getElementById("recordedAudio").controls=true; 
            document.getElementById("recordedAudio").autplay=true; 
        }
    }
}

function mouseMoveEvent(e) {
    var canvas = document.getElementById("canvas");
    var spos = getScroll()
    rect_x1 = (e.x - $(canvas).offset().left) / canvasWidth;
    rect_y1 = (e.y - $(canvas).offset().top) / canvasHeight;

    document.getElementById('canvas').style.cursor = 'default';
    hoveringObjectIndex = -1;

    var minDistance = 1000;
    for (var i = 0; i < objects.length; i++){
        var object = objects[i];
        if (object['mode'] == 'COMM' || object['mode'] == 'AUDIO'){
            var _x0 = rect_x1 * canvasWidth;
            var _y0 = rect_y1 * canvasHeight;
            var _x1 = object['attributes']['x0'] * canvasWidth + 30 + spos[0];
            var _y1 = object['attributes']['y0'] * canvasHeight + 20 - spos[1];
            var distance = (_x0 - _x1) * (_x0 - _x1) + (_y0 - _y1) * (_y0 - _y1);
            if (distance < minDistance){
                minDistance = distance;
                hoveringObjectIndex = i;
                document.getElementById('canvas').style.cursor = 'pointer';
            }
        }
    }
}

window.addEventListener("resize", loadModule);
window.addEventListener("DOMContentLoaded", loadModule);
    