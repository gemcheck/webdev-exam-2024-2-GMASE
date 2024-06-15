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