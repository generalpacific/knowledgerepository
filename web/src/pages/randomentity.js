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
        const digest = data["digest"];
        const randomIndex = Math.floor(Math.random() * digest.length);
        const randomData = digest[randomIndex];

        const content = randomData.highlight !== undefined ? (
          randomData.highlight
        ) : randomData.quote !== undefined ? (
          randomData.quote
        ) : (
          // Updated this part for responsiveness
          <div style={{ maxWidth: '100%', overflow: 'hidden' }}>
            <Tweet
              tweetId={randomData.tweet_id}
              options={{ conversation: "none", cards: 'hidden' }}
            />
          </div>
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
    <div className="content-container">
      {error && <p>{error}</p>}
      {!error && <div>{randomEntity}</div>}
    </div>
  );
};

export default function RandomEntity() {
  return (
    <div className="app-container">
      <FetchDigest />
    </div>
  );
}

