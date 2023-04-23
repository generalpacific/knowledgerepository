
chrome.runtime.onMessage.addListener((msg, sender) => {
  console.log("Got msg: " + msg)
  // First, validate the message's structure.
  if ((msg.from === 'content') && (msg.subject === 'showPageAction')) {
    // Enable the page-action for the requesting tab.
    chrome.pageAction.show(sender.tab.id);
  }
});
