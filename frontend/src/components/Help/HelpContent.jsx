import React, { useState } from 'react';
import './HelpContent.css'; // Import CSS file for styling

function HelpContent({ searchQuery }) {
  // Sample help content data
  const helpContent = [
    { id: 1, title: 'How do I use the translator?', content: 'Just paste ur code and press "translate"' },
    { id: 2, title: 'What coding languages are accepted?', content: 'JavaScript, Python, C++, Java, Rust' },
    { id: 3, title: 'How complex can code be?', content: 'Sky is the limit with codeCraft!' },
    { id: 4, title: 'What is the max length for the translation?', content: '16,384 characters' },
    { id: 5, title: 'Why am I getting errors when I try to translate?', 
    content: 'You are most likely seeing errors because your code does not comply with the selected language. Please check your code and double check the selected language and try again!' },
    { id: 6, title: 'How do I see my past translations?', content: 'Click on the history icon in the top left corner! You will be able to see your past translations.' },
    { id: 7, title: 'How do I change my password?', content: 'Hover on the profile icon in the top right corner. Hover over Account Management. Click on Edit Password!' },
    { id: 8, title: 'How do I change my username?', content: 'Hover on the profile icon in the top right corner. Hover over Account Management. Click on Edit Username!' },
    { id: 9, title: 'How do I delete my account?', content: 'Hover on the profile icon in the top right corner. Hover over Account Management. Click on Delete Account!' },
    { id: 10, title: 'How do submit feedback?', content: 'Click on the feedback button on the banner! Let us know what we can do better!' },
  ];

  // Filter help content based on search query
  const filteredContent = helpContent.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // State to manage which FAQ items are expanded
  const [expandedId, setExpandedId] = useState(null);

  // Function to toggle the expanded state of an FAQ item
  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="accordion-container">
      <div className="accordion">
        {filteredContent.map((item) => (
          <div key={item.id} className="faq-item">
            <button
              className={`accordion-btn ${expandedId === item.id ? 'active' : ''}`}
              onClick={() => toggleAccordion(item.id)}
            >
              <p className="faq-title">{item.title}</p>
              <span className="arrow">&#9660;</span> {/* Down arrow icon check for different ones*/}
            </button>
            <div className={`panel ${expandedId === item.id ? 'show' : ''}`}>
              <p className="faq-content">{item.content}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HelpContent;
