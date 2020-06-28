const COLOR_PRIMARY = '#9c27b066';
const COLOR_INFO = '#00bcd466';
const COLOR_SUCCESS = '#4caf5066';
const COLOR_DANGER = '#f48b3666';
const COLOR_WARNING = '#ffee0066';
const COLOR_GREY = '#33333366';
var color = "#00000000";

var mode = "";
var pushes = [];
var pops = [];
var poppedDrawables = [];
var poppedComments = [];
var poppedImages = [];
var drawables = [];
var comments = [];
var images = [];
var competencies = {
    'comments': {},
    'grades': {},
};

var lastImage = undefined;
var canvas = undefined;
var canvasPlaceholder = undefined;

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
    canvasWidth = canvas.width;
    canvasHeight = canvas.height;
    canvasPlaceholder.style.position = "absolute";
    canvasPlaceholder.style.left = img.offsetLeft + "px";
    canvasPlaceholder.style.top = img.offsetTop + "px";
    canvasPlaceholder.width = img.width;
    canvasPlaceholder.height = img.height;
    PEN_SIZE = img.height * 30 / 2000
}

function setColor(newColor) {
    color = newColor;
}

function setMode(newMode) {
    mode = newMode;
}

function addDrawable(x0, y0, x1, y1, color, mode_) {
    var ctx = canvas.getContext("2d");
    drawables.push(
        [x0, y0, x1, y1, color, mode_ ? mode_ : mode]
        );
    pushes.push(mode_ ? mode_ : mode);
    ctx.beginPath();
    if (mode == "LINE" || mode_ == "LINE") {
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.moveTo(x0 * canvasWidth, y0 * canvasHeight);
        ctx.lineTo(x1 * canvasWidth, y1 * canvasHeight);
    }
    else if (mode == "RECT" || mode_ == "RECT"){
        ctx.lineWidth = PEN_SIZE / RECT_PEN_CORRECTION;
        ctx.rect(x0 * canvasWidth, y0 * canvasHeight, x1 * canvasWidth - x0 * canvasWidth, y1 * canvasHeight - y0 * canvasHeight);
        ctx.fillStyle = "#00000000";
        ctx.fill()
        ctx.strokeStyle = color;
        ctx.stroke();
    }
    console.log('@addDrawable', pushes, drawables);
    ctx.stroke();
}
       
function drawRectangles() {
    var ctx = canvas.getContext("2d");
    for (var i = 0; i < drawables.length; i++) {
        var obj = drawables[i];
        ctx.beginPath();
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = obj[4];
        ctx.fillStyle = obj[4];
        if (obj[5] == "LINE") {
            ctx.moveTo(obj[0] * canvasWidth, obj[1] * canvasHeight);
            ctx.lineTo(obj[2] * canvasWidth, obj[3] * canvasHeight);
        } 
        else if (obj[5] == "RECT") {
            ctx.lineWidth = PEN_SIZE / RECT_PEN_CORRECTION;
            ctx.rect(obj[0] * canvasWidth, obj[1] * canvasHeight, obj[2] * canvasWidth - obj[0] * canvasWidth, obj[3] * canvasHeight - obj[1] * canvasHeight);
            ctx.fillStyle = "#00000000";
            ctx.fill()
            ctx.strokeStyle = obj[4];
            ctx.stroke();
        }
        ctx.stroke();
    }
}

function addImage(x, y, src_) {
    console.log('@addImage', x, y, src_);
    var src = '/static/essay_manager/img/comments/';
    switch (color){
        case COLOR_PRIMARY: src += 'primary.png'; break;
        case COLOR_INFO: src += 'info.png'; break;
        case COLOR_SUCCESS: src += 'success.png'; break;
        case COLOR_DANGER: src += 'danger.png'; break;
        case COLOR_WARNING: src += 'warning.png'; break;
        case COLOR_GREY: src += 'light.png'; break;
    }
    images.push([src_ ? src_ : src, x, y]);
    pushes.push(mode);
    comments.push('temp-comment')
    drawImage(src_ ? src_ : src, x, y);
}

function drawImage(src, x, y) {
    var ctx = canvas.getContext("2d");
    var image = new Image();
    image.src = src;
    image.onload = function(){
        ctx.drawImage(image, x * canvasWidth, y * canvasHeight);
    }
}

