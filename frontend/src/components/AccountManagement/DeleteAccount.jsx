import React, { useState, useEffect } from 'react';
import { SITE_URL, FLASK_URL, setSessionLogin, isExpired, Logout } from '../../vars';
import axios from 'axios';
import './AccountManagement.css';
import { ToastContainer, toast } from 'react-toastify';


const DeleteAccount = () => {
    const handleDelete = (e) => {
        e.preventDefault();
        if (window.confirm("Are you sure you want to delete your account?")) {
            deleteAccount();
        }
    }
    
    const deleteAccount = () => {
        const user = localStorage.getItem("sessionToken");

        axios.post(`${FLASK_URL}/deleteAccount`, { sessionToken: user })
            .then((response) => {
                const res = response.data;
                if (res.success) {
                    toast(`Account deleted!`, {
                        className: 'success',
                        autoClose: 2000
                      });
                    setTimeout(Logout, 0);
                    setTimeout(() => { window.location.href = `${SITE_URL}/login?redirect=true`; }, 500);
                }
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                console.log(`Response has error: ${res.hasError}`);
                if (res.logout) {
                    toast(`Deletion failed, session expired. Please login again.`,{
                        className: 'fail',
                        autoClose: 2000
                      });
                    toast(`Deletion failed, session expired. Please login again.`);
                    setTimeout(Logout, 2000);
                    setTimeout(() => {window.location.href = SITE_URL}, 2000);
                }
            }).catch((error, response) => {
                if (error.response) {
                    toast(`Backend has failed.`, {
                        className: 'fail',
                        autoClose: 2000
                      });
                    console.log(error.response);
                    console.log(error.response.status);
                    console.log(error.response.headers);
                }
            });
    };

    return(
        <div className="box-container">
            <ToastContainer position='top-center' style={{ zIndex: 1100 }}/>
            <div className='login-form-box'>
                <p className="note">Please note that once you delete your account, you cannot log back in or reactivate your account</p>
                <form onSubmit={handleDelete}>
                    <div>
                        <button type='submit' className='delete-form-button'>Delete Account</button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default DeleteAccount;