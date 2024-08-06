import { React, useEffect, useState } from 'react';
import { FLASK_URL, SITE_URL, Logout } from '../../vars.js';
import axios from 'axios';



const DisplayFeedback = ({currentTranslationId}) => {

    const [rating, setRating] = useState('');
    const [openended, setOpenEnded] = useState('');
    const [date, setDate] = useState('');


    useEffect(() => {
        axios.get(`${FLASK_URL}/getTranslationFeedbackHistory`, currentTranslationId)
            .then(response => {
                console.log('Verification response:', response.data); 
                const res = response.data;
                if (res.success) {
                    setDate(res.rows);
                    console.log(`inside of displayfeedback ${date}`);
                }
                if (res.hasError) console.log(`Error response: ${res.errorMessage}`);
                console.log(`Response has error: ${res.hasError}`);
                if (res.logout) {
                }
            })
            .catch(error => {
                console.error('Verification error:', error);
                // TODO: failed verification message
            });
    },[currentTranslationId]);

    return(


        <div><p> hello </p>
        </div>
    );

}

export default DisplayFeedback