function drawImages() {
    for (var i = 0; i < images.length; i++) {
        drawImage(images[i][0], images[i][1], images[i][2])
    }
}

function importCorrectionData(data) {
    if (data['objects'] == undefined) return;
    for (var i = 0; i < data['objects'].length; i++) {
        var mode = data['objects'][i]['mode']
        var attributes = data['objects'][i]['attributes'];
        switch (mode){
            case 'LINE':  
            case 'RECT':  
                addDrawable(attributes['x0'], attributes['y0'], attributes['x1'], attributes['y1'], attributes['color'], mode);
                break; 
            case 'COMM':  
                addImage(attributes['x0'], attributes['y0'], attributes['src']);
                comments.push(attributes['comment'])
                break;
        }
    }

    grades = data['competencies']['grades'];
    textfieldComments = data['competencies']['comments'];
    competencies['grades'] = grades;
    document.getElementById('inlineRadioOptions1-' + grades['a1']).checked = true; 
    document.getElementById('inlineRadioOptions2-' + grades['a2']).checked = true; 
    document.getElementById('inlineRadioOptions3-' + grades['a3']).checked = true; 
    document.getElementById('inlineRadioOptions4-' + grades['a4']).checked = true; 
    document.getElementById('inlineRadioOptions5-' + grades['a5']).checked = true; 
    for (var key in textfieldComments){
        console.log(key, 'formTextarea-' + key);
        document.getElementById('formTextarea-' + key).value = textfieldComments[key]; 
    }
}

function updateExportCorrectionData(){
    console.log('@updateExportCorrectionData');
    var data = {};
    var objects = [];
    var a = 0;
    var b = 0;
    data['PEN_SIZE'] = PEN_SIZE;
    for (var i = 0; i < pushes.length; i++) {
        var object = {};
        object['mode'] = pushes[i];
        
        switch (pushes[i]){
            case 'COMM': 
            object['attributes'] = {
                'comment': comments[a],
                'src': images[a][0],
                'x0': images[a][1],
                'y0': images[a][2],
            };
            a += 1;
            break;
            
            case 'LINE':  
            object['attributes'] = {
                'x0': drawables[b][0],
                'y0': drawables[b][1],
                'x1': drawables[b][2],
                'y1': drawables[b][3],
                'color': drawables[b][4],
            };
            b += 1;
            break;
            
            case 'RECT':  
            object['attributes'] = {
                'x0': drawables[b][0],
                'y0': drawables[b][1],
                'x1': drawables[b][2],
                'y1': drawables[b][3],
                'color': drawables[b][4],
            };
            b += 1;
            break;
        } 
        
        objects.push(object);
    }
    data['objects'] = objects;
    data['competencies'] = competencies;
    console.log('@updateExportCorrectionData data', data);
    document.getElementById('formInput').value = JSON.stringify(data);
    document.getElementById('submitUpdateForm').submit(); 
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
    $('#selectColorInfo').click(function(){
        setColor(COLOR_INFO);
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
    $('#selectColorGrey').click(function(){
        setColor(COLOR_GREY);
    });
}

function mouseDownEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    
    rect_x0 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
    rect_y0 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;
    rect_x1 = 0;
    rect_y1 = 0;
    spos = getScroll()
    var ctx = canvasPlaceholder.getContext("2d");
    ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    if(rect_x0 && rect_y0 && mode == "LINE") {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.moveTo(rect_x0 * canvasWidth - spos[0], rect_y0 * canvasHeight + spos[1])
        ctx.lineTo(rect_x0 * canvasWidth - spos[0], rect_y0 * canvasHeight + spos[1]);
        ctx.lineWidth = PEN_SIZE;
        ctx.stroke();
    }
    if (mode == "COMM"){
        var src = '/static/essay_manager/img/comments/';
        switch (color){
            case COLOR_PRIMARY: src += 'primary.png'; break;
            case COLOR_INFO: src += 'info.png'; break;
            case COLOR_SUCCESS: src += 'success.png'; break;
            case COLOR_DANGER: src += 'danger.png'; break;
            case COLOR_WARNING: src += 'warning.png'; break;
            case COLOR_GREY: src += 'light.png'; break;
        }
        image = new Image();
        image.src = src;
        lastImage = image;
        image.onload = function(){
            ctx.drawImage(image, rect_x0 * canvasWidth - spos[0] - 15, rect_y0 * canvasHeight + spos[1] - 25);
        }
    }
}

function mouseMoveEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    var ctx = canvasPlaceholder.getContext("2d");
    spos = getScroll()
    rect_x1 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
    rect_y1 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;
    
    if(rect_x0 && rect_y0){
        ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
        ctx.beginPath();
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        if (mode == "LINE") {
            ctx.moveTo(rect_x0 * canvasWidth - spos[0], rect_y0 * canvasHeight + spos[1]);
            ctx.lineTo(rect_x1 * canvasWidth - spos[0], rect_y1 * canvasHeight + spos[1]);
            ctx.stroke();
        }
        else if (mode == "RECT"){
            ctx.lineWidth = PEN_SIZE / RECT_PEN_CORRECTION;
            ctx.rect(rect_x0 * canvasWidth - spos[0], rect_y0 * canvasHeight + spos[1], rect_x1 * canvasWidth - rect_x0 * canvasWidth, rect_y1 * canvasHeight - rect_y0 * canvasHeight);
            ctx.fillStyle = "#00000000";
            ctx.fill()
            ctx.strokeStyle = color;
            ctx.stroke();
        }
        else if (mode == 'COMM'){
            ctx.drawImage(lastImage, rect_x1 * canvasWidth - 15 - spos[0], rect_y1 * canvasHeight - 25 + spos[1] );
        }
    }
}

function mouseUpEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled()) return;
    spos = getScroll()
    rect_x1 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
    rect_y1 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;
    canvasPlaceholder.getContext("2d").clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    
    if (mode == 'LINE' || mode == 'RECT'){
        // if minimal movement, add square instead
        if ((rect_x1 * canvasWidth - rect_x0 * canvasWidth) * (rect_x1 * canvasWidth - rect_x0 * canvasWidth) < 100 && (rect_y1 * canvasHeight - rect_y0 * canvasHeight) * (rect_y1 * canvasHeight - rect_y0 * canvasHeight) < 100){
            addDrawable(rect_x0 - spos[0] / canvasWidth - PEN_SIZE / 2 / canvasWidth, rect_y0 + spos[1] / canvasHeight, rect_x0 - spos[0] / canvasWidth + PEN_SIZE / 2 / canvasWidth, rect_y0 + spos[1] / canvasHeight, color);
        } 
        else {
            addDrawable(rect_x0 - spos[0] / canvasWidth, rect_y0 + spos[1] / canvasHeight, rect_x1 - spos[0] / canvasWidth, rect_y1 + spos[1] / canvasHeight, color);
        }
    }
    if (mode=='COMM'){
        addImage(rect_x1 - 15 / canvasWidth - spos[0] / canvasWidth, rect_y1 - 25 / canvasHeight + spos[1] / canvasHeight);
        lastImage = undefined;
        document.getElementById("openModal").click();
        savedImagePos = [rect_x1 - 15 / canvasWidth - spos[0] / canvasWidth, rect_y1 - 25 / canvasHeight + spos[1] / canvasHeight]
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
    drawImages();
    drawRectangles();
    document.onkeydown = onKeyDown;
}

function showBtnsOnEssayVisible() {
    var rect = document.getElementById('card-essay').getBoundingClientRect();
    document.getElementById('btns').hidden = rect.height + rect.top < 100;
}

function addClass(id, className) {
    var element = document.getElementById(id);
    arr = element.className.split(" ");
    if (arr.indexOf(className) == -1) {
      element.className += " " + className;
    }
}

function removeClass(id, className) {
    var element = document.getElementById(id);
    element.className = element.className.replace(className, "");
}

function showCompetencyErrors(id) {
    var divs = ['errorsC1', 'errorsC2', 'errorsC3', 'errorsC4'];
    for (var i = 0; i < divs.length; i++){
        addClass(divs[i], 'collapse');
    }
    removeClass(id, 'collapse');
}

function saveComment(){
    assignGrades();

    // whenever modal closes, remove last added comment
    // as a side effect, saved comments will also be removed.
    // so, if we wish to save a comment, we must add another one, since
    // only the last added will be saved.
    //
    // add latest comment AGAIN
    addImage(savedImagePos[0], savedImagePos[1]);
}

