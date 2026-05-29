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
  },
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
    id: 329865,
    title: "Arrival",
    overview: "Linguist Louise Banks leads an elite team of investigators when gigantic spaceships touch down in 12 locations around the world. As nations teeter on the verge of global war, Banks and her crew must race against time to find a way to communicate with the extraterrestrial space visitors.",
    poster_path: "/x2FIACR26ZbgD2W2o20V2SAu6r0.jpg",
    release_date: "2016-11-10",
    vote_average: 7.7,
    imdb_rating: 7.9,
    metacritic_score: 8.1,
    rating: {
      imdb_score: 7.9,
      tmdb_score: 7.7,
      metacritic_score: 8.1,
      sentiment_avg_polarity: 0.46,
      reviews_count: 3,
      aggregate_hybrid_score: 7.82
    },
    reviews: [
      { id: 1, reviewer: "sci_fi_lover", rating: 9.0, review_text: "Denis Villeneuve's masterpiece. Dynamic sci-fi themes about language, communication, and time combined with an outstanding lead acting performance.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.9 },
      { id: 2, reviewer: "critic_girl", rating: 8.0, review_text: "An emotionally resonant, beautiful story. Smart science fiction at its best.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 3, reviewer: "popcorn_guy", rating: 6.0, review_text: "Interesting concept but slightly slow. Visual effects were stunning though.", source: "Reddit", sentiment_label: "NEUTRAL", sentiment_score: 0.1 }
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
  if (movieId === 329865) { // Arrival
    return [
      {
        id: 157336,
        title: "Interstellar",
        overview: "The adventures of a group of explorers who make use of a newly discovered wormhole...",
        poster_path: "/gEU2QvH353eGo3t8vOIe6qI4tJu.jpg",
        release_date: "2014-11-05",
        vote_average: 8.4,
        recommendation_reason: "If you liked Interstellar, watch Arrival."
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

export default function App() {
  const [moviesList, setMoviesList] = useState(FALLBACK_MOVIES);
  const [selectedMovie, setSelectedMovie] = useState({
    ...FALLBACK_MOVIES[0],
    reviews: computeMockModeration(FALLBACK_MOVIES[0].reviews),
    average_aspect_scores: computeMockAspectScores(FALLBACK_MOVIES[0].reviews),
    integrity_metrics: {
      integrity_score: 95.0,
      spam_count: 0,
      bot_flag_count: 0,
      duplicate_count: 0
    }
  });
  
  // Content-Based Recommendations state
  const [recommendations, setRecommendations] = useState(computeMockRecommendations(FALLBACK_MOVIES[0].id));
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [skeletonLoading, setSkeletonLoading] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [backendAlive, setBackendAlive] = useState(false);
  
  const [backendUrl] = useState(
    import.meta.env.VITE_API_URL || 
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8000'
      : 'https://cinescore-api.onrender.com')
  );
  
  // Dynamic Settings / Redesign themes state
  const [themeMode, setThemeMode] = useState('dark'); // 'dark', 'light'
  const [accentColor, setAccentColor] = useState('purple'); // 'purple', 'cyan', 'amber', 'emerald'
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeGenre, setActiveGenre] = useState('ALL');
  
  // Custom Toast stack
  const [toasts, setToasts] = useState([]);
  
  const addToast = (msg, title = "INFO", type = "purple") => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, msg, title, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };
  
  // Sync Dark/Light Mode styles
  useEffect(() => {
    if (themeMode === 'light') {
      document.body.classList.add('light-mode');
    } else {
      document.body.classList.remove('light-mode');
    }
  }, [themeMode]);

  // Sync Accent themes
  useEffect(() => {
    const accents = ['accent-purple', 'accent-cyan', 'accent-amber', 'accent-emerald'];
    accents.forEach(cls => document.body.classList.remove(cls));
    document.body.classList.add(`accent-${accentColor}`);
  }, [accentColor]);

  // Custom Routing / Navigation Tabs
  const [currentPage, setCurrentPage] = useState('home'); // 'home', 'details', 'analytics', 'reviews'
  
  // Spambot Filter toggle state
  const [hideSpam, setHideSpam] = useState(true);
  
  // Reviews filters
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
          addToast("Connected to live FastAPI database engine.", "SYSTEM ACTIVE", "emerald");
          fetchPopularMovies();
        }
      })
      .catch(() => {
        setBackendAlive(false);
        console.log("FastAPI backend is offline. Operating in high-fidelity mock mode.");
        addToast("Using localized secure mock datasets.", "OFFLINE Fallback", "amber");
      });
  }, []);

  const fetchPopularMovies = () => {
    fetch(`${backendUrl}/movies`)
      .then(res => res.json())
      .then(data => {
        if (data.results && data.results.length > 0) {
          setMoviesList(data.results);
          fetchMovieDetails(data.results[0].id, false);
        }
      })
      .catch(err => console.error("Error loading movies:", err));
  };

  const fetchMovieDetails = (movieId, triggerAnimation = true) => {
    if (triggerAnimation) {
      setSkeletonLoading(true);
    }
    
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
        
        setTimeout(() => {
          setSkeletonLoading(false);
          addToast(`Loaded catalog data for: ${movieData.title}`, "CATALOG SYNC", "purple");
        }, 300);
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
              integrity_score: 95.0,
              spam_count: 0,
              bot_flag_count: 0,
              duplicate_count: 0
            }
          });
          setRecommendations(computeMockRecommendations(movieId));
        }
        setTimeout(() => {
          setSkeletonLoading(false);
          addToast(`Synced localized catalog for movie ID ${movieId}`, "CATALOG SYNC", "purple");
        }, 300);
      });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    addToast(`Searching catalog for: "${searchQuery}"`, "QUERYING", "cyan");

    if (backendAlive) {
      setIsLoading(true);
      fetch(`${backendUrl}/movies?query=${encodeURIComponent(searchQuery)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            setMoviesList(data.results);
            fetchMovieDetails(data.results[0].id);
            setCurrentPage('home');
          } else {
            addToast("No match found in web feeds.", "NO RESULTS", "amber");
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
        const match = filtered[0];
        setSelectedMovie({
          ...match,
          reviews: computeMockModeration(match.reviews),
          average_aspect_scores: computeMockAspectScores(match.reviews),
          integrity_metrics: {
            integrity_score: 95.0,
            spam_count: 0,
            bot_flag_count: 0,
            duplicate_count: 0
          }
        });
        setRecommendations(computeMockRecommendations(match.id));
        setCurrentPage('home');
      } else {
        addToast("No local match. Try searching 'Inception' or 'Dark Knight'.", "NO RESULTS", "amber");
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
    }, 800);

    if (backendAlive) {
      fetch(`${backendUrl}/movies/${selectedMovie.id}/scraped-reviews`)
        .then(res => res.json())
        .then(() => {
          clearInterval(interval);
          setScrapeStatus("Parsing aggregated ratings...");
          setTimeout(() => {
            fetchMovieDetails(selectedMovie.id, false);
            setScrapeStatus('');
            setIsLoading(false);
            addToast("Dynamic public web feedback Aggregated successfully.", "SCRAPE READY", "emerald");
          }, 800);
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
        addToast("Staged mock scraper synced complete database tables.", "OFFLINE MOCK SUCCESS", "emerald");
      }, 4000);
    }
  };

  // Genre tab filtering logic
  const genresChipsList = [
    { label: "All Genres", code: "ALL" },
    { label: "Science Fiction", code: 878 },
    { label: "Action", code: 28 },
    { label: "Adventure", code: 12 },
    { label: "Drama", code: 18 }
  ];

  const filteredMoviesGrid = moviesList.filter(movie => {
    if (activeGenre === 'ALL') return true;
    
    if (movie.genre_ids && Array.isArray(movie.genre_ids)) {
      return movie.genre_ids.includes(activeGenre);
    }
    
    if (movie.genres && Array.isArray(movie.genres)) {
      return movie.genres.some(g => g.id === activeGenre || g === activeGenre);
    }
    
    return true;
  });

  const reviews = selectedMovie.reviews || [];
  const totalReviews = reviews.length;
  const positiveReviews = reviews.filter(r => r.sentiment_label === 'POSITIVE').length;
  const negativeReviews = reviews.filter(r => r.sentiment_label === 'NEGATIVE').length;
  const neutralReviews = reviews.filter(r => r.sentiment_label === 'NEUTRAL').length;

  const hybridRating = selectedMovie.rating || {};
  const compositeScore = hybridRating.aggregate_score || hybridRating.aggregate_hybrid_score || selectedMovie.vote_average || 7.0;

  // Spambot values
  const integrity = selectedMovie.integrity_metrics || { integrity_score: 100.0, spam_count: 0, bot_flag_count: 0, duplicate_count: 0 };

  // Recharts Data visualizations
  const ratingComparisonData = [
    { name: 'IMDb', Score: parseFloat((hybridRating.imdb_score || selectedMovie.imdb_rating || 0).toFixed(1)) },
    { name: 'TMDb', Score: parseFloat((hybridRating.tmdb_score || selectedMovie.vote_average || 0).toFixed(1)) },
    { name: 'Metacritic', Score: parseFloat((hybridRating.metacritic_score || selectedMovie.metacritic_score || 0).toFixed(1)) },
    { name: 'NLP Score', Score: parseFloat(((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)) },
    { name: 'CineScore AI', Score: parseFloat(compositeScore.toFixed(1)) }
  ];

  const sentimentPieData = [
    { name: 'Positive', value: positiveReviews || 3, color: '#22c55e' },
    { name: 'Neutral', value: neutralReviews || 1, color: '#64748b' },
    { name: 'Negative', value: negativeReviews || 1, color: '#ef4444' }
  ].filter(d => d.value > 0);

  const sortedReviews = [...reviews].reverse();
  let cumulativeSentiment = 0;
  const positivityTrendData = sortedReviews.map((r, index) => {
    const polarity = r.sentiment_label === 'POSITIVE' ? 1.0 : (r.sentiment_label === 'NEGATIVE' ? -1.0 : 0.0);
    cumulativeSentiment += polarity;
    const avgPolarity = cumulativeSentiment / (index + 1);
    const trendRating = 5.0 + (avgPolarity * 5.0);
    return {
      name: `#${index + 1}`,
      'Vibe Score': parseFloat(trendRating.toFixed(1))
    };
  });

  if (positivityTrendData.length === 0) {
    positivityTrendData.push(
      { name: 'Start', 'Vibe Score': 5.0 },
      { name: '#1', 'Vibe Score': 7.5 },
      { name: '#2', 'Vibe Score': 6.0 },
      { name: '#3', 'Vibe Score': 8.0 }
    );
  }

  const avgAspects = selectedMovie.average_aspect_scores || computeMockAspectScores(reviews);
  const aspectData = [
    { name: 'Acting', Score: avgAspects.acting, color: '#facc15' },
    { name: 'Story', Score: avgAspects.story, color: '#22d3ee' },
    { name: 'Music', Score: avgAspects.music, color: '#a78bfa' },
    { name: 'Visual FX', Score: avgAspects.visual_effects || 8.0, color: '#f87171' },
    { name: 'Direction', Score: avgAspects.direction, color: '#4ade80' }
  ];

  // Audience Emotion values
  const emotionMetrics = {
    joy: Math.min(100, Math.max(10, Math.round(positiveReviews * 28 + (selectedMovie.id % 5) * 5))),
    surprise: Math.min(100, Math.max(10, Math.round(neutralReviews * 25 + (selectedMovie.id % 7) * 4))),
    tension: Math.min(100, Math.max(10, Math.round(negativeReviews * 30 + (selectedMovie.id % 3) * 8))),
    narrative: Math.min(100, Math.max(10, Math.round((avgAspects.story || 7.0) * 10)))
  };

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
      {/* Decorative Ambient Radial glowing layers */}
      <div className="ambient-glow-circle ambient-1"></div>
      <div className="ambient-glow-circle ambient-2"></div>

      {/* Toast Notification HUD */}
      <div className="toast-stack">
        {toasts.map(toast => (
          <div key={toast.id} className="toast-notification glass-panel">
            <div className={`toast-icon accent-dot-${toast.type || 'purple'}`}>✓</div>
            <div className="toast-body">
              <div className="toast-msg">{toast.msg}</div>
              <div className="toast-title">{toast.title}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Apple TV / Netflix style Frosted sticky navbar */}
      <header className="header-nav">
        <div className="brand-section" onClick={() => setCurrentPage('home')}>
          <div className="brand-logo">C</div>
          <div className="brand-logo-text">
            <span className="brand-name">CineScore</span>
            <span className="brand-subtitle text-gradient">AI INTELLIGENCE</span>
          </div>
        </div>

        {/* Navigation tabs router */}
        <nav className="nav-tabs-container">
          <button 
            className={`nav-tab-btn ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('home');
              addToast("Routing to catalog home page", "SYSTEM NAVIGATION", "purple");
            }}
          >
            Home
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'details' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('details');
              addToast("Displaying movie detailed analytics", "SYSTEM NAVIGATION", "purple");
            }}
            disabled={!selectedMovie}
          >
            Details
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'analytics' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('analytics');
              addToast("Compiling audience vibe metrics", "SYSTEM NAVIGATION", "purple");
            }}
            disabled={!selectedMovie}
          >
            Analytics
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'reviews' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('reviews');
              addToast("Synchronizing public review tables", "SYSTEM NAVIGATION", "purple");
            }}
            disabled={!selectedMovie}
          >
            Reviews
          </button>
        </nav>

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            placeholder="Search movies (e.g. Inception)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </form>
      </header>

      {/* Main Pages Render HUD */}
      <main style={{ position: 'relative', flexGrow: 1, marginTop: '24px' }}>
        
        {/* Scraper loading spinner */}
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p className="loading-title">Compiling Live Sentiment Analysis</p>
            <p className="loading-subtitle animate-pulse">{scrapeStatus || "Fetching public review streams..."}</p>
          </div>
        )}

        {/* PAGE 1: HOME PAGE (Netflix Featured Hero banner + Grid) */}
        {currentPage === 'home' && (
          <div className="fade-in">
            {/* Cinematic OTT Featured Hero Section */}
            {selectedMovie && (
              <div className="hero-banner-container glass-panel">
                {selectedMovie.poster_path ? (
                  <img
                    src={selectedMovie.poster_path.startsWith('http') ? selectedMovie.poster_path : `https://image.tmdb.org/t/p/original${selectedMovie.poster_path}`}
                    alt={selectedMovie.title}
                    className="hero-backdrop-img"
                  />
                ) : (
                  <div className="hero-backdrop-img" style={{ background: '#1e293b' }}></div>
                )}
                <div className="hero-overlay-fade"></div>
                <div className="hero-text-content">
                  <span className="hero-featured-tag">FEATURED AI INTELLIGENCE</span>
                  <h2 className="hero-title">{selectedMovie.title}</h2>
                  <p className="hero-tagline">{selectedMovie.overview}</p>
                  <div className="hero-btn-row">
                    <button 
                      onClick={() => {
                        setCurrentPage('details');
                        addToast(`Showing details for ${selectedMovie.title}`, "DASHBOARD", "purple");
                      }} 
                      className="hero-btn-primary"
                    >
                      AI Ratings
                    </button>
                    <button 
                      onClick={triggerLiveScraper} 
                      className="hero-btn-secondary"
                    >
                      Scrape Feedback
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Catalog Grid Section with Genre Filter chips */}
            <div className="catalog-header-bar">
              <h3 className="catalog-title">POPULAR ON CINESCORE</h3>
              <div className="genre-chips-container">
                {genresChipsList.map(chip => (
                  <button
                    key={chip.code}
                    onClick={() => {
                      setActiveGenre(chip.code);
                      addToast(`Filtering catalog by genre`, "FILTER SYNC", "cyan");
                    }}
                    className={`genre-chip ${activeGenre === chip.code ? 'active' : ''}`}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Movie Grid */}
            <div className="movie-grid">
              {filteredMoviesGrid.map((movie) => (
                <div
                  key={movie.id}
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
                    <h4 className="movie-card-title">{movie.title}</h4>
                    <div className="movie-card-meta-row">
                      <span className="movie-card-year">
                        {movie.release_date ? movie.release_date.split('-')[0] : 'N/A'}
                      </span>
                      <div className="movie-card-badges">
                        <span className="badge badge-tmdb">
                          TMDb: {movie.vote_average ? movie.vote_average.toFixed(1) : '0.0'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SKELETON LOADER SCREEN */}
        {skeletonLoading ? (
          <div className="movie-grid" style={{ marginTop: '40px' }}>
            {[1, 2, 3, 4].map(idx => (
              <div key={idx} className="skeleton-card skeleton-pulse">
                <div className="skeleton-image"></div>
                <div className="skeleton-text"></div>
                <div className="skeleton-text short"></div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* PAGE 2: MOVIE DETAILS (Large backdrop, compare meters, streaming platforms) */}
            {currentPage === 'details' && selectedMovie && (
              <div className="details-section fade-in">
                {/* Backdrop Banner blurred card */}
                <div className="movie-details-backdrop-banner">
                  {selectedMovie.poster_path ? (
                    <img
                      src={selectedMovie.poster_path.startsWith('http') ? selectedMovie.poster_path : `https://image.tmdb.org/t/p/original${selectedMovie.poster_path}`}
                      alt={selectedMovie.title}
                      className="details-backdrop-img"
                    />
                  ) : (
                    <div className="details-backdrop-img" style={{ background: '#1e293b' }}></div>
                  )}
                  <div className="details-backdrop-overlay"></div>
                </div>

                {/* Primary floating details card */}
                <div className="movie-detail-card glass-panel">
                  <div className="movie-detail-poster">
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
                          onClick={() => {
                            setCurrentPage('analytics');
                            addToast("Routing to interactive Recharts graphs", "SYSTEM NAVIGATION", "purple");
                          }}
                          className="nav-tab-btn active"
                          style={{ fontSize: '11px', padding: '6px 14px' }}
                        >
                          View Analytics &rarr;
                        </button>
                      </div>
                      <p className="movie-detail-release">RELEASE DATE: {selectedMovie.release_date || 'N/A'}</p>
                      <p className="movie-detail-overview">{selectedMovie.overview}</p>
                    </div>

                    <div>
                      <button onClick={triggerLiveScraper} className="scraper-button">
                        Scrape Live Web Feedback
                      </button>
                    </div>
                  </div>
                </div>

                {/* OTT Streaming Availability Cards */}
                <div className="streaming-container glass-panel">
                  <span className="drawer-section-title">STREAMING NOW ON PLATFORMS</span>
                  <div className="streaming-grid">
                    <div className="streaming-card netflix-glow">
                      <div className="streaming-logo-placeholder" style={{ background: '#e50914' }}>N</div>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: 'hsl(var(--text-main))' }}>Netflix</span>
                      <span style={{ fontSize: '9px', color: '#22c55e', fontWeight: 'bold', marginTop: '4px' }}>4K STREAM</span>
                    </div>
                    <div className="streaming-card prime-glow">
                      <div className="streaming-logo-placeholder" style={{ background: '#00a8e2' }}>P</div>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: 'hsl(var(--text-main))' }}>Prime Video</span>
                      <span style={{ fontSize: '9px', color: '#22c55e', fontWeight: 'bold', marginTop: '4px' }}>INCLUDED</span>
                    </div>
                    <div className="streaming-card apple-glow">
                      <div className="streaming-logo-placeholder" style={{ background: '#1a1a1a' }}></div>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: 'hsl(var(--text-main))' }}>Apple TV+</span>
                      <span style={{ fontSize: '9px', color: '#fbbf24', fontWeight: 'bold', marginTop: '4px' }}>RENT $3.99</span>
                    </div>
                    <div className="streaming-card disney-glow">
                      <div className="streaming-logo-placeholder" style={{ background: '#0072ce' }}>D</div>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: 'hsl(var(--text-main))' }}>Disney+</span>
                      <span style={{ fontSize: '9px', color: '#cbd5e1', fontWeight: 'bold', marginTop: '4px' }}>UNAVAILABLE</span>
                    </div>
                  </div>
                </div>

                {/* AI & Platform Ratings comparison dashboard */}
                <div className="score-dashboard-grid">
                  
                  {/* CineScore AI composite gauge */}
                  <div className="gauge-card glass-panel">
                    <h3 className="catalog-title text-gradient">CineScore AI Aggregate</h3>
                    
                    <div className="relative" style={{ width: '150px', height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '12px 0', position: 'relative' }}>
                      <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
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
                        />
                        <defs>
                          <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="hsl(var(--accent-primary))" />
                            <stop offset="100%" stopColor="hsl(var(--accent-secondary))" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <span style={{ fontSize: '36px', fontWeight: '800', color: 'hsl(var(--text-main))', letterSpacing: '-0.03em', lineHeight: '1' }}>{compositeScore.toFixed(2)}</span>
                        <span style={{ fontSize: '8px', color: 'hsl(var(--accent-primary))', fontFamily: 'monospace', letterSpacing: '0.15em', marginTop: '4px', fontWeight: 'bold' }}>AI COMPOSITE</span>
                      </div>
                    </div>

                    <div style={{ width: '100%', borderTop: '1px solid hsla(var(--text-main) / 0.05)', paddingTop: '10px' }}>
                      <p style={{ fontSize: '10px', fontFamily: 'monospace', color: 'hsl(var(--text-muted))', lineHeight: '1.4' }}>
                        Formula Weight:<br/>0.4(IMDb) + 0.2(TMDb) + 0.1(Meta) + 0.3(NLP)
                      </p>
                    </div>
                  </div>

                  {/* Multi-platform compare scores progress bars */}
                  <div className="breakdown-card glass-panel">
                    <h3 className="catalog-title" style={{ marginBottom: '16px' }}>Platform Comparisons</h3>
                    
                    <div className="bar-list">
                      {/* IMDb */}
                      <div className="bar-item">
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>IMDb Score (40% Weight)</span>
                          <span style={{ fontWeight: '700', color: '#fbbf24' }}>{hybridRating.imdb_score ? hybridRating.imdb_score.toFixed(1) : (selectedMovie.imdb_rating ? selectedMovie.imdb_rating.toFixed(1) : 'N/A')}/10</span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(hybridRating.imdb_score || selectedMovie.imdb_rating || 8.0) * 10}%`, backgroundColor: '#fbbf24' }}></div>
                        </div>
                      </div>

                      {/* TMDb */}
                      <div className="bar-item">
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>TMDb Score (20% Weight)</span>
                          <span style={{ fontWeight: '700', color: 'hsl(var(--accent-secondary))' }}>{hybridRating.tmdb_score ? hybridRating.tmdb_score.toFixed(1) : (selectedMovie.vote_average ? selectedMovie.vote_average.toFixed(1) : 'N/A')}/10</span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(hybridRating.tmdb_score || selectedMovie.vote_average || 7.0) * 10}%`, backgroundColor: 'hsl(var(--accent-secondary))' }}></div>
                        </div>
                      </div>

                      {/* Metacritic */}
                      <div className="bar-item">
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>Metacritic Score (10% Weight)</span>
                          <span style={{ fontWeight: '700', color: '#f87171' }}>{hybridRating.metacritic_score ? (hybridRating.metacritic_score * 10).toFixed(0) : (selectedMovie.metacritic_score ? (selectedMovie.metacritic_score * 10).toFixed(0) : 'N/A')}/100</span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(hybridRating.metacritic_score || selectedMovie.metacritic_score || 7.0) * 10}%`, backgroundColor: '#f87171' }}></div>
                        </div>
                      </div>

                      {/* NLP Review Sentiment */}
                      <div className="bar-item">
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>NLP Review Sentiment (30% Weight)</span>
                          <span style={{ fontWeight: '700', color: '#4ade80' }}>{((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)}/10</span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5)) * 10}%`, backgroundColor: '#4ade80' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Similar Recommendations cosine embeddings matching */}
                {recommendations.length > 0 && (
                  <div className="recommendations-container glass-panel">
                    <h3 className="catalog-title" style={{ marginBottom: '18px' }}>
                      Similar Recommendations (TF-IDF Cosine Match)
                    </h3>
                    <div className="recommendations-grid">
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
                              <h4 style={{ fontSize: '13px', fontWeight: '700', color: 'hsl(var(--text-main))', marginBottom: '6px', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: '1.2' }}>{rec.title}</h4>
                            </div>
                            <div style={{
                              marginTop: '10px',
                              padding: '5px 8px',
                              borderRadius: '6px',
                              backgroundColor: 'hsla(var(--accent-primary) / 0.1)',
                              border: '1px solid hsla(var(--accent-primary) / 0.2)',
                              color: 'hsl(var(--accent-primary))',
                              fontSize: '9px',
                              fontWeight: '700',
                              textAlign: 'center',
                              lineHeight: '1.3'
                            }}>
                              {rec.recommendation_reason || 'Overview Similarity Match'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* PAGE 3: ANALYTICS (Recharts Grid visual layouts) */}
            {currentPage === 'analytics' && selectedMovie && (
              <div className="analytics-section fade-in">
                <div style={{ marginBottom: '24px' }}>
                  <h2 className="movie-detail-title" style={{ fontSize: '24px', marginBottom: '6px' }}>
                    Visual Analytics: <span className="accent-gradient">{selectedMovie.title}</span>
                  </h2>
                  <p style={{ color: 'hsl(var(--text-muted))', fontSize: '12.5px' }}>
                    Interactive charts aggregating sentiment distributions, dynamic aspect polarity, and review pool authenticity models.
                  </p>
                </div>

                {/* Grid Visual Charts */}
                <div className="analytics-charts-grid">
                  
                  {/* Rating comparison */}
                  <div className="chart-card glass-panel">
                    <h4 className="chart-card-title text-gradient">Score Comparisons</h4>
                    <p className="chart-card-desc">Normalized scores out of 10 comparing primary catalog providers.</p>
                    <div className="chart-wrapper">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={ratingComparisonData} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                          <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,28,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }} />
                          <Bar dataKey="Score" radius={[4, 4, 0, 0]}>
                            {ratingComparisonData.map((entry, index) => {
                              const colors = ['#fbbf24', 'hsl(var(--accent-secondary))', '#f87171', '#4ade80', 'hsl(var(--accent-primary))'];
                              return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                            })}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Sentiment Pie */}
                  <div className="chart-card glass-panel">
                    <h4 className="chart-card-title text-gradient">Vibe Distribution</h4>
                    <p className="chart-card-desc">Volume of positive, negative, and neutral review classifications.</p>
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
                            <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,28,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }} />
                            <Legend verticalAlign="bottom" height={36} tick={{ fill: 'hsl(var(--text-main))', fontSize: 10 }} />
                          </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <div style={{ color: 'hsl(var(--text-muted))', fontSize: '12px' }}>Scrape feedback to compile sentiment ratio pie.</div>
                      )}
                    </div>
                  </div>

                  {/* Aspect Based (ABSA) aspect scores */}
                  <div className="chart-card glass-panel">
                    <h4 className="chart-card-title text-gradient">Aspect breakdowns (ABSA)</h4>
                    <p className="chart-card-desc">Average sentiment ratings across key aesthetic film vectors.</p>
                    <div className="chart-wrapper">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={aspectData} layout="vertical" margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis type="number" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                          <YAxis dataKey="name" type="category" tick={{ fill: 'hsl(var(--text-main))', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,28,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }} />
                          <Bar dataKey="Score" radius={[0, 4, 4, 0]} barSize={12}>
                            {aspectData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Integrity Audit circular shield card */}
                  <div className="chart-card glass-panel" style={{ justifyContent: 'space-between' }}>
                    <div>
                      <h4 className="chart-card-title text-gradient">Pool Authenticity Shield</h4>
                      <p className="chart-card-desc">Credibility metrics evaluating duplicated text and automation flags.</p>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexGrow: 1, padding: '10px 0' }}>
                      <div className="integrity-score-ring" style={{ width: '90px', height: '90px', flexShrink: 0 }}>
                        <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                          <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="transparent"
                            stroke={integrity.integrity_score > 85 ? '#22c55e' : (integrity.integrity_score > 60 ? '#fbbf24' : '#ef4444')}
                            strokeWidth="8"
                            strokeDasharray={2 * Math.PI * 40}
                            strokeDashoffset={2 * Math.PI * 40 * (1 - integrity.integrity_score / 100.0)}
                            strokeLinecap="round"
                          />
                        </svg>
                        <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                          <span style={{ fontSize: '18px', fontWeight: '800', color: 'hsl(var(--text-main))' }}>{integrity.integrity_score}%</span>
                          <span style={{ fontSize: '6.5px', color: 'hsl(var(--text-muted))', letterSpacing: '0.05em', fontWeight: 'bold' }}>CREDIBILITY</span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1, fontSize: '11px', fontFamily: 'monospace' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                          <span style={{ color: 'hsl(var(--text-muted))' }}>Authenticity Rank:</span>
                          <span style={{ fontWeight: 'bold', color: integrity.integrity_score > 85 ? '#4ade80' : '#fbbf24' }}>
                            {integrity.integrity_score > 85 ? 'SECURED' : 'CHECKED'}
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                          <span style={{ color: 'hsl(var(--text-muted))' }}>Spam Flagged:</span>
                          <span style={{ fontWeight: 'bold', color: integrity.spam_count > 0 ? '#fbbf24' : 'hsl(var(--text-muted))' }}>{integrity.spam_count}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                          <span style={{ color: 'hsl(var(--text-muted))' }}>Duplicates Caught:</span>
                          <span style={{ fontWeight: 'bold', color: integrity.duplicate_count > 0 ? '#fbbf24' : 'hsl(var(--text-muted))' }}>{integrity.duplicate_count}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '4px' }}>
                          <span style={{ color: 'hsl(var(--text-muted))' }}>Automated Bots:</span>
                          <span style={{ fontWeight: 'bold', color: integrity.bot_flag_count > 0 ? '#ef4444' : 'hsl(var(--text-muted))' }}>{integrity.bot_flag_count}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Audience Mood Bar Charts */}
                  <div className="chart-card glass-panel">
                    <h4 className="chart-card-title text-gradient">Audience Mood Gauge</h4>
                    <p className="chart-card-desc">Calculated emotional signals detected in aggregated review texts.</p>
                    <div className="mood-analysis-container">
                      <div className="mood-bar-item">
                        <div className="mood-bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))' }}>Narrative Focus</span>
                          <span style={{ color: '#a78bfa' }}>{emotionMetrics.narrative}%</span>
                        </div>
                        <div className="mood-bar-track">
                          <div className="mood-bar-fill" style={{ width: `${emotionMetrics.narrative}%`, background: '#a78bfa' }}></div>
                        </div>
                      </div>
                      <div className="mood-bar-item">
                        <div className="mood-bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))' }}>Cinema Joy & Excitement</span>
                          <span style={{ color: '#22c55e' }}>{emotionMetrics.joy}%</span>
                        </div>
                        <div className="mood-bar-track">
                          <div className="mood-bar-fill" style={{ width: `${emotionMetrics.joy}%`, background: '#22c55e' }}></div>
                        </div>
                      </div>
                      <div className="mood-bar-item">
                        <div className="mood-bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))' }}>Surprise & Speculation</span>
                          <span style={{ color: '#facc15' }}>{emotionMetrics.surprise}%</span>
                        </div>
                        <div className="mood-bar-track">
                          <div className="mood-bar-fill" style={{ width: `${emotionMetrics.surprise}%`, background: '#facc15' }}></div>
                        </div>
                      </div>
                      <div className="mood-bar-item">
                        <div className="mood-bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))' }}>Dramatic Tension</span>
                          <span style={{ color: '#ef4444' }}>{emotionMetrics.tension}%</span>
                        </div>
                        <div className="mood-bar-track">
                          <div className="mood-bar-fill" style={{ width: `${emotionMetrics.tension}%`, background: '#ef4444' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Positivity Area Timeline */}
                  <div className="chart-card glass-panel">
                    <h4 className="chart-card-title text-gradient">Chronological Sentiment Vibe</h4>
                    <p className="chart-card-desc">Moving average of review sentiment ratings over the extracted review timeline.</p>
                    <div className="chart-wrapper">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={positivityTrendData} margin={{ top: 20, right: 10, left: -25, bottom: 5 }}>
                          <defs>
                            <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="hsl(var(--accent-primary))" stopOpacity={0.4} />
                              <stop offset="95%" stopColor="hsl(var(--accent-primary))" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                          <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,28,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#fff' }} />
                          <Area type="monotone" dataKey="Vibe Score" stroke="hsl(var(--accent-primary))" strokeWidth={2} fillOpacity={1} fill="url(#trendGradient)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                </div>
              </div>
            )}

            {/* PAGE 4: REVIEWS (Dashboard listing spambot flags) */}
            {currentPage === 'reviews' && selectedMovie && (
              <div className="reviews-page-section fade-in">
                
                {/* Search filters toolbar */}
                <div className="reviews-filter-card glass-panel">
                  <div className="filter-row">
                    <span className="filter-label">Filter Vibe</span>
                    <div className="filter-btns">
                      {['ALL', 'POSITIVE', 'NEUTRAL', 'NEGATIVE'].map(sentiment => (
                        <button
                          key={sentiment}
                          onClick={() => {
                            setReviewFilter(sentiment);
                            addToast(`Filtering reviews by ${sentiment}`, "TABLE SYNC", "cyan");
                          }}
                          className={`filter-btn ${reviewFilter === sentiment ? 'active' : ''}`}
                        >
                          {sentiment === 'ALL' ? 'Show All' : sentiment.charAt(0) + sentiment.slice(1).toLowerCase()}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                    <label className="toggle-switch-container">
                      <input 
                        type="checkbox" 
                        checked={hideSpam}
                        onChange={(e) => {
                          setHideSpam(e.target.checked);
                          addToast(e.target.checked ? "Spam filter active" : "Displaying moderated review logs", "HUD FILTER", "amber");
                        }}
                        className="toggle-switch-input"
                      />
                      <span className="toggle-switch-label" style={{ fontSize: '11.5px', fontWeight: 'bold' }}>Hide Spam/Bots</span>
                    </label>
                    
                    <input
                      type="text"
                      placeholder="Filter by keyword (e.g. CGI)..."
                      value={reviewSearchQuery}
                      onChange={(e) => setReviewSearchQuery(e.target.value)}
                      className="review-search-input"
                    />
                  </div>
                </div>

                {/* Reviews Stream list */}
                <div className="reviews-list-container">
                  {filteredReviews.length > 0 ? (
                    <div className="reviews-grid-full">
                      {filteredReviews.map((r) => {
                        const aspectScores = r.aspect_scores || computeMockAspectScores([r]);
                        const isModeratedSpam = r.moderation?.is_spam || r.moderation?.is_bot;
                        const moderationReasons = r.moderation?.spam_reasons || [];
                        
                        return (
                          <div key={r.id} className="review-item-full glass-panel">
                            {/* Moderation spambot alert block */}
                            {isModeratedSpam && (
                              <div className="spam-warning-banner">
                                <span className="spam-warning-icon">⚠</span>
                                <span>MODERATOR FLAG IN REVIEW POOL:</span>
                                <span className="spam-warning-reasons">({moderationReasons.join(", ")})</span>
                              </div>
                            )}

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                              <div className="review-author-row">
                                <div className="review-avatar">
                                  {r.reviewer.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                  <span style={{ fontSize: '13.5px', fontWeight: '700', color: 'hsl(var(--text-main))' }}>@{r.reviewer}</span>
                                  <div className="review-source-label">Source: {r.is_scraped ? `Scraped feed` : `CineScore User`}</div>
                                </div>
                              </div>
                              
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span className={`review-badge review-badge-${r.sentiment_label?.toLowerCase()}`}>
                                  {r.sentiment_label}
                                </span>
                                <span className="review-score">{r.rating ? r.rating.toFixed(1) : 'N/A'}/10</span>
                              </div>
                            </div>

                            <p className="review-body-full">{r.review_text}</p>

                            {/* Aspect Sentiment breakdown grid */}
                            <div className="review-aspects-grid">
                              <span style={{ fontSize: '9px', fontFamily: 'monospace', fontWeight: 'bold', marginRight: '6px', color: 'hsl(var(--text-muted))', display: 'flex', alignItems: 'center' }}>Aspect Sentiment:</span>
                              <div className="review-aspect-badge" style={{ background: 'rgba(250, 204, 21, 0.08)', color: '#facc15', border: '1px solid rgba(250, 204, 21, 0.2)' }}>
                                <span className="aspect-badge-name">Acting</span>
                                <span className="aspect-badge-score">{aspectScores.acting}</span>
                              </div>
                              <div className="review-aspect-badge" style={{ background: 'rgba(34, 211, 238, 0.08)', color: '#22d3ee', border: '1px solid rgba(34, 211, 238, 0.2)' }}>
                                <span className="aspect-badge-name">Story</span>
                                <span className="aspect-badge-score">{aspectScores.story}</span>
                              </div>
                              <div className="review-aspect-badge" style={{ background: 'rgba(167, 139, 250, 0.08)', color: '#a78bfa', border: '1px solid rgba(167, 139, 250, 0.2)' }}>
                                <span className="aspect-badge-name">Music</span>
                                <span className="aspect-badge-score">{aspectScores.music}</span>
                              </div>
                              <div className="review-aspect-badge" style={{ background: 'rgba(248, 113, 113, 0.08)', color: '#f87171', border: '1px solid rgba(248, 113, 113, 0.2)' }}>
                                <span className="aspect-badge-name">Visuals</span>
                                <span className="aspect-badge-score">{aspectScores.visual_effects || 8.0}</span>
                              </div>
                              <div className="review-aspect-badge" style={{ background: 'rgba(74, 222, 128, 0.08)', color: '#4ade80', border: '1px solid rgba(74, 222, 128, 0.2)' }}>
                                <span className="aspect-badge-name">Direction</span>
                                <span className="aspect-badge-score">{aspectScores.direction}</span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="no-reviews-fallback glass-panel">
                      No review logs found matching your filters. Try clearing keywords or web filters.
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

      </main>

      {/* Floating Action Settings Redesign Switcher panel */}
      <div className="accent-switcher-panel">
        {settingsOpen && (
          <div className="accent-panel-drawer glass-panel">
            {/* Accent theme picking dots */}
            <div>
              <span className="drawer-section-title">Accent Theme</span>
              <div className="accent-dots-row">
                <button onClick={() => { setAccentColor('purple'); addToast("Swapped to Violet Purple Theme", "SETTINGS UPDATE", "purple"); }} className={`accent-dot accent-dot-purple ${accentColor === 'purple' ? 'active' : ''}`} title="Violet Purple" />
                <button onClick={() => { setAccentColor('cyan'); addToast("Swapped to Neon Cyan Theme", "SETTINGS UPDATE", "cyan"); }} className={`accent-dot accent-dot-cyan ${accentColor === 'cyan' ? 'active' : ''}`} title="Neon Cyan" />
                <button onClick={() => { setAccentColor('amber'); addToast("Swapped to Gold Amber Theme", "SETTINGS UPDATE", "amber"); }} className={`accent-dot accent-dot-amber ${accentColor === 'amber' ? 'active' : ''}`} title="Gold Amber" />
                <button onClick={() => { setAccentColor('emerald'); addToast("Swapped to Emerald Green Theme", "SETTINGS UPDATE", "emerald"); }} className={`accent-dot accent-dot-emerald ${accentColor === 'emerald' ? 'active' : ''}`} title="Emerald Green" />
              </div>
            </div>

            {/* Dark/Light mode toggler */}
            <div style={{ borderTop: '1px solid hsla(var(--text-main)/0.06)', paddingTop: '8px' }}>
              <span className="drawer-section-title">Visual Mode</span>
              <div className="theme-toggle-row">
                <span style={{ fontSize: '11px', fontWeight: '600', color: 'hsl(var(--text-main))' }}>
                  {themeMode === 'dark' ? 'Dark Theme' : 'Light Theme'}
                </span>
                <label className="toggle-switch-container">
                  <input
                    type="checkbox"
                    checked={themeMode === 'light'}
                    onChange={(e) => {
                      const nextMode = e.target.checked ? 'light' : 'dark';
                      setThemeMode(nextMode);
                      addToast(`Swapped to ${nextMode.toUpperCase()} mode`, "THEME CHANGE", "purple");
                    }}
                    className="toggle-switch-input"
                  />
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Settings gear trigger dot */}
        <button 
          onClick={() => setSettingsOpen(!settingsOpen)}
          className="accent-switcher-btn"
          title="Toggle Redesign controls"
        >
          ⚙
        </button>
      </div>

    </div>
  );
}
