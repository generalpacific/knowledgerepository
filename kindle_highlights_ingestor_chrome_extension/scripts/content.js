
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
    books = document.getElementById('library').querySelector('kp-notebook-library-each-book')
    console.log('Books: ' + JSON.stringify(books))
    var domInfo = {
      library: books
    };

    // Directly respond to the sender (popup),
    // through the specified callback.
    response(domInfo);
  }
});
