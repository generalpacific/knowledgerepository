import React, { useEffect, useState } from "react";
import pako from "pako";

function ArtOfTheDay(props) {
  const [imageData, setImageData] = useState(null);
  const [promptData, setPromptData] = useState(null);
  const [errorData, setErrorData] = useState(null);

  useEffect(() => {
    const tzOffset = new Date().getTimezoneOffset() * 60000;
    const today = new Date(Date.now() - tzOffset).toISOString().slice(0, 10);
    const url = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${today}`;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        if (data.image) {
          // Decompress the data.image
          // Decode base64 (convert ascii to binary)
          const binaryString = window.atob(data.image);
          // Convert binary string to character-number array
          const charCodeArray = Array.from(binaryString, c => c.charCodeAt(0));
          // Convert character-number array to Uint8Array
          const binData = new Uint8Array(charCodeArray);
          // Decompress using pako
          const decompressedData = pako.inflate(binData);
          // Convert Uint8Array to binary string more safely
          let binaryStr = '';
          const chunkSize = 512;
          for (let i = 0; i < decompressedData.length; i += chunkSize) {
            const chunk = decompressedData.subarray(i, i + chunkSize);
            binaryStr += String.fromCharCode.apply(null, chunk);
          }
          // Convert binary string to base64
          const decompressedBase64 = window.btoa(binaryStr);
          setImageData(decompressedBase64);
          setPromptData(data.prompt);
        } else {
          setErrorData("Got error from api: " + data.error);
        }
      })
      .catch((error) => {
        console.log("Error fetching image data:", error);
        setErrorData("Got error from api: " + error);
      });
  }, []);

  return (
    <div>
      {errorData && <h style={{ marginBottom: "10px" }}>{errorData}</h>}
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
