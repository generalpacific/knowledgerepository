import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "react-router-dom";
import "../App.css";

const FetchKnowledge = ({ title, source }) => {
  const [result, setResult] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = useCallback(() => {
    setIsLoading(true);
    const titleString = encodeURIComponent(title);
    const sourceString = encodeURIComponent(source);
    fetch(
      "https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/knowledgequery?source=" +
        sourceString +
        "&title=" +
        titleString
    )
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Sorry something went wrong");
        }
      })
      .then((data) => {
        console.info("Got data");
        setResult(data);
        setIsLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setIsLoading(false);
        console.error(error);
      });
  }, [title, source]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div>
      {error && <p>{error}</p>}
      {isLoading && <p>Loading...</p>}
      {!isLoading && !error && (
        <div>
          <h1> Highlights: </h1>
          <h2> Title: {title.title} </h2>
          {result
            .sort((a, b) => b[1] - a[1])
            .map((item, index) => (
              <p key={index} style={{ fontSize: 15 + 2 * item[1] }}>
                {item[0]}
              </p>
            ))}
        </div>
      )}
    </div>
  );
};

export default function KnowledgeQuery() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const title = queryParams.get("title");
  const source = queryParams.get("source");

  return (
    <div>
      <FetchKnowledge title={title} source={source} />
    </div>
  );
}
