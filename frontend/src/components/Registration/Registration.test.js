import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import RegistrationPage from './RegistrationPage';
import axios from 'axios';
import { ToastContainer } from 'react-toastify';
import { BrowserRouter as Router } from 'react-router-dom';
import { FLASK_URL } from '../../vars';

jest.mock('axios');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), // use actual for all non-hook parts
  useNavigate: () => jest.fn() // mock hook
}));

describe('RegistrationPage', () => {
  const setup = () => {
    render(<RegistrationPage />, { wrapper: Router });
  };

  test('inputs should be initially empty', () => {
    setup();
    expect(screen.getByLabelText('Username:').value).toBe('');
    expect(screen.getByLabelText('Email:').value).toBe('');
    expect(screen.getByLabelText('Password:').value).toBe('');
  });

  test('displays validation messages for incorrect inputs', async () => {
    setup();
    fireEvent.input(screen.getByLabelText('Username:'), {
      target: { value: 'sh' } // intentionally short to trigger validation
    });
    fireEvent.input(screen.getByLabelText('Email:'), {
      target: { value: 'wrong-email' } // incorrect email format
    });
    fireEvent.input(screen.getByLabelText('Password:'), {
      target: { value: '123' } // short password
    });
    fireEvent.submit(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText('Username must be between 8 to 24 characters and can only contain alphanumeric characters, underscores, and hyphens.')).toBeInTheDocument();
    });
  });

  test('Email notif', async () => {
    setup();
    fireEvent.input(screen.getByLabelText('Username:'), {
      target: { value: 'asfjhasjkhajhf' } // intentionally short to trigger validation
    });
    fireEvent.input(screen.getByLabelText('Email:'), {
      target: { value: 'wrong-email' } // incorrect email format
    });
    fireEvent.input(screen.getByLabelText('Password:'), {
      target: { value: '123' } // short password
    });
    fireEvent.submit(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
    });
  });

  test('Email notif', async () => {
    setup();
    fireEvent.input(screen.getByLabelText('Username:'), {
      target: { value: 'asfjhasjkhajhf' } // intentionally short to trigger validation
    });
    fireEvent.input(screen.getByLabelText('Email:'), {
      target: { value: 'jack@hamdi.com' } // incorrect email format
    });
    fireEvent.input(screen.getByLabelText('Password:'), {
      target: { value: '123' } // short password
    });
    fireEvent.submit(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters long, have a special character, and number.')).toBeInTheDocument();
    });
  });



  test('calls axios post on valid form submission', async () => {
    axios.post.mockResolvedValue({ data: { success: true, sessionToken: 'fakeToken' } });

    setup();
    fireEvent.change(screen.getByLabelText('Username:'), { target: { value: 'validUser' } });
    fireEvent.change(screen.getByLabelText('Email:'), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByTestId('Password:'), { target: { value: 'Password123!' } });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`${FLASK_URL}/registerNewUser`, expect.anything());
      expect(screen.getByText(/registration success!/i)).toBeInTheDocument();
    });
  });
});
