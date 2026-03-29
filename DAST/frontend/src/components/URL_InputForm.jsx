import { useState } from "react";
import { useNavigate } from "react-router-dom"
import "./URL_InputForm.css";

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
  const navigate = useNavigate();

  //Different URL types (.gov, .edu, .org, etc.) supported but not tested

  const handleSubmit = (e) => {
    e.preventDefault();
    const regex = /^https?:\/\/(www\.)?[a-z]+\.[a-z]{2,3}$/
    const isURLValid = regex.test(url);

    setIsValid(isURLValid);

    console.log("URL: ", url);

    if (isURLValid) {
      console.log("Valid URL Submitted: " + url);
      //Send URL to backend

      navigate('/results/1')
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
        />
        <button className='scan-button' type='submit'>Scan</button>
      </form>
      <ErrorMessage isValid={isValid} />
    </div>
  );
}

export default UrlInputForm;