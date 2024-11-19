console.log("Content script loaded");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Content script received message:", request);
  if (request.action === "getVideoUrl") {
    const videoUrl = window.location.href;
    console.log("Content script sending video URL:", videoUrl);
    sendResponse({ youtubeUrl: videoUrl });
  }
});
