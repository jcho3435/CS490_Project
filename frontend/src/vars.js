import { v4 as uuidv4 } from 'uuid';
import axios from 'axios'

export const FLASK_URL = "http://localhost:5000"; //these will need to be changed on deploy- maybe load out of env vars?
export const SITE_URL = window.location.origin;

// export const setSessionLogin = (user_id, username) => {
//     sessionStorage.setItem("isLoggedIn", "true")
//     sessionStorage.setItem("user_id", user_id)
//     const sessionToken = uuidv4();
//     sessionStorage.setItem("sessionToken", sessionToken)
//     setTimeout(() => {
//         sessionStorage.clear();
//         window.location.href = SITE_URL + "/login";
//     }, 60 * 60 * 1000); // 60 minutes in milliseconds
// }

export const setLocal = (session_token, username, loginTime, rememberMe, isLoggedIn = false) => {
    localStorage.setItem("lastLogIn", loginTime)
    localStorage.setItem("isLoggedIn", isLoggedIn.toString())
    localStorage.setItem("sessionToken", session_token)
    // const sessionToken = uuidv4();
    // localStorage.setItem("sessionToken", sessionToken)
    localStorage.setItem("username", username)
    localStorage.setItem("rememberMe", rememberMe)
}

export const set2FAVerification = (passIsVerified) => {
    localStorage.setItem("passIsVerified", passIsVerified.toString());
}

export const isExpired = () => {
    const expires = 60 *60 *24; //in seconds
    const lastLogIn = parseInt(localStorage.getItem("lastLogIn"), 10);
    const currentTime = Math.floor(Date.now() / 1000)
    const elapsedTime = currentTime - lastLogIn;
    // console.log(`current time: ${currentTime}`)
    // console.log(`lastLogin: ${lastLogIn}`)
    // console.log(`elapsed time: ${elapsedTime}`)

    if (elapsedTime > expires){
        localStorage.clear();
        window.location.href = SITE_URL + "/login";
    }
}

export const Logout = async (nav) => {
    var sessionToken = localStorage.getItem("sessionToken")
    localStorage.clear();
    console.log('User logged out');
    await LogoutBackend(sessionToken)
    // window.location.href = SITE_URL + "/login";
    nav("/login")
}

// *************** OTHER FUNCTIONS ***************
async function LogoutBackend(sessionToken) {
    await axios.post(`${FLASK_URL}/userLogout`, { sessionToken: sessionToken })
        .then((response) => {
            const res = response.data;
            if (res.success) {
                console.log("Session cleared")
            }
            console.log(`Response has error: ${res.hasError}`);
            if (res.hasError) alert(`Error response: ${res.errorMessage}`);
        }).catch((error) => {
            if (error.response) {
                console.log(error.response);
                console.log(error.response.status);
                console.log(error.response.headers);
            }
        });
}

// ******** DO NOT EXPORT THESE FUNCTIONS ********
