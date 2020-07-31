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
var lastTouch = undefined;
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
var nullified = false;
var username = '';
var modalVisible = false;
var editModeActive = false;
var hoveringObjectIndex = -1;

function setUsername(val) {
    username = val;
}

function isDrawEnabled() {
    return color != "#00000000" && mode != "" && editModeActive != true;
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

function drawMarker(x0, y0, x1, y1, color, mode) {
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
        if (object['mode'] != 'COMM') continue;
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
    objects = data['objects']
    nullified = data['nullified'];
    grades = data['competencies']['grades'];
    textfieldComments = data['competencies']['comments'];
    
    competencies['comments'] = textfieldComments;
    competencies['grades'] = grades;
    document.getElementById('inlineRadioOptions1-' + grades['a1']).checked = true; 
    document.getElementById('inlineRadioOptions2-' + grades['a2']).checked = true; 
    document.getElementById('inlineRadioOptions3-' + grades['a3']).checked = true; 
    document.getElementById('inlineRadioOptions4-' + grades['a4']).checked = true; 
    document.getElementById('inlineRadioOptions5-' + grades['a5']).checked = true; 
    for (var key in textfieldComments){
        document.getElementById('formTextarea' + key).value = textfieldComments[key]; 
    }
}

function updateExportCorrectionData(){
    // console.log('@updateExportCorrectionData');
    var data = {};

    data['PEN_SIZE'] = PEN_SIZE;
    data['nullified'] = nullified;
    data['objects'] = objects;
    data['competencies'] = competencies;

    document.getElementById('formInput').value = JSON.stringify(data);
    document.getElementById('submitUpdateForm').submit(); 
}

function onKeyDown(e) {
    var evtobj = window.event? event : e
    editModeActive = evtobj.ctrlKey; 
    // control z
    if (evtobj.keyCode == 90 && evtobj.ctrlKey){
        var m = objects.pop();
        pops.push(m);
        
        updateCanvas();
        drawMarkers();
        drawImages();
    }
    
    // control y
    if (evtobj.keyCode == 89 && evtobj.ctrlKey){
        var m = pops.pop();
        pushes.push(m)
        
        updateCanvas();
        drawMarkers();
        drawImages();
    }

    // shortcuts
    if (!modalVisible){
        switch(evtobj.keyCode){
            // colors of c1 c2 c3 c4 c5 thesis
            case 49:
            case 97:
                document.getElementById('selectColorDanger').click();
                break;
            case 50:
            case 98:
                document.getElementById('selectColorPrimary').click();
                break;
            case 51:
            case 99:
                document.getElementById('selectColorInfo').click();
                break;
            case 52:
            case 100:
                document.getElementById('selectColorWarning').click();
                break;
            case 53:
            case 101:
                document.getElementById('selectColorSuccess').click();
                break;
            case 54:
            case 84:
            case 102:
                document.getElementById('selectColorGrey').click();
                break;
                
            // line, rect, comment
            case 81:
                document.getElementById('selectModeLine').click();
                break;
            case 87:
                document.getElementById('selectModeComment').click();
                break;
        }
    }
}

function onKeyUp(e) {
    var evtobj = window.event? event : e
    editModeActive = evtobj.ctrlKey;
}

function loadModeSelectionButtons() {
    $('#selectModeLine').click(function(){
        setMode('LINE');
    });
    $('#selectModeComment').click(function(){
        setMode('RECT');
    });
}

function loadColorSelectionButtons() {
    $('#selectColorPrimary').click(function(){
        setColor(COLOR_PRIMARY);
        document.getElementById("selectModeLine").click();
        document.getElementById("modalC2").click();
    });
    $('#selectColorInfo').click(function(){
        setColor(COLOR_INFO);
        document.getElementById("selectModeLine").click();
        document.getElementById("modalC3").click();
    });
    $('#selectColorSuccess').click(function(){
        setColor(COLOR_SUCCESS);
        document.getElementById("selectModeLine").click();
        document.getElementById("modalC5").click();
    });
    $('#selectColorDanger').click(function(){
        setColor(COLOR_DANGER);
        document.getElementById("selectModeComment").click();
        document.getElementById("modalC1").click();
    });
    $('#selectColorWarning').click(function(){
        setColor(COLOR_WARNING);
        document.getElementById("selectModeLine").click();
        document.getElementById("modalC4").click();
    });
    $('#selectColorGrey').click(function(){
        setColor(COLOR_GREY);
        document.getElementById("selectModeLine").click();
    });
}

function mouseDownEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    
    if (editModeActive && hoveringObjectIndex >= 0) {
        document.getElementById("openModal").click();
        modalVisible = true;
        document.getElementById('comment-text').value = objects[hoveringObjectIndex]['attributes']['comment'];
    }
    if (!isDrawEnabled()) return;
    
    if (e.touchType && e.touchType == 'stylus'){
        rect_x0 = (e.clientX - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y0 = (e.clientY - $(canvasPlaceholder).offset().top) / canvasHeight;
    }
    else {
        rect_x0 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y0 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;    
    }
    rect_x1 = 0;
    rect_y1 = 0;
    spos = getScroll()
    var ctx = canvasPlaceholder.getContext("2d");
    ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    if(rect_x0 && rect_y0 && mode == "LINE") {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.moveTo(rect_x0 * canvasWidth + spos[0], rect_y0 * canvasHeight + spos[1])
        ctx.lineTo(rect_x0 * canvasWidth + spos[0], rect_y0 * canvasHeight + spos[1]);
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
            ctx.drawImage(image, rect_x0 * canvasWidth + spos[0] - 15, rect_y0 * canvasHeight + spos[1] - 25);
        }
    }
}

function mouseMoveEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    var spos = getScroll()
    if (e.touchType && e.touchType == 'stylus'){
        rect_x1 = (e.clientX - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y1 = (e.clientY - $(canvasPlaceholder).offset().top) / canvasHeight;
    }
    else {
        rect_x1 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y1 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;    
    }

    document.getElementById('canvasPlaceholder').style.cursor = 'default';
    // if modal is visible, do not reset hover index
    if (!modalVisible) 
        hoveringObjectIndex = -1;

    if (editModeActive) {
        var minDistance = 1000;
        var minDistanceObj = null;
        for (var i = 0; i < objects.length; i++){
            var object = objects[i];
            if (object['mode'] == 'COMM'){
                var _x0 = rect_x1 * canvasWidth;
                var _y0 = rect_y1 * canvasHeight;
                var _x1 = object['attributes']['x0'] * canvasWidth + 30 + spos[0];
                var _y1 = object['attributes']['y0'] * canvasHeight + 20 - spos[1];
                var distance = (_x0 - _x1) * (_x0 - _x1) + (_y0 - _y1) * (_y0 - _y1);
                if (distance < minDistance){
                    minDistance = distance;
                    minDistanceObj = objects[i];
                    hoveringObjectIndex = i;
                    document.getElementById('canvasPlaceholder').style.cursor = 'pointer';
                }
            }
        }
        // if (minDistanceObj) console.log(minDistance, minDistanceObj['attributes']['comment']);
    }
    
    if (!isDrawEnabled()) return;
    var ctx = canvasPlaceholder.getContext("2d");
    
    if(rect_x0 && rect_y0){
        ctx.clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
        ctx.beginPath();
        ctx.lineWidth = PEN_SIZE;
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        if (mode == "LINE") {
            ctx.moveTo(rect_x0 * canvasWidth + spos[0], rect_y0 * canvasHeight + spos[1]);
            ctx.lineTo(rect_x1 * canvasWidth + spos[0], rect_y1 * canvasHeight + spos[1]);
            ctx.stroke();
        }
        else if (mode == "RECT"){
            ctx.lineWidth = PEN_SIZE / RECT_PEN_CORRECTION;
            ctx.rect(rect_x0 * canvasWidth + spos[0], rect_y0 * canvasHeight + spos[1], rect_x1 * canvasWidth - rect_x0 * canvasWidth, rect_y1 * canvasHeight - rect_y0 * canvasHeight);
            ctx.fillStyle = "#00000000";
            ctx.fill()
            ctx.strokeStyle = color;
            ctx.stroke();
        }
        else if (mode == 'COMM'){
            ctx.drawImage(lastImage, rect_x1 * canvasWidth - 15 + spos[0], rect_y1 * canvasHeight - 25 + spos[1]);
        }
    }
}

