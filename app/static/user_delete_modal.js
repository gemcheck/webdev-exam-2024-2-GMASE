'use strict';

function modalShownBook(event) {
  let button = event.relatedTarget;
  let bookId = button.getAttribute('data-book-id');
  let bookName = button.getAttribute('data-name-book');
  let newUrl = `/books/${bookId}/delete_book`;
  let form = document.getElementById('deleteModalBookForm');
  form.action = newUrl;
  document.getElementById('bookName').textContent = bookName;
}

let modalBook = document.getElementById('deleteModalBook');
modalBook.addEventListener('show.bs.modal', modalShownBook);

document.addEventListener('DOMContentLoaded', function() {
  var textElement = document.getElementById('text');
  if (textElement) {
    new EasyMDE({ element: textElement });
  }
  var shortDescriptionElement = document.getElementById('short_description');
  if (shortDescriptionElement) {
    new EasyMDE({ element: shortDescriptionElement });
  }
});