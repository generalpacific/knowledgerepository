import React from 'react';

function ArtOfTheDay(props) {
  return (
    <div>
      <img src='https://6h5c17qwla.execute-api.us-east-2.amazonaws.com/prod/artoftheday?date=2023-05-14' alt="API Image" />
    </div>
  );
}

export default ArtOfTheDay;

