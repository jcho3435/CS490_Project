import { React, useState } from 'react';
import { FLASK_URL, SITE_URL, Logout } from '../../vars.js';
import axios from 'axios';
import './TranslationFeedback.css';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';

const Star = ({ selected = false, onClick }) => (
    <span onClick={onClick} style={{ cursor: 'pointer', color: selected ? 'orange' : 'gray', fontSize: '35px' }}>
        {selected ? '★' : '☆'}
    </span>
);


const TranslationFeedback = ({ currentTranslationId }) => {
    const navigate = useNavigate();
    console.log(`im here ${currentTranslationId}`);

    const [rating, setRating] = useState('');
    const [openended, setOpenEnded] = useState('');
    const [limit, setLimit] = useState(150);


    const handleChange = (event) => {
        const inputValue = event.target.value;
        if (inputValue.length <= limit) {
            setOpenEnded(inputValue);
        }
    };

    const handleRating = (rate) => {
        setRating(rate);
        console.log(rate);
    };

    function formatSubmissionDate(date) {
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (date.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        } else {
            return 'Previous 30 Days';
        }
    }

    const handleSubmit = (e) => {
        e.preventDefault();

        const translationFBData = {
            sessionToken: localStorage.getItem("sessionToken"),
            translation_id: currentTranslationId,
            star_rating: parseInt(rating),
            note: openended
        };


        console.log('Sending feedback request with data:', translationFBData);
        axios.post(`${FLASK_URL}/submitTranslationFeedback`, translationFBData)
            .then((response) => {
                const res = response.data;
                console.log(`Response has error: ${res.hasError}`);
                console.log(`Session token: ${res.sessionCheck}`);
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                else if (res.success) {
                    console.log('Translation Feedback submitted successfully');
                    toast(`TRANSLATION FEEDBACK SUBMITTED SUCCESFULLY!`);
                }
                if (res.logout) {
                    toast("Session expired. Please login again..");
                    Logout(navigate);
                }
                setOpenEnded('');
                setRating('');
                setLimit(150);
            }).catch((error) => {
                if (error.response) {
                    toast(`FEEBACK NOT SUBMITTED DUE TO: ${error.response}`);
                    console.log(error.response);
                    console.log(error.response.status);
                    console.log(error.response.headers);
                }
            });

    };


    return (
        <div>
            <ToastContainer position='top-center' style={{ zIndex: 1100 }}/>
            <p>Rate Translation:</p>
            <p>note: any new feedback will overwrite previous feedback for this translation</p>
            <div>
                <form onSubmit={handleSubmit}>
                    {[1, 2, 3, 4, 5].map((star, index) => (
                        <Star
                            key={index}
                            className="star"
                            selected={rating >= star}
                            onClick={() => handleRating(star)}
                        />
                    ))}

                    <textarea
                        className="textbox"
                        value={openended}
                        onChange={handleChange}
                        placeholder={`Type here (Limit: ${limit} characters)`}
                        rows={4}
                        cols={50}
                    />
                    <button className="submit-button" type="submit">Submit</button>
                </form>
            </div >
        </div>
            );
};

            export default TranslationFeedback;;