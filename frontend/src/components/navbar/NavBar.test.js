import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import NavBar from './NavBar';
import MiniMenu from './MiniMenu';

jest.mock('./MiniMenu', () => () => (<div>MiniMenuMock</div>)); // Mock MiniMenu for simplicity in tests

describe('NavBar Component', () => {
  beforeEach(() => {
    // Clear all items in localStorage
    localStorage.clear();
  });

  test('renders all navigation links correctly', () => {
    render(
      <Router>
        <NavBar />
      </Router>
    );
    expect(screen.getByTestId('translink')).toHaveTextContent('Translator');
    expect(screen.getByTestId('feedlink')).toHaveTextContent('Feedback');
    expect(screen.getByTestId('helplink')).toHaveTextContent('Help');
    expect(screen.getByTestId('releaselink')).toHaveTextContent('Release Notes');
  });

  test('shows login icon when user is not logged in', () => {
    localStorage.setItem("isLoggedIn", "false");
    render(
      <Router>
        <NavBar />
      </Router>
    );
    expect(screen.getByAltText('Profile')).toBeInTheDocument();
    expect(screen.queryByText('MiniMenuMock')).not.toBeInTheDocument(); // MiniMenu should not be shown
  });

  test('shows profile and MiniMenu when user is logged in and hovers over profile icon', () => {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("username", "testUser");
    render(
      <Router>
        <NavBar />
      </Router>
    );
    expect(screen.getByText('testUser')).toBeInTheDocument(); // Check if username is displayed

    // Hover over the profile icon to trigger MiniMenu
    fireEvent.mouseEnter(screen.getByTestId('prof'));
    expect(screen.getByText('MiniMenuMock')).toBeInTheDocument();

    // Mouse leave should hide MiniMenu
    fireEvent.mouseLeave(screen.getByTestId('prof'));
    expect(screen.queryByText('MiniMenuMock')).not.toBeInTheDocument();
  });
});

