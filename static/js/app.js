$('.shelf').click(function() {
  var $this = $(this);

  $.ajax({
    type : "POST",
    url : "sequelize",
    data: JSON.stringify({name: $this.data("name")}),
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      $this.text("Done!");
      $this.prop('onclick',null).off('click');
    }
  });
});