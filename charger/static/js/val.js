<script>
    function validateSignupForm() {
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        if (username.length < 5 || password.length < 8) {
            alert('Username must be at least 5 characters, and password must be at least 8
characters');
            return false;
        }

        return true;
    }
</script>