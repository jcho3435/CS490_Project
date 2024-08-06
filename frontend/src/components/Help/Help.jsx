import React, { useState } from 'react';
import SearchBar from './SearchBar'; // Changed to uppercase
import HelpContent from './HelpContent'; // Changed to uppercase
import './Help.css';
import UserGuide from './UserGuide';
import faq from './faq.svg';
import { FLASK_URL, SITE_URL, Logout } from '../../vars.js';

function Help() {
  const [searchQuery, setSearchQuery] = useState('');

  // Function to handle search query change
  const handleSearchChange = (query) => {
    setSearchQuery(query);
  };

  if (!(localStorage.getItem("isLoggedIn") === "true")) window.location.assign(`${SITE_URL}/login?redirect=true`);
  else {
  return (
    <div>
          <div className='help-title-container'>
              <p className='title'>codeCraft Help Center</p>
              <p className='subtitle'>Have questions? Here you'll find the answers!</p> 
          </div>
        <div>
            <div style={{ marginTop: '20px' }}>
                <SearchBar onSearchChange={handleSearchChange} /> {/* Changed to uppercase */}
            </div>
            <div style={{ marginTop: '20px' }}>
                <HelpContent searchQuery={searchQuery} style={{visibility:'visible'}}/> 
            </div>
            <div style={{ marginTop: '20px' }}>
                <UserGuide/> 
            </div>
            <div style={{ marginTop: '70px' }}>
              <p className='resources'>Still having trouble? Here are some resources that might help: </p>
              <div style={{ marginBottom: '5rem', display: 'flex', justifyContent: 'space-between', margin: '0 auto', maxWidth: '800px' }}>
                <div className='left-box'>
                  <p className='resources'>Resources</p>
                  <ul>
                    <li><a href="https://machinelearningmastery.com/using-chatgpt-for-translation-effectively/" target="_blank">Using chatGPT for effective code translation</a></li>
                    <li><a href="https://gpt.space/blog/can-chat-gpt-translate#:~:text=Chat%20GPT%20is%20a%20large,questions%20in%20an%20informative%20way." target="_blank">How does it work</a></li>
                  </ul>
                </div>
                <div className='right-box'>
                  <p className='resources'>Contact us</p>
                  <ul>
                    <li>support@codeCraft.com</li>
                    <li>+1 973-000-0000</li>
                  </ul>
                </div>
              </div>
            </div>
        </div>
    </div>
  );
 }
}

export default Help;