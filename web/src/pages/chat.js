import React, { useState } from 'react';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const sendMessage = () => {
    if (inputValue.trim() !== '') {
      const userMessage = { text: inputValue, sender: 'user' };
      setMessages([...messages, userMessage]);

      // Simulate server response
      setTimeout(() => {
        const serverMessage = { text: "Response from server WIP.", sender: 'server' };
        setMessages(currentMessages => [...currentMessages, serverMessage]);
      }, 1000);

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

