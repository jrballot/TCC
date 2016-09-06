$(".nav li").click(function(){
    if ( ! $(this).hasClass('active') ) {
        $('li.active').removeClass('active');
        $(this).addClass('active')
    }
});


// Datepicker
$(function() {
    $("#datepicker").datepicker({
        changeMonth: true,
        changeYear: true
    });
});
