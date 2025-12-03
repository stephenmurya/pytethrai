import axios from "axios";

// Get CSRF token from cookie
function getCookie(name: string) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== "") {
		const cookies = document.cookie.split(";");
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === name + "=") {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

// Configure axios defaults
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.withCredentials = true;

// Add CSRF token to all requests
axios.interceptors.request.use((config) => {
	const csrftoken = getCookie("csrftoken");
	if (csrftoken) {
		config.headers["X-CSRFToken"] = csrftoken;
	}
	return config;
});

export default axios;
