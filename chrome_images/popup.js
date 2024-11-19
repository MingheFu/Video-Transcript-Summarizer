document.addEventListener('DOMContentLoaded', function () {
    const summaryDiv = document.getElementById('summary');
    const summarizeButton = document.getElementById('summarizeButton');
  
    summarizeButton.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: "getVideoUrl" }, (response) => {
        const youtubeUrl = response.youtubeUrl;
        if (youtubeUrl) {
          summaryDiv.innerHTML = "Loading summary...";
  
          fetch(
            `http://127.0.0.1:5000/api/summarize?youtube_url=${encodeURIComponent(
              youtubeUrl
            )}`
          )
            .then((response) => {
              if (!response.ok) {
                throw new Error("Error fetching summary");
              }
              return response.json();
            })
            .then((data) => {
              summaryDiv.innerHTML = data.summary;
            })
            .catch((error) => {
              console.error("Error:", error);
              summaryDiv.innerHTML = "Failed to fetch summary. Please try again.";
            });
        } else {
          summaryDiv.innerHTML = "Failed to capture YouTube URL.";
        }
      });
    });
  });
  