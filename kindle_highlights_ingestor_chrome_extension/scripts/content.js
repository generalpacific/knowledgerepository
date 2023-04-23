
// this tab should have a page-action.
function pingBackground() {
  chrome.runtime.sendMessage('showPageAction', response => {
    if(chrome.runtime.lastError) {
      console.log("Got error while sending ShowPageAction. Retrying...")
      setTimeout(pingBackground, 1000);
    } else {
      console.log("Sent pageaction successfully.")

    }
  });
}

pingBackground();

// Listen for messages from the popup.
chrome.runtime.onMessage.addListener((msg, sender, response) => {
  console.log("Got msg from popup")
  // First, validate the message's structure.
  if ((msg.from === 'popup') && (msg.subject === 'DOMInfo')) {
    // Collect the necessary data.
    books = document.getElementsByClassName('kp-notebook-library-each-book')[0]
    console.log('Books: ' + JSON.stringify(books))
    bookTitle = books.querySelectorAll("h2")[0].textContent
    console.log('Book: ' + JSON.stringify(bookTitle))
    var domInfo = {
      library: bookTitle
    };

    // Directly respond to the sender (popup),
    // through the specified callback.
    response(domInfo);
  }
});
