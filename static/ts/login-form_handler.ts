import { userLogin } from "./auth";



export function LoginFormHandler() {
    const loginForm = document.getElementById("login-form");
    const errorMessageDisplay = document.getElementById("errorMessage");
    if (loginForm && errorMessageDisplay) {
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const usernameElement = document.getElementById("username") as HTMLInputElement;
            const passwordElement = document.getElementById("password") as HTMLInputElement;

            if (!usernameElement || !passwordElement) {
                console.error("Username or password field not found");
                return;
            }

            var username = usernameElement.value;
            var password = passwordElement.value;
            var loginResponse = await userLogin(username, password);
            switch (loginResponse.status) {
                case 200:
                    window.location.assign("https://grimoire.foo/home");
                    return

                default:
                    errorMessageDisplay.innerText = loginResponse.message
                    return
            }
        });
    } else {
        console.error("Login form not found");
    }
}

