import React from 'react';

function ArtOfTheDay(props) {
  // generate today's date in the format 'YYYY-MM-DD'
  // By defaul the timezone is the browsers timezone.
  const today = new Date().toISOString().slice(0, 10);
  const url = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${today}`;
  return (
    <div>
      <img src={url} alt="Art of the Day" />
    </div>
  );
}

export default ArtOfTheDay;

