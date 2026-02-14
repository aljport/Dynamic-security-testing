import { useState } from 'react'
import './App.css'
import UrlInputForm from './components/URL_InputForm.jsx'
import Results from './components/Results.jsx'
import SecurityTests from './components/SecurityTestsInfo.jsx'

function App() {
  return (
    <>
    <div className='header'>
      <p className='group-name'>Team SAAB</p>
      </div>
      <div className='app-container'>
        <h1 className='app-title'>Dynamic Security Testing Tool</h1>
        <p className='app-subtitle'>This tool use 4 tests to scan websites for different types of vulnerabilities</p>
        <p className='app-instructions'>Enter a URL below to start a security scan:</p>
        <UrlInputForm/>
        <Results/>
        <SecurityTests/>
      </div>
    </>
  )
}

export default App
