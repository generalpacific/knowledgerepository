import React from 'react';

function ArtOfTheDay(props) {
  // generate today's date in the format 'YYYY-MM-DD'
  const tzOffset = new Date().getTimezoneOffset() * 60000; // Timezone offset in milliseconds
  const today = new Date(Date.now() - tzOffset).toISOString().slice(0, 10);
  console.error("Calling artoftheday for: " + today)
  const url = `https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=${today}`;
  return (
    <div>
      <img src={url} alt="Art of the Day" />
    </div>
  );
}

export default ArtOfTheDay;

