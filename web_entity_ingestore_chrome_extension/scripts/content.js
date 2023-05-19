
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
    const highlightElems = document.querySelectorAll('.kp-notebook-highlight');
    const highlights = [];
    const bookTitleElement = document.querySelectorAll('.kp-notebook-metadata');

    for (let i = 0; i < highlightElems.length; i++) {
      const highlight = {};

      highlight.text = highlightElems[i].querySelector('.a-size-base-plus').textContent.trim();
      highlights.push(highlight)
    }
    console.log('Book: ' + JSON.stringify(highlights))

    var domInfo = {
      library: highlights
    };

    // Directly respond to the sender (popup),
    // through the specified callback.
    response(domInfo);
  }
});
