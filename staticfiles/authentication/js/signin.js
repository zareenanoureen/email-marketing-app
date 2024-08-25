// You can add JavaScript functionality here if needed
// This example handles basic form submission and validation

document.getElementById('signInForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Validate form fields (if needed)
    var email = document.getElementsByName('email')[0].value.trim();
    var password = document.getElementsByName('password')[0].value.trim();

    if (email === '' || password === '') {
        alert('Email and password are required!');
        return;
    }

    // Submit the form (optional)
    this.submit();
});
