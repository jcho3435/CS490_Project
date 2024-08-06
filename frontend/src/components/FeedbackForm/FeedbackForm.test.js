import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import FeedbackForm from './FeedbackForm';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import { FLASK_URL } from '../../vars';

// Mocking modules and components
jest.mock('axios');
jest.mock('react-toastify', () => ({
  ToastContainer: () => (<div>ToastContainerMock</div>),
  toast: jest.fn()
}));

describe('FeedbackForm', () => {
  beforeEach(() => {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("sessionToken", "someToken");
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('input changes update component state', () => {
    render(<FeedbackForm />, { wrapper: Router });

    // Use the id to select the fifth radio button for question1
    const inputQuestion1 = document.getElementById('changing-test');
    const textArea = screen.getByPlaceholderText(/Type here/i);

    // Simulate user clicking the radio button and entering text in the textarea
    fireEvent.click(inputQuestion1);
    fireEvent.change(textArea, { target: { value: 'Great tool!' } });

    // Since `getByDisplayValue` might not directly check 'checked' state, let's ensure the correct value is set
    expect(inputQuestion1.checked).toBe(true);
    expect(textArea.value).toBe('Great tool!');
  });

  test('form submission sends correct data', async () => {
    axios.post.mockResolvedValue({
      data: { success: true }
    });

    const { getByText } = render(<FeedbackForm />, { wrapper: Router });

    fireEvent.submit(getByText('Submit'));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`${FLASK_URL}/submitFeedback`, {
        ease_rating: NaN,
        future_use_rating: NaN,
        note: "",
        precision_rating: NaN,
        sessionToken: "someToken",
        speed_rating: NaN,
      });
    });
  });

  test('handles response for successful feedback submission', async () => {
    axios.post.mockResolvedValue({
      data: { success: true }
    });

    render(<FeedbackForm />, { wrapper: Router });
    fireEvent.submit(screen.getByText('Submit'));

    await waitFor(() => {
      expect(screen.getByText('ToastContainerMock')).toBeInTheDocument();
      expect(toast).toHaveBeenCalledWith('FEEDBACK SUBMITTED SUCCESFULLY!', expect.any(Object));
    });
  });

  test('handles error response properly', async () => {
    axios.post.mockRejectedValue({
      response: { data: 'Error submitting feedback' }
    });

    render(<FeedbackForm />, { wrapper: Router });
    fireEvent.submit(screen.getByText('Submit'));

    await waitFor(() => {
      expect(screen.getByText('ToastContainerMock')).toBeInTheDocument();
      expect(toast).toHaveBeenCalledWith("FEEBACK NOT SUBMITTED DUE TO: BACKEND, please contact Support", {"autoClose": 2000, "className": "fail"});
    });
  });
});
