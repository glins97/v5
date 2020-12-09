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
    'grades': {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
    },
    'vars': {
        'contentGrade': 0,
        'errors': 0,
        'lineCount': 0,
        'finalGrade': 0,
    }
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

var errors = [];

function removeFromArray(element, array){
    for (var i = array.length - 1; i >= 0; i--) {
        if (array[i] === element) {
            array.splice(i, 1);
        }
    }
}

function updateGrades(){
    var contentGrade = (parseFloat(competencies['grades']['1']) + parseFloat(competencies['grades']['2']) + parseFloat(competencies['grades']['3']) + parseFloat(competencies['grades']['4']) + parseFloat(competencies['grades']['5']));
    var errorCount = errors.length;
    var lineCount = document.getElementById('total-lines').value;
    console.log(errors, errorCount);
    document.getElementById('contentGrade').innerText = 'Nota no conteúdo: ' + contentGrade;
    document.getElementById('errorCount').innerText = 'Número de erros: ' + errorCount;
    var finalGrade = (contentGrade - errorCount * 2 / lineCount);
    if (finalGrade < 0)
        finalGrade = 0;
    document.getElementById('finalGrade').innerText = 'Nota final: ' + finalGrade.toFixed(2);
    competencies['vars']['contentGrade'] = contentGrade;
    competencies['vars']['errors'] = errors;
    competencies['vars']['lineCount'] = lineCount;
    competencies['vars']['finalGrade'] = finalGrade.toFixed(2);
}

function toggleError(line, column){
    var errorId = 'err' + line + '-' + column;
    var errorDiv = document.getElementById(errorId);
    if (errors.includes(errorId)) {
        errorDiv.classList.remove('error-selection-active');
        removeFromArray(errorId, errors);
    }
    else {
        errorDiv.classList.add('error-selection-active');
        errors.push(errorId);
    }
    updateGrades();
}

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

function getColorSource() {
    var src = '/static/essay_manager/img/comments/';
    if (mode == 'AUDIO')
        src = '/static/essay_manager/img/audios/'
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
        if (object['mode'] != 'COMM' && object['mode'] != 'AUDIO') continue;
        drawImage(object['attributes']['src'], object['attributes']['x0'], object['attributes']['y0'])
    }
}

function addComment(x0, y0, src) {
    objects.push({
        'mode': 'COMM',
        'attributes': {
            'comment': '',
            'x0': x0,
            'y0': y0,
            'src': src,
        }
    })
    drawImage(src, x0, y0);
}

