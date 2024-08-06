import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DeleteAccount from './DeleteAccount';
import axios from 'axios';
import { SITE_URL, FLASK_URL } from '../../vars';
import { ToastContainer } from 'react-toastify';

// Mock Axios
jest.mock('axios');

// Mock window.location to prevent actual navigation during tests
delete window.location;
window.location = { assign: jest.fn(), href: '' };

// Mock the confirmation prompt to always confirm deletion
jest.spyOn(window, 'confirm').mockImplementation(() => true);



// Basic unit tests for DeleteAccount component
describe('DeleteAccount Component', () => {
  // Test if the component renders correctly
  test('renders correctly', () => {
    render(<DeleteAccount />);
    expect(screen.getByText('Please note that once you delete your account, you cannot log back in or reactivate your account')).toBeInTheDocument();
    expect(screen.getByText('Delete Account')).toBeInTheDocument();
  });

  test('deletes account after confirmation', () => {
    render(<DeleteAccount />);

    const deleteButton = screen.getByText('Delete Account');

    fireEvent.click(deleteButton); // Simulate clicking the delete button

    expect(window.confirm).toHaveBeenCalled(); // Ensure confirmation is triggered
  });


  // Test for deletion failure due to an error or session expiration
  test('handles deletion error and session expiration', async () => {
    // Mock the confirmation prompt to always confirm deletion
    window.confirm = jest.fn(() => true);

    // Mock an error response for account deletion
    axios.post.mockRejectedValueOnce({
      response: { status: 500, data: { message: 'Server error' } },
    });

    // Render the component
    render(<DeleteAccount />);

    // Simulate clicking the delete button
    const deleteButton = screen.getByText('Delete Account');
    fireEvent.click(deleteButton);

    // Check if ToastContainer shows error message
    await waitFor(() => {
      const toastMessages = screen.getAllByRole('alert');
      expect(toastMessages.length).toBeGreaterThan(0);
    });
  });
});
