import React, { useState } from 'react';
import axios from 'axios';

const SearchForm = ({ onResults }) => {
  const [query, setQuery] = useState('');
  const [k, setK] = useState(5);
  const [showList, setShowList] = useState(true);
  const [showSummary, setShowSummary] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || '/api';
  console.log("The API URL: ", `${API_URL}`);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate input
    if (!query.trim()) {
      setError('Please enter a search query.');
      return;
    }

    if (k <= 0) {
      setError('Please enter a positive number for top k.');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Prepare request payload
      let requestPayload = {
        query: query,
        k: k,
      };

      // Include summarizer field only if "Show Summary" is checked
      if (showSummary) {
        requestPayload.summarizer = "True";
      }

      // Log the payload to verify
      console.log('Request payload:', requestPayload);

      // Make API request using axios
      const response = await axios.post(`${API_URL}/api/search`, requestPayload);

      // Process response based on selected options
      const data = response.data;
      const results = {
        documents: showList ? data.documents : [],
        summary: showSummary ? data.summary : '', // Only show summary if "Show Summary" is checked
      };

      onResults(results);
    } catch (err) {
      console.log('API Request failed: ', err);
      setError('An error occurred while fetching the results.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <div>
        <label htmlFor="query">Search Query:</label>
        <input
          type="text"
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="k">Top K Results:</label>
        <input
          type="number"
          id="k"
          value={k}
          onChange={(e) => setK(parseInt(e.target.value))}
          min="1"
          required
        />
      </div>

      <div className="checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={showList}
            onChange={(e) => setShowList(e.target.checked)}
          />
          Show List View
        </label>

        <label>
          <input
            type="checkbox"
            checked={showSummary}
            onChange={(e) => setShowSummary(e.target.checked)}
          />
          Show Summary View
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
};

export default SearchForm;
