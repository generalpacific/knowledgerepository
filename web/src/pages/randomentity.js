import React, { useEffect, useState } from "react";
import { Tweet } from "react-twitter-widgets";
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
          <Tweet
            tweetId={randomData.tweet_id}
            options={{ conversation: "none", width: "400px" }}
          />
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
        <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100vh', // This will take the full height of the viewport
            fontSize: '2rem', // Adjust this value to increase or decrease the size
            textAlign: 'center' // Ensures the text is centered if it wraps to a new line
        }}>
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
