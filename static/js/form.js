
  $(window).on("load",function(){
    $(".loader-wrapper").fadeOut(2000);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, options);
  });

  // Or with jQuery

  $(document).ready(function(){
    $('select').formSelect();
  });
  $(function() {
    $('form').submit(function() {
       console.log(JSON.stringify($('form').serializeJSON()));
      return false;
    });
  });