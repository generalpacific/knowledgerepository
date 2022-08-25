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
  const [twitterDigest, setTwitterDigest] = useState([])
  const [notionDigest, setNotionDigest] = useState([])
  const [kindleDigest, setKindleDigest] = useState([])
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
        setTwitterDigest(data['TWITTER'])
        setKindleDigest(data['KINDLE'])
        setNotionDigest(data['NOTION'])
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
       
        <h2>Kindle:</h2>
        {/*<pre>{JSON.stringify(twitterDigest, null, 2) }</pre>*/}
          <tbody>
            <tr>
              <th>Highlight</th>
              <th>Upvote</th>
              <th>Score</th>
              <th>Title</th>
              <th>Author</th>
            </tr>
            {kindleDigest.map((data, key) => {
              return (
                <tr key={key}>
                  <td><q>{data.highlight}</q></td>
                  <td><button onClick={() => UpvoteButtonHandler(data.entityid, setPlusOneStatus)}>+1</button></td>
                  <td>{data.plusones}</td>
                  <td>{data.title}</td>
                  <td>{data.author}</td>
                </tr>
              );
            })}
          </tbody>
  
        <h2>Notion:</h2>
          {/*<pre>{JSON.stringify(twitterDigest, null, 2) }</pre>*/}
          <tbody>
            <tr>
              <th>Highlight</th>
              <th>Upvote</th>
              <th>Score</th>
              <th>Title</th>
              <th>Author</th>
            </tr>
            {notionDigest.map((data, key) => {
              return (
                <tr key={key}>
                  <td><q>{data.quote}</q></td>
                  <td><button onClick={() => UpvoteButtonHandler(data.entityid, setPlusOneStatus)}>+1</button></td>
                  <td>{data.plusones}</td>
                  <td>{data.title}</td>
                  <td>{data.author}</td>
                </tr>
              );
            })}
          </tbody>
      
        <h2>Twitter:</h2>
          {/*<pre>{JSON.stringify(twitterDigest, null, 2) }</pre>*/}
          <tbody>
            <tr>
              <th>Tweet</th>
              <th>Upvote</th>
              <th>Score</th>
            </tr>
          {twitterDigest.map((data, key) => {
              return (
                <tr key={key}>
                {/*<td>{data.embedded_tweet}</td>*/}
                  <td><Tweet tweetId={data.tweet_id} /></td>
                  <td><button onClick={() => UpvoteButtonHandler(data.entityid, setPlusOneStatus)}>+1</button></td>
                  <td>{data.plusones}</td>
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
