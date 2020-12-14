function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function execBodyScripts(el) {
    console.log('@execBodyScripts')
    function nodeName(elem, name) {
        return elem.nodeName && elem.nodeName.toUpperCase() ===
        name.toUpperCase();
    };
    
    function evalScript(elem) {
        var data = (elem.text || elem.textContent || elem.innerHTML || "" ),
        head = document.getElementsByTagName("head")[0] ||
        document.documentElement,
        script = document.createElement("script");
        
        script.type = "text/javascript";
        try {
            script.appendChild(document.createTextNode(data));      
        } catch(e) {
            script.text = data;
        }
        
        head.insertBefore(script, head.firstChild);
        head.removeChild(script);
    };
    
    // main section of function
    var scripts = [],
    script,
    children_nodes = el.childNodes,
    child,
    i;
    
    for (i = 0; children_nodes[i]; i++) {
        child = children_nodes[i];
        if (nodeName(child, "script" ) &&
        (!child.type || child.type.toLowerCase() === "text/javascript")) {
            scripts.push(child);
        }
    }
    
    for (i = 0; scripts[i]; i++) {
        script = scripts[i];
        if (script.parentNode) {script.parentNode.removeChild(script);}
        evalScript(scripts[i]);
    }
};

pjax = {
    _: console.log('loaded pjax'),
    
    request: function(url, method) {
        var me = this;
        method = method || 'GET';
        
        var content_el = document.getElementById("pjax-content");
        document.getElementById("loader").classList.add('active');
        content_el.innerHTML = ''
        
        var xhr = new XMLHttpRequest(); 
        xhr.open(method, url);  
        xhr.send();        
        xhr.onreadystatechange = function() { 
            if (xhr.readyState == 4 && xhr.status == 200){
                var parser = new DOMParser();
                var response = parser.parseFromString(xhr.response, 'text/html');
                var title = (/<title>(.*?)<\/title>/m).exec(xhr.response)[1];
                
                document.title = title;
                content_el.innerHTML = response.getElementById('pjax-content').innerHTML;
                execBodyScripts(content_el);
                window.history.pushState("", title, url);
                
                document.getElementById("loader").classList.remove('active');
                me.load();
            }
        };
    },
    
    load: function() {
        let elements = document.getElementsByTagName('a');
        for (var i = 0; i < elements.length; i++) {
            let element = elements[i];
            let href = element.getAttribute('href');
            let pref = element.getAttribute('pref');
            let skip = element.getAttribute('skip-pjax') || element.getAttribute('data-toggle');
            if (href && !pref && !skip) {
                element.setAttribute('pref', href);
                element.removeAttribute('href');
                element.setAttribute('style', 'cursor: pointer;');
                element.setAttribute('onclick', "pjax.request('" + href + "', 'GET')");
            } 
        }
    }
}

$(document).ready(function() {
    pjax.load();
});

window.onpopstate = function(){
    pjax.request(location.href);
};