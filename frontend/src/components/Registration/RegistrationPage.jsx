import React, { useState } from 'react';
import axios from 'axios'
import { FLASK_URL, SITE_URL, setSessionLogin } from '../../vars';
import './RegistrationPage.css';
import SHA256 from 'crypto-js/sha256';
import { setLocal } from '../../vars';
import { ToastContainer, toast } from 'react-toastify';
import eyeicon from './eyeicon.svg';


const RegistrationPage = () => {
  const [showPassword, setShowPassword] = useState(false);

  const [user, setUser] = useState({
    username: '',
    email: '',
    password: '',
  });

  const handleCheck = (message) => {
    switch (message){
      case 'stop': case 'from_db':
        return "Translation Success!!"
        break;
      case 'length':
        return "Unsuccessful Translation :((, input text is too long"
        break;
      case 'content_filter':
        return "Code content was flagged by openai content filters"
        break;
      case '401':
        return "OpenAI API Authentication failed "
        break;
      case '403':
        return "Country not supported with OpenAI"
        break;
      case '429':
        return "Please wait you sent too many characters"
        break;
      case '500':
        return "Unknown OpenAI server error"
        break;
      case '503':
        return "OpenAI server is currently being overloaded, please before submitting again"
        break;
      default:
        return message
        break;
    }
  }
  const [error, setError] = useState(null);
  // use this if toast breaks again lmfao
  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser({ ...user, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateUsername()) {
      toast(handleCheck("Username must be between 8 to 24 characters and can only contain alphanumeric characters, underscores, and hyphens."), {
        className: 'fail',
        autoClose: 2000
      });
      return;
    }
    if (!validateEmail()) {
      toast(handleCheck("Please enter a valid email address."), {
        className: 'fail',
        autoClose: 2000
      });
      return;
    }

     if (!validatePassword(user.password)) {
      toast(handleCheck('Password must be at least 8 characters long, have a special character, and number.'), {
          className: 'fail',
          autoClose: 2000
        });
      return;
     }

    register();
    console.log('Registration details:', user);
  };

  const validateUsername = () => {
    return /^(?=[a-zA-Z0-9_])(?!.*?_{2,})[a-zA-Z0-9_-]{8,24}$/.test(user.username);
  }

  const validateEmail = () => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email);
  }

  const validatePassword = () => {
    const password = user.password || '';
    // Check if password length is at least 8 characters
    if (password.length < 8) {
      return false;
    }
    // Check if password contains at least one number
    if (!/\d/.test(password)) {
      return false;
    }
    // Check if password contains at least one special character
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return false;
    }
    return true;
  }

  var res
  const register = () => {
    
    const hashedPassword = SHA256(user.password + "CS490!").toString()
    delete user.password
    const userData = {
      ...user,
      password: hashedPassword
    };

    axios.post(`${FLASK_URL}/registerNewUser`, userData)
    .then((response) => {
      res = response.data
      if (res.success) {
        setLocal(res.sessionToken, user.username, Math.floor(Date.now() / 1000))
        localStorage.setItem("isLoggedIn", true);
        delete user.username 
        delete user.email
        toast(handleCheck('Registration Success!'),  {
          className: 'success',
          autoClose: 2000
        })
        setTimeout(() => {window.location.href = '/'}, 2000);
      }
      console.log(`Response has error: ${res.hasError}`)
      toast(handleCheck(`${res.errorMessage}`),  {
        className: 'fail',
        autoClose: 2000
      })
      if(res.usernameErrors) {
        console.log(`Username errors: ${res.usernameErrors}`)
        toast(handleCheck(`${res.usernameErrors}`),  {
          className: 'fail',
          autoClose: 2000
        })
      if(res.emailErrors) {
        console.log(`Email errors: ${res.emailErrors}`)
        toast(handleCheck(`${res.emailErrors}`), {
          className: 'fail',
          autoClose: 2000
        })
        }
      if(res.errorMessage) console.log(`Other errors: ${res.errorMessage}`)
      if(res.sqlErrors && res.sqlErrors.length > 0) { // TODO: This is where we will see information on duplicate username or email - make sure to handle this
        toast(handleCheck(`${res.sqlErrors}`),  {
          className: 'fail',
          autoClose: 2000
        })
        console.log(`SQL Errors: ${res.sqlErrors}`)
      }
    }}).catch((error) => {
      if (error.response) {
        toast(handleCheck(`${error.response}`), {
          className: 'fail',
          autoClose: 2000
        })
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })
  }

  if ((localStorage.getItem("isLoggedIn") === "true")) window.location.assign(`${SITE_URL}?redirect=true`)
  else
  {  
    return (
      <div className="registration-page-container">
        <div className="registration-form-box">
        <ToastContainer position='top-center' style={{ zIndex: 1100 }}/>
          <form onSubmit={handleSubmit}>
            <h2 className="registration-form-title">Register</h2>
            <div className="registration-form-group">
              <label htmlFor='Username'>Username:</label>
              <input 
                id="Username"
                type="text" 
                name="username" 
                value={user.username} 
                onChange={handleChange} 
                className="registration-form-control"
                required
              />
            </div>
            <div className="registration-form-group">
              <label htmlFor='Email'>Email:</label>
              <input 
                id='Email'
                type="email" 
                name="email" 
                value={user.email} 
                onChange={handleChange} 
                className="registration-form-control"
                required
              />
            </div>
            <div className="registration-form-group">
              <label htmlFor='Password:' >Password:</label>
              <div className="password-container">
                <input
                  data-testid="Password:"
                  id='Password:'
                  type="password" 
                  name="password" 
                  value={user.password} 
                  onChange={handleChange} 
                  className="registration-form-control"
                  required
                />
                <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="show-password-button"
                  >
                      <img src={eyeicon} className='eye-icon' alt="eyeicon" />
                  </button></div>
            </div>
            <div className="registration-button-container">
              <button type="submit" className="registration-form-button">Register</button>
            </div>
          </form>
        </div>
      </div>
    );
  }
};

export default RegistrationPage;