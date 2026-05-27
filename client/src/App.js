import React from 'react';
import axios from 'axios';
import "./App.css"
// App component for Q&A Search Assistant
function App() {
  // Query input state
  const [query,setQuery] = React.useState('');
  // State to store search results
  const [results,setResults] = React.useState([]);
  // State to handle loading state
  const [loading,setLoading] = React.useState(false);
  // State to handle whether a search has been performed
  const [hasSearched,setHasSearched] = React.useState(false);
  // Ref for input element
  const inputRef = React.useRef(null);
  // Function to handle search
  const handleSearch = async (e) => {
    // Prevent default form submission
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);
    // Try to query the knowledge base/backend server
    try {
      const res = await axios.post('/api/query', {
        query: query.trim(),
        threshold: 50.0,
        top_k: 3
      });
      // Set the results state with the matches from the backend
      setResults(res.data?.matches || []);
    } catch (err) {
      console.error("Query failed:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };
  // Function to handle back button click
  const handleBack = () => {
    setResults([]);
    setQuery('');
    setHasSearched(false);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 50);
  };
  // Render function to display the UI based on the current state
  return (
    <div className="app-container">
      {!hasSearched && !loading ? (
        // If no search has been performed and not loading, display the search form
        <form onSubmit={handleSearch} className="search-form">
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your query and press Enter..."
            autoFocus
          />
        </form>
      ) : (
        // If search has been performed and loading, display the results container
        <div className="results-container">
          {loading ? (
            <div className="loading">Searching...</div>
          ) : (
            // If loading is false, display the results
            <>
              <button className="back-button" onClick={handleBack}>
                ← Go Back
              </button>
              {results.length > 0 ? (
                // If results are found, display the results
                <>
                  <h2 className="results-header">Possible solutions are:</h2>
                  {results.map((match, idx) => (
                    //Map through the results and display each result
                    <div key={idx} className="result-card">
                      <div className="matched-question">{match.matched_question}</div>
                      <div className="answer">{match.answer}</div>
                    </div>
                  ))}
                </>
              ) : (
                // If no results are found, display the no results message
                <div className="no-results">No answers found matching your question.</div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
