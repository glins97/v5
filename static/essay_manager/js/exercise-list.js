function remove(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

var exerciseList = {
    associatedExercises: [],
    tempAssociatedExercises: [],
    currentEssay: -1,
    
    setCurrentEssay: function (id) {
        this.currentEssay = id;
    },
    
    loadAssociatedExercises: function(obj) {
        this.associatedExercises = obj || [];
        this.tempAssociatedExercises = this.associatedExercises;
        console.log('this.associatedExercises', this.associatedExercises);
        for (var i = 0; i < this.associatedExercises.length; i++) {
            document.getElementById('exercise-' + this.associatedExercises[i]).checked = true;
        }
    },
    
    holdTempExercise: function(id) {
        if (this.tempAssociatedExercises.includes(id))
            remove(this.tempAssociatedExercises, id);
        else
            this.tempAssociatedExercises.push(id);
    },
    
    discardAssociatedExercises: function() {
        this.tempAssociatedExercises = this.associatedExercises;
    },
    
    saveAssociatedExercises: function() {
        this.associatedExercises = this.tempAssociatedExercises;
        let currentEssay = this.currentEssay;
        var xhr = new XMLHttpRequest();  
        xhr.open("POST", "/api/exercises/recommendations/save/");  
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.send("&essay=" + currentEssay + ";lists=" + JSON.stringify(this.associatedExercises)); 
        xhr.onreadystatechange = function() { 
            console.log(xhr.status)
        };
    }   
}