function addAudio(x0, y0, src) {
    objects.push({
        'mode': 'AUDIO',
        'attributes': {
            'b64': '',
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

    errors = competencies['vars']['errors'];
    for (var i=0; i<errors.length; i++){
        var errorDiv = document.getElementById(errorId);
        errorDiv.classList.add('error-selection-active');
    }
    document.getElementById('total-lines').value = competencies['vars']['lineCount']; 

    for (var key in grades){
        var el = document.getElementById('inlineRadioOptionsc' + key + '-' + grades[key]);
        console.log('el', el)
        if (el)
            el.click();
    }

    for (var key in textfieldComments){
        var el = document.getElementById('formTextarea' + key);
        if (el)
            el.value = textfieldComments[key];
    }
    
    loadModule();
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
    $('#selectModeAudio').click(function(){
        setMode('AUDIO');
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
    
    document.getElementById("recordedAudio").controls = true; 
    document.getElementById("recordedAudio").autoplay = false; 
    document.getElementById("audioControls").hidden = false; 
    if (editModeActive && hoveringObjectIndex >= 0) {
        var object = objects[hoveringObjectIndex];
        if (object['mode'] == 'COMM'){
            document.getElementById('comment-text').value = object['attributes']['comment'];
            document.getElementById("openCommentModal").click();
            modalVisible = true;
        }
        else if (object['mode'] == 'AUDIO')
        {
            document.getElementById("openAudioModal").click();
            document.getElementById("recordedAudio").src = URL.createObjectURL(b64toBlob(object['attributes']['b64']))
            document.getElementById("recordedAudio").controls = true; 
            document.getElementById("recordedAudio").autoplay = true; 
            document.getElementById("audioControls").hidden = true; 
            modalVisible = true;
        }
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
    if (mode == "AUDIO"){
        var src = '/static/essay_manager/img/audios/';
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
                    minDistanceObj = objects[i];
                    hoveringObjectIndex = i;
                    document.getElementById('canvasPlaceholder').style.cursor = 'pointer';
                }
            }
        }
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
        else if (mode == 'AUDIO'){
            ctx.drawImage(lastImage, rect_x1 * canvasWidth - 45 + spos[0], rect_y1 * canvasHeight - 55 + spos[1]);
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
        addComment(Math.max(rect_x1, rect_x0) - 15 / canvasWidth + spos[0] / canvasWidth, Math.min(rect_y1, rect_y0) - 35 / canvasHeight + spos[1] / canvasHeight, getColorSource());
        document.getElementById("openCommentModal").click();
        modalVisible = true;
        savedImagePos = [Math.max(rect_x1, rect_x0) - 15 / canvasWidth + spos[0] / canvasWidth, Math.min(rect_y1, rect_y0) - 35 / canvasHeight + spos[1] / canvasHeight]
    }
    if (mode == 'AUDIO'){
        addAudio(rect_x1 - 45 / canvasWidth + spos[0] / canvasWidth, rect_y1 - 55 / canvasHeight + spos[1] / canvasHeight, getColorSource());
        document.getElementById("openAudioModal").click();
        modalVisible = true;
        savedImagePos = [rect_x1 - 45 / canvasWidth + spos[0] / canvasWidth, rect_y1 - 55 / canvasHeight + spos[1] / canvasHeight]
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

function saveAudio(){
    objects.push(objects[objects.length - 1]);
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

    $('#audioModal').on('hide.bs.modal', function () {
        modalVisible = false;
        
        if (hoveringObjectIndex == -1) {
           objects.pop();
        }
        else {
            hoveringObjectIndex = -1;
        }

        // redraw;
        updateCanvas();
        drawMarkers();
        drawImages();
    });

    $('input[type=radio][name=inlineRadioOptions]').on('change', function() {
        switch ($(this).val()) {
          case 'option2':
            competencies['grades']['1'] = '0';
            break;
          case 'option1':
            competencies['grades']['1'] = '1';
            break;
          case 'option0':
            competencies['grades']['1'] = '1';
            break;
            default: break;
        };
        updateGrades();
    });

    $('input[type=radio][name=inlineRadioOptions2]').on('change', function() {
        switch ($(this).val()) {
            case 'option2':
              competencies['grades']['2'] = '0';
              break;
            case 'option1':
              competencies['grades']['2'] = '0.5';
              break;
            case 'option0':
              competencies['grades']['2'] = '1';
              break;
            default: break;
        };
        updateGrades();
    });

    $('input[type=radio][name=inlineRadioOptions3]').on('change', function() {
        switch ($(this).val()) {
            case 'option3':
              competencies['grades']['3'] = '0';
              break;
            case 'option2':
              competencies['grades']['3'] = '1.25';
              break;
            case 'option1':
              competencies['grades']['3'] = '2.25';
              break;
            case 'option0':
              competencies['grades']['3'] = '3.5';
              break;
            default: break;
        };
        updateGrades();
    });

    $('input[type=radio][name=inlineRadioOptions4]').on('change', function() {
        switch ($(this).val()) {
            case 'option3':
              competencies['grades']['4'] = '0';
              break;
            case 'option2':
              competencies['grades']['4'] = '1';
              break;
            case 'option1':
              competencies['grades']['4'] = '1.5';
              break;
            case 'option0':
              competencies['grades']['4'] = '2';
              break;
            default: break;
        };
        updateGrades();
    });

    $('input[type=radio][name=inlineRadioOptions5]').on('change', function() {
        switch ($(this).val()) {
            case 'option3':
              competencies['grades']['5'] = '0';
              break;
            case 'option2':
              competencies['grades']['5'] = '1';
              break;
            case 'option1':
              competencies['grades']['5'] = '1.75';
              break;
            case 'option0':
              competencies['grades']['5'] = '2.5';
              break;
            default: break;
        };
        updateGrades();
    });

});

function updateTextfield(textfield, comp) {
    competencies['comments'][comp] = document.getElementById(textfield).value;
}

loadModeSelectionButtons();
loadColorSelectionButtons();
window.addEventListener("resize", loadModule);
window.addEventListener("DOMContentLoaded", loadModule);

// Audio recording related ---------------------------------------

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

var updateb64 = function(blob) {
    var reader = new FileReader();
    reader.onload = function() {
        var dataUrl = reader.result;
        var base64 = dataUrl.split(',')[1];
        objects[objects.length - 1]['attributes']['b64'] = base64;
    };
    reader.readAsDataURL(blob);
};

var audioData = [];
var record = document.getElementById('record');
var save = document.getElementById('save');

var loadedMediaRecorder = false;
var rec = null;
var recStartTime = null;
function startRecording() {
    navigator.mediaDevices.getUserMedia({audio:true})
    .then(stream => {handlerFunction(stream)})
    function handlerFunction(stream) {
        rec = new MediaRecorder(stream);
        rec.ondataavailable = e => {
            audioData.push(e.data);
            el = document.getElementsByClassName('plyr__time--current')[0];
            if (!recStartTime)
                recStartTime = new Date()
            var seconds = Math.trunc((new Date() - recStartTime) / 1000)
            var minutes = 0;
            while (seconds > 60) {
                seconds -= 60;
                minutes += 1;
            }
            if (seconds < 10)
                seconds = "0" + seconds
            if (minutes < 10)
                minutes = "0" + minutes

            el.innerHTML = minutes + ":" + seconds;

            var blob = null;
            if (rec.state == "inactive"){
                blob = new Blob(audioData,{type:'audio/mpeg-3'});
                recordedAudio.src = URL.createObjectURL(blob);
                recordedAudio.controls = true;
                document.getElementById("audioControls").hidden = false; 
            updateb64(blob);
            }
        }
        rec.start(250);
        record.textContent = "Parar gravação";
    }
}

record.onclick = e => {
    if (record.textContent == "Começar gravação"){
        recStartTime = new Date();
        audioData = [];
        startRecording();
        save.disabled = true;
        record.textContent = "Parar gravação";
    }
    else {
        recStartTime = null;
        rec.stop();
        save.disabled = false;
        record.textContent = "Começar gravação";
    }
}