function mouseUpEvent(e) {
    var canvasPlaceholder = document.getElementById("canvasPlaceholder");
    if (!isDrawEnabled() && rect_x0 > 0 && rect_y0 > 0) return;
    spos = getScroll()
    if (e.touchType && e.touchType == 'stylus'){
        rect_x1 = (e.clientX - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y1 = (e.clientY - $(canvasPlaceholder).offset().top) / canvasHeight;
    }
    else {
        rect_x1 = (e.x - $(canvasPlaceholder).offset().left) / canvasWidth;
        rect_y1 = (e.y - $(canvasPlaceholder).offset().top) / canvasHeight;    
    }
    canvasPlaceholder.getContext("2d").clearRect(0, 0, canvasPlaceholder.width, canvasPlaceholder.height);
    
    if (mode == 'LINE' || mode == 'RECT'){
        addMarker(rect_x0 + spos[0] / canvasWidth, rect_y0 + spos[1] / canvasHeight, rect_x1 + spos[0] / canvasWidth, rect_y1 + spos[1] / canvasHeight, color, mode);
    }
    if (mode == 'RECT'){
        if (color == COLOR_DANGER)
            document.getElementById('comment-text').value = username + ', ';
        addImage(Math.max(rect_x1, rect_x0) - 15 / canvasWidth + spos[0] / canvasWidth, Math.min(rect_y1, rect_y0) - 35 / canvasHeight + spos[1] / canvasHeight, getImageSrc(color));
        document.getElementById("openModal").click();
        modalVisible = true;
        savedImagePos = [Math.max(rect_x1, rect_x0) - 15 / canvasWidth + spos[0] / canvasWidth, Math.min(rect_y1, rect_y0) - 35 / canvasHeight + spos[1] / canvasHeight]
    }
    
    rect_x0 = 0;
    rect_x1 = 0;
    rect_y0 = 0;
    rect_y1 = 0;
    lastTouch = undefined;
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

        canvasPlaceholder.removeEventListener('touchstart', {});
        canvasPlaceholder.removeEventListener('touchmove', {});
        canvasPlaceholder.removeEventListener('touchend', {});
        canvasPlaceholder.removeEventListener('touchcancel', {});
    }
    
    canvasPlaceholder.addEventListener('mousedown', mouseDownEvent);
    canvasPlaceholder.addEventListener('mousemove', mouseMoveEvent);
    canvasPlaceholder.addEventListener('mouseup', mouseUpEvent);
        
    canvasPlaceholder.addEventListener("touchstart", function(event) {
        mouseDownEvent(event);
        if(event.touches[event.touches.length - 1].touchType === "stylus"){
            lastTouch = event.touches[event.touches.length - 1];
            mouseDownEvent(lastTouch);
        }
        event.preventDefault()})

    canvasPlaceholder.addEventListener("touchmove", function(event) {
        if(event.touches[event.touches.length - 1].touchType === "stylus"){
            lastTouch = event.touches[event.touches.length - 1];
            mouseMoveEvent(lastTouch);
        }
        event.preventDefault()})
    
    canvasPlaceholder.addEventListener("touchend", function(event) {
        mouseUpEvent(lastTouch);
        event.preventDefault()})
    
    canvasPlaceholder.addEventListener("touchcancel", function(event) {
        event.preventDefault()})
    
    updateCanvas();
    drawImages();
    drawMarkers();
    document.onkeydown = onKeyDown;
    document.onkeyup = onKeyUp;
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
    var divs = ['errorsC1', 'errorsC2', 'errorsC3', 'errorsC4', 'errorsC5'];
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
    // add latest comment & its rectangle AGAIN
    if (hoveringObjectIndex == -1) {
        objects.push(objects[objects.length - 2]);
        objects.push(objects[objects.length - 2]);
        // clear comments
        objects[objects.length - 1]['attributes']['comment'] = document.getElementById('comment-text').value;
    }
    else {
        objects[hoveringObjectIndex]['attributes']['comment'] = document.getElementById('comment-text').value;
    }
}

