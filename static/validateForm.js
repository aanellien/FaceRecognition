

function validateForm() {
    var x = document.getElementsByName("file");
    if (x[0].value == "") {
        alert("Select Image for upload");
        return false;
    }
}
