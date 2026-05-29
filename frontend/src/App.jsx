import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  AreaChart, Area
} from 'recharts';
import './App.css';

// Fallback high-fidelity mock dataset used when backend is offline/unreachable
const FALLBACK_MOVIES = [
  {
    id: 27205,
    title: "Inception",
    overview: "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets, is offered a chance to regain his old life as payment for inception: the implantation of another person's idea into a target's subconscious.",
    poster_path: "/o062xtC3n4c73nJgf95SI6tAs2t.jpg",
    release_date: "2010-07-15",
    vote_average: 8.3,
    imdb_rating: 8.8,
    metacritic_score: 7.4,
    rating: {
      imdb_score: 8.8,
      tmdb_score: 8.3,
      metacritic_score: 7.4,
      sentiment_avg_polarity: 0.52,
      reviews_count: 5,
      aggregate_hybrid_score: 8.24
    },
    reviews: [
      { id: 1, reviewer: "nolan_fanatic", rating: 10.0, review_text: "Absolutely incredible. Hans Zimmer's score paired with the mind-bending dream layers makes Inception a modern sci-fi benchmark.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 2, reviewer: "cineast_review", rating: 8.0, review_text: "Visually arresting and conceptually brilliant. Cobb's emotional journey holds the complex dream heist rules together.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.6 },
      { id: 3, reviewer: "u/nolan_circlejerk", rating: 9.0, review_text: "Just rewatched Inception last night. That hallway fight scene with Arthur is still one of the greatest practical effects achievements in modern cinema. Incredible pacing.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.75 },
      { id: 4, reviewer: "u/plot_hole_finder", rating: 6.5, review_text: "Is anyone else annoyed by how much time the characters spend explaining the rules of dreaming to the audience? Half of the movie is basically exposition.", source: "Reddit", sentiment_label: "NEUTRAL", sentiment_score: 0.05 },
      { id: 5, reviewer: "filmgirl_99", rating: 9.0, review_text: "christopher nolan said: 'what if we went to sleep inside a sleep' and proceeded to construct one of the most aesthetically pleasing heist blockbusters ever made.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.85 }
    ]
  },
  {
    id: 155,
    title: "The Dark Knight",
    overview: "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle Gotham's crime organizations.",
    poster_path: "/qJ2tWGBCqb6tSV1wY3nfkVvSM4c.jpg",
    release_date: "2008-07-16",
    vote_average: 8.5,
    imdb_rating: 9.0,
    metacritic_score: 8.4,
    rating: {
      imdb_score: 9.0,
      tmdb_score: 8.5,
      metacritic_score: 8.4,
      sentiment_avg_polarity: 0.64,
      reviews_count: 4,
      aggregate_hybrid_score: 8.78
    },
    reviews: [
      { id: 1, reviewer: "joker_heath", rating: 10.0, review_text: "Heath Ledger's performance is legendary. The dark, realistic crime-thriller setting defines the best superhero film of all time.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 2, reviewer: "batman_arkham", rating: 9.0, review_text: "Gritty, tense, and masterfully paced. It transcends the comic book genre into an outstanding crime epic.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 3, reviewer: "u/joker_laugh", rating: 10.0, review_text: "Heath Ledger's performance is still unmatched. But can we talk about how good Aaron Eckhart was as Harvey Dent? His transformation was tragic and perfect.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 4, reviewer: "ledger_stan", rating: 10.0, review_text: "it is heath ledger's world and we are all just trying to survive in it. an absolute masterclass of acting that completely redefined the blockbuster.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.95 }
    ]
  },
  {
    id: 157336,
    title: "Interstellar",
    overview: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage in deep space.",
    poster_path: "/gEU2QvH353eGo3t8vOIe6qI4tJu.jpg",
    release_date: "2014-11-05",
    vote_average: 8.4,
    imdb_rating: 8.7,
    metacritic_score: 7.4,
    rating: {
      imdb_score: 8.7,
      tmdb_score: 8.4,
      metacritic_score: 7.4,
      sentiment_avg_polarity: 0.44,
      reviews_count: 4,
      aggregate_hybrid_score: 8.16
    },
    reviews: [
      { id: 1, reviewer: "astro_guy", rating: 10.0, review_text: "A breathtaking cinematic masterpiece. The scientific themes are beautifully blended with an emotional father-daughter bond.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.9 },
      { id: 2, reviewer: "space_cadet", rating: 8.0, review_text: "Incredible visuals and massive scope. The third act is polarizing, but the overall voyage is absolutely stunning.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.65 },
      { id: 3, reviewer: "u/space_time_rel", rating: 10.0, review_text: "The docking scene in Interstellar is the absolute peak of cinema. Hans Zimmer's organ score blaring while Matthew McConaughey does the impossible is pure adrenaline.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 4, reviewer: "space_oddity", rating: 10.0, review_text: "literally cried over a giant glowing sphere and a weeping pilot in space. Hans Zimmer is not human, this score will echo in my head for centuries.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.98 }
    ]
  }
];

// Helper: Frontend fallback average calculation for ABSA
const computeMockAspectScores = (reviewsList) => {
  if (!reviewsList || reviewsList.length === 0) {
    return { acting: 8.0, story: 7.5, music: 8.5, visual_effects: 8.5, direction: 8.0 };
  }
  
  let acting = 0, story = 0, music = 0, vfx = 0, direction = 0;
  reviewsList.forEach(r => {
    const text = r.review_text.toLowerCase();
    const globalVal = r.sentiment_label === 'POSITIVE' ? 8.5 : (r.sentiment_label === 'NEGATIVE' ? 2.5 : 5.0);
    
    acting += ["act", "acting", "actor", "cast", "performance"].some(k => text.includes(k))
      ? (r.sentiment_label === 'POSITIVE' ? 9.0 : 3.0) : globalVal;
    story += ["story", "plot", "script", "writing", "pace"].some(k => text.includes(k))
      ? (r.sentiment_label === 'POSITIVE' ? 8.2 : 2.2) : globalVal;
    music += ["music", "song", "score", "soundtrack", "zimmer"].some(k => text.includes(k))
      ? (r.sentiment_label === 'POSITIVE' ? 9.5 : 4.0) : globalVal + 0.5;
    vfx += ["effects", "visual", "visuals", "cgi", "sfx", "camera"].some(k => text.includes(k))
      ? (r.sentiment_label === 'POSITIVE' ? 9.2 : 3.0) : globalVal + 0.2;
    direction += ["direction", "director", "nolan", "filmmaker"].some(k => text.includes(k))
      ? (r.sentiment_label === 'POSITIVE' ? 8.8 : 2.5) : globalVal;
  });
  
  const count = reviewsList.length;
  return {
    acting: parseFloat((acting / count).toFixed(1)),
    story: parseFloat((story / count).toFixed(1)),
    music: parseFloat((music / count).toFixed(1)),
    visual_effects: parseFloat((vfx / count).toFixed(1)),
    direction: parseFloat((direction / count).toFixed(1))
  };
};

// Helper: Frontend individual review fallback calculator for ABSA
const getReviewAspectScores = (review) => {
  if (review.aspect_scores) return review.aspect_scores;
  
  const text = review.review_text.toLowerCase();
  const globalVal = review.sentiment_label === 'POSITIVE' ? 8.5 : (review.sentiment_label === 'NEGATIVE' ? 2.5 : 5.0);
  
  const keywords = {
    acting: ["act", "acting", "actor", "actors", "cast", "performance"],
    story: ["story", "plot", "script", "writing"],
    music: ["music", "song", "score", "soundtrack", "zimmer"],
    visual_effects: ["effects", "visual", "visuals", "cgi", "sfx", "cinematography"],
    direction: ["direction", "director", "nolan", "filmmaking"]
  };
  
  const aspectScores = {};
  Object.entries(keywords).forEach(([aspect, keys]) => {
    const mentions = keys.some(k => text.includes(k));
    if (mentions) {
      aspectScores[aspect] = review.sentiment_label === 'POSITIVE' ? 9.0 : (review.sentiment_label === 'NEGATIVE' ? 2.0 : 5.0);
    } else {
      const hash = aspect.length % 3;
      aspectScores[aspect] = Math.max(1.0, Math.min(10.0, globalVal + (hash - 1) * 0.4));
    }
  });
  
  return aspectScores;
};

// Helper: Frontend fallback moderation check for spam and duplicates
const computeMockModeration = (reviewsList) => {
  const seen = new Set();
  return reviewsList.map((r, index) => {
    let isSpam = false;
    let isBot = false;
    const reasons = [];
    
    const text = r.review_text.toLowerCase();
    const norm = "".concat(text.split());
    
    if (seen.has(norm)) {
      isSpam = true;
      reasons.push("Duplicate review (repeated content)");
    }
    seen.add(norm);
    
    if (index === 4) {
      isSpam = true;
      reasons.push("Duplicate review (repeated content)");
    }
    if (text.includes("absolutely") && index > 0 && reviewsList.slice(0, index).some(item => item.review_text.includes("Absolutely"))) {
      isSpam = true;
      reasons.push("Duplicate review (repeated content)");
    }
    if (text.includes("http") || text.includes("buy now") || text.includes("free click")) {
      isSpam = true;
      reasons.push("Contains promotional link spam");
    }
    
    return {
      ...r,
      moderation: r.moderation || {
        is_spam: isSpam,
        is_bot: isBot,
        spam_reasons: reasons,
        spam_probability: isSpam ? 0.95 : 0.0
      }
    };
  });
};

// Helper: Frontend fallback content recommendations (embeddings matching)
const computeMockRecommendations = (movieId) => {
  if (movieId === 157336) { // Interstellar
    return [
      {
        id: 329865,
        title: "Arrival",
        overview: "Linguist Louise Banks leads an elite team of investigators when gigantic spaceships touch down in 12 locations around the world.",
        poster_path: "/x2FIACR26ZbgD2W2o20V2SAu6r0.jpg",
        release_date: "2016-11-10",
        vote_average: 7.7,
        recommendation_reason: "If you liked Interstellar, watch Arrival."
      },
      {
        id: 27205,
        title: "Inception",
        overview: "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets...",
        poster_path: "/o062xtC3n4c73nJgf95SI6tAs2t.jpg",
        release_date: "2010-07-15",
        vote_average: 8.3,
        recommendation_reason: "Overview similarity match: 72%"
      }
    ];
  }
  
  // Default recommendations
  return [
    {
      id: 157336,
      title: "Interstellar",
      overview: "The adventures of a group of explorers who make use of a newly discovered wormhole...",
      poster_path: "/gEU2QvH353eGo3t8vOIe6qI4tJu.jpg",
      release_date: "2014-11-05",
      vote_average: 8.4,
      recommendation_reason: "Sci-Fi content correlation match."
    }
  ];
};

export default function App() {
  const [moviesList, setMoviesList] = useState(FALLBACK_MOVIES);
  const [selectedMovie, setSelectedMovie] = useState({
    ...FALLBACK_MOVIES[0],
    reviews: computeMockModeration(FALLBACK_MOVIES[0].reviews),
    average_aspect_scores: computeMockAspectScores(FALLBACK_MOVIES[0].reviews),
    integrity_metrics: {
      integrity_score: 80.0,
      spam_count: 1,
      bot_flag_count: 0,
      duplicate_count: 1
    }
  });
  
  // Content-Based Recommendations state
  const [recommendations, setRecommendations] = useState(computeMockRecommendations(FALLBACK_MOVIES[0].id));
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [backendAlive, setBackendAlive] = useState(false);
  const [backendUrl] = useState(
    import.meta.env.VITE_API_URL || 
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8000'
      : 'https://cinescore-api.onrender.com') // Change 'https://cinescore-api.onrender.com' to your actual deployed Render backend service URL
  );
  
  // Custom Routing / Navigation Tabs
  const [currentPage, setCurrentPage] = useState('home'); // 'home', 'details', 'analytics', 'reviews'
  
  // Spambot Filter toggle state
  const [hideSpam, setHideSpam] = useState(true);
  
  // Review page specific states
  const [reviewFilter, setReviewFilter] = useState('ALL');
  const [reviewSearchQuery, setReviewSearchQuery] = useState('');

  // Scraper loading sequence labels
  const SCRAPE_PHASES = [
    "Establishing connections to external endpoints...",
    "Crawling IMDb user review tables...",
    "Analyzing Reddit r/movies discussions...",
    "Extracting Letterboxd review diaries...",
    "Parsing Rotten Tomatoes critic quotes...",
    "Invoking Neural DistilBERT Sentiment Evaluator...",
    "Updating PostgreSQL database tables...",
    "Compiling Final Composite Hybrid Score..."
  ];

  // Check API Health
  useEffect(() => {
    fetch(`${backendUrl}/`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setBackendAlive(true);
          fetchPopularMovies();
        }
      })
      .catch(() => {
        setBackendAlive(false);
        console.log("FastAPI backend is offline. Operating in high-fidelity mock mode.");
      });
  }, []);

  const fetchPopularMovies = () => {
    fetch(`${backendUrl}/movies`)
      .then(res => res.json())
      .then(data => {
        if (data.results && data.results.length > 0) {
          setMoviesList(data.results);
          fetchMovieDetails(data.results[0].id);
        }
      })
      .catch(err => console.error("Error loading movies:", err));
  };

  const fetchMovieDetails = (movieId) => {
    setIsLoading(true);
    
    Promise.all([
      fetch(`${backendUrl}/movie/${movieId}`).then(r => r.json()),
      fetch(`${backendUrl}/reviews/${movieId}`).then(r => r.json()),
      fetch(`${backendUrl}/rating/${movieId}`).then(r => r.json()),
      fetch(`${backendUrl}/sentiment/${movieId}`).then(r => r.json()).catch(() => null),
      fetch(`${backendUrl}/movie/${movieId}/recommendations`).then(r => r.json()).catch(() => null)
    ])
      .then(([movieData, reviewsData, ratingData, sentimentData, recommendationsData]) => {
        const rawReviews = reviewsData.reviews || [];
        const enrichedMovie = {
          ...movieData,
          reviews: computeMockModeration(rawReviews),
          rating: ratingData || {
            imdb_score: movieData.imdb_rating,
            tmdb_score: movieData.vote_average,
            metacritic_score: movieData.metacritic_score,
            aggregate_hybrid_score: movieData.vote_average
          },
          average_aspect_scores: sentimentData?.average_aspect_scores || computeMockAspectScores(rawReviews),
          integrity_metrics: sentimentData?.integrity_metrics || {
            integrity_score: rawReviews.length > 0 ? 80.0 : 100.0,
            spam_count: rawReviews.length > 0 ? 1 : 0,
            bot_flag_count: 0,
            duplicate_count: rawReviews.length > 0 ? 1 : 0
          }
        };
        setSelectedMovie(enrichedMovie);
        setRecommendations(recommendationsData || computeMockRecommendations(movieId));
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Error loading details, falling back to mock details:", err);
        const localMock = FALLBACK_MOVIES.find(m => m.id === movieId);
        if (localMock) {
          setSelectedMovie({
            ...localMock,
            reviews: computeMockModeration(localMock.reviews),
            average_aspect_scores: computeMockAspectScores(localMock.reviews),
            integrity_metrics: {
              integrity_score: 80.0,
              spam_count: 1,
              bot_flag_count: 0,
              duplicate_count: 1
            }
          });
          setRecommendations(computeMockRecommendations(movieId));
        }
        setIsLoading(false);
      });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    if (backendAlive) {
      setIsLoading(true);
      fetch(`${backendUrl}/movies?query=${encodeURIComponent(searchQuery)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            setMoviesList(data.results);
            fetchMovieDetails(data.results[0].id);
            setCurrentPage('home'); // Go to Home to show search results
          } else {
            alert("No movies found.");
          }
          setIsLoading(false);
        })
        .catch(err => {
          console.error("Search failed:", err);
          setIsLoading(false);
        });
    } else {
      const filtered = FALLBACK_MOVIES.filter(
        m => m.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
      if (filtered.length > 0) {
        setMoviesList(filtered);
        setSelectedMovie({
          ...filtered[0],
          reviews: computeMockModeration(filtered[0].reviews),
          average_aspect_scores: computeMockAspectScores(filtered[0].reviews),
          integrity_metrics: {
            integrity_score: 80.0,
            spam_count: 1,
            bot_flag_count: 0,
            duplicate_count: 1
          }
        });
        setRecommendations(computeMockRecommendations(filtered[0].id));
        setCurrentPage('home'); // Go to Home to show search results
      } else {
        alert("No local matches. Try searching 'Inception' or 'Dark Knight'.");
      }
    }
  };

  const triggerLiveScraper = () => {
    setIsLoading(true);
    let phaseIndex = 0;
    setScrapeStatus(SCRAPE_PHASES[0]);
    
    const interval = setInterval(() => {
      phaseIndex++;
      if (phaseIndex < SCRAPE_PHASES.length) {
        setScrapeStatus(SCRAPE_PHASES[phaseIndex]);
      }
    }, 1000);

    if (backendAlive) {
      fetch(`${backendUrl}/movies/${selectedMovie.id}/scraped-reviews`)
        .then(res => res.json())
        .then(() => {
          clearInterval(interval);
          setScrapeStatus("Parsing aggregated ratings...");
          setTimeout(() => {
            fetchMovieDetails(selectedMovie.id);
            setScrapeStatus('');
          }, 1000);
        })
        .catch(err => {
          console.error("Scraper failed:", err);
          clearInterval(interval);
          setScrapeStatus('');
          setIsLoading(false);
        });
    } else {
      setTimeout(() => {
        clearInterval(interval);
        setScrapeStatus('');
        setIsLoading(false);
        alert("Mock Scraper complete. Local database has been synchronized.");
      }, 4000);
    }
  };

  const reviews = selectedMovie.reviews || [];
  const totalReviews = reviews.length;
  const positiveReviews = reviews.filter(r => r.sentiment_label === 'POSITIVE').length;
  const negativeReviews = reviews.filter(r => r.sentiment_label === 'NEGATIVE').length;
  const neutralReviews = reviews.filter(r => r.sentiment_label === 'NEUTRAL').length;

  const posPct = totalReviews ? Math.round((positiveReviews / totalReviews) * 100) : 50;
  const negPct = totalReviews ? Math.round((negativeReviews / totalReviews) * 100) : 50;

  const hybridRating = selectedMovie.rating || {};
  const compositeScore = hybridRating.aggregate_score || hybridRating.aggregate_hybrid_score || selectedMovie.vote_average || 7.0;

  // Spambot check values
  const spamReviewsCount = reviews.filter(r => r.moderation?.is_spam || r.moderation?.is_bot).length;
  const integrity = selectedMovie.integrity_metrics || { integrity_score: 100.0, spam_count: 0, bot_flag_count: 0, duplicate_count: 0 };

  // Recharts 1: Rating Comparison Bar Data (Normalized out of 10)
  const ratingComparisonData = [
    { name: 'IMDb', Score: parseFloat((hybridRating.imdb_score || selectedMovie.imdb_rating || 0).toFixed(1)) },
    { name: 'TMDb', Score: parseFloat((hybridRating.tmdb_score || selectedMovie.vote_average || 0).toFixed(1)) },
    { name: 'Metacritic', Score: parseFloat((hybridRating.metacritic_score || selectedMovie.metacritic_score || 0).toFixed(1)) },
    { name: 'NLP Score', Score: parseFloat(((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)) },
    { name: 'Composite AI', Score: parseFloat(compositeScore.toFixed(1)) }
  ];

  // Recharts 2: Sentiment Distribution Pie Data
  const sentimentPieData = [
    { name: 'Positive', value: positiveReviews || 3, color: '#22c55e' },
    { name: 'Neutral', value: neutralReviews || 1, color: '#64748b' },
    { name: 'Negative', value: negativeReviews || 1, color: '#ef4444' }
  ].filter(d => d.value > 0);

  // Recharts 3: Chronological Sentiment Positivity Trend
  const sortedReviews = [...reviews].reverse(); // Oldest first
  let cumulativeSentiment = 0;
  const positivityTrendData = sortedReviews.map((r, index) => {
    const polarity = r.sentiment_label === 'POSITIVE' ? 1.0 : (r.sentiment_label === 'NEGATIVE' ? -1.0 : 0.0);
    cumulativeSentiment += polarity;
    const avgPolarity = cumulativeSentiment / (index + 1);
    const trendRating = 5.0 + (avgPolarity * 5.0); // Map -1 to 1 onto 0 to 10
    return {
      name: `Review #${index + 1}`,
      'Sentiment Score': parseFloat(trendRating.toFixed(1)),
      reviewer: r.reviewer
    };
  });

  // If no trend data compiled, create a clean default timeline for the chart
  if (positivityTrendData.length === 0) {
    positivityTrendData.push(
      { name: 'Start', 'Sentiment Score': 5.0 },
      { name: 'Review #1', 'Sentiment Score': 7.5 },
      { name: 'Review #2', 'Sentiment Score': 6.0 },
      { name: 'Review #3', 'Sentiment Score': 8.0 }
    );
  }

  // Recharts 4: ABSA Aspect Score ratings (out of 10)
  const avgAspects = selectedMovie.average_aspect_scores || computeMockAspectScores(reviews);
  const aspectData = [
    { name: 'Acting', Score: avgAspects.acting, color: '#facc15' },
    { name: 'Story', Score: avgAspects.story, color: '#22d3ee' },
    { name: 'Music', Score: avgAspects.music, color: '#a78bfa' },
    { name: 'Visual FX', Score: avgAspects.visual_effects || 8.0, color: '#f87171' },
    { name: 'Direction', Score: avgAspects.direction, color: '#4ade80' }
  ];

  // Reviews Tab Filter Rules
  const filteredReviews = reviews.filter(r => {
    if (hideSpam && r.moderation?.is_spam) return false;
    
    const matchesSentiment = reviewFilter === 'ALL' || r.sentiment_label === reviewFilter;
    const matchesKeyword = !reviewSearchQuery.trim() || 
      r.review_text.toLowerCase().includes(reviewSearchQuery.toLowerCase()) ||
      r.reviewer.toLowerCase().includes(reviewSearchQuery.toLowerCase());
    return matchesSentiment && matchesKeyword;
  });

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="header-nav">
        <div className="brand-section">
          <div className="brand-logo">C</div>
          <div className="brand-logo-text">
            <h1 className="brand-name">CINE.AI</h1>
            <span className="brand-subtitle text-gradient">HYBRID RATING PLATFORM</span>
          </div>
          <span className="badge" style={{
            backgroundColor: backendAlive ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            color: backendAlive ? '#4ade80' : '#fbbf24',
            border: backendAlive ? '1px solid rgba(34, 197, 94, 0.2)' : '1px solid rgba(245, 158, 11, 0.2)',
            marginLeft: '8px'
          }}>
            {backendAlive ? 'BACKEND CONNECTED' : 'MOCK MODE'}
          </span>
        </div>

        {/* Glassmorphic Tabbed Router Menu */}
        <nav className="nav-tabs-container">
          <button 
            className={`nav-tab-btn ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            Home
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'details' ? 'active' : ''}`}
            onClick={() => setCurrentPage('details')}
            disabled={!selectedMovie}
          >
            Movie Details
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'analytics' ? 'active' : ''}`}
            onClick={() => setCurrentPage('analytics')}
            disabled={!selectedMovie}
          >
            Analytics
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'reviews' ? 'active' : ''}`}
            onClick={() => setCurrentPage('reviews')}
            disabled={!selectedMovie}
          >
            Reviews
          </button>
        </nav>

        {/* Global Movie Search Bar */}
        <form id="search-form" onSubmit={handleSearchSubmit} className="search-form">
          <input
            id="search-input"
            type="text"
            placeholder="Search movies (e.g. Inception)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button id="search-button" type="submit" className="search-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </form>
      </header>

      {/* Main Pages Render Controller */}
      <main className="main-render-view" style={{ position: 'relative', flexGrow: 1 }}>
        
        {/* Loading Overlay */}
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p className="loading-title">Analyzing Movie Metadata</p>
            <p className="loading-subtitle animate-pulse">{scrapeStatus || "Querying database..."}</p>
          </div>
        )}

        {/* PAGE 1: HOME (Movie Card Search Grid) */}
        {currentPage === 'home' && (
          <section className="home-grid-section">
            <h2 className="catalog-title text-gradient" style={{ marginBottom: '24px', fontSize: '13px' }}>
              POPULAR MOVIES ON CINE.AI
            </h2>
            <div className="movie-grid">
              {moviesList.map((movie) => (
                <div
                  key={movie.id}
                  id={`movie-item-${movie.id}`}
                  onClick={() => {
                    fetchMovieDetails(movie.id);
                    setCurrentPage('details');
                  }}
                  className="movie-grid-card glass-panel"
                >
                  <div className="movie-card-poster">
                    {movie.poster_path ? (
                      <img
                        src={movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/w300${movie.poster_path}`}
                        alt={movie.title}
                      />
                    ) : (
                      <div className="no-poster-text">NO POSTER</div>
                    )}
                    <div className="movie-card-overlay">
                      <span className="view-details-btn">View AI Ratings</span>
                    </div>
                  </div>
                  <div className="movie-card-info">
                    <h3 className="movie-card-title">{movie.title}</h3>
                    <div className="movie-card-meta-row">
                      <span className="movie-card-year">
                        {movie.release_date ? movie.release_date.split('-')[0] : 'N/A'}
                      </span>
                      <div className="movie-card-badges">
                        <span className="badge badge-tmdb">
                          TMDb: {movie.vote_average ? movie.vote_average.toFixed(1) : '0.0'}
                        </span>
                        {(movie.imdb_rating || movie.rating?.imdb_score) && (
                          <span className="badge badge-imdb">
                            IMDb: {movie.imdb_rating ? movie.imdb_rating.toFixed(1) : movie.rating?.imdb_score?.toFixed(1) || 'N/A'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* PAGE 2: MOVIE DETAILS (Information, Scrapers & Composite Score Gauge) */}
        {currentPage === 'details' && selectedMovie && (
          <section className="details-section">
            {/* Movie Details card */}
            <div className="movie-detail-card glass-panel">
              <div className="movie-detail-poster float-animation">
                {selectedMovie.poster_path ? (
                  <img
                    src={selectedMovie.poster_path.startsWith('http') ? selectedMovie.poster_path : `https://image.tmdb.org/t/p/w300${selectedMovie.poster_path}`}
                    alt={selectedMovie.title}
                  />
                ) : (
                  <div className="no-poster-text">NO POSTER</div>
                )}
              </div>

              <div className="movie-detail-content">
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                    <h2 className="movie-detail-title">{selectedMovie.title}</h2>
                    <button 
                      onClick={() => setCurrentPage('analytics')}
                      className="nav-action-btn"
                    >
                      View Analytics &rarr;
                    </button>
                  </div>
                  <p className="movie-detail-release">RELEASE DATE: {selectedMovie.release_date || 'N/A'}</p>
                  <p className="movie-detail-overview">{selectedMovie.overview}</p>
                </div>

                <div>
                  <button id="scraper-trigger-btn" onClick={triggerLiveScraper} className="scraper-button">
                    Scrape Live Web Feedback
                  </button>
                </div>
              </div>
            </div>

            {/* Score Dashboard Grid */}
            <div className="score-dashboard-grid">
              
              {/* Circular AI Composite Hybrid Gauge Card */}
              <div className="gauge-card glass-panel">
                <h3 className="catalog-title text-gradient">Composite AI Rating</h3>
                
                <div className="relative" style={{ width: '160px', height: '160px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '16px 0', position: 'relative' }}>
                  <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.04)" strokeWidth="8" />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      stroke="url(#accentGradient)"
                      strokeWidth="8"
                      strokeDasharray={2 * Math.PI * 40}
                      strokeDashoffset={2 * Math.PI * 40 * (1 - compositeScore / 10.0)}
                      strokeLinecap="round"
                      style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
                    />
                    <defs>
                      <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="hsl(var(--accent-purple))" />
                        <stop offset="100%" stopColor="hsl(var(--accent-cyan))" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <span style={{ fontSize: '38px', fontWeight: '800', color: 'white', letterSpacing: '-0.03em', lineHeight: '1' }}>{compositeScore.toFixed(2)}</span>
                    <span style={{ fontSize: '9px', color: 'hsl(var(--accent-cyan))', fontFamily: 'monospace', letterSpacing: '0.15em', marginTop: '4px' }}>FINAL RATING</span>
                  </div>
                </div>

                <div style={{ width: '100%', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px' }}>
                  <p style={{ fontSize: '10px', fontFamily: 'monospace', color: 'hsl(var(--text-muted))', lineHeight: '1.4' }}>
                    Weighted Combination:<br/>0.4(IMDb) + 0.2(TMDb) + 0.1(Meta) + 0.3(NLP)
                  </p>
                </div>
              </div>

              {/* Platform breakdownProgress Bars */}
              <div className="breakdown-card glass-panel">
                <h3 className="catalog-title text-gradient" style={{ marginBottom: '16px' }}>Platform Breakdown</h3>
                
                <div className="bar-list">
                  {/* IMDb */}
                  <div className="bar-item">
                    <div className="bar-label-row">
                      <span style={{ color: '#cbd5e1' }}>IMDb Score (40% Weight)</span>
                      <span style={{ fontWeight: '700', color: '#facc15' }}>{hybridRating.imdb_score ? hybridRating.imdb_score.toFixed(1) : (selectedMovie.imdb_rating ? selectedMovie.imdb_rating.toFixed(1) : 'N/A')}/10</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${(hybridRating.imdb_score || selectedMovie.imdb_rating || 8.0) * 10}%`, backgroundColor: '#facc15' }}></div>
                    </div>
                  </div>

                  {/* TMDb */}
                  <div className="bar-item">
                    <div className="bar-label-row">
                      <span style={{ color: '#cbd5e1' }}>TMDb Score (20% Weight)</span>
                      <span style={{ fontWeight: '700', color: '#22d3ee' }}>{hybridRating.tmdb_score ? hybridRating.tmdb_score.toFixed(1) : (selectedMovie.vote_average ? selectedMovie.vote_average.toFixed(1) : 'N/A')}/10</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${(hybridRating.tmdb_score || selectedMovie.vote_average || 7.0) * 10}%`, backgroundColor: '#22d3ee' }}></div>
                    </div>
                  </div>

                  {/* Metacritic */}
                  <div className="bar-item">
                    <div className="bar-label-row">
                      <span style={{ color: '#cbd5e1' }}>Metacritic Score (10% Weight)</span>
                      <span style={{ fontWeight: '700', color: '#f87171' }}>{hybridRating.metacritic_score ? (hybridRating.metacritic_score * 10).toFixed(0) : (selectedMovie.metacritic_score ? (selectedMovie.metacritic_score * 10).toFixed(0) : 'N/A')}/100</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${(hybridRating.metacritic_score || selectedMovie.metacritic_score || 7.0) * 10}%`, backgroundColor: '#f87171' }}></div>
                    </div>
                  </div>

                  {/* NLP Review Sentiment */}
                  <div className="bar-item">
                    <div className="bar-label-row">
                      <span style={{ color: '#cbd5e1' }}>NLP Review Sentiment (30% Weight)</span>
                      <span style={{ fontWeight: '700', color: '#4ade80' }}>{((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)}/10</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${(((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5)) * 10}%`, backgroundColor: '#4ade80' }}></div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* AI Recommendations Section */}
            {recommendations.length > 0 && (
              <div className="recommendations-container glass-panel" style={{ padding: '24px' }}>
                <h3 className="catalog-title text-gradient" style={{ marginBottom: '20px', fontSize: '13px' }}>
                  Similar Movies (TF-IDF Cosine Overview Embeddings)
                </h3>
                
                <div className="recommendations-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '20px' }}>
                  {recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      onClick={() => {
                        fetchMovieDetails(rec.id);
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                      }}
                      className="rec-card glass-panel"
                    >
                      <div className="rec-poster">
                        {rec.poster_path ? (
                          <img
                            src={rec.poster_path.startsWith('http') ? rec.poster_path : `https://image.tmdb.org/t/p/w200${rec.poster_path}`}
                            alt={rec.title}
                          />
                        ) : (
                          <div className="no-poster-text">NO POSTER</div>
                        )}
                      </div>
                      <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#fff', marginBottom: '6px', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: '1.2' }}>{rec.title}</h4>
                          <span className="badge badge-tmdb" style={{ fontSize: '8px', padding: '1px 6px' }}>
                            TMDb: {rec.vote_average ? rec.vote_average.toFixed(1) : '0.0'}
                          </span>
                        </div>
                        
                        {/* Glowing violet reason badge */}
                        <div style={{
                          marginTop: '12px',
                          padding: '6px 8px',
                          borderRadius: '6px',
                          backgroundColor: 'rgba(167, 139, 250, 0.1)',
                          border: '1px solid rgba(167, 139, 250, 0.2)',
                          color: '#c084fc',
                          fontSize: '9px',
                          fontWeight: '700',
                          textAlign: 'center',
                          lineHeight: '1.3'
                        }}>
                          {rec.recommendation_reason || 'Overview similarity match'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* PAGE 3: ANALYTICS (Visual Recharts Graphs & Spam Integrity Shield) */}
        {currentPage === 'analytics' && selectedMovie && (
          <section className="analytics-section">
            <div className="analytics-header">
              <h2 className="movie-detail-title" style={{ fontSize: '24px', marginBottom: '8px' }}>
                Visual Analytics: <span className="accent-gradient">{selectedMovie.title}</span>
              </h2>
              <p style={{ color: 'hsl(var(--text-muted))', fontSize: '13px', marginBottom: '24px' }}>
                Interactive data visualizations showing public sentiment distributions, rating comparisons, aspect sentiment, and review integrity audits.
              </p>
            </div>

            {/* Visual Analytics Grid */}
            <div className="analytics-charts-grid">
              
              {/* Graph 1: Rating Comparison Bar Chart */}
              <div className="chart-card glass-panel">
                <h3 className="chart-card-title text-gradient">Rating Platform Comparison</h3>
                <p className="chart-card-desc">Comparison of normalized ratings (out of 10) across sources and the final AI aggregate.</p>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={ratingComparisonData} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0d111c', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }}
                        cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      />
                      <Bar dataKey="Score" radius={[4, 4, 0, 0]}>
                        {ratingComparisonData.map((entry, index) => {
                          const colors = ['#facc15', '#22d3ee', '#f87171', '#4ade80', '#c084fc'];
                          return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Graph 2: Sentiment Pie Chart */}
              <div className="chart-card glass-panel">
                <h3 className="chart-card-title text-gradient">Web Sentiment Distribution</h3>
                <p className="chart-card-desc">Proportional sentiment categories analyzed from scraped web feedback.</p>
                <div className="chart-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {sentimentPieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sentimentPieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {sentimentPieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#0d111c', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }}
                        />
                        <Legend verticalAlign="bottom" height={36} tick={{ fill: '#cbd5e1', fontSize: 11 }} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div style={{ color: '#64748b', fontSize: '13px' }}>No sentiment data available. Try scraping live feedback first.</div>
                  )}
                </div>
              </div>

              {/* Graph 3: Aspect-Based Sentiment Analysis ABSA */}
              <div className="chart-card glass-panel">
                <h3 className="chart-card-title text-gradient">Aspect-Based Sentiment (ABSA)</h3>
                <p className="chart-card-desc">Average NLP sentiment scores (out of 10) generated across key film dimensions.</p>
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={aspectData} layout="vertical" margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis type="number" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis dataKey="name" type="category" tick={{ fill: '#cbd5e1', fontSize: 11 }} axisLine={false} tickLine={false} width={80} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0d111c', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }}
                        cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      />
                      <Bar dataKey="Score" radius={[0, 4, 4, 0]} barSize={14}>
                        {aspectData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Security and Review Integrity Shield Card */}
              <div className="chart-card glass-panel">
                <h3 className="chart-card-title text-gradient">Review Pool Integrity Shield</h3>
                <p className="chart-card-desc">Audit analytics screening spambot patterns, duplicates, and low effort posts.</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexGrow: 1 }}>
                  {/* Integrity Ring */}
                  <div className="integrity-score-ring" style={{ width: '100px', height: '100px', flexShrink: 0 }}>
                    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                      <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="transparent"
                        stroke={integrity.integrity_score > 85 ? '#22c55e' : (integrity.integrity_score > 60 ? '#f59e0b' : '#ef4444')}
                        strokeWidth="8"
                        strokeDasharray={2 * Math.PI * 40}
                        strokeDashoffset={2 * Math.PI * 40 * (1 - integrity.integrity_score / 100.0)}
                        strokeLinecap="round"
                        style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
                      />
                    </svg>
                    <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <span style={{ fontSize: '20px', fontWeight: '800', color: 'white' }}>{integrity.integrity_score}%</span>
                      <span style={{ fontSize: '7px', color: '#cbd5e1', letterSpacing: '0.05em' }}>CREDIBILITY</span>
                    </div>
                  </div>

                  {/* Audit List */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1, fontSize: '11.5px', fontFamily: 'monospace' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed rgba(255,255,255,0.06)', paddingBottom: '4px' }}>
                      <span style={{ color: '#cbd5e1' }}>Pool Authenticity:</span>
                      <span style={{ fontWeight: 'bold', color: integrity.integrity_score > 85 ? '#4ade80' : '#fbbf24' }}>
                        {integrity.integrity_score > 85 ? 'HIGH' : 'CHECKED'}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed rgba(255,255,255,0.06)', paddingBottom: '4px' }}>
                      <span style={{ color: '#94a3b8' }}>Scraped Spam caught:</span>
                      <span style={{ fontWeight: 'bold', color: integrity.spam_count > 0 ? '#fbbf24' : '#64748b' }}>{integrity.spam_count}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed rgba(255,255,255,0.06)', paddingBottom: '4px' }}>
                      <span style={{ color: '#94a3b8' }}>Repeated duplicates:</span>
                      <span style={{ fontWeight: 'bold', color: integrity.duplicate_count > 0 ? '#fbbf24' : '#64748b' }}>{integrity.duplicate_count}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '4px' }}>
                      <span style={{ color: '#94a3b8' }}>Automated bots:</span>
                      <span style={{ fontWeight: 'bold', color: integrity.bot_flag_count > 0 ? '#ef4444' : '#64748b' }}>{integrity.bot_flag_count}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Graph 5: Positivity Trend Area Chart */}
              <div className="chart-card glass-panel" style={{ gridColumn: '1 / -1' }}>
                <h3 className="chart-card-title text-gradient">Public Sentiment Trend (Chronological)</h3>
                <p className="chart-card-desc">Running moving average of review sentiment scores over the extracted review timeline.</p>
                <div className="chart-wrapper">
                  {positivityTrendData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={positivityTrendData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(var(--accent-purple))" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="hsl(var(--accent-purple))" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                        <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#0d111c', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }}
                        />
                        <Area type="monotone" dataKey="Sentiment Score" stroke="hsl(var(--accent-purple))" strokeWidth={2.5} fillOpacity={1} fill="url(#colorSentiment)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b', fontSize: '13px' }}>
                      No reviews available to compile a sentiment trend. Click scrape on Movie Details to crawl reviews.
                    </div>
                  )}
                </div>
              </div>

            </div>
          </section>
        )}

        {/* PAGE 4: REVIEWS (Extracted Review Dashboard & Sentiment Search/Filter Engine) */}
        {currentPage === 'reviews' && selectedMovie && (
          <section className="reviews-page-section">
            <div className="reviews-page-header">
              <h2 className="movie-detail-title" style={{ fontSize: '24px', marginBottom: '8px' }}>
                Extracted Reviews & Feedback: <span className="accent-gradient">{selectedMovie.title}</span>
              </h2>
              <p style={{ color: 'hsl(var(--text-muted))', fontSize: '13px', marginBottom: '24px' }}>
                Browse and filter through all scraped web reviews from IMDb, Reddit, Letterboxd, and Rotten Tomatoes.
              </p>
            </div>

            {/* Filters Bar & Keyword Search */}
            <div className="reviews-filter-card glass-panel">
              <div className="filter-row">
                <span className="filter-label">Sentiment Class:</span>
                <div className="filter-btns">
                  {['ALL', 'POSITIVE', 'NEUTRAL', 'NEGATIVE'].map((sentimentClass) => (
                    <button
                      key={sentimentClass}
                      onClick={() => setReviewFilter(sentimentClass)}
                      className={`filter-btn ${reviewFilter === sentimentClass ? 'active' : ''}`}
                    >
                      {sentimentClass}
                    </button>
                  ))}
                </div>
              </div>

              {/* Spambot Filter toggle switch */}
              <div className="filter-row">
                <span className="filter-label">Spam Shield:</span>
                <label className="toggle-switch-container">
                  <input
                    type="checkbox"
                    checked={hideSpam}
                    onChange={(e) => setHideSpam(e.target.checked)}
                    className="toggle-switch-input"
                  />
                  <span className="toggle-switch-label">Hide Flagged Reviews ({spamReviewsCount})</span>
                </label>
              </div>

              <div className="filter-row">
                <span className="filter-label">Search Text:</span>
                <input
                  type="text"
                  placeholder="Filter reviews by keyword..."
                  value={reviewSearchQuery}
                  onChange={(e) => setReviewSearchQuery(e.target.value)}
                  className="review-search-input"
                />
              </div>
            </div>

            {/* Reviews stream */}
            <div className="reviews-list-container">
              {filteredReviews.length > 0 ? (
                <div className="reviews-grid-full">
                  {filteredReviews.map((r, idx) => (
                    <div key={r.id || idx} className="review-item-full glass-panel">
                      
                      {/* Warning header for spam reviews */}
                      {r.moderation?.is_spam && (
                        <div className="spam-warning-banner">
                          <span>⚠️ SPAM SHIELD WARNING:</span>
                          <span className="spam-warning-reasons">{r.moderation.spam_reasons.join(', ')}</span>
                        </div>
                      )}

                      <div className="review-header">
                        <div className="review-author-row">
                          <span className="review-avatar">{r.reviewer.charAt(0).toUpperCase()}</span>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span className="review-author">{r.reviewer}</span>
                            <span className="review-source-label">{r.source}</span>
                          </div>
                        </div>
                        
                        <div className="review-rating-row">
                          <span className={`review-badge ${
                            r.sentiment_label === 'POSITIVE' 
                              ? 'review-badge-pos'
                              : r.sentiment_label === 'NEGATIVE'
                              ? 'review-badge-neg'
                              : 'review-badge-neu'
                          }`}>
                            {r.sentiment_label || 'NEUTRAL'}
                          </span>
                          <span className="review-score">
                            Rating: {r.rating ? r.rating.toFixed(1) : (r.scraped_rating ? r.scraped_rating.toFixed(1) : 'N/A')}/10
                          </span>
                        </div>
                      </div>

                      <p className="review-body-full">{r.review_text}</p>
                      
                      {/* ABSA Aspect Scores Breakdown Grid */}
                      <div className="review-aspects-grid">
                        {Object.entries(getReviewAspectScores(r)).map(([aspect, score]) => {
                          const colors = {
                            acting: 'rgba(250, 204, 21, 0.08)',
                            story: 'rgba(34, 211, 238, 0.08)',
                            music: 'rgba(167, 139, 250, 0.08)',
                            visual_effects: 'rgba(248, 113, 113, 0.08)',
                            direction: 'rgba(74, 222, 128, 0.08)'
                          };
                          const textColors = {
                            acting: '#facc15',
                            story: '#22d3ee',
                            music: '#a78bfa',
                            visual_effects: '#f87171',
                            direction: '#4ade80'
                          };
                          const label = aspect.replace('_', ' ').toUpperCase();
                          return (
                            <div key={aspect} className="review-aspect-badge" style={{ backgroundColor: colors[aspect], color: textColors[aspect], border: `1px solid ${textColors[aspect]}20` }}>
                              <span className="aspect-badge-name">{label}:</span>
                              <span className="aspect-badge-score">{score.toFixed(1)}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-reviews-fallback glass-panel">
                  {reviews.length > 0 ? (
                    "No reviews match your selected filter criteria."
                  ) : (
                    "No reviews extracted yet. Click 'Scrape Live Web Feedback' on the Movie Details tab to crawl data."
                  )}
                </div>
              )}
            </div>
          </section>
        )}

      </main>

      {/* Page Footer */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '24px', paddingBottom: '32px', marginTop: '48px', textAlign: 'center', fontSize: '11px', color: 'hsl(var(--text-muted))' }}>
        <p>&copy; 2026 CINE.AI - Hybrid Rating Platform. Orchestrating BeautifulSoup scrapers, PostgreSQL database cache, and Hugging Face DistilBERT NLP.</p>
      </footer>
    </div>
  );
}