function nullify(){
    nullified = true;
    var event = new Event('change');

    document.getElementById('inlineRadioOptions1-40').checked = true; 
    document.getElementById('inlineRadioOptions1-40').dispatchEvent(event);
    document.getElementById('inlineRadioOptions2-0').checked = true; 
    document.getElementById('inlineRadioOptions2-0').dispatchEvent(event);
    document.getElementById('inlineRadioOptions3-40').checked = true; 
    document.getElementById('inlineRadioOptions3-40').dispatchEvent(event);
    document.getElementById('inlineRadioOptions4-40').checked = true; 
    document.getElementById('inlineRadioOptions4-40').dispatchEvent(event);
    document.getElementById('inlineRadioOptions5-0').checked = true; 
    document.getElementById('inlineRadioOptions5-0').dispatchEvent(event);
}

$(window).on('DOMContentLoaded load resize scroll', showBtnsOnEssayVisible);
$(document).ready(function() {
    $('#myModal').on('hide.bs.modal', function () {
        modalVisible = false;
        
        if (hoveringObjectIndex == -1) {
            // whenever modal closes, remove last added comment
            // as a side effect, saved comments will also be removed.
            // so, if we wish to save a comment, we must add another one, since
            // only the last added will be saved.
            //
            // remove last added comment & its rectangle;
            objects.pop();
            objects.pop();
        }
        else {
            hoveringObjectIndex = -1;
        }

        // redraw;
        updateCanvas();
        drawMarkers();
        drawImages();

        // uncheck every checkbox
        var checkboxes = document.getElementsByName('competencyError');
        for (var i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = false;
        }
        document.getElementById('comment-text').value = '';
    });

    competencies['grades'] = {};
    competencies['grades']['a1'] = '200';
    competencies['grades']['a2'] = '200';
    competencies['grades']['a3'] = '200';
    competencies['grades']['a4'] = '200';
    competencies['grades']['a5'] = '200';

    $('input[type=radio][name=inlineRadioOptions]').on('change', function() {
        // console.log('inlineRadioOptions', $(this).val());
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
          case 'option6':
            competencies['grades']['a2'] = '0';
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
    // console.log('assignGrades', countErrorsC1, countErrorsC2, countErrorsC3, countErrorsC4, countErrorsC5);
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

    if (countErrorsC2 >= 5) {
        document.getElementById('inlineRadioOptions2-0').checked = true;
        document.getElementById('inlineRadioOptions2-0').dispatchEvent(event);
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
    updateTextfield(textfield, comp);

    switch(comp){
        case 'c1': 
            countErrorsC1 += weight;
            break;
        case 'c2': 
            countErrorsC2 += weight;
            break;
        case 'c3': 
            countErrorsC3 += weight;
            break;
        case 'c4': 
            countErrorsC4 += weight;
            break;
        case 'c5': 
            countErrorsC5 += weight;
            default: break;
    }
    
    if (apply)
        assignGrades()
}

loadModeSelectionButtons();
loadColorSelectionButtons();
window.addEventListener("resize", loadModule);
window.addEventListener("DOMContentLoaded", loadModule);
console.log('DSADSADS')
var body = document.getElementByTagName('body');
body.addEventListener('touchstart', function(evt){
    console.log(evt.touches[0])
    console.log(evt.touches[0].touchType);
});