import React from 'react';
import upload from './upload.svg';
import translate from './translate.svg';
import input from './input.svg';
import output from './output.svg';
import download from './download.svg';
import './UserGuide.css';

function UserGuide(){


    return(
        <div className='guide-container'>
            <p className='title'>User Guide</p>
            <div className='steps-container'>
                <p className='step-title-container'>
                     <p className='step-title'>First, grab your code and drop it into the translator</p>
                </p>
                   <p style={{color:'white', marginLeft:'-5rem'}}>You can do this by simply pasting or by uploading files:</p>
                <div className='tut-img-holder-1'><img className='tutorial-img' src={upload} alt="upload"/></div>
                <p className='step-title-container'>
                     <p className='step-title'>Then, select your input language</p>
                </p>
                <div className='tut-img-holder-2'><img className='tutorial-img'src={input} alt="input"/></div>
                <p className='step-title-container'>
                     <p className='step-title'>Select your output language</p>
                </p>
                <div className='tut-img-holder-3'><img className='tutorial-img'src={output} alt="output"/></div>
                <p className='step-title-container'>
                     <p className='step-title'>Click translate</p>
                </p>
                <div className='tut-img-holder-4'><img className='tutorial-img'src={translate} alt="translate"/></div>
                <p className='step-title-container'>
                     <p className='step-title'>Now, copy the code using the clipboard button, and/or download using the download button! All done!</p>
                </p>
                <div className='tut-img-holder-5'><img className='tutorial-img' src={download} alt="download"/></div>
            </div>
        </div>
    )
}

export default UserGuide