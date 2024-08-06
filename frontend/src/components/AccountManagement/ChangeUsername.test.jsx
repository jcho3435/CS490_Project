import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChangeUserame from './ChangeUsername';
import axios from 'axios';
import { FLASK_URL } from '../../vars';

// Mock Axios
jest.mock('axios');

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});

describe('ChangeUserame Component', () => {
  test('renders correctly', () => {
    render(<ChangeUserame />);
    expect(screen.getByText('Change Username')).toBeInTheDocument(); // Check for the title
    expect(screen.getByText('Submit')).toBeInTheDocument(); // Check for the button
  });

  test('handles input changes', () => {
    render(<ChangeUserame />);

    const inputs = screen.getAllByRole('textbox'); // Get all textboxes
    const currentUsernameInput = inputs[0];
    const newUsernameInput = inputs[1];

    // Simulate changing input values
    fireEvent.change(currentUsernameInput, { target: { value: 'old_user' } });
    fireEvent.change(newUsernameInput, { target: { value: 'new_user' } });

    // Verify the input values were updated
    expect(currentUsernameInput.value).toBe('old_user');
    expect(newUsernameInput.value).toBe('new_user');
  });

  test('submits form and calls changeUser', async () => {
    const changeUserSpy = jest.spyOn(axios, 'post').mockResolvedValueOnce({ data: { success: true } });

    render(<ChangeUserame />);

    const submitButton = screen.getByText('Submit'); // Find the submit button
    fireEvent.click(submitButton); // Simulate click

    // Verify that the changeUser function was called with the expected endpoint
    await waitFor(() => {
      expect(changeUserSpy).toHaveBeenCalledWith(
        expect.stringMatching(/userChangeUsername/),
        expect.any(Object)
      );
    });
  });
});
