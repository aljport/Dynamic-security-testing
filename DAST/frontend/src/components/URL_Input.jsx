import {React, useState} from 'react';
import "./URL_Input.css"

function URL_Input() {
  const [url, setUrl] = useState("");
  
  return (
    <div>
      <input
        type="text"
        className='url-input'
        placeholder='https://www.example.com'
        value={url}
        onChange={(e) => {
          setUrl(e.target.value);
        }}
      />
    </div>
  );
}

export default URL_Input;
