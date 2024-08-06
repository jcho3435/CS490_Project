import { React, useState } from 'react';
import { Link } from 'react-router-dom';
import logo3 from './logo3.webp';
import './NavBar.css';
import profile from './Profile.png'; 
import MiniMenu from './MiniMenu';
import LazyImage from './LazyImage';

const NavBar = () => {

const [isMenuOpen, setIsMenuOpen] = useState(false);

  const isLoggedIn = (localStorage.getItem("isLoggedIn") === "true");
  const username = localStorage.getItem("username");


  return (
    <div className="nav-bar">
      <div className="nav-bar-banner">
        <div className="nav-bar-logo-container">
          <Link to={'/'} data-testid='lin'>
            <LazyImage src={logo3} alt="Logo" width="200px" height="90px" />
          </Link>
        </div>
        <div className="nav-bar-links">
          <ul>
            <Link to={'/translate'} style={{ textDecoration: 'none' }} data-testid='translink'>
              <li>Translator</li>
            </Link>
            {/* <Link to={'/refernces'} style={{ textDecoration: 'none' }} data-testid='reflink'>
            <li>References</li>
            </Link> */}
            <Link to={'/feedback'} style={{ textDecoration: 'none' }} data-testid='feedlink'>
            <li>Feedback</li>
            </Link>
            <Link to={'/help'} style={{ textDecoration: 'none' }} data-testid='helplink'>
            <li>Help</li>
            </Link>
            <Link to={'/releasenotes'} style={{ textDecoration: 'none' }} data-testid='releaselink'>
            <li>Release Notes</li>
            </Link>
          </ul>
        </div>
        {/* <div className='nav-bar-log-in'>
          <Link to={'/login'} data-testid='prof'>
            <img src={profile} height={40} alt="Profile"/>
          </Link>
          {
            isLoggedIn &&
            <p className="username">{username}</p>
          }
        </div> */}
        <div className='nav-bar-log-in'>
          { //if they're not logged in, when they click, send to login
            !(isLoggedIn) && 
            <div>
              <Link to={'/login'} data-testid='prof'>
                <img src={profile} height={40} alt="Profile" />
              </Link>
            </div>
          }
          { //if they are loggedin, hovering over will show minimenu
            isLoggedIn && 
            <div>
              <div
                onMouseEnter={() => setIsMenuOpen(true)}
                onMouseLeave={() => setIsMenuOpen(false)}
                data-testid='prof'
              >
                <img src={profile} height={40} alt="Profile" />
                {isMenuOpen && <MiniMenu />}
              </div>
              <p className="username">{username}</p>
            </div>
          }
          
        </div>
        
      </div>
    </div>
  );
};

export default NavBar;