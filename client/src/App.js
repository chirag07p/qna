import React from 'react';
import axios from 'axios';
import { Search, Sparkles, Copy, Check, ChevronLeft, HelpCircle } from 'lucide-react';
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

  // Custom search parameters
  const threshold = 50.0;
  const topK = 3;

  // Copied state mapping result card index to copy-success boolean
  const [copiedIndex, setCopiedIndex] = React.useState(null);

  // Ref for input element
  const inputRef = React.useRef(null);
  // Pool of suggested queries, initialized with fallbacks
  const [allSuggestedQueries, setAllSuggestedQueries] = React.useState([
    "How to reset my password?",
    "Check system status",
    "How to export answers to Excel?",
    "Database connection configuration"
  ]);

  // Load dynamic suggestions from backend on mount
  React.useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const res = await axios.get('/api/suggestions');
        if (res.data?.status === 'success' && Array.isArray(res.data.questions) && res.data.questions.length > 0) {
          setAllSuggestedQueries(res.data.questions);
        }
      } catch (err) {
        console.error("Failed to fetch suggestions from backend:", err);
      }
    };
    loadSuggestions();
  }, []);

  // States for rotating suggestions
  const [suggestionIdx, setSuggestionIdx] = React.useState(0);
  const [fadeSuggestions, setFadeSuggestions] = React.useState(true);

  // Rotate suggestions every 5 seconds with a fade effect
  React.useEffect(() => {
    if (hasSearched || loading || allSuggestedQueries.length <= 4) return;
    
    const interval = setInterval(() => {
      setFadeSuggestions(false);
      setTimeout(() => {
        setSuggestionIdx((prev) => (prev + 4) % allSuggestedQueries.length);
        setFadeSuggestions(true);
      }, 300); // match transition duration
    }, 5000);

    return () => clearInterval(interval);
  }, [hasSearched, loading, allSuggestedQueries.length]);

  // Get currently visible 4 suggestions (using modulo wrap-around to always show exactly 4 items)
  const currentSuggestions = React.useMemo(() => {
    const sliced = [];
    if (allSuggestedQueries.length > 0) {
      for (let i = 0; i < 4; i++) {
        sliced.push(allSuggestedQueries[(suggestionIdx + i) % allSuggestedQueries.length]);
      }
    }
    return sliced;
  }, [suggestionIdx, allSuggestedQueries]);

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
    <div className="app-layout">
      <div className="background-glows">
        <div className="glow-circle glow-1"></div>
        <div className="glow-circle glow-2"></div>
        <div className="glow-circle glow-3"></div>
      </div>
      <div className="grid-overlay"></div>

      <div className="app-container">
        
        {/* Brand Header */}
        <header className="search-header">
          <div className="logo-container" onClick={handleBack}>
            <span className="brand-dot"></span>
            <span className="logo-text">Cognitive Search</span>
          </div>
          <p className="search-subtitle">Locally-powered vector and token matching index</p>
        </header>

        {/* Search Input Form */}
        <form onSubmit={(e) => handleSearch(e)} className="search-form">
          <div className="search-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask your question..."
              autoFocus
            />
            <button type="submit" className="search-icon-btn">
              <Search size={22} />
            </button>
          </div>
        </form>

        {/* Suggested Quick Searches */}
        {!hasSearched && !loading && (
          <div className={`suggestions-container ${fadeSuggestions ? 'fade-in' : 'fade-out'}`}>
            {currentSuggestions.map((q, idx) => (
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

        {/* Results Container (Directly under search input on the same page) */}
        {(hasSearched || loading) && (
          <div className="results-container">
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <div className="loading-text">Analyzing query similarity...</div>
              </div>
            ) : (
              <div className="results-content-wrapper">
                <div className="results-info-bar">
                  <span>About {results.length} results found matching "{query}"</span>
                  <button className="clear-search-btn" onClick={handleBack}>Clear Search</button>
                </div>

                {results.length > 0 ? (
                  <div className="results-list">
                    {results.map((match, idx) => {
                      const confidence = getConfidenceLevel(match.score);
                      return (
                        <div key={idx} className="search-result-card">
                          <div className="card-header">
                            <span className="result-breadcrumb">Q&A Knowledge Base</span>
                            <h3 className="matched-question" onClick={() => { setQuery(match.matched_question); handleSearch(null, match.matched_question); }}>{match.matched_question}</h3>
                            <span className={`confidence-badge ${confidence.class}`}>
                              {confidence.label} ({match.score.toFixed(1)}%)
                            </span>
                          </div>
                          <div className="result-answer">
                            <p className="answer-text">{match.answer}</p>
                          </div>
                          <div className="result-actions">
                            <button
                              className={`copy-btn ${copiedIndex === idx ? 'copied' : ''}`}
                              onClick={() => handleCopy(match.answer, idx)}
                            >
                              {copiedIndex === idx ? (
                                <>
                                  <Check size={13} style={{ marginRight: '4px' }} />
                                  Copied!
                                </>
                              ) : (
                                <>
                                  <Copy size={13} style={{ marginRight: '4px' }} />
                                  Copy Answer
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="no-results">
                    <HelpCircle size={32} style={{ marginBottom: '1rem', color: '#64748b' }} />
                    <p>No answers found matching your criteria.</p>
                    <p style={{ fontSize: '0.875rem', color: '#64748b' }}>
                      Try choosing one of the dynamic query suggestions.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
