import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { GoogleOAuthProvider } from '@react-oauth/google';

const GoogleLoginButton = () => {
  const responseGoogle = (response) => {
    console.log(response);
    // Handle successful login here
  };

  const onFailure = (error) => {
    console.log(error);
    // Handle login failure here
  };

  return (
    <div>
      <h2>React Google Login</h2>
      <br />
      <br />
      <GoogleOAuthProvider clientId="481783681600-g219mmrl19blv252h8b6t10981rqi8bq.apps.googleusercontent.com">
        <GoogleLogin
          buttonText="Sign in with Google"
          onSuccess={responseGoogle}
          onFailure={onFailure}
        />
      </GoogleOAuthProvider>
    </div>
  );
};

export default GoogleLoginButton;

