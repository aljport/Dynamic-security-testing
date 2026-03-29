import { useNavigate } from 'react-router-dom';
import {React, useState, useEffect} from 'react'
import Results from '../components/Results';
import './ResultsPage.css';
import AxiosInstance from '../utils/Axios';

function ResultsPage() {
  const navigate = useNavigate();
  const [website, setWebsite] = useState([])

  console.log(website)

  const GetData = () => {
    AxiosInstance.get('website/').then((res) => {
      setWebsite(res.data)
    } )
  }

  useEffect(() => {
    GetData()
  },[])

  return (
    <>
      <div className='header'>
        <p className='group-name'>Team SAAB</p>
      </div>
      <div className='app-container'>
        <h1 className='app-title'>Scan Results</h1>
        <button className='back-button' onClick={() => navigate('/')}>
          ← Back to Home
        </button>
        <Results />
      </div>
    </>
  );
}

export default ResultsPage;
