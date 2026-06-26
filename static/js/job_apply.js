function showLoginPopup() {
    document.getElementById("loginPopup").style.display = "flex";
}

function closePopup() {
    document.getElementById("loginPopup").style.display = "none";
}

function validateApplication(isAuthenticated) {
    if (isAuthenticated === 'False') {
        showLoginPopup();
        return false;
    }
    return true;
}


document.addEventListener("DOMContentLoaded", function () {
    const resumeInput = document.getElementById("resume-input");
    const fileNameDisplay = document.getElementById("file-name");

    if (resumeInput && fileNameDisplay) {
        resumeInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = "No file chosen";
            }
        });
    }
});


function updateFileName(input) {
        const fileNameSpan = document.getElementById('file-name');
        if (input.files.length > 0) {
            fileNameSpan.innerText = input.files[0].name;
        } else {
            fileNameSpan.innerText = "Drag and drop or click to upload";
        }
    }