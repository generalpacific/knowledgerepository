// Update the relevant fields with the new data.
const setDOMInfo = info => {
  console.log("Got info: " + info)
  document.getElementById('library').textContent = JSON.stringify(info.library);
};

// Once the DOM is ready...
window.addEventListener('DOMContentLoaded', () => {
  // ...query for the active tab...
  chrome.tabs.query({
    active: true,
    currentWindow: true
  }, tabs => {
    // ...and send a request for the DOM info...
    console.log("Popup requesting DomInfo")
    chrome.tabs.sendMessage(
        tabs[0].id,
        {from: 'popup', subject: 'DOMInfo'},
        // ...also specifying a callback to be called 
        //    from the receiving end (content script).
        setDOMInfo);
  });
});
