import logo from '../logo.svg';
import React, { useEffect, useState } from "react"
import { Tweet } from 'react-twitter-widgets'
import '../App.css';

const UpvoteButtonHandler = (entityid, setPlusOneStatus) => {
          const requestOptions = {
            method: 'POST',
            headers: { 
              'Content-Type' : 'application/json'},
          };
          const encoded_id = encodeURIComponent(entityid)
          fetch(`https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/plusone?entityid=${encoded_id}`, requestOptions)
          .then(response => {
              setPlusOneStatus("Successfully plusoned!")
          })
          .catch(error => {
             console.error(error);
             setPlusOneStatus(error);
          });   
}

const FetchDigest = () => {
  const [digest, setDigest] = useState([])
  const [error, setError] = useState("")
  const [plusOneStatus, setPlusOneStatus] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const fetchData = () => {
    setIsLoading(true)
    fetch("https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/dailydigest")
      .then(response => {
         if (response.ok) {
          return response.json()
        } else {
          throw new Error("Sorry something went wrong")
        }
      })
      .then(data => {
        setDigest(data['digest'])
        setIsLoading(false)
      })
      .catch(error => {
          setError(error.message)
          setIsLoading(false)
          console.error(error);
      })
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div>
      {error && <p>{error}</p>}
      {plusOneStatus && <p>{plusOneStatus}</p>}
      {isLoading && <p>Loading...</p>}
      {!isLoading && !error && (
        <div>
        <h1> Digest: </h1> 
       
          <tbody>
            <tr>
              <th>Highlight</th>
              <th>Upvote</th>
            </tr>
            {digest.map((data, key) => {
              return (
                <tr key={key}>
                  <td><q>{data[`highlight`] !== undefined ? data.highlight : data['quote'] !== undefined ? data.quote : <Tweet tweetId={data.tweet_id} options={{conversation: 'none', width: '400'}}/>}</q></td>
                  <td><button onClick={() => UpvoteButtonHandler(data.entityid, setPlusOneStatus)}>+1</button></td>
                </tr>
              );
            })}
          </tbody>
  
        </div>
      )}
    </div>
  )
}

export default function KnowledgeDailyDigest() {
  return (
    <div>
      <FetchDigest />
    </div>
  );
}
