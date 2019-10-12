$("#select_all").change(function() { 
    $(":checkbox.layer").prop('checked', $(this).prop("checked"));
});

$(':checkbox.layer').change(function(){ 
    if(false == $(this).prop("checked")) {
        $("#select_all").prop('checked', false);
    }
    if ($(':checkbox.layer:checked').length == $(':checkbox.layer').length) {
      $("#select_all").prop('checked', true);
    }
});


$(document).ready(function() {
    $(":checkbox.layer").prop('checked', true);
    $("#submitform").submit();
});
