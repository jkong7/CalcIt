document.addEventListener("DOMContentLoaded", function() {

    // ------------------ Smooth Scrolling for Anchor Links ------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // ------------------ Initial Setup: Hide Sign-In and Registration Forms ------------------
    document.getElementById('signInForm').style.display = 'none';

    // ------------------ Toggle Dashboard Visibility ------------------
    const dashboardBtn = document.getElementById('dashboardBtn');
    const dimOverlay = document.getElementById('dimOverlay');
    const dashboard = document.getElementById('dashboard');

    dashboardBtn.addEventListener('click', function() {
        dashboard.classList.toggle('show');
        dimOverlay.classList.toggle('show');
    });

    // ------------------ Close Forms and Dashboard When Clicking Outside ------------------
    dimOverlay.addEventListener('click', function() {
        closeForms();
        dashboard.classList.remove('show');
        dimOverlay.classList.remove('show');
    });

    // ------------------ Toggle Sign-In Form Visibility ------------------
    const signInBtn = document.getElementById('signInBtn');
    signInBtn.addEventListener('click', function() {
        document.querySelector('.form-box.register').style.transform = 'translateX(400px)';
        document.querySelector('.form-box.login').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.remove('active');

        document.getElementById('signInForm').style.display = 'block';

        setTimeout(function() {
            document.getElementById('signInForm').classList.add('active-popup');
            dimOverlay.classList.add('show');
        }, 10);
    });

    // ------------------ Switch to Register Form ------------------
    document.querySelector('.register-link').addEventListener('click', function() {
        document.querySelector('.form-box.login').style.transform = 'translateX(-400px)';
        document.querySelector('.form-box.register').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.add('active');
    });

    // ------------------ Switch Back to Login Form ------------------
    document.querySelector('.login-link').addEventListener('click', function() {
        document.querySelector('.form-box.register').style.transform = 'translateX(400px)';
        document.querySelector('.form-box.login').style.transform = 'translateX(0)';
        document.querySelector('.wrapper').classList.remove('active');
    });

    // ------------------ Close Sign-In or Registration Form ------------------
    function closeForms() {
        document.getElementById('signInForm').classList.remove('active-popup');
        dimOverlay.classList.remove('show');
        setTimeout(function() {
            document.getElementById('signInForm').style.display = 'none';
        }, 500);
    }

    document.querySelector('.icon-close').addEventListener('click', closeForms);

    // ------------------ Toggle Dashboard Sections ------------------
    const sectionHeaders = document.querySelectorAll('.dashboard-header');

    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const section = this.nextElementSibling;
            if (section.style.display === "none" || section.style.display === "") {
                section.style.display = "block";
            } else {
                section.style.display = "none";
            }
        });
    });

    // ------------------ Progress Checkbox Handling ------------------
    const progressCheckboxes = document.querySelectorAll(".progress-checkbox");

    progressCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function() {
            updateProgressBar(this.dataset.section);
            if (document.body.dataset.loggedIn === "true") {
                updateProgress(this.id.replace('status', ''), this.checked);
            }
        });

        updateProgressBar(checkbox.dataset.section);
    });

    // ------------------ Update Progress Bar ------------------
    function updateProgressBar(section) {
        const sectionElement = document.querySelector(`[data-section="${section}"]`).closest(".dashboard-section");
        const totalCheckboxes = sectionElement.querySelectorAll(".progress-checkbox").length;
        const checkedCheckboxes = sectionElement.querySelectorAll(".progress-checkbox:checked").length;
        const progressBar = document.getElementById(`${section}-progress-bar`);

        const progressPercentage = (checkedCheckboxes / totalCheckboxes) * 100;
        progressBar.style.width = `${progressPercentage}%`;
    }

    // ------------------ Update Progress in Backend ------------------
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

    // ------------------ Flash Message Handling ------------------
    const flashMessageElement = document.querySelector(".flash");
    if (flashMessageElement) {
        const message = flashMessageElement.textContent.trim();
        const type = flashMessageElement.dataset.category || "success";
        showFlashMessage(message, type);
    }

    function showFlashMessage(message, type = "success") {
        const flashContainer = document.getElementById("flash-container");
        flashContainer.textContent = message;
        flashContainer.classList.add("flash-message", type, "show");

        setTimeout(() => {
            flashContainer.classList.remove("show");
            setTimeout(() => {
                flashContainer.classList.remove(type);
            }, 300);
        }, 3000);
    }

    // ------------------ Loading a Handout ------------------
    loadHandout(0);

    function loadHandout(index) {
        const handout = handouts[index];
        document.getElementById('handout-title').innerText = handout.title;
        document.getElementById('handout-image').src = handout.image;
        document.getElementById('handout-description').innerText = handout.description;
        
        const downloadButton = document.getElementById('download-handout-btn');
        downloadButton.href = handout.downloadLink;
    }

});
