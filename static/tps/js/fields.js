function toggleUsedQuestions() {
    toggleFieldVisibility(parseInt(document.getElementById('id_max_questions').value));
}

function toggleFieldVisibility(index) {
    for (var i = index + 1; i < 121; i++)
        document.getElementsByClassName("field-q" + i)[0].style.display = 'none';

    for (var i = 1; i < index + 1; i++)
        document.getElementsByClassName("field-q" + i)[0].style.removeProperty("display");
}

$(document).ready(function() {
    toggleUsedQuestions();
    $("#id_max_questions").bind('change click mouseup', function () {
        var id_max_questions = document.getElementById('id_max_questions');
        if (id_max_questions.value > 121)
            id_max_questions.value = 121
        else if (id_max_questions.value < 0)
            id_max_questions.value = 0
        toggleUsedQuestions();
    });
});