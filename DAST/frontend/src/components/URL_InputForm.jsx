import { useState } from "react";
import "./URL_InputForm.css";

function UrlInputForm() {
  const [url, setUrl] = useState("");

  //Different URL types (.gov, .edu, .org, etc.) supported but not tested

  const handleSubmit = (e) => {
    e.preventDefault();
    let isURLValid = url.match("^https?:\/\/(www\.)?[a-z]+\.[a-z]{2,3}$");
    isURLValid ? (console.log("Valid URL Submitted: " + url)) : (console.warn("Invalid URL") ); 
  };

  return (
    <form className='url-form' onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="https://www.example.com"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="url-input"
      />
      <button className='scan-button' type='submit'>Scan</button>
    </form>
  );
}

export default UrlInputForm;