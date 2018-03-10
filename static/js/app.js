$('.shelf').click(function() {
  var $this = $(this);
  var shelfName = $this.data("name");
  $.ajax({
    type : "POST",
    url : "sequelize",
    data: JSON.stringify({
      name: shelfName,
      count: $this.data("count")
    }),
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      console.log("done");
      console.log(result);

      var myDiv = $('#' + shelfName + '-result');
      console.log(myDiv);
      myDiv.html(result);

      $this.prop('onclick',null).off('click');
    }
  });
});