$(document).ready(function () {
    $("#toggle-form").click(function () {

        $("#patient-form").slideToggle();
    });
});

$(document).ready(function () {
    $("#add-user-btn").click(function () {
        $("#user-form").fadeIn();
    });

    $("#close-form-btn").click(function () {
        $("#user-form").fadeOut();
        $("#user-form")[0].reset();
        $("#additional-fields").slideUp();
        $("#doctor-fields").slideUp();
    });

    $("#role").change(function () {
        var selectedRole = $(this).val();
        if (selectedRole === "patient") {
            $("#additional-fields").slideDown();
            $("#doctor-fields").slideUp();
        } else if (selectedRole === "doctor") {
            $("#additional-fields").slideUp();
            $("#doctor-fields").slideDown();
        } else {
            $("#additional-fields").slideUp();
            $("#doctor-fields").slideUp();
        }
    });
});

function filterSymptoms() {
    var input, filter, ul, li, label, i, txtValue;
    input = document.getElementById("search");
    filter = input.value.toLowerCase();
    ul = document.getElementById("symptom-list");
    li = ul.getElementsByTagName("li");

    for (i = 0; i < li.length; i++) {
        label = li[i].getElementsByTagName("label")[0];
        txtValue = label.textContent || label.innerText;
        if (txtValue.toLowerCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}



