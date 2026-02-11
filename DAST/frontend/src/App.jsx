import { useState } from 'react'
import './App.css'
import UrlInputForm from './components/URL_InputForm.jsx'

function App() {
  return (
    <>
    <div className='header'>
      <p className='group-name'>Team SAAB</p>
      </div>
      <div className='app-container'>
        <h1 className='app-title'>Dynamic Security Testing Tool</h1>
        <p className='app-subtitle'>Enter a URL below to start a security scan:</p>
        <UrlInputForm/>
        {/* TODO: Create results component with invalid url feedback */}
        <div className='results'>
          <p className='results-title'>Results</p>
        </div>
      </div>
    </>
  )
}

export default App
