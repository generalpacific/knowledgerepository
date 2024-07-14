// Update the relevant fields with the new data.
const setDOMInfo = info => {
  console.log("Got info: " + JSON.stringify(info))
  document.getElementById('highlighted_entity').textContent = info.highlightedText;
  document.getElementById('entity_title').textContent = info.pageTitle;
  document.getElementById('entity_source').textContent = info.pageUrl;
};


const sendToServer = (data) => {
  fetch('https://abc.com/ingest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
    alert('Ingested successfully!');
  })
  .catch((error) => {
    console.error('Error:', error);
    alert('Failed to ingest. Error: ' + error);
  });
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

  document.getElementById('ingestButton').addEventListener('click', () => {
    const highlightedEntity = document.getElementById('highlighted_entity').textContent;
    const entityTitle = document.getElementById('entity_title').textContent;
    const entitySource = document.getElementById('entity_source').textContent;

    const data = {
      highlightedEntity: highlightedEntity,
      entityTitle: entityTitle,
      entitySource: entitySource
    };

    sendToServer(data);
  });
});