$(window).on('DOMContentLoaded load resize scroll', showBtnsOnEssayVisible);
$(document).ready(function() {
    $('#myModal').on('hide.bs.modal', function () {
        console.log('modalclose');
        
        // whenever modal closes, remove last added comment
        // as a side effect, saved comments will also be removed.
        // so, if we wish to save a comment, we must add another one, since
        // only the last added will be saved.
        //
        // remove last added comment;
        images.pop();
        pushes.pop();
        comments.pop();

        // redraw;
        updateCanvas();
        drawRectangles();
        drawImages();

        // clear comments
        comments[comments.length - 1] = document.getElementById('comment-text').value;
        document.getElementById('comment-text').value = '';

        // uncheck every checkbox
        var checkboxes = document.getElementsByName('competencyError');
        for (var i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = false;
        }
    });

    competencies['grades'] = {};
    competencies['grades']['a1'] = '200';
    competencies['grades']['a2'] = '200';
    competencies['grades']['a3'] = '200';
    competencies['grades']['a4'] = '200';
    competencies['grades']['a5'] = '200';

    $('input[type=radio][name=inlineRadioOptions]').on('change', function() {
        console.log('inlineRadioOptions', $(this).val());
        switch ($(this).val()) {
          case 'option1':
            competencies['grades']['a1'] = '200';
            break;
          case 'option2':
            competencies['grades']['a1'] = '160';
            break;
          case 'option3':
            competencies['grades']['a1'] = '120';
            break;
          case 'option4':
            competencies['grades']['a1'] = '80';
            break;
          case 'option5':
            competencies['grades']['a1'] = '40';
            break;
          case 'option6':
            competencies['grades']['a1'] = '0';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions2]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['grades']['a2'] = '200';
            break;
          case 'option2':
            competencies['grades']['a2'] = '160';
            break;
          case 'option3':
            competencies['grades']['a2'] = '120';
            break;
          case 'option4':
            competencies['grades']['a2'] = '80';
            break;
          case 'option5':
            competencies['grades']['a2'] = '40';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions3]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['grades']['a3'] = '200';
            break;
          case 'option2':
            competencies['grades']['a3'] = '160';
            break;
          case 'option3':
            competencies['grades']['a3'] = '120';
            break;
          case 'option4':
            competencies['grades']['a3'] = '80';
            break;
          case 'option5':
            competencies['grades']['a3'] = '40';
            break;
          case 'option6':
            competencies['grades']['a3'] = '0';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions4]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['grades']['a4'] = '200';
            break;
          case 'option2':
            competencies['grades']['a4'] = '160';
            break;
          case 'option3':
            competencies['grades']['a4'] = '120';
            break;
          case 'option4':
            competencies['grades']['a4'] = '80';
            break;
          case 'option5':
            competencies['grades']['a4'] = '40';
            break;
          case 'option6':
            competencies['grades']['a4'] = '0';
            break;
        }
      });

      $('input[type=radio][name=inlineRadioOptions5]').on('change', function() {
        switch ($(this).val()) {
          case 'option1':
            competencies['grades']['a5'] = '200';
            break;
          case 'option2':
            competencies['grades']['a5'] = '160';
            break;
          case 'option3':
            competencies['grades']['a5'] = '120';
            break;
          case 'option4':
            competencies['grades']['a5'] = '80';
            break;
          case 'option5':
            competencies['grades']['a5'] = '40';
            break;
          case 'option6':
            competencies['grades']['a5'] = '0';
            break;
        }
    });
  });

function updateTextfield(textfield, comp) {
    competencies['comments'][comp] = document.getElementById(textfield).value;
}

