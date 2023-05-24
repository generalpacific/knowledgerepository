import React, { useEffect, useState } from "react";

function ArtOfTheDay(props) {
  const [imageData, setImageData] = useState(null);
  const [promptData, setPromptData] = useState(null);

  useEffect(() => {
    const tzOffset = new Date().getTimezoneOffset() * 60000;
    const today = new Date(Date.now() - tzOffset).toISOString().slice(0, 10);
    const url = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${today}`;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        setImageData(data.image);
        setPromptData(data.prompt);
      })
      .catch((error) => {
        console.log("Error fetching image data:", error);
      });
  }, []);

  return (
    <div>
      {promptData && <h style={{ marginBottom: "10px" }}>{promptData}</h>}
      <br />
      <br />
      {imageData && (
        <img src={`data:image/png;base64,${imageData}`} alt="Art of the Day" />
      )}
    </div>
  );
}

export default ArtOfTheDay;
