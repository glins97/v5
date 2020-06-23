const COLOR_PRIMARY = '#9c27b099';
const COLOR_LIGHT = '#afafaf99';
const COLOR_SUCCESS = '#4caf5099';
const COLOR_DANGER = '#f4433699';
const COLOR_WARNING = '#ff980099';
var color = "#00000000";

var mode = "";
var pushes = [];
var pops = [];
var poppedDrawables = [];
var poppedComments = [];
var poppedImages = [];
var drawables = [];
var comments = []
var images = [];
var competencies = {};

var lastImage = undefined;
var canvas = undefined;
var canvasPlaceholder = undefined;

var rect_x0 = 0;
var rect_x1 = 0;
var rect_y0 = 0;
var rect_y1 = 0;
var PEN_SIZE = 25;

function reset(){
    competencies = {};
    pushes = [];
    pops = [];
    poppedDrawables = [];
    poppedComments = [];
    poppedImages = [];
    drawables = [];
    comments = []
    images = [];
    
    lastImage = undefined;
    canvas = undefined;
    canvasPlaceholder = undefined;
    
    rect_x0 = 0;
    rect_x1 = 0;
    rect_y0 = 0;
    rect_y1 = 0;
    PEN_SIZE = 25;
    updateCanvas();
}

function isDrawEnabled() {
    return color != "#00000000" && mode != "";
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
        console.log(sx, sy)
        return [sx, sy];
    }
}

function updateCanvas() {
    var img = document.getElementById("src");
    canvas = document.getElementById("canvas");
    canvasPlaceholder = document.getElementById("canvasPlaceholder");
    canvas.style.position = "absolute";
    canvas.style.left = img.offsetLeft + "px";
    canvas.style.top = img.offsetTop + "px";
    canvas.width = img.width;
    canvas.height = img.height;
    canvasPlaceholder.style.position = "absolute";
    canvasPlaceholder.style.left = img.offsetLeft + "px";
    canvasPlaceholder.style.top = img.offsetTop + "px";
    canvasPlaceholder.width = img.width;
    canvasPlaceholder.height = img.height;
    PEN_SIZE = img.height * 25 / 2000
    console.log(img.height, PEN_SIZE, canvas.width, canvas.height);
}

function getColor(color) {
    switch (color) {
        case COLOR_PRIMARY: return [0, 0, 1, 0.5];
        case COLOR_DANGER: return [1, 0, 0, 0.5];
        case COLOR_WARNING: return [0, 1, 1, 0.5];
        case COLOR_LIGHT: return [1, 1, 1, 0.5];
        case COLOR_SUCCESS: return [0, 1, 0, 0.5];
    }
    return [0, 0, 0, 0];
}

function setColor(newColor) {
    color = newColor;
}

function setMode(newMode) {
    console.log('@setMode', newMode);
    mode = newMode;
}

function addDrawable(x0, y0, x1, y1, color) {
    if (!isDrawEnabled()) return;
    var ctx = canvas.getContext("2d");
    drawables.push(
        [x0, y0, x1, y1, color, mode]
        );
    pushes.push(mode);
    ctx.beginPath();
    ctx.lineWidth = PEN_SIZE;
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    if (mode == "LINE") {
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
    }
    else if (mode == "RECT"){
        ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
    }
    ctx.stroke();
}
    
function addImage(x, y) {
    if (!isDrawEnabled()) return;
    if (mode != "COMM") return;
    
    var src = '/static/essay_manager/img/comments/';
    switch (color){
        case COLOR_PRIMARY: src += 'primary.png'; break;
        case COLOR_LIGHT: src += 'light.png'; break;
        case COLOR_SUCCESS: src += 'success.png'; break;
        case COLOR_DANGER: src += 'danger.png'; break;
        case COLOR_WARNING: src += 'warning.png'; break;
    }
    images.push([src, x, y]);
    pushes.push(mode);
    drawImage(src, x, y);
}
    
function drawRectangles() {
    if (!isDrawEnabled()) return;
    var ctx = canvas.getContext("2d");
    for (var i = 0; i < drawables.length; i++) {
        var obj = drawables[i];
        ctx.beginPath();
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = obj[4];
        ctx.fillStyle = obj[4];
        if (obj[5] == "LINE") {
            ctx.moveTo(obj[0], obj[1]);
            ctx.lineTo(obj[2], obj[3]);
        } 
        else if (obj[5] == "RECT") {
            ctx.fillRect(obj[0], obj[1], obj[2] - obj[0], obj[3] - obj[1]);
        }
        ctx.stroke();
    }
}

function drawImage(src, x, y) {
    if (!isDrawEnabled()) return;
    var ctx = canvas.getContext("2d");
    var image = new Image();
    image.src = src;
    image.onload = function(){
        ctx.drawImage(image, x, y);
    }
}

function drawImages() {
    if (!isDrawEnabled()) return;
    for (var i = 0; i < images.length; i++) {
        drawImage(images[i][0], images[i][1], images[i][2])
    }
}

