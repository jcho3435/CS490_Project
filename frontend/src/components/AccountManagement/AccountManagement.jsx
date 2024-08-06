import React, { useState, useEffect } from 'react';
import { SITE_URL, FLASK_URL, setSessionLogin, setLocal, isExpired, Logout } from '../../vars';
import axios from 'axios';
import './AccountManagement.css';
import { Link } from 'react-router-dom';

// account management needs to take care of 3 things:
// 1. username changing
// 2. password changing
// 3. delete account
// # all functions handling this will be in this file as they are not needed elsewhere

const AccountManagement = () => { 

    return (
        <div>
            <div className='left-sidebar'>
                <ul>
                    <li><Link to="/accountmanagement/changeusername">Change Username</Link></li>
                    <li><Link to="/accountmanagement/changepassword">Change Password</Link></li>
                    <li><Link to="/accountmanagement/deleteaccount">Delete Account</Link></li>
                </ul>
            </div>
            <div>
                <h1>Welcome, {localStorage.getItem("username")}!</h1>

            </div>
        </div>
    );
};

export default AccountManagement;