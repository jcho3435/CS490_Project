import React, { useState, useEffect } from 'react';
import './ResetPass.css';
import { FLASK_URL, SITE_URL, setSessionLogin, setLocal, isExpired, Logout } from '../../vars';
import axios from 'axios';
import SHA256 from 'crypto-js/sha256';
import { useHistory, useNavigate } from 'react-router-dom';

const ForgotPass = () => {
    const navigate = useNavigate()
    
    const [newPass, setNewPass] = useState({
        password: '',
        conf: ''
      });
    
    const handlePassChange = (e) => {
        const { name, value } = e.target;
        setNewPass({ ...newPass, [name]: value });
        
    };

    const handlePassSubmit = (e) => {
        console.log(e); 
        e.preventDefault();
        changePass();
    };

    const validatePassword = () => {
        const password = newPass.password || '';
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

      const changePass = () => {
        const newhash = SHA256(newPass.password + "CS490!").toString();
        const queryParameters = new URLSearchParams(window.location.search);
        const user = queryParameters.get("token")
        const check = {
            newPass: newhash,
            emailToken: user,
        };
        console.log(`Token: ${user}`)
        if (newPass.password != newPass.conf) {
            alert(`New and confirmed are different. Change it to match!`);
            return;
        }

        if (!validatePassword(newPass.password)) {
            alert('Password must be at least 8 characters long, have a special character, and number.')
            return;
        }
        
        axios.post(`${FLASK_URL}/userResetPassword`, check)
            .then((response) => {
                const res = response.data;
                if (res.success) {
                    delete newPass.conf;
                    delete newPass.password;
                    alert(`NEW PASSWORD CHANGED SUCCESSFUL!`);
                }
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                console.log(`Response has error: ${res.hasError}`);
                if (res.logout) {
                    alert("Session expired. Please login again..")
                    Logout(navigate)
                }
            }).catch((error) => {
                if (error.response) {
                    if (error.response == '500 (INTERNAL SERVER ERROR)') {
                        alert(`BACKEND FAILED`);
                    }
                    console.log(error.response);
                    console.log(error.response.status);
                    console.log(error.response.headers);
                }
            });
    };

    return(
        <div className="forgot-pass-container">
            <form onSubmit={handlePassSubmit}> 
                        <div className='change_password'>
                            <h2>Change Password</h2>
                            <p className="note">Password must be at least 8 characters long, have a special character, and number</p>
                            <div className="login-form-group">
                                <label>New Password:</label>
                                <input
                                    type="password"
                                    name="password"
                                    value={newPass.password}
                                    onChange={handlePassChange}
                                    className="login-form-control"
                                />
                            </div>
                            <div className="login-form-group">
                                <label>Confirm Password:</label>
                                <input
                                    type="password"
                                    name="conf"
                                    value={newPass.conf}
                                    onChange={handlePassChange}
                                    className="login-form-control"
                                />
                                <div className="login-button-container">
                                    <button type="submit" className="login-form-button">Submit</button>
                                </div>
                            </div>
                        </div>
            </form>
        </div>
    )
}

export default ForgotPass;