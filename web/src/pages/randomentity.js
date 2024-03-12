import React, { useEffect, useState } from "react";
import { Tooltip } from "@mui/material";
import { Tweet } from "react-twitter-widgets";
import { useNavigate } from "react-router-dom";
import "../App.css";

const FetchDigest = () => {
  const [randomEntity, setRandomEntity] = useState([]);
  const [error, setError] = useState("");

  const fetchData = () => {
    fetch(
      "https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/dailydigest"
    )
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Sorry something went wrong");
        }
      })
      .then((data) => {
        var digest = data["digest"]
        // Select a random quote from the digest
        const randomIndex = Math.floor(Math.random() * digest.length);
        const randomData = digest[randomIndex];

        // Determine content to display based on the data type
        const content = randomData.highlight !== undefined ? (
          randomData.highlight
        ) : randomData.quote !== undefined ? (
          randomData.quote
        ) : (
          "No quote available for this item."
        );
        setRandomEntity(content);
      })
      .catch((error) => {
        setError(error.message);
        console.error(error);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      {error && <p>{error}</p>}
      {!error && (
        <div>
          <h1> Entity: </h1>
          <p>{randomEntity}</p>
        </div>
      )}
    </div>
  );
};

export default function RandomEntity() {
  return (
    <div>
      <FetchDigest/>
    </div>
  );
}
