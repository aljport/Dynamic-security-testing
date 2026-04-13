import { useState } from "react";
import { useNavigate } from "react-router-dom"
import "./URL_InputForm.css";
import AxiosInstance from "../utils/Axios"

function ErrorMessage({ isValid }) {
  return (
    <p className="error-text">
      {isValid ? "\u00a0" : "Please enter a valid URL"}
    </p>
  );
}

function UrlInputForm() {
  const [url, setUrl] = useState("");
  const [isValid, setIsValid] = useState(true);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const old_regex = /^https?:\/\/(www\.)?[a-z | . | -]+\.[a-z]{2,}(\/[a-z0-9]+)*$/
    const regex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/
    const isURLValid = regex.test(url);

    setIsValid(isURLValid);

    if (isURLValid) {
      console.log("Valid URL Submitted: " + url);

      setLoading(true);

      try {
        const response = await AxiosInstance.post('api/scan/', {
          url: url
        });

        console.log("Backend response: ", response.data);

        navigate('/results/1', {
          state: {
            url: url, 
            scanResults: response.data
          }
        });
      } catch (error) {
        console.log("URL: ", url);
        console.error("Error sending URL to backend: ", error);
        setIsValid(false);
      } finally {
        setLoading(false);
      }
    } else {
      console.warn("Invalid URL");
    }
  };

  return (
    <div className="url-box">
      <form className="url-form" onSubmit={handleSubmit} method="POST">
        <input
          type="text"
          placeholder="https://www.example.com"
          value={url}
          onChange={(e) =>  {
            setUrl(e.target.value);
          }}
          className="url-input"
          disabled = {loading}
        />
        <button className='scan-button' type='submit' disabled={loading}>Scan</button>
      </form>
      <ErrorMessage isValid={isValid} />
    </div>
  );
}

export default UrlInputForm;