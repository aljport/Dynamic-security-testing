import UrlInputForm from '../components/URL_InputForm';
import SecurityTests from '../components/SecurityTestsInfo';
import './HomePage.css';

function HomePage() {
  return (
    <>
      <div className='header'>
        <p className='group-name'>Team SAAB</p>
      </div>
      <div className='app-container'>
        <h1 className='app-title'>Dynamic Security Testing Tool</h1>
        <p className='app-subtitle'>This tool uses 4 tests to scan websites for different types of vulnerabilities</p>
        <p className='app-instructions'>Enter a URL below to start a security scan:</p>
        <UrlInputForm />
        <SecurityTests />
      </div>
    </>
  );
}

export default HomePage;
