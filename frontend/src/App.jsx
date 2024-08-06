import React, { Suspense, lazy } from 'react';
import NavBar from './components/navbar/NavBar';
import './App.css'; // Assuming you have global styles here
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { isExpired } from './vars.js';

//non-lazy components
import Home from './components/homepage/Home';
import TranslatePage from './components/translatepage/TranslatePage';
import ReleaseNotes from './components/ReleaseNotes/ReleaseNotes.jsx';
import LoadTesting from './components/ReleaseNotes/Loadtesting.jsx'
import 'react-toastify/dist/ReactToastify.css';

//lazy load is used to import components only when theyre needed. non-lazy = needed fast and consistently
//lazy load heavy components
const LoginPage = lazy(() => import('./components/LoginPage/LoginPage.jsx'));
const Register = lazy(() => import('./components/Registration/RegistrationPage.jsx'));
const Feedback = lazy(() => import('./components/FeedbackForm/FeedbackForm.jsx'));
const References = lazy(() => import('./components/References/References.jsx'));
const Help = lazy(() => import('./components/Help/Help.jsx'));
const AccountManagement = lazy(() => import('./components/AccountManagement/AccountManagement.jsx'));
const ChangeUsername = lazy(() => import('./components/AccountManagement/ChangeUsername.jsx'));
const ChangePassword = lazy(() => import('./components/AccountManagement/ChangePassword.jsx'));
const DeleteAccount = lazy(() => import('./components/AccountManagement/DeleteAccount.jsx'));
const ForgotPass = lazy(() => import('./components/ForgotPass/ForgotPass.jsx'));
const ResetPass = lazy(() => import('./components/ForgotPass/ResetPass.jsx'));
const TwoFA = lazy(() => import('./components/AccountManagement/TwoFA.jsx'));
const TwoFAcode = lazy(() => import('./components/LoginPage/TwoFAcode.jsx'));

function App() {
  setInterval(isExpired, 1000); //checks every second

  return (
    <div className="App">
      <NavBar />
      <div className='routing'>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path='/' element={<Home />}/>
            <Route path='/translate' element={<TranslatePage />}/>
            <Route path='/login' element={<LoginPage />}/>
            <Route path='/register' element={<Register />}/>
            <Route path='/feedback' element={<Feedback />}/>
            <Route path='/references' element={<References />}/>
            <Route path='/help' element={<Help />}/>
            <Route path='/accountmanagement' element={<AccountManagement />} />
            <Route path='/accountmanagement/changeusername' element={<ChangeUsername />} />
            <Route path='/accountmanagement/changepassword' element={<ChangePassword />} />
            <Route path='/accountmanagement/deleteaccount' element={<DeleteAccount />} />
            <Route path='/accountmanagement/twoFA' element={<TwoFA/>} />
            <Route path='/login/2FA' element={<TwoFAcode />} />
            <Route path='/forgotpassword' element={<ForgotPass />} />
            <Route path='/resetpassword' element={<ResetPass />}/>
            <Route path='/releasenotes' element={<ReleaseNotes />} />
            <Route path='/releasenotes/loading' element={<LoadTesting />}/>
          </Routes>
        </Suspense>
      </div>
    </div>
  );
}

export default App;
