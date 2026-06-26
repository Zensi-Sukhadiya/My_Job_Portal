document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".search-box form") || 
                 document.querySelector(".search-row form");

    const jobContainer = document.getElementById("job-container");
    const filterButtons = document.querySelectorAll(".filter-btn");

    // ===============================
    // SEARCH FORM
    // ===============================
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(form);
            const queryString = new URLSearchParams(formData).toString();

            fetch(`?${queryString}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                jobContainer.innerHTML = data.html;
            });
        });
    }

    // ===============================
    // CATEGORY BUTTON CLICK
    // ===============================
    filterButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            const url = this.href;

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                jobContainer.innerHTML = data.html;
            });

            // 🔥 REMOVE ACTIVE FROM ALL
            filterButtons.forEach(btn => btn.classList.remove("active"));

            // 🔥 ADD ACTIVE TO CLICKED BUTTON
            this.classList.add("active");
        });
    });

});





/*document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".search-box form") || document.querySelector(".search-row form");
    const jobContainer = document.getElementById("job-container");
    const filterButtons = document.querySelectorAll(".filter-btn");

    Handle Search Form Submit
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const queryString = new URLSearchParams(formData).toString();

        fetch(`?${queryString}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                jobContainer.innerHTML = data.html;
            });
    });

    Handle Category Button Click
    filterButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            fetch(this.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    jobContainer.innerHTML = data.html;
                });
        });
    });

});
*/