function assignGrades() {
    var event = new Event('change');
    if (countErrorsC1 >= 5) {
        document.getElementById('inlineRadioOptions1-40').checked = true;
        document.getElementById('inlineRadioOptions1-40').dispatchEvent(event);
    } 
    if (countErrorsC1 <= 4) {
        document.getElementById('inlineRadioOptions1-80').checked = true;
        document.getElementById('inlineRadioOptions1-80').dispatchEvent(event);
    } 
    if (countErrorsC1 <= 3) {
        document.getElementById('inlineRadioOptions1-120').checked = true;
        document.getElementById('inlineRadioOptions1-120').dispatchEvent(event);
    } 
    if (countErrorsC1 <= 2) {
        document.getElementById('inlineRadioOptions1-160').checked = true;
        document.getElementById('inlineRadioOptions1-160').dispatchEvent(event);
    } 
    if (countErrorsC1 <= 1) {
        document.getElementById('inlineRadioOptions1-200').checked = true;
        document.getElementById('inlineRadioOptions1-200').dispatchEvent(event);
    } 

    if (countErrorsC2 >= 4) {
        document.getElementById('inlineRadioOptions2-40').checked = true;
        document.getElementById('inlineRadioOptions2-40').dispatchEvent(event);
    } 
    if (countErrorsC2 <= 3) {
        document.getElementById('inlineRadioOptions2-80').checked = true;
        document.getElementById('inlineRadioOptions2-80').dispatchEvent(event);
    } 
    if (countErrorsC2 <= 2) {
        document.getElementById('inlineRadioOptions2-120').checked = true;
        document.getElementById('inlineRadioOptions2-120').dispatchEvent(event);
    } 
    if (countErrorsC2 <= 1) {
        document.getElementById('inlineRadioOptions2-160').checked = true;
        document.getElementById('inlineRadioOptions2-160').dispatchEvent(event);
    } 
    if (countErrorsC2 == 0) {
        document.getElementById('inlineRadioOptions2-200').checked = true;
        document.getElementById('inlineRadioOptions2-200').dispatchEvent(event);
    } 

    if (countErrorsC3 >= 4) {
        document.getElementById('inlineRadioOptions3-40').checked = true;
        document.getElementById('inlineRadioOptions3-40').dispatchEvent(event);
    } 
    if (countErrorsC3 <= 3) {
        document.getElementById('inlineRadioOptions3-80').checked = true;
        document.getElementById('inlineRadioOptions3-80').dispatchEvent(event);
    } 
    if (countErrorsC3 <= 2) {
        document.getElementById('inlineRadioOptions3-120').checked = true;
        document.getElementById('inlineRadioOptions3-120').dispatchEvent(event);
    } 
    if (countErrorsC3 <= 1) {
        document.getElementById('inlineRadioOptions3-160').checked = true;
        document.getElementById('inlineRadioOptions3-160').dispatchEvent(event);
    } 
    if (countErrorsC3 == 0) {
        document.getElementById('inlineRadioOptions3-200').checked = true;
        document.getElementById('inlineRadioOptions3-200').dispatchEvent(event);
    } 

    if (countErrorsC4 >= 4) {
        document.getElementById('inlineRadioOptions4-40').checked = true;
        document.getElementById('inlineRadioOptions4-40').dispatchEvent(event);
    } 
    if (countErrorsC4 <= 3) {
        document.getElementById('inlineRadioOptions4-80').checked = true;
        document.getElementById('inlineRadioOptions4-80').dispatchEvent(event);
    } 
    if (countErrorsC4 <= 2) {
        document.getElementById('inlineRadioOptions4-120').checked = true;
        document.getElementById('inlineRadioOptions4-120').dispatchEvent(event);
    } 
    if (countErrorsC4 <= 1) {
        document.getElementById('inlineRadioOptions4-160').checked = true;
        document.getElementById('inlineRadioOptions4-160').dispatchEvent(event);
    } 
    if (countErrorsC4 == 0) {
        document.getElementById('inlineRadioOptions4-200').checked = true;
        document.getElementById('inlineRadioOptions4-200').dispatchEvent(event);
    } 

    if (countErrorsC5 >= 5) {
        document.getElementById('inlineRadioOptions5-0').checked = true;
        document.getElementById('inlineRadioOptions5-0').dispatchEvent(event);
    } 
    if (countErrorsC5 <= 4) {
        document.getElementById('inlineRadioOptions5-40').checked = true;
        document.getElementById('inlineRadioOptions5-40').dispatchEvent(event);
    } 
    if (countErrorsC5 <= 3) {
        document.getElementById('inlineRadioOptions5-80').checked = true;
        document.getElementById('inlineRadioOptions5-80').dispatchEvent(event);
    } 
    if (countErrorsC5 <= 2) {
        document.getElementById('inlineRadioOptions5-120').checked = true;
        document.getElementById('inlineRadioOptions5-120').dispatchEvent(event);
    } 
    if (countErrorsC5 <= 1) {
        document.getElementById('inlineRadioOptions5-160').checked = true;
        document.getElementById('inlineRadioOptions5-160').dispatchEvent(event);
    } 
    if (countErrorsC5 == 0) {
        document.getElementById('inlineRadioOptions5-200').checked = true;
        document.getElementById('inlineRadioOptions5-200').dispatchEvent(event);
    } 
}

