import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import axios from 'axios';
import TwoFAcode from './TwoFAcode';
import { FLASK_URL } from '../../vars';

// Mock axios
jest.mock('axios');

describe('TwoFAcode Component', () => {
    beforeEach(() => {
        // Set the initial local storage state to ensure the component renders
        localStorage.setItem("isLoggedIn", "false");
      });
  test('renders correctly', () => {
    render(
      <Router>
        <TwoFAcode />
      </Router>
    );

    // Check for the presence of the 6-digit code inputs
    for (let i = 0; i < 6; i++) {
      const digitInput = screen.getByTestId(`digit-input-${i}`);
      expect(digitInput).toBeInTheDocument();
      expect(digitInput).toHaveAttribute('type', 'text');
    }

    // Check for the presence of the submit button
    const submitButton = screen.getByTestId('submit-button');
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  test('submits a valid 2FA code', async () => {
    axios.post.mockResolvedValue({
      data: {
        success: true,
        sessionToken: 'newToken',
      }
    });

    render(
      <Router>
        <TwoFAcode />
      </Router>
    );

    // Simulate user entering the digits
    for (let i = 0; i < 6; i++) {
      fireEvent.change(screen.getByTestId(`digit-input-${i}`), { target: { value: '1' } });
    }

    fireEvent.click(screen.getByTestId('submit-button'));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`${FLASK_URL}/validateTOTP`, {
        sessionToken: localStorage.getItem("sessionToken"),
        passcode: '111111',
      });
    });
  });

  test('submits a 2FA code with an error response', async () => {
    axios.post.mockResolvedValueOnce({
      data: { 
        success: false,
        errorMessage: 'Invalid code'
      }
    });

    render(
      <Router>
        <TwoFAcode />
      </Router>
    );

    // Enter an incorrect 2FA code
    for (let i = 0; i < 6; i++) {
      fireEvent.change(screen.getByTestId(`digit-input-${i}`), { target: { value: '2' } });
    }

    fireEvent.click(screen.getByTestId('submit-button'));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`${FLASK_URL}/validateTOTP`, {
        sessionToken: localStorage.getItem("sessionToken"),
        passcode: '222222',
      });
      // Check for error handling in the component (not visible without implementing)
    });
  });
});
