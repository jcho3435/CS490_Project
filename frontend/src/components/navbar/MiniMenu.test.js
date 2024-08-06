import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import MiniMenuComponent from './MiniMenu.jsx';
import { Logout } from '../../vars';

jest.mock('../../vars', () => ({
  Logout: jest.fn(),
}));

describe('MiniMenuComponent', () => {
  beforeEach(() => {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("username", "testUser");
    localStorage.setItem("passIsVerified", "true");
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('displays user information and account management options', () => {
    render(
      <Router>
        <MiniMenuComponent />
      </Router>
    );
    expect(screen.getByText('testUser')).toBeInTheDocument();

    // Verify initial hidden state of account management menu
    expect(screen.queryByText('Edit Username')).not.toBeInTheDocument();

    // Simulate click to show account management options
    fireEvent.click(screen.getByText('Account Management'));
    expect(screen.getByText('Edit Username')).toBeInTheDocument();
    expect(screen.getByText('Edit Password')).toBeInTheDocument();
    expect(screen.getByText('Delete Account')).toBeInTheDocument();
    expect(screen.getByText('2 Factor Authentication')).toBeInTheDocument();
  });

  test('triggers Logout function on logout button click', () => {
    render(
      <Router>
        <MiniMenuComponent />
      </Router>
    );
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(Logout).toHaveBeenCalled();
  });

  test('2 Factor Authentication link resets local storage verification', () => {
    render(
      <Router>
        <MiniMenuComponent />
      </Router>
    );

    // Open Account Management to access the link
    fireEvent.click(screen.getByText('Account Management'));
    const faLink = screen.getByText('2 Factor Authentication');
    fireEvent.click(faLink);

    expect(localStorage.getItem("passIsVerified")).toBe("false");
  });
});
