import React, { useState, useRef, useEffect } from 'react';
import './LoginPage.css';
import { FLASK_URL, setLocal, isExpired, Logout, isLoggedIn } from '../../vars';
import axios from 'axios';
import SHA256 from 'crypto-js/sha256';
import { useNavigate } from 'react-router-dom';
import NavBar from '../navbar/NavBar';
import eyeicon from './eyeicon.svg';
import { ToastContainer, toast } from 'react-toastify';


const TwoFAcode = () => {
    const navigate = useNavigate();
    const [code, setCode] = useState(Array(6).fill(""));
    const inputsRef = useRef([]);

    const handleSubmit = (event) => {
        event.preventDefault();
        const pinValue = code.join('');
        const user = localStorage.getItem("sessionToken");
        console.log(`TOKEN inside 2FA page ${localStorage.getItem("sessionToken")}`);
        console.log(`PIN CODE inside 2FA page ${[pinValue]}`);
        const passcodeData = {
            sessionToken: user,
            passcode: pinValue,
        };

        axios.post(`${FLASK_URL}/validateTOTP`, passcodeData)
            .then(response => {
                console.log('Verification response:', response.data);
                // TODO: redirect to home page and show success message
                const res = response.data;
                if (res.success) {
                    // setLocal(res.sessionToken, credentials.username, Math.floor(Date.now() / 1000), credentials.rememberMe, true);
                    localStorage.setItem("isLoggedIn", true);
                    toast(`Login successful!`, {
                        className: 'success',
                        autoClose: 2000
                      });
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 500);
                }
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                console.log(`Response has error: ${res.hasError}`);
                if (res.logout) {
                    toast(`Session expired. Please login again.`, {
                        className: 'fail',
                        autoClose: 2000
                      });
                    setTimeout(Logout, 4000);
                }
            })
            .catch(error => {
                console.error('Verification error:', error);
                // TODO: failed verification message
            });
    };


    const handleInput = (index, event) => {
        const nums = [...code];
        nums[index] = event.target.value;
        setCode(nums);

        if (event.target.value && index < 5) {
            inputsRef.current[index + 1].focus();
        }
    };

    const handleBackspace = (index, event) => {
        if (event.key === "Backspace" && !code[index]) {
            if (index > 0) {
                inputsRef.current[index - 1].focus();
            }
        }
    };

   if (localStorage.getItem("isLoggedIn") != "false") window.location.href = "/"
        else {
    return (
        
        <div className="login-page-container">
            <ToastContainer position='top-center'/>
            <form onSubmit={handleSubmit}>
                <div className='login-form-box-2fa'>
                    <div className="login-form-group">
                        <label>Please enter your 6-digit code:</label>
                        <div className="input-container">
                            {code.map((num, index) => (
                                <input
                                    key={index}
                                    type="text"
                                    maxLength="1"
                                    value={num}
                                    onChange={e => handleInput(index, e)}
                                    onKeyDown={e => handleBackspace(index, e)}
                                    className="login-form-control digit-input"
                                    ref={el => inputsRef.current[index] = el}
                                    data-testid={`digit-input-${index}`}
                                />
                            ))}
                           </div>
                        </div>
                        <div className="login-button-container">
                            <button type="submit" className="login-form-button" data-testid='submit-button'>Submit</button>
                        </div>
                    </div>
                </form>
            </div>
        );
    }
};

export default TwoFAcode; 