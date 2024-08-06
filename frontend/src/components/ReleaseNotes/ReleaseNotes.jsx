import React from 'react';
import './ReleaseNotes.css'
import { Link } from 'react-router-dom';
import tottime from './CS490 screenshots/total time.png'
import caching from './CS490 screenshots/caching comparison.png'


const ReleaseNotes = () => {
    return (
        <div className='holder'>
            <div className='release-container'>
                <div className='code-title'>
                    <h1><b>codecraft v1.0</b></h1>
                    <a>Welcome to the the 1.0 release of codecraft, your favorite code translation tool.</a>
                    <p>Here we describe our tech stack improvements and new changes.</p>
                </div>
                <div className='tech-stck'>
                    <h2 className='titles'>Tech Stack</h2>
                    <p>Our tech stack was decided upon by a group preference. This is our final selection.</p>
                    <ul>
                        <li><b>Frontend-React:</b> React is our frontend due to our team already having experience and it being a standard in today’s web.</li>
                        <li><b>Backend-Flask:</b> Flask is our backend due to our team being very familiar with python and Flask has very good documentation.</li>
                        <li><b>Database-MySQL:</b> MySQL is easy to setup, works well with almost every package and has good scalability for further upgrades.</li>
                        <li><b>Authentication-Self Hosted:</b> As a team we decided to host our own authentication holding our sessions and never hosting a plain text password.</li>
                        <li><b>Testing-Jest&PyTest:</b> We used two libraries for testing Jest for frontend and PyTest for backend, mostly due to personal preference.</li>
                    </ul>
                </div>
            </div>
            <div className='space'></div>
            <div className='release-container'>
                <div className='tech-stck'>
                    <h2 className='titles'>New Features and Improvments</h2>
                    <p>We added some new features for you to enjoy, explore them in the translation, account management features and some new backend features. Read details below </p>
                    <ul>
                        <li>Translation history now has backend caching making it more efficient and less time waiting for you. Translation histroy now has the ability to delete entries or clear history all together.
                            Here are some images:
                            <img src={tottime}/> <img src={caching} width='80%'/>
                        </li>
                        <li>Documentation has been updated with a new video make the most of your codecraft experience.</li>
                        <li>2FA has been added with the Google Authenticator app. Try it out in the profile icon.</li>
                        <li>Improved translation for more accuracy</li>
                        <li>Improved UI look around see if you notice it.</li>
                        <li>Upgraded code mirror to allow for auto-complete when typing out.</li>
                    </ul>
                </div>
            </div>
            <div className='space'></div>
            <div className='release-container'>
                <div className='tech-stck'>
                    <h2 className='titles'>Bug Fixes</h2>
                    <p>We found some bugs and fixed them as needed.</p>
                    <ul>
                        <li>Fixed profile drop down so it would not disappear inside the translation page on smaller screens.</li>
                        <li>Fixed problem with translation history cache that caused nothing to be displayed.</li>
                    </ul>
                </div>
            </div>
            <div className='space'></div>
            <div className='release-container'>
                <div className='tech-stck'>
                    <h2 className='titles'>Deployment</h2>
                    <p>Some information on our Deployment</p>
                    <ul>
                        <li>Hosted on DigitalOcean thorugh their github student package.</li>
                        <li>Used nginx to display the static html frontend and to reverse proxy to our backend.</li>
                        <li>Gunicorn hosts our backend flask for a WSGI server.</li>
                        <li>MySQL database is also deployed by DigitalOcean but configured by us.</li>
                    </ul>
                </div>
            </div>
            <div className='space'></div>
            <div className='release-container'>
                <div className='tech-stck'>
                    <h2 className='titles'>Future Possiblities</h2>
                    <p>We have some potienal new paths for upgrading our new </p>
                    <ul>
                        <li>Load testing is a important part of scalability so if you are interested go to the <Link to={'/releasenotes/loadtesting'} style={{color: 'blue', textDecoration: 'underline'}}>Load Testing</Link></li>
                        <li>Creating a more robust server for our MySQL server </li>
                        <li>Including more languages such as C or Rust etc.</li>
                    </ul>
                </div>
            </div>
            <div className='space'></div>
        </div>
    )
}

export default ReleaseNotes;