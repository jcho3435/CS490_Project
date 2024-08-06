import React, { useState, useEffect } from 'react';
import './LoginPage.css';
import { FLASK_URL, setLocal, isExpired, Logout, isLoggedIn } from '../../vars';
import axios from 'axios';
import SHA256 from 'crypto-js/sha256';
import { useNavigate, useLocation } from 'react-router-dom';
import NavBar from '../navbar/NavBar';
import eyeicon from './eyeicon.svg';
import { ToastContainer, toast } from 'react-toastify';


const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  const location = useLocation();
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [is2FASuccess, setIs2FASuccess] = useState(false);

  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
    rememberMe: false
  });

  const [loggedInUser, setLoggedInUser] = useState('');
  const navigate = useNavigate(); // Initialize useNavigate hook
  const [width, setWidth] = useState();

  useEffect(() => {
    // Check if user is already logged in
    if (sessionStorage.getItem('isLoggedIn')) {
      setLoggedInUser(sessionStorage.getItem('username'));
      setWidth({
        maxWidth: '100rem',
        height: '50rem',
      });
    }
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    setCredentials({ ...credentials, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    login();
    console.log('Login credentials:', credentials);
  };

  var res;
  const login = () => {
    const hashedPassword = SHA256(credentials.password + "CS490!").toString();
    const key = SHA256(credentials.password + "2FAkey").toString();
    delete credentials.password;
    const loginData = {
      ...credentials,
      password: hashedPassword,
      key: key,
    };

    axios.post(`${FLASK_URL}/userLoginCredentials`, loginData)
      .then((response) => {
        res = response.data;
        if (res.success) {
          setLocal(res.sessionToken, credentials.username, Math.floor(Date.now() / 1000), credentials.rememberMe);
          const is2FAEnabled = (res.totp === "enabled");
          check2FA(is2FAEnabled);
          // delete credentials.username;
          // delete credentials.password;
          // setMessage(`Welcome to codeCraft!`);
          // showAlert();
          // setTimeout(() => {
          //   window.location.href = '/';
          // }, 2000);
        }
        if (res.hasError) {
          console.log(`Error response: ${res.errorMessage}`);
          toast(`${res.errorMessage}`, {
            className: 'fail',
            autoClose: 2000
          });
        }
        console.log(`Response has error: ${res.hasError}`);
      }).catch((error) => {
        if (error.response) {
          toast(`${error.response}`, {
            className: 'fail',
            autoClose: 2000
          });
          console.log(error.response);
          console.log(error.response.status);
          console.log(error.response.headers);
        }
      });
  };

  const check2FA = (isEnabled) => {
    if (isEnabled == true) {
      setTimeout(() => {
        window.location.href = '/login/2FA';
      }, 500);
    }
    else {
      localStorage.setItem("isLoggedIn", true);
      setTimeout(() => {
        window.location.href = '/';
      }, 500);
      toast(`Welcome to codeCraft!`, {
        className: 'success',
        autoClose: 2000
      });
    }
  };



  return (
    <div>
      <ToastContainer position='top-center' style={{ zIndex: 1100 }}/>
      <div className="login-page-container">
        <div className="login-form-box">
          {!(localStorage.getItem("isLoggedIn") === "true") &&
            <form onSubmit={handleSubmit}>
              <h2>Login</h2>
              <div className="login-form-group">
                <label htmlFor="Username or Email:" id="Username or Email:">Username or Email:</label>
                <input
                  id="Username or Email:"
                  type="text"
                  name="username"
                  value={credentials.username}
                  onChange={handleChange}
                  className="login-form-control"
                  data-testid="username-input"
                />
              </div>
              <div className="login-form-group">
                <label htmlFor="password">Password:</label>
                <div className="password-container">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={credentials.password}
                    onChange={handleChange}
                    className="login-form-control"
                    data-testid="password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="show-password-button"
                  >
                    <img src={eyeicon} className='eye-icon' alt="eyeicon" />
                  </button>
                </div>
                <div className="login-form-group">
                  <label>
                    <input
                      type="checkbox"
                      name="rememberMe"
                      checked={credentials.rememberMe}
                      onChange={handleChange}
                    /> Remember Me
                  </label>
                </div>
                <p><a href='/register'>
                  Don't have an account? Register here
                </a></p>
                <a href='/forgotpassword'>
                  Forgot password?
                </a>
                <div className="login-button-container">
                  <button type="submit" className="login-form-button">Login</button>
                </div>
              </div>
            </form>
          }
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
