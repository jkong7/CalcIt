document.addEventListener("DOMContentLoaded", function() {
    // Hide Sign-In and Registration forms initially
    document.getElementById('signInForm').style.display = 'none'; // Ensure the form is hidden initially

    // Toggle Dashboard
    document.getElementById('dashboardBtn').addEventListener('click', function() {
        document.getElementById('dashboard').classList.toggle('show');
        document.getElementById('dimOverlay').classList.toggle('show');
    });

    // Toggle Sign-In Form
    document.getElementById('signInBtn').addEventListener('click', function() {
        document.querySelector('.form-box.register').style.transform = 'translateX(400px)';
        document.querySelector('.form-box.login').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.remove('active');

        document.getElementById('signInForm').style.display = 'block';

        setTimeout(function() { // Add a slight delay to allow the display to be set before the transition
            document.getElementById('signInForm').classList.add('active-popup');
            document.getElementById('dimOverlay').classList.add('show');
        }, 10); // 10ms delay to trigger the transition
    });

    // Switch to Register Form
    document.querySelector('.register-link').addEventListener('click', function() {
        document.querySelector('.form-box.login').style.transform = 'translateX(-400px)';
        document.querySelector('.form-box.register').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.add('active');
    });

    // Switch back to Login Form
    document.querySelector('.login-link').addEventListener('click', function() {
        document.querySelector('.form-box.register').style.transform = 'translateX(400px)';
        document.querySelector('.form-box.login').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.remove('active');
    });

    // Close Sign-In or Registration Form
    function closeForms() {
        document.getElementById('signInForm').classList.remove('active-popup');
        document.getElementById('dimOverlay').classList.remove('show');
        setTimeout(function() {
            document.getElementById('signInForm').style.display = 'none'; // Hide the form after transition
        }, 500); // Wait for the transition to complete before hiding
    }

    // Add event listeners for closing forms
    document.querySelector('.icon-close').addEventListener('click', function() {
        closeForms();
    });

    document.getElementById('dimOverlay').addEventListener('click', function() {
        closeForms();
    });

    // Close Dashboard when clicking outside
    document.getElementById('dimOverlay').addEventListener('click', function() {
        document.getElementById('dashboard').classList.remove('show');
        document.getElementById('dimOverlay').classList.remove('show');
    });
});

function toggleSection(sectionId) {
    var section = document.getElementById(sectionId);
    if (section.style.display === "none" || section.style.display === "") {
        section.style.display = "block";
    } else {
        section.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const progressCheckboxes = document.querySelectorAll(".progress-checkbox");

    progressCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function() {
            updateProgressBar(this.dataset.section);
            if (document.body.dataset.loggedIn === "true") {  // Check if the user is logged in
                updateProgress(this.id.replace('status', ''), this.checked);
            }
        });

        // Initialize progress bar based on existing state
        updateProgressBar(checkbox.dataset.section);
    });

    function updateProgressBar(section) {
        const sectionElement = document.querySelector(`[data-section="${section}"]`).closest(".dashboard-section");
        const totalCheckboxes = sectionElement.querySelectorAll(".progress-checkbox").length;
        const checkedCheckboxes = sectionElement.querySelectorAll(".progress-checkbox:checked").length;
        const progressBar = document.getElementById(`${section}-progress-bar`);

        const progressPercentage = (checkedCheckboxes / totalCheckboxes) * 100;
        progressBar.style.width = `${progressPercentage}%`;
    }

    function updateProgress(handoutId, isCompleted) {
        fetch('/update_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            },
            body: JSON.stringify({
                'handout_id': handoutId,
                'is_completed': isCompleted
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
});
