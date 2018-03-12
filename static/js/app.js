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
      attachBookClicks();
      attachCreateShelf();

      $this.prop('onclick',null).off('click');
    }
  });
});

function attachBookClicks() {
  $('.book-selectable').click(function() {
    console.log("book clicked");
    $(this).toggleClass("book-selected");
  });
}

function attachCreateShelf() {
  $('.shelf-create-button').click(function() {
    console.log($('.book-selected'));
    var booksToAdd = $.map($('.book-selected'), function(n) {
      return $(n).data("book-id");
    });

  });
}