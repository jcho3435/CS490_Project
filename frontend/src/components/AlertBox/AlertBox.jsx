import React, { useState, useEffect } from 'react';
import './AlertBox.css';

function AlertBox({ message, isOpen }) {
  const [show, setShow] = useState(isOpen);

  useEffect(() => {
    if (isOpen) {
      setShow(true);
      const timer = setTimeout(() => {
        setShow(false);
      }, 2000); // 2000 milliseconds = 2 seconds
      return () => clearTimeout(timer); // Cleanup the timer on component unmount
    }
  }, [isOpen]); // Effect runs only when `isOpen` changes

  const handleResponse = (message) => {
    let response;
    switch (message){
      case 'stop': case 'from_db':
        response = "Translation Success!!"
        break;
      case 'length':
        response = "Unsuccessful Translation :((, input text is too long"
        break;
      case 'content_filter':
        response = "Code content was flagged by openai content filters"
        break;
      case '401':
        response = "OpenAI API Authentication failed "
        break;
      case '403':
        response = "Country not supported with OpenAI"
        break;
      case '429':
        response = "Please wait you sent too many characters"
        break;
      case '500':
        response = "Unknown OpenAI server error"
        break;
      case '503':
        response = "OpenAI server is currently being overloaded, please before submitting again"
        break;
      default:
        response = message
        break;
    }
    return response;
  }

  return (
    <div className="alertbox">
      {show && (
        <dialog open>
          <p>{handleResponse(message)}</p>
        </dialog>
      )}
    </div>
  );
}

export default AlertBox;
