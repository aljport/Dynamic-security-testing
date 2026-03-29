import { useState } from 'react'
import './App.css';
import {Routes, Route} from 'react-router';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <Routes>
      <Route path='/' element={<HomePage />}/>
      <Route path='/results/:id' element={<ResultsPage />}/>
    </Routes>
  )
}

export default App;