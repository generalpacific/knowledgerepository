import React, { useEffect, useState } from "react";
import pako from "pako";

function ArtOfTheDay(props) {
  const [imageData, setImageData] = useState(null);
  const [promptData, setPromptData] = useState(null);
  const [errorData, setErrorData] = useState(null);
  const [imageData1, setImageData1] = useState(null);
  const [promptData1, setPromptData1] = useState(null);
  const [errorData1, setErrorData1] = useState(null);
  const [imageData2, setImageData2] = useState(null);
  const [promptData2, setPromptData2] = useState(null);
  const [errorData2, setErrorData2] = useState(null);
  const [selectedDate, setSelectedDate] = useState("");

  useEffect(() => {
    setErrorData("")
    setErrorData1("")
    setErrorData2("")
    const url = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${selectedDate}`;
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
          setErrorData("Got error from api for index 0: " + data.error);
        }
      })
      .catch((error) => {
        console.log("Error fetching image data index 0:", error);
        setErrorData("Exception: Got error from api index 0: " + error);
      });
    const url1 = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${selectedDate}&index=1`;
    fetch(url1)
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
          setImageData1(decompressedBase64);
          setPromptData1(data.prompt);
        } else {
          setErrorData1("Got error from api index 1: " + data.error);
        }
      })
      .catch((error) => {
        console.log("Error fetching image data index 1:", error);
        setErrorData1("Exception: Got error from api index 1: " + error);
      });
    const url2 = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${selectedDate}&index=2`;
    fetch(url2)
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
          setImageData2(decompressedBase64);
          setPromptData2(data.prompt);
        } else {
          setErrorData2("Got error from api index 2: " + data.error);
        }
      })
      .catch((error) => {
        console.log("Error fetching image data index 2:", error);
        setErrorData2("Exception: Got error from api index 2: " + error);
      });
  }, [selectedDate]);


  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
  };

  return (
    <div>
      <h> Select date: </h>
      <input
        type="date"
        value={selectedDate}
        onChange={handleDateChange}
      />
      <div>
        <br /><br />
        {<h> Art 1: </h>}
        {errorData && <h style={{ marginBottom: "10px" }}>{errorData}</h>}
        {promptData && <h style={{ marginBottom: "10px" }}>{promptData}</h>}
        <br />
        <br />
        {imageData && (
          <img src={`data:image/png;base64,${imageData}`} alt="Art of the Day" />
        )}
      </div>
      <div>
        <br /><br />
        {<h> Art 2: </h>}
        {errorData1 && <h style={{ marginBottom: "10px" }}>{errorData1}</h>}
        {promptData1 && <h style={{ marginBottom: "10px" }}>{promptData1}</h>}
        <br />
        <br />
        {imageData1 && (
          <img src={`data:image/png;base64,${imageData1}`} alt="Art of the Day 1" />
        )}
      </div>
      <div>
        <br /><br />
        {<h> Art 3: </h>}
        {errorData2 && <h style={{ marginBottom: "10px" }}>{errorData2}</h>}
        {promptData2 && <h style={{ marginBottom: "10px" }}>{promptData2}</h>}
        <br />
        <br />
        {imageData2 && (
          <img src={`data:image/png;base64,${imageData2}`} alt="Art of the Day 2" />
        )}
      </div>
    </div>
  );
}

export default ArtOfTheDay;
