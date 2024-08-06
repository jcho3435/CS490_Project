import React from 'react';
import './SearchBar.css';

function searchBar({ onSearchChange }) {
  const handleChange = (event) => {
    const query = event.target.value;
    onSearchChange(query);
  };

  return (
    <div className="search-bar-container">
      <input
        id='search-bar'
        type="text"
        placeholder="Search..."
        onChange={handleChange}
        className="search-input"
      />
      {/* <button className="search-button"><i className="fa fa-search"></i></button> */}
    </div>
  );
}

export default searchBar;
