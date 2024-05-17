import Cookies from "../vendor/js-cookie.min.js"



function expirationStringToDateTime(input: string) {
    const [hours, minutes, seconds] = input.split(':').map(Number);
    const now = new Date();
    now.setHours(now.getHours() + hours);
    now.setMinutes(now.getMinutes() + minutes);
    now.setSeconds(now.getSeconds() + seconds);
    return now;
}


export function setCookie(name: string, data: string, expiration: string): void {
    Cookies.set(name, data, {
        sameSite: "strict",
        secure: true,
        expires: expirationStringToDateTime(expiration),
        path: "/"
    });
}


function deleteCookie(name: string): void {
    Cookies.remove(name);
}


export async function validateSession(sessionToken: string, refreshToken: string): Promise<boolean> {
    interface ValidateSessionResponse {
        status: number;
        message: string;
    }

    const response = await fetch("https://grimoire.foo/api/auth/validate", {
        method: "POST",
        headers: { "Authorization": "Bearer " + sessionToken },
    });

    const data: ValidateSessionResponse = await response.json();
    switch (data.status) {
        case 200:
            return true;

        case 401:
            if (data.message === "Session token is expired") {
                let refreshed: boolean = await refreshSession(sessionToken, refreshToken);
                if (refreshed) {
                    return true;
                }
            }
            break;
    }

    // Invalid session / refreshed failed
    deleteCookie("X-Session-Token");
    deleteCookie("X-Refresh-Token");
    return false;
}


interface LoginResponse {
    status: number;
    message: string;
    data: {
        session_token: string;
        refresh_token: string;
        session_expiration: string;
        refresh_expiration: string;
    };
}

export async function userLogin(username: string, password: string): Promise<LoginResponse> {
    const RequestBody = JSON.stringify({
        username,
        password,
    });

    const response = await fetch("https://grimoire.foo/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: RequestBody
    });

    const data: LoginResponse = await response.json();
    switch (data.status) {
        case 200:
            setCookie("X-Session-Token", data.data.session_token, data.data.refresh_expiration);
            setCookie("X-Refresh-Token", data.data.refresh_token, data.data.refresh_expiration);
            break;

        default:
            break;
    }
    return data;
}



async function refreshSession(sessionToken: string, refreshToken: string): Promise<boolean> {
    interface RefreshSessionResponse {
        status: number;
        message: string;
        data: {
            refresh_token: string;
            refresh_expiration: string;
        }
    }

    const response = await fetch("https://grimoire.foo/api/auth/refresh", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + sessionToken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({refresh_token: refreshToken})
    });

    const data: RefreshSessionResponse = await response.json();
    if (data.status === 200) {
        setCookie("X-Session-Token", sessionToken, data.data.refresh_expiration);
        setCookie("X-Refresh-Token", data.data.refresh_token, data.data.refresh_expiration);
        return true;
    } else {
        return false;
    }
}


