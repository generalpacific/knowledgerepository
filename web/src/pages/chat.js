import React, { useState } from 'react';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const sendMessage = () => {
    if (inputValue.trim() !== '') {
      const userMessage = { text: inputValue, sender: 'user' };
      setMessages([...messages, userMessage]);

      // Send request to server
      fetch("https://9xj3ly8j6i.execute-api.us-east-2.amazonaws.com/prod/chat?chatinput=" +
        encodeURIComponent(inputValue), {
      })
      .then(response => response.json())
      .then(data => {
        const serverMessage = { text: data.response, sender: 'server' };
        setMessages(currentMessages => [...currentMessages, serverMessage]);
      })
      .catch(error => {
        console.error('Error sending message:', error);
        const errorMessage = { text: "Error sending message. Please try again later.", sender: 'server' };
        setMessages(currentMessages => [...currentMessages, errorMessage]);
      });

      setInputValue('');
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div>
      <div style={{ height: '300px', overflowY: 'scroll', border: '1px solid black', marginBottom: '10px' }}>
        {messages.map((message, index) => (
          <div key={index} style={{ textAlign: message.sender === 'user' ? 'right' : 'left' }}>
            {message.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        style={{ marginRight: '5px' }}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default Chat;

