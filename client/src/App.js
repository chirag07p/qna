import React from 'react';
import axios from 'axios';
import { Search, Database, Sparkles, Copy, Check, ChevronLeft, HelpCircle } from 'lucide-react';
import "./App.css";

// App component for Q&A Search Assistant
function App() {
  // Query input state
  const [query, setQuery] = React.useState('');
  // State to store search results
  const [results, setResults] = React.useState([]);
  // State to handle loading state
  const [loading, setLoading] = React.useState(false);
  // State to handle whether a search has been performed
  const [hasSearched, setHasSearched] = React.useState(false);
  // Stats state
  const [stats, setStats] = React.useState({ total_records: 0, columns: [] });
  
  // Custom search parameters
  const threshold = 50.0;
  const topK = 3;
  
  // Copied state mapping result card index to copy-success boolean
  const [copiedIndex, setCopiedIndex] = React.useState(null);

  // Ref for input element
  const inputRef = React.useRef(null);

  // Load backend stats on mount
  React.useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await axios.get('/api/stats');
        if (res.data?.status === 'success') {
          setStats({
            total_records: res.data.total_records,
            columns: res.data.columns
          });
        }
      } catch (err) {
        console.error("Failed to load statistics:", err);
      }
    };
    fetchStats();
  }, []);

  // Suggested starter queries
  const suggestedQueries = [
    "How to reset my password?",
    "Check system status",
    "How to export answers to Excel?",
    "Database connection configuration"
  ];

  // Function to handle search
  const handleSearch = async (e, customQuery = null) => {
    if (e) e.preventDefault();
    const activeQuery = customQuery !== null ? customQuery : query;
    if (!activeQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);
    
    try {
      const res = await axios.post('/api/query', {
        query: activeQuery.trim(),
        threshold: parseFloat(threshold),
        top_k: parseInt(topK)
      });
      setResults(res.data?.matches || []);
    } catch (err) {
      console.error("Query failed:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Helper for copy to clipboard
  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(idx);
      setTimeout(() => {
        setCopiedIndex(null);
      }, 1500);
    });
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

  // Helper to determine confidence level
  const getConfidenceLevel = (score) => {
    if (score >= 80) return { label: 'High Confidence', class: 'confidence-high' };
    if (score >= 60) return { label: 'Mid Confidence', class: 'confidence-mid' };
    return { label: 'Low Confidence', class: 'confidence-low' };
  };

  return (
    <div className="app-container">
      {/* Brand Header */}
      <div className="header-container">
        <div className="brand-badge">
          <span className="brand-badge-dot"></span>
          <span>Cognitive Search Engine</span>
        </div>
        <h1 className="main-title">Q&A Knowledge Base</h1>
        <p className="main-subtitle">Locally-powered vector and token matching index</p>
        
        {stats.total_records > 0 && (
          <div className="stats-bar">
            <span className="stat-item">
              <Database size={13} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
              Loaded Records: <strong>{stats.total_records}</strong>
            </span>
            <span className="stat-item">
              Columns: <strong>{stats.columns.slice(0, 2).join(', ')}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Suggested Quick Searches (Hidden after search is done or when searching) */}
      {!hasSearched && !loading && (
        <div className="suggestions-container">
          {suggestedQueries.map((q, idx) => (
            <button
              key={idx}
              className="suggestion-pill"
              onClick={(e) => {
                setQuery(q);
                handleSearch(e, q);
              }}
            >
              <Sparkles size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Control Configuration Panel */}

      {!hasSearched && !loading ? (
        // Search bar for new search
        <form onSubmit={(e) => handleSearch(e)} className="search-form">
          <div className="search-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your query and press Enter..."
              autoFocus
            />
            <button type="submit" className="search-icon-btn">
              <Search size={22} />
            </button>
          </div>
        </form>
      ) : (
        // Results or Loading Container
        <div className="results-container">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <div className="loading-text">Analyzing query similarity...</div>
            </div>
          ) : (
            <>
              <div className="results-header-wrapper">
                <h2 className="results-title">
                  Search Results for "{query}"
                </h2>
                <button className="back-button" onClick={handleBack}>
                  <ChevronLeft size={16} />
                  New Search
                </button>
              </div>

              {results.length > 0 ? (
                results.map((match, idx) => {
                  const confidence = getConfidenceLevel(match.score);
                  return (
                    <div key={idx} className="result-card">
                      <div className="card-header">
                        <h3 className="matched-question">{match.matched_question}</h3>
                        <span className={`confidence-badge ${confidence.class}`}>
                          {confidence.label} ({match.score.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="answer-wrapper">
                        <p className="answer">{match.answer}</p>
                      </div>
                      <div className="card-actions">
                        <button
                          className={`copy-btn ${copiedIndex === idx ? 'copied' : ''}`}
                          onClick={() => handleCopy(match.answer, idx)}
                        >
                          {copiedIndex === idx ? (
                            <>
                              <Check size={14} />
                              Copied!
                            </>
                          ) : (
                            <>
                              <Copy size={14} />
                              Copy Answer
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="no-results">
                  <HelpCircle size={40} style={{ marginBottom: '1rem', color: '#64748b' }} />
                  <p>No answers found matching your criteria.</p>
                  <p style={{ fontSize: '0.875rem', color: '#64748b' }}>
                    Try lowering the similarity threshold or refining your question.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

