import React, { useEffect, useState } from "react";
import "../App.css";

const FetchKnowledge = (title) => {
  const [result, setResult] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = () => {
    setIsLoading(true);
    fetch(
      "https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/knowledgequery?title=" +
        title
    )
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Sorry something went wrong");
        }
      })
      .then((data) => {
        setResult(data);
        setIsLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setIsLoading(false);
        console.error(error);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      {error && <p>{error}</p>}
      {isLoading && <p>Loading...</p>}
      {!isLoading && !error && (
        <div>
          <h1> Highlights: </h1>
          {result}
        </div>
      )}
    </div>
  );
};

export default function KnowledgeQuery(props) {
  return (
    <div>
      <FetchKnowledge title={props.match.params.title} />
    </div>
  );
}
