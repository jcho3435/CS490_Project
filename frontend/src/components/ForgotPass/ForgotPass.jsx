import React, { useState, useEffect } from 'react';
import './Forgot.css';
import { FLASK_URL, SITE_URL, setSessionLogin, setLocal, isExpired, Logout } from '../../vars';
import axios from 'axios';
import SHA256 from 'crypto-js/sha256';
import { useNavigate } from 'react-router-dom';

const ForgotPass = () => {

    const [credentials, setCredentials] = useState({
        email: '',
      });
    
    const handleUser = (e) => {
        const { name, value } = e.target;
        setCredentials({ ...credentials, [name]: value });
    };

    const handleUserSubmit = (e) => {
        e.preventDefault();
        changeUser();
    };

    const changeUser = () => {
        axios.post(`${FLASK_URL}/userSendEmail`, credentials)
            .then((response) => {
                const res = response.data;
                console.log(`Has error: ${res.hasError}`)
                if (res.success) {
                    alert(`Email link set!`);
                    delete credentials.email;
                    window.location.reload();
                }
                else if(res.hasError) {
                    console.log(`Errors: ${res.errorMessage}`)
                }
            }).catch((error) => {
                if (error.response) {
                    if (error.response == 500) {
                        alert(`BACKEND FAILED`);
                    }
                    else if (error.response == 'Email does not exist') {
                        alert(`Username or email does not exist`);
                    }
                    console.log(error.response);
                    console.log(error.response.status);
                    console.log(error.response.headers);
                }
            });
    };


    return(
        <div className="forgot-pass-container">
            <form onSubmit={handleUserSubmit}>
                <div className="username-box">
                    <h2>Reset Password</h2>
                    <label>Username or Email:</label>
                    <input
                    type="text"
                    name="email"
                    value={credentials.email}
                    onChange={handleUser}
                    className="username-control"
                    />
                <div className="reset-button-container">
                    <button type="submit" className="login-form-button">Send Link</button>
                </div>
                </div>
            </form>
        </div>
    )
}

export default ForgotPass;