// $(document).ready(function () {
//     $("#toggle-form").click(function () {
//
//         $("#patient-form").slideToggle();
//     });
// });

$(document).ready(function () {
    $("#add-user-btn").click(function () {
        $("#user-form").fadeIn();
    });

    $("#close-form-btn").click(function () {
        $("#user-form").fadeOut();
        $("#user-form form")[0].reset();
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

function validateForm() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var checked = false;

    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            checked = true;
            break;
        }
    }

    if (!checked) {
        alert("Please select at least one symptom.");
        return false; // Prevent the form from submitting
    }

    // Retrieve the patient ID from the hidden input field
    var patientIdInput = document.querySelector('input[name="patient_id"]');
    var patientId = patientIdInput.value;

    // Add the patient ID to the form submission URL
    var form = document.querySelector('form');
    form.action = "/symptoms/" + patientId;

    return true; // Allow the form to submit
}


