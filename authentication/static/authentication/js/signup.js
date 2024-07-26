document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.input-group input');

    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentNode.classList.add('focused');
        });

        input.addEventListener('blur', () => {
            if (input.value === '') {
                input.parentNode.classList.remove('focused');
            }
        });
    });
});
