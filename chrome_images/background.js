background.jschrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Background script received message:", request);
  if (request.action === "getVideoUrl") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        sendResponse({ youtubeUrl: null });
        return;
      }
      chrome.tabs.sendMessage(
        tabs[0].id,
        { action: "getVideoUrl" },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error("Error sending message to content script:", chrome.runtime.lastError);
            sendResponse({ youtubeUrl: null });
          } else if (response && response.youtubeUrl) {
            sendResponse({ youtubeUrl: response.youtubeUrl });
          } else {
            console.error("No response or youtubeUrl from content script.");
            sendResponse({ youtubeUrl: null });
          }
        }
      );
    });
    return true; 
  }
})
