import React from "react";
import logo3 from '../navbar/logo3.webp';
import './Home.css';
import javascr from './Image 9.webp';
import py from './Image 10.webp';
import cprog from './Image 11.webp';
import jav from './Image 12.webp';
import { Link } from 'react-router-dom';
import { useState, useEffect } from "react";
import axios from "axios";
import { FLASK_URL, setLocal, isExpired, Logout, isLoggedIn } from '../../vars';
import halfstar from './halfstar.png';
import star from './fullstar.png';
import emptystar from './emptystar.png';


const Home = () => {

    const [rating, setRating] = useState('');
    const [totalRatings, setTotalRatings] = useState();

    useEffect(() => {
        fetchRating();
    }, []);

    const fetchRating = () => {
        axios.get(`${FLASK_URL}/getAggregatedFeedback`)
            .then(response => {
                console.log('Verification response:', response.data);
                const res = response.data;
                if (res.success) {
                    setRating(res.average_rating);
                    console.log(`rating ${res.average_rating}`);
                    setTotalRatings(res.total_ratings);
                }
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                console.log(`Response has error: ${res.hasError}`);
                if (res.logout) {
                    setTimeout(Logout, 4000);
                }
            })
            .catch(error => {
                console.error('Verification error:', error);
                // TODO: failed verification message
            });
    };

    const renderStars = () => {
        const stars = [];
        const maxRating = 5; // Maximum rating possible
        const fullStars = Math.floor(rating); // Number of full stars
        const hasHalfStar = rating % 1 >= 0.5; // Check if there should be a half star

        for (let i = 0; i < maxRating; i++) {
            if (i < fullStars) {
                // Replace 'fullStar.png' with the path to your full star image
                stars.push(<img key={i} src={star} alt="Full Star" className="star" />);
            } else if (i === fullStars && hasHalfStar) {
                // Replace 'halfStar.png' with the path to your half star image
                stars.push(<img key={i} src={halfstar} alt="Half Star" className="halfstar" />);
            } else {
                // Optionally, have an 'emptyStar.png' or just keep using the Unicode character
                stars.push(<img key={i} src={emptystar} alt="Empty Star" className="star" />);
            }
        }
        return stars;
    };

    return (
        <div className="back">
            <div>
                <img className="title" src={logo3} />

                <div className="intro">
                    <h2>codeCraft is where all your code translating needs are met!</h2>
                    <h2>Powered by the new ChatGPT-3.5 and fine tuned by us to accomplish all your coding needs.</h2>
                </div>
            </div>
            <div className="reviews">
                <h2>How our users    <span className="rating-number">   ({totalRatings})</span> rate us: <span style={{ color: 'gold', }}>   {Number.parseFloat(rating).toFixed(1)} stars</span></h2>
                {renderStars()}
            </div>
            <h1>Accepted Languages</h1>
            <div className="Accepted">
                <img className="langs" src={javascr} />
                <img className="langs" src={py} />
                <img className="langs" src={cprog} />
                <img className="langs" id="jav" src={jav} />
            </div>
            <div className="box">
                <Link to="/translate">
                    <button className="translate_now" >Try it out !!!</button>
                </Link>
            </div>
        </div>
    );
};

export default Home;