function updateTextfieldValue(checkbox, textfield, value, comp, weight, apply) {
    var checked = document.getElementById(checkbox).checked;
    if (checked)
        document.getElementById(textfield).value += value;
    else {
        weight = -weight;
        document.getElementById(textfield).value = document.getElementById(textfield).value.replace(value, '');
    }

    switch(comp){
        case 'c1': 
            countErrorsC1 += weight;
            if (!apply) break;
            if (countErrorsC1 >= 6) document.getElementById('inlineRadioOptions1-0').checked = true; 
            if (countErrorsC1 <= 5) document.getElementById('inlineRadioOptions1-40').checked = true; 
            if (countErrorsC1 <= 4) document.getElementById('inlineRadioOptions1-80').checked = true; 
            if (countErrorsC1 <= 3) document.getElementById('inlineRadioOptions1-120').checked = true; 
            if (countErrorsC1 <= 2) document.getElementById('inlineRadioOptions1-160').checked = true; 
            if (countErrorsC1 <= 1) document.getElementById('inlineRadioOptions1-200').checked = true; 
            break;
        case 'c2': 
            countErrorsC2 += weight;
            if (!apply) break;
            if (countErrorsC2 >= 4) document.getElementById('inlineRadioOptions2-40').checked = true; 
            if (countErrorsC2 <= 3) document.getElementById('inlineRadioOptions2-80').checked = true; 
            if (countErrorsC2 <= 2) document.getElementById('inlineRadioOptions2-120').checked = true; 
            if (countErrorsC2 <= 1) document.getElementById('inlineRadioOptions2-160').checked = true; 
            if (countErrorsC2 == 0) document.getElementById('inlineRadioOptions2-200').checked = true; 
            break;
        case 'c3': 
            countErrorsC3 += weight;
            if (!apply) break;
            if (countErrorsC3 >= 5) document.getElementById('inlineRadioOptions3-0').checked = true; 
            if (countErrorsC3 <= 4) document.getElementById('inlineRadioOptions3-40').checked = true; 
            if (countErrorsC3 <= 3) document.getElementById('inlineRadioOptions3-80').checked = true; 
            if (countErrorsC3 <= 2) document.getElementById('inlineRadioOptions3-120').checked = true; 
            if (countErrorsC3 <= 1) document.getElementById('inlineRadioOptions3-160').checked = true; 
            if (countErrorsC3 == 0) document.getElementById('inlineRadioOptions3-200').checked = true; 
            break;
        case 'c4': 
            countErrorsC4 += weight;
            if (!apply) break;
            if (countErrorsC4 >= 4) document.getElementById('inlineRadioOptions4-40').checked = true; 
            if (countErrorsC4 <= 3) document.getElementById('inlineRadioOptions4-80').checked = true; 
            if (countErrorsC4 <= 2) document.getElementById('inlineRadioOptions4-120').checked = true; 
            if (countErrorsC4 <= 1) document.getElementById('inlineRadioOptions4-160').checked = true; 
            if (countErrorsC4 == 0) document.getElementById('inlineRadioOptions4-200').checked = true; 
            break;
        case 'c5': 
            countErrorsC5 += weight;
            if (!apply) break;
            if (countErrorsC5 >= 5) document.getElementById('inlineRadioOptions5-0').checked = true; 
            if (countErrorsC5 <= 4) document.getElementById('inlineRadioOptions5-40').checked = true; 
            if (countErrorsC5 <= 3) document.getElementById('inlineRadioOptions5-80').checked = true; 
            if (countErrorsC5 <= 2) document.getElementById('inlineRadioOptions5-120').checked = true; 
            if (countErrorsC5 <= 1) document.getElementById('inlineRadioOptions5-160').checked = true; 
            if (countErrorsC5 == 0) document.getElementById('inlineRadioOptions5-200').checked = true;
            break;
        default: break;
    }
}

loadModeSelectionButtons();
loadColorSelectionButtons();
window.addEventListener("resize", loadModule);
window.addEventListener("DOMContentLoaded", loadModule);
    