// assessment/static/admin/js/question_admin.js
document.addEventListener('DOMContentLoaded', function() {
    const questionTypeSelect = document.querySelector('#id_question_type');
    const choicesGroup = document.querySelector('#choice_set-group');

    function toggleChoices() {
        if (questionTypeSelect.value === 'multiple') {
            choicesGroup.style.display = 'block';
        } else {
            choicesGroup.style.display = 'none';
        }
    }

    // Initial check
    toggleChoices();

    // Add event listener
    questionTypeSelect.addEventListener('change', toggleChoices);
});