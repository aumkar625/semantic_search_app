import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import Results from './components/Results';
import './App.css';

function App() {
  const [results, setResults] = useState(null);

  const handleResults = (data) => {
    setResults(data);
  };

  return (
    <div className="App">
      <h1>Semantic Search Application</h1>
      <SearchForm onResults={handleResults} />
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
