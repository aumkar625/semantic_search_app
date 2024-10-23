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
      const response = await axios.post(`/search`, {
        query: query,
        k: k,
      });

      // Process response based on selected options
      const data = response.data;
      const results = {
        documents: showList ? data.documents : [],
        summary: showSummary ? data.summary : '',
      };

      onResults(results);
    } catch (err) {
      console.error(err);
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