function assembleJsonExport(){
    var data = {};
    var height = document.getElementById("src").height;
    data['source'] = document.getElementById("src").src;
    var objects = [];
    var a = 0;
    var b = 0;
    for (var i = 0; i < pushes.length; i++) {
        var object = {};
        object['mode'] = pushes[i];
        
        switch (pushes[i]){
            case 'COMM': 
            object['attributes'] = {
                'comment': comments[a],
                'src': images[a][0],
                'x0': images[a][1],
                'y0': height - images[a][2],
            };
            a += 1;
            break;
            
            case 'LINE':  
            object['attributes'] = {
                'x0': drawables[b][0],
                'y0': height - drawables[b][1],
                'x1': drawables[b][2],
                'y1': height - drawables[b][3],
                'color': getColor(drawables[b][4])
            };
            b += 1;
            break;
            
            case 'RECT':  
            object['attributes'] = {
                'x0': drawables[b][0],
                'y0': height - drawables[b][1],
                'x1': drawables[b][2],
                'y1': height - drawables[b][3],
                'color': getColor(drawables[b][4])
            };
            b += 1;
            break;
        } 
        
        objects.push(object);
    }
    data['objects'] = objects;
    console.log(JSON.stringify(data))
    return data;
}

function onKeyDown(e) {
    var evtobj = window.event? event : e
    console.log(evtobj.keyCode);
    // control z
    if (evtobj.keyCode == 90 && evtobj.ctrlKey){
        var m = pushes.pop();
        pops.push(m);
        if (m == "LINE" || m == "RECT") 
        poppedDrawables.push(drawables.pop());
        else if (m == "COMM"){
            poppedImages.push(images.pop());
            poppedComments.push(comments.pop());
        }
        updateCanvas();
        drawRectangles();
        drawImages();
    }
    
    // control y
    if (evtobj.keyCode == 89 && evtobj.ctrlKey){
        var m = pops.pop();
        pushes.push(m)
        if (m == "LINE" || m == "RECT")
        drawables.push(poppedDrawables.pop());
        else if (m == "COMM") { 
            images.push(poppedImages.pop());
            comments.push(poppedComments.pop());
        }
        updateCanvas();
        drawRectangles();
        drawImages();
    }
}

function loadModeSelectionButtons() {
    $('#selectModeLine').click(function(){
        setMode('LINE');
    });
    $('#selectModeRectangle').click(function(){
        setMode('RECT');
    });
    $('#selectModeComment').click(function(){
        setMode('COMM');
    });
}

function loadColorSelectionButtons() {
    $('#selectColorPrimary').click(function(){
        setColor(COLOR_PRIMARY);
    });
    $('#selectColorLight').click(function(){
        setColor(COLOR_LIGHT);
    });
    $('#selectColorSuccess').click(function(){
        setColor(COLOR_SUCCESS);
    });
    $('#selectColorDanger').click(function(){
        setColor(COLOR_DANGER);
    });
    $('#selectColorWarning').click(function(){
        setColor(COLOR_WARNING);
    });
}


function mouseDownEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    
    rect_x0 = e.x - $(canvasPlaceholder).offset().left;
    rect_y0 = e.y - $(canvasPlaceholder).offset().top;
    rect_x1 = 0;
    rect_y1 = 0;
    spos = getScroll()
    var ctx = canvasPlaceholder.getContext("2d");
    ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    if(rect_x0 && rect_y0 && mode == "LINE") {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.moveTo(rect_x0 - spos[0], rect_y0 + spos[1])
        ctx.lineTo(rect_x0 - spos[0], rect_y0 + spos[1]);
        ctx.lineWidth = PEN_SIZE;
        ctx.stroke();
    }
    if (mode == "COMM"){
        var src = '/static/essay_manager/img/comments/';
        switch (color){
            case COLOR_PRIMARY: src += 'primary.png'; break;
            case COLOR_LIGHT: src += 'light.png'; break;
            case COLOR_SUCCESS: src += 'success.png'; break;
            case COLOR_DANGER: src += 'danger.png'; break;
            case COLOR_WARNING: src += 'warning.png'; break;
        }
        image = new Image();
        image.src = src;
        lastImage = image;
        image.onload = function(){
            ctx.drawImage(image, rect_x0 - spos[0] - 15, rect_y0 + spos[1] - 25);
        }
    }
}

function mouseMoveEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    var ctx = canvasPlaceholder.getContext("2d");
    spos = getScroll()
    rect_x1 = e.x - $(canvasPlaceholder).offset().left;
    rect_y1 = e.y - $(canvasPlaceholder).offset().top;
    
    if(rect_x0 && rect_y0){
        ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
        ctx.beginPath();
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        if (mode == "LINE") {
            ctx.moveTo(rect_x0 - spos[0], rect_y0 + spos[1]);
            ctx.lineTo(rect_x1 - spos[0], rect_y1 + spos[1]);
            ctx.stroke();
        }
        else if (mode == "RECT"){
            ctx.fillRect(rect_x0 - spos[0], rect_y0 + spos[1], rect_x1 - rect_x0, rect_y1 - rect_y0)
            ctx.stroke();
        }
        else if (mode == 'COMM'){
            ctx.drawImage(lastImage, rect_x1 - 15 - spos[0], rect_y1 - 25 + spos[1]);
        }
    }
}

function mouseUpEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    spos = getScroll()
    rect_x1 = e.x - $(canvasPlaceholder).offset().left;
    rect_y1 = e.y - $(canvasPlaceholder).offset().top;
    canvasPlaceholder.getContext("2d").clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    
    if (mode == 'LINE' || mode == 'RECT'){
        // if minimal movement, add square instead
        if ((rect_x1 - rect_x0) * (rect_x1 - rect_x0) < 100 && (rect_y1 - rect_y0) * (rect_y1 - rect_y0) < 100){
            addDrawable(rect_x0 - spos[0] - PEN_SIZE / 2, rect_y0 + spos[1], rect_x0 - spos[0] + PEN_SIZE / 2, rect_y0 + spos[1], color);
        } 
        else {
            addDrawable(rect_x0 - spos[0], rect_y0 + spos[1], rect_x1 - spos[0], rect_y1 + spos[1], color);
        }
    }
    if (mode=='COMM'){
        addImage(rect_x1 - 15 - spos[0], rect_y1 - 25 + spos[1]);
        lastImage = undefined;
        document.getElementById("openModal").click();
    }
    
    rect_x0 = 0;
    rect_x1 = 0;
    rect_y0 = 0;
    rect_y1 = 0;
}

var loadCount = 0;
function loadModule() {
    loadCount += 1;
    var img = document.getElementById("src");
    img.onload = function() {
        loadModule();
    }

    canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (loadCount > 1) {
        canvasPlaceholder.removeEventListener('mousedown', {});
        canvasPlaceholder.removeEventListener('mousemove', {});
        canvasPlaceholder.removeEventListener('mouseup', {});
    }
    
    canvasPlaceholder.addEventListener('mousedown', mouseDownEvent);
    canvasPlaceholder.addEventListener('mousemove', mouseMoveEvent);
    canvasPlaceholder.addEventListener('mouseup', mouseUpEvent);
    
    updateCanvas();
    document.onkeydown = onKeyDown;
}

$(document).ready(function() {
    $('input[type=radio][name=inlineRadioOptions]').on('change', function() {
        console.log('inlineRadioOptions', $(this).val());
        switch ($(this).val()) {
          case 'option1':
            competencies['a1'] = '200';
            break;
          case 'option2':
            competencies['a1'] = '160';
            break;
          case 'option3':
            competencies['a1'] = '120';
            break;
          case 'option4':
            competencies['a1'] = '80';
            break;
          case 'option5':
            competencies['a1'] = '40';
            break;
          case 'option6':
            competencies['a1'] = '0';
            break;
        }
        console.log(competencies);
      });

      $('input[type=radio][name=inlineRadioOptions2]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['a2'] = '200';
            break;
          case 'option2':
            competencies['a2'] = '160';
            break;
          case 'option3':
            competencies['a2'] = '120';
            break;
          case 'option4':
            competencies['a2'] = '80';
            break;
          case 'option5':
            competencies['a2'] = '40';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions3]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['a3'] = '200';
            break;
          case 'option2':
            competencies['a3'] = '160';
            break;
          case 'option3':
            competencies['a3'] = '120';
            break;
          case 'option4':
            competencies['a3'] = '80';
            break;
          case 'option5':
            competencies['a3'] = '40';
            break;
          case 'option6':
            competencies['a3'] = '0';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions4]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['a4'] = '200';
            break;
          case 'option2':
            competencies['a4'] = '160';
            break;
          case 'option3':
            competencies['a4'] = '120';
            break;
          case 'option4':
            competencies['a4'] = '80';
            break;
          case 'option5':
            competencies['a4'] = '40';
            break;
          case 'option6':
            competencies['a4'] = '0';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions5]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['a5'] = '200';
            break;
          case 'option2':
            competencies['a5'] = '160';
            break;
          case 'option3':
            competencies['a5'] = '120';
            break;
          case 'option4':
            competencies['a5'] = '80';
            break;
          case 'option5':
            competencies['a5'] = '40';
            break;
          case 'option6':
            competencies['a5'] = '0';
            break;
        }
    });
  });

function updateTextfield(textfield, comp){
    competencies[comp] = document.getElementById(textfield).value;
    console.log(competencies);
}

function updateTextfieldValue(checkbox, textfield, value, comp) {
    if (document.getElementById(checkbox).checked)
        document.getElementById(textfield).value += value;
    else
        document.getElementById(textfield).value = document.getElementById(textfield).value.replace(value, '');
    updateTextfield(textfield, comp);
}

loadModeSelectionButtons();
loadColorSelectionButtons();
window.addEventListener("resize", loadModule);
window.addEventListener("DOMContentLoaded", loadModule);
    