$('.shelf').click(function() {
  var $this = $(this);
  var shelfName = $this.data("name");
  $.ajax({
    type: "POST",
    url: "sequelize",
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
      attachIgnoreSeries();

      $this.prop('onclick',null).off('click');
    }
  });
});

function attachBookClicks() {
  $('.book-selectable').click(function() {
    console.log("book clicked");
    if (!$(this).closest('.potential-books').hasClass('ignored')) {
      $(this).toggleClass("book-selected");
    }
  });
}

function attachCreateShelf() {
  $('.shelf-create-button').click(function() {
    console.log($('.book-selected'));
    var booksToAdd = $.map($('.potential-books:not(.ignored) .book-selected'), function(n) {
      return $(n).data("book-id");
    });
    var shelfName = $("#shelf-name-input").val();
    console.log(shelfName);
    console.log(booksToAdd);
    $.ajax({
      type: "POST",
      url: "createShelf",
      data: JSON.stringify({
        booksToAdd: booksToAdd,
        shelfName: shelfName
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        console.log("got result");
        console.log(result);

      }
    })
  });
}

function attachIgnoreSeries() {
  $('.shelf-ignore-button').click(function() {
    console.log("click");
    $(this).closest('.shelf-series').find('.potential-books').toggleClass("ignored");
  });
}