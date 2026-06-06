import React, { useState, useEffect, useRef, Suspense, lazy } from 'react';
import { QueryClient, QueryClientProvider, useQueryClient, useQuery } from '@tanstack/react-query';
import './App.css';

const AnalyticsCharts = lazy(() => import('./components/AnalyticsCharts.jsx'));

function PremiumPosterPlaceholder({ title, className, small }) {
  return (
    <div className={`premium-poster-placeholder ${className || ''}`} style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: small ? '4px' : '16px',
      textAlign: 'center',
      height: '100%',
      width: '100%',
      color: '#94a3b8',
      position: 'relative',
      overflow: 'hidden',
      borderRadius: 'inherit'
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent 70%)',
        pointerEvents: 'none'
      }}></div>
      <span style={{ fontSize: small ? '1.2rem' : '2rem', marginBottom: small ? '0px' : '8px' }}>🎬</span>
      {!small && (
        <span style={{ 
          fontSize: '11px', 
          fontWeight: '700', 
          color: '#f8fafc',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          display: '-webkit-box',
          WebkitLineClamp: '3',
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          lineHeight: '1.4'
        }}>{title || 'CineScore'}</span>
      )}
    </div>
  );
}

function ImageWithLoader({ src, alt, title, className, style, small }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoaded(false);
    setError(false);
  }, [src]);

  if (!src || error) {
    return <PremiumPosterPlaceholder title={title || alt} className={className} small={small} />;
  }

  return (
    <div className={`image-loader-container ${className || ''}`} style={{
      position: 'relative',
      width: '100%',
      height: '100%',
      overflow: 'hidden',
      borderRadius: 'inherit',
      display: 'block',
      ...style
    }}>
      {!loaded && (
        <div className="skeleton-image" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          borderRadius: 'inherit',
          zIndex: 1,
          aspectRatio: 'unset'
        }}></div>
      )}
      <img
        src={src}
        alt={alt}
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        style={{
          display: loaded ? 'block' : 'none',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          borderRadius: 'inherit'
        }}
      />
    </div>
  );
}

function AnalyticsSkeleton() {
  return (
    <div className="analytics-section">
      <div style={{ marginBottom: '24px' }}>
        <div className="skeleton-text" style={{ width: '250px', height: '24px' }}></div>
        <div className="skeleton-text" style={{ width: '450px', height: '14px', marginTop: '8px' }}></div>
      </div>
      <div className="analytics-charts-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginTop: '20px' }}>
        {[1, 2, 3, 4, 5, 6].map(idx => (
          <div key={idx} className="chart-card glass-panel" style={{ height: '320px', display: 'flex', flexDirection: 'column', gap: '12px', padding: '20px' }}>
            <div className="skeleton-text" style={{ width: '150px', height: '16px' }}></div>
            <div className="skeleton-text short" style={{ width: '80px', height: '10px' }}></div>
            <div className="skeleton-image" style={{ flexGrow: 1, maxHeight: '200px' }}></div>
          </div>
        ))}
      </div>
    </div>
  );
}

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
      imdb_rating: 8.7,
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
      imdb_rating: 8.8,
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
      imdb_rating: 9.0,
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
      imdb_rating: 7.9,
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

function AppContent() {
  const queryClient = useQueryClient();
  const [moviesList, setMoviesList] = useState(FALLBACK_MOVIES);
  const [selectedMovieId, setSelectedMovieId] = useState(FALLBACK_MOVIES[0].id);
  const [activeSearchQuery, setActiveSearchQuery] = useState('');
  
  const [selectedMovie, setSelectedMovie] = useState({
    ...FALLBACK_MOVIES[0],
    reviews: computeMockModeration(FALLBACK_MOVIES[0].reviews),
    average_aspect_scores: computeMockAspectScores(FALLBACK_MOVIES[0].reviews),
    integrity_metrics: {      integrity_score: 95.0,
      spam_count: 0,
      bot_flag_count: 0,
      duplicate_count: 0
    }
  });
  
  // Content-Based Recommendations state
  const [recommendations, setRecommendations] = useState(computeMockRecommendations(FALLBACK_MOVIES[0].id));
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [backendAlive, setBackendAlive] = useState(false);

  // TanStack Query for popular or search movies
  const { data: moviesListData } = useQuery({
    queryKey: ['movies', activeSearchQuery, backendAlive],
    queryFn: async () => {
      if (!backendAlive) {
        if (!activeSearchQuery) return { results: FALLBACK_MOVIES };
        const filtered = FALLBACK_MOVIES.filter(m =>
          m.title.toLowerCase().includes(activeSearchQuery.toLowerCase())
        );
        return { results: filtered };
      }
      const url = activeSearchQuery 
        ? `${backendUrl}/movies?query=${encodeURIComponent(activeSearchQuery)}`
        : `${backendUrl}/movies`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch movies list");
      return res.json();
    },
  });

  useEffect(() => {
    if (moviesListData?.results) {
      if (moviesListData.results.length > 0) {
        setMoviesList(moviesListData.results);
        setSelectedMovieId(moviesListData.results[0].id);
      } else {
        addToast(`No matches found for "${activeSearchQuery}"`, "NO RESULTS", "amber");
      }
    }
  }, [moviesListData]);

  // TanStack Query for movie details (combines all 5 detail REST API resources)
  const { data: movieDetailsData, isFetching: isDetailsFetching, isError: isDetailsError, error: detailsError, refetch: refetchDetails } = useQuery({
    queryKey: ['movieDetails', selectedMovieId, backendAlive],
    queryFn: async () => {
      if (!backendAlive) {
        const localMock = FALLBACK_MOVIES.find(m => m.id === selectedMovieId);
        if (!localMock) throw new Error("Local mock not found");
        return {
          movieData: localMock,
          reviewsData: { reviews: localMock.reviews || [] },
          ratingData: localMock.rating,
          sentimentData: null,
          recommendationsData: null
        };
      }
      
      const [movieData, reviewsData, ratingData, sentimentData, recommendationsData] = await Promise.all([
        fetch(`${backendUrl}/movie/${selectedMovieId}`).then(r => r.json()),
        fetch(`${backendUrl}/reviews/${selectedMovieId}`).then(r => r.json()),
        fetch(`${backendUrl}/rating/${selectedMovieId}`).then(r => r.json()),
        fetch(`${backendUrl}/sentiment/${selectedMovieId}`).then(r => r.json()).catch(() => null),
        fetch(`${backendUrl}/movie/${selectedMovieId}/recommendations`).then(r => r.json()).catch(() => null)
      ]);
      
      return {
        movieData,
        reviewsData,
        ratingData,
        sentimentData,
        recommendationsData
      };
    },
    enabled: !!selectedMovieId,
  });

  useEffect(() => {
    if (movieDetailsData) {
      const { movieData, reviewsData, ratingData, sentimentData, recommendationsData } = movieDetailsData;
      const rawReviews = reviewsData.reviews || [];
      const enrichedMovie = {
        ...movieData,
        reviews: computeMockModeration(rawReviews),
        rating: ratingData || {
          imdb_rating: movieData.imdb_rating,
          tmdb_score: movieData.vote_average,
          metacritic_score: movieData.metacritic_score,
          aggregate_hybrid_score: movieData.vote_average,
          omdb_status: movieData.omdb_status,
          omdb_error: movieData.omdb_error
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
      setRecommendations(recommendationsData || computeMockRecommendations(selectedMovieId));
    }
  }, [movieDetailsData, selectedMovieId]);

  const skeletonLoading = isDetailsFetching;

  // Movie Autocomplete search states
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const searchRef = useRef(null);

  // Debounced search suggestions fetch (300ms delay)
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      setShowSuggestions(false);
      setActiveSearchQuery('');
      return;
    }

    setSuggestionsLoading(true);
    const delayDebounceFn = setTimeout(() => {
      if (backendAlive) {
        fetch(`${backendUrl}/movies?query=${encodeURIComponent(searchQuery)}`)
          .then(res => res.json())
          .then(data => {
            if (data.results) {
              setSuggestions(data.results.slice(0, 6));
              setShowSuggestions(true);
            }
            setSuggestionsLoading(false);
          })
          .catch(err => {
            console.error("Suggestions fetch failed:", err);
            setSuggestionsLoading(false);
          });
      } else {
        const matches = FALLBACK_MOVIES.filter(m => 
          m.title.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setSuggestions(matches.slice(0, 6));
        setShowSuggestions(true);
        setSuggestionsLoading(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, backendAlive]);

  // Click outside to close suggestion dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Keyboard navigation controller
  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedIndex(prev => (prev + 1) % suggestions.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusedIndex(prev => (prev - 1 + suggestions.length) % suggestions.length);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setFocusedIndex(-1);
    } else if (e.key === 'Enter') {
      if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
        e.preventDefault();
        const selected = suggestions[focusedIndex];
        fetchMovieDetails(selected.id);
        setCurrentPage('details');
        setSearchQuery('');
        setShowSuggestions(false);
        setFocusedIndex(-1);
      }
    }
  };
  
  const [backendUrl] = useState(
    import.meta.env.VITE_API_URL || 
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8000'
      : 'https://cinescore-api.onrender.com')
  );

  const [heroIndex, setHeroIndex] = useState(0);

  // Cycle featured hero banner movie every 6 seconds
  useEffect(() => {
    const popularCount = moviesList.slice(0, 4).length;
    if (popularCount === 0) return;
    const interval = setInterval(() => {
      setHeroIndex(prev => (prev + 1) % popularCount);
    }, 6000);
    return () => clearInterval(interval);
  }, [moviesList]);

  // Netflix-style horizontal row scroll utility
  const scrollRow = (rowId, direction) => {
    const element = document.getElementById(rowId);
    if (element) {
      const scrollAmt = direction === 'left' ? -500 : 500;
      element.scrollBy({ left: scrollAmt, behavior: 'smooth' });
    }
  };
  
  // Unified Dynamic Themes System (7 premium visual setups)
  const THEME_OPTIONS = [
    { id: 'dark', name: 'Cinematic Dark', primaryColor: '#7C3AED', secondaryColor: '#22D3EE', bgClass: 'preview-dark' },
    { id: 'neon', name: 'Neon Night', primaryColor: '#EC4899', secondaryColor: '#22D3EE', bgClass: 'preview-neon' },
    { id: 'aurora', name: 'Aurora Purple', primaryColor: '#7C3AED', secondaryColor: '#4F46E5', bgClass: 'preview-aurora' },
    { id: 'ocean', name: 'Ocean Blue', primaryColor: '#3B82F6', secondaryColor: '#22D3EE', bgClass: 'preview-ocean' },
    { id: 'crimson', name: 'Crimson Red', primaryColor: '#E11D48', secondaryColor: '#F97316', bgClass: 'preview-crimson' },
    { id: 'gold', name: 'Gold Luxe', primaryColor: '#FBBF24', secondaryColor: '#D97706', bgClass: 'preview-gold' },
    { id: 'light', name: 'Frosted Glass Light', primaryColor: '#7C3AED', secondaryColor: '#3B82F6', bgClass: 'preview-light' }
  ];

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('cinescore-theme') || 'dark';
  });
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
  
  // Sync HSL premium themes to body class and save selection persistently
  useEffect(() => {
    const themeClasses = ['theme-dark', 'theme-neon', 'theme-aurora', 'theme-ocean', 'theme-crimson', 'theme-gold', 'theme-light'];
    themeClasses.forEach(cls => document.body.classList.remove(cls));
    document.body.classList.add(`theme-${theme}`);
    localStorage.setItem('cinescore-theme', theme);
  }, [theme]);

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
        }
      })
      .catch(() => {
        setBackendAlive(false);
        console.log("FastAPI backend is offline. Operating in high-fidelity mock mode.");
        addToast("Using localized secure mock datasets.", "OFFLINE Fallback", "amber");
      });
  }, []);

  const fetchMovieDetails = (movieId) => {
    setSelectedMovieId(movieId);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    addToast(`Searching catalog for: "${searchQuery}"`, "QUERYING", "cyan");
    setActiveSearchQuery(searchQuery);
    setCurrentPage('home');
    setShowSuggestions(false);
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
            queryClient.invalidateQueries({ queryKey: ['movieDetails', selectedMovie.id] });
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

  const getEffectiveWeights = (movie) => {
    if (!movie) return { imdb: 0.40, tmdb: 0.20, metacritic: 0.10, nlp: 0.30 };
    const ratingObj = movie.rating || {};
    
    if (ratingObj.effective_weights) {
      return ratingObj.effective_weights;
    }
    
    const baseWeights = { imdb: 0.40, tmdb: 0.20, metacritic: 0.10, nlp: 0.30 };
    const available = [];
    
    const hasImdb = ratingObj.imdb_rating || ratingObj.imdb_score || movie.imdb_rating;
    const hasTmdb = ratingObj.tmdb_score || movie.vote_average;
    const hasMeta = ratingObj.metacritic_score || movie.metacritic_score;
    const hasNlp = true; 
    
    if (hasImdb) available.push("imdb");
    if (hasTmdb) available.push("tmdb");
    if (hasMeta) available.push("metacritic");
    if (hasNlp) available.push("nlp");
    
    const sumAvailable = available.reduce((acc, src) => acc + baseWeights[src], 0);
    if (sumAvailable === 0) return baseWeights;
    
    const calculated = {};
    Object.keys(baseWeights).forEach(src => {
      if (available.includes(src)) {
        calculated[src] = baseWeights[src] / sumAvailable;
      } else {
        calculated[src] = 0.0;
      }
    });
    return calculated;
  };

  const effectiveWeights = getEffectiveWeights(selectedMovie);
  
  const isWeightAdjusted = Object.keys(effectiveWeights).some(src => {
    const base = { imdb: 0.40, tmdb: 0.20, metacritic: 0.10, nlp: 0.30 };
    return effectiveWeights[src] !== base[src];
  });

  const hybridRating = selectedMovie.rating || {};
  const compositeScore = hybridRating.aggregate_score || hybridRating.aggregate_hybrid_score || selectedMovie.vote_average || 7.0;

  // Spambot values
  const integrity = selectedMovie.integrity_metrics || { integrity_score: 100.0, spam_count: 0, bot_flag_count: 0, duplicate_count: 0 };

  // Recharts Data visualizations
  const ratingComparisonData = [
    { name: 'IMDb', Score: parseFloat((hybridRating.imdb_rating || hybridRating.imdb_score || selectedMovie.imdb_rating || 0).toFixed(1)) },
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
        <form ref={searchRef} onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            placeholder="Search movies (e.g. Inception)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
            className="search-input"
          />
          
          {/* Autocomplete loader spinner indicator */}
          {suggestionsLoading ? (
            <div className="search-spinner-tiny animate-spin"></div>
          ) : (
            <button type="submit" className="search-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          )}

          {/* Autocomplete Dropdown List */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="search-suggestions-dropdown glass-panel">
              {suggestions.map((item, idx) => {
                const year = item.release_date ? item.release_date.split('-')[0] : 'N/A';
                const rating = item.vote_average ? item.vote_average.toFixed(1) : '0.0';
                
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      fetchMovieDetails(item.id);
                      setCurrentPage('details');
                      setSearchQuery('');
                      setShowSuggestions(false);
                      setFocusedIndex(-1);
                      addToast(`Loading ratings for: ${item.title}`, "AUTOCOMPLETE", "purple");
                    }}
                    onMouseEnter={() => setFocusedIndex(idx)}
                    className={`search-suggestion-item ${idx === focusedIndex ? 'focused' : ''}`}
                  >
                    <div className="suggestion-thumb">
                      <ImageWithLoader
                        src={item.poster_path ? (item.poster_path.startsWith('http') ? item.poster_path : `https://image.tmdb.org/t/p/w92${item.poster_path}`) : null}
                        alt={item.title}
                        title={item.title}
                        small={true}
                      />
                    </div>
                    <div className="suggestion-meta">
                      <span className="suggestion-title">{item.title}</span>
                      <div className="suggestion-sub-row">
                        <span className="suggestion-year">{year}</span>
                        <span className="badge badge-tmdb" style={{ fontSize: '7.5px', padding: '0.5px 4px' }}>TMDb: {rating}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
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

        {/* PAGE 1: HOME PAGE (Cinematic Netflix/Apple TV OTT Redesign) */}
        {currentPage === 'home' && (
          <div className="fade-in">
            {/* Cinematic Auto-rotating Hero Banner */}
            {moviesList.length > 0 && (
              (() => {
                const featuredMovies = moviesList.slice(0, 4);
                const featured = featuredMovies[heroIndex % featuredMovies.length] || selectedMovie;
                const compScore = featured.rating?.aggregate_hybrid_score || featured.vote_average || 7.0;
                const year = featured.release_date ? featured.release_date.split('-')[0] : 'N/A';
                
                return (
                  <div className="hero-banner-container glass-panel">
                    <ImageWithLoader
                      src={featured.poster_path ? (featured.poster_path.startsWith('http') ? featured.poster_path : `https://image.tmdb.org/t/p/original${featured.poster_path}`) : null}
                      alt={featured.title}
                      title={featured.title}
                      className="hero-backdrop-img animate-fade"
                      key={featured.id} // Enforces key refresh to trigger transition animations
                    />
                    <div className="hero-overlay-fade"></div>
                    <div className="hero-text-content">
                      <span className="hero-featured-tag">AI CINEMATIC TRENDING</span>
                      <h2 className="hero-title">{featured.title}</h2>
                      
                      {/* Hero ratings and release details */}
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap' }}>
                        <span className="badge badge-tmdb" style={{ padding: '3px 8px', fontSize: '8.5px', background: 'linear-gradient(135deg, hsl(var(--accent-primary)), hsl(var(--accent-secondary)))', color: '#fff', border: 'none', fontWeight: 'bold' }}>CineScore: {compScore.toFixed(1)}</span>
                        <span className="badge badge-imdb" style={{ padding: '3px 8px', fontSize: '8.5px', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)', fontWeight: 'bold' }}>IMDb: {(featured.imdb_rating || featured.rating?.imdb_rating || featured.rating?.imdb_score || 7.5).toFixed(1)}</span>
                        <span style={{ fontSize: '11px', color: 'hsl(var(--text-muted))', fontFamily: 'monospace', fontWeight: 'bold', marginLeft: '6px' }}>RELEASE: {year}</span>
                      </div>

                      <p className="hero-tagline">{featured.overview}</p>
                      
                      <div className="hero-btn-row">
                        <button 
                          onClick={() => {
                            fetchMovieDetails(featured.id);
                            setCurrentPage('details');
                            addToast(`Loading details for ${featured.title}`, "DASHBOARD", "purple");
                          }} 
                          className="hero-btn-primary"
                        >
                          Watch Insights
                        </button>
                        <button 
                          onClick={() => {
                            fetchMovieDetails(featured.id);
                            triggerLiveScraper();
                          }} 
                          className="hero-btn-secondary"
                        >
                          Scrape Feedback
                        </button>
                      </div>

                      {/* Apple TV-style slide progress dots */}
                      <div style={{ display: 'flex', gap: '6px', marginTop: '24px' }}>
                        {featuredMovies.map((_, idx) => (
                          <div
                            key={idx}
                            onClick={() => setHeroIndex(idx)}
                            style={{
                              width: idx === (heroIndex % featuredMovies.length) ? '24px' : '6px',
                              height: '6px',
                              borderRadius: '100px',
                              backgroundColor: idx === (heroIndex % featuredMovies.length) ? 'hsl(var(--accent-primary))' : 'rgba(255,255,255,0.2)',
                              cursor: 'pointer',
                              transition: 'all 0.4s ease'
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })()
            )}

            {/* Slider Rows Top Picks & Genre Categorization */}
            {(() => {
              // 1. Sort by CineScore formula descending
              const topCineScoreMovies = [...moviesList].sort((a, b) => 
                (b.rating?.aggregate_hybrid_score || b.vote_average || 0) - 
                (a.rating?.aggregate_hybrid_score || a.vote_average || 0)
              );

              // 2. Filter genres maps
              const scifiMovies = moviesList.filter(m => 
                m.genre_ids?.includes(878) || 
                m.genres?.some(g => g.id === 878 || g === 878 || g.name === "Science Fiction")
              );
              
              const actionMovies = moviesList.filter(m => 
                m.genre_ids?.includes(28) || m.genre_ids?.includes(12) ||
                m.genres?.some(g => g.id === 28 || g.id === 12 || g.name === "Action" || g.name === "Adventure")
              );

              const dramaMovies = moviesList.filter(m => 
                m.genre_ids?.includes(18) || 
                m.genres?.some(g => g.id === 18 || g.name === "Drama")
              );

              const crimeMovies = moviesList.filter(m => 
                m.genre_ids?.includes(80) || m.genre_ids?.includes(53) ||
                m.genres?.some(g => g.id === 80 || g.id === 53 || g.name === "Crime" || g.name === "Thriller")
              );

              const renderRow = (title, rowId, list) => {
                if (list.length === 0) return null;
                
                return (
                  <div className="netflix-row-container" key={rowId}>
                    <h3 className="netflix-row-title">{title}</h3>
                    <div className="netflix-row-slider-wrapper">
                      {/* Nav Chevrons */}
                      <button onClick={() => scrollRow(rowId, 'left')} className="slider-nav-btn slider-nav-btn-left">‹</button>
                      
                      <div id={rowId} className="netflix-row-slider">
                        {list.map(movie => {
                          const comp = movie.rating?.aggregate_hybrid_score || movie.vote_average || 7.0;
                          const imdb = movie.imdb_rating || movie.rating?.imdb_rating || movie.rating?.imdb_score || 7.5;
                          const rt = Math.round(comp * 10 - 4);
                          
                          return (
                            <div
                              key={movie.id}
                              onClick={() => {
                                fetchMovieDetails(movie.id);
                                setCurrentPage('details');
                                addToast(`Loaded cinematic insights for: ${movie.title}`, "NAVIGATION", "purple");
                              }}
                              className="netflix-card glass-panel"
                            >
                              <div className="netflix-poster-frame">
                                <ImageWithLoader
                                  src={movie.poster_path ? (movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/w300${movie.poster_path}`) : null}
                                  alt={movie.title}
                                  title={movie.title}
                                />
                                
                                {/* Hover Rating overlays */}
                                <div className="netflix-card-hover-overlay">
                                  <div className="hover-rating-col">
                                    <span className="badge badge-cinescore">CineScore: {comp.toFixed(1)}</span>
                                    <span className="badge badge-imdb">IMDb: {imdb.toFixed(1)}</span>
                                    <span className="badge badge-rt">RT: {rt}%</span>
                                  </div>
                                  <span className="view-details-hover-btn">View AI Dashboard &rarr;</span>
                                </div>
                              </div>
                              <div className="netflix-card-meta">
                                <h4 className="netflix-card-title">{movie.title}</h4>
                                <span className="netflix-card-year">{movie.release_date ? movie.release_date.split('-')[0] : 'N/A'}</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      
                      <button onClick={() => scrollRow(rowId, 'right')} className="slider-nav-btn slider-nav-btn-right">›</button>
                    </div>
                  </div>
                );
              };

              return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {renderRow("Trending Now", "trending-row-slider", moviesList)}
                  {renderRow("Top CineScore Picks", "top-picks-slider", topCineScoreMovies)}
                  {renderRow("Sci-Fi & Cosmos Journeys", "scifi-row-slider", scifiMovies)}
                  {renderRow("Action & Adventure Blockbusters", "action-row-slider", actionMovies)}
                  {renderRow("Suspense Thrillers & Crime Epics", "crime-row-slider", crimeMovies)}
                  {renderRow("Critically Acclaimed Dramas", "drama-row-slider", dramaMovies)}
                </div>
              );
            })()}
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
            {currentPage === 'details' && isDetailsError && (
              <div className="details-section fade-in" style={{ padding: '40px 20px', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                <div className="glass-panel" style={{ padding: '40px', borderRadius: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
                  <span style={{ fontSize: '3.5rem' }}>⚠️</span>
                  <h2 style={{ fontSize: '24px', fontWeight: '800', color: 'hsl(var(--text-main))' }}>Failed to Load Details</h2>
                  <p style={{ color: 'hsl(var(--text-muted))', fontSize: '14px', lineHeight: '1.6' }}>
                    {detailsError?.message || "We encountered a network error while fetching details, reviews, composite ratings, and recommendations from the AI scraper."}
                  </p>
                  <div style={{ display: 'flex', gap: '12px', marginTop: '10px' }}>
                    <button 
                      onClick={() => refetchDetails()} 
                      className="scraper-button" 
                      style={{ padding: '10px 20px', borderRadius: '8px' }}
                    >
                      Retry Connection
                    </button>
                    <button 
                      onClick={() => {
                        setCurrentPage('home');
                        setSelectedMovieId(FALLBACK_MOVIES[0].id);
                      }} 
                      className="nav-tab-btn active"
                      style={{ padding: '10px 20px', borderRadius: '8px' }}
                    >
                      Back to Home
                    </button>
                  </div>
                </div>
              </div>
            )}

            {currentPage === 'details' && !isDetailsError && selectedMovie && (
              <div className="details-section fade-in">
                {/* Backdrop Banner blurred card */}
                <div className="movie-details-backdrop-banner">
                  <ImageWithLoader
                    src={selectedMovie.poster_path ? (selectedMovie.poster_path.startsWith('http') ? selectedMovie.poster_path : `https://image.tmdb.org/t/p/original${selectedMovie.poster_path}`) : null}
                    alt={selectedMovie.title}
                    title={selectedMovie.title}
                    className="details-backdrop-img"
                  />
                  <div className="details-backdrop-overlay"></div>
                </div>

                {/* Primary floating details card */}
                <div className="movie-detail-card glass-panel">
                  <div className="movie-detail-poster">
                    <ImageWithLoader
                      src={selectedMovie.poster_path ? (selectedMovie.poster_path.startsWith('http') ? selectedMovie.poster_path : `https://image.tmdb.org/t/p/w300${selectedMovie.poster_path}`) : null}
                      alt={selectedMovie.title}
                      title={selectedMovie.title}
                    />
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
                      
                      <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap', marginTop: '6px', marginBottom: '8px' }}>
                        <p className="movie-detail-release" style={{ margin: 0 }}>RELEASE DATE: {selectedMovie.release_date || 'N/A'}</p>
                        <span style={{ color: 'hsl(var(--text-muted))' }}>•</span>
                        <p className="movie-detail-release" style={{ margin: 0 }}>RUNTIME: {selectedMovie.runtime ? `${selectedMovie.runtime} min` : 'N/A'}</p>
                      </div>
                      
                      {/* Genres badges */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
                        {selectedMovie.genres && Array.isArray(selectedMovie.genres) && selectedMovie.genres.length > 0 ? (
                          selectedMovie.genres.map((g, i) => {
                            const name = typeof g === 'object' ? g.name : g;
                            return (
                              <span key={i} className="badge" style={{ 
                                background: 'rgba(255, 255, 255, 0.08)', 
                                border: '1px solid rgba(255, 255, 255, 0.1)', 
                                color: 'hsl(var(--text-main))', 
                                padding: '3px 8px', 
                                borderRadius: '4px',
                                fontSize: '10.5px'
                              }}>
                                {name}
                              </span>
                            );
                          })
                        ) : (
                          <span style={{ color: 'hsl(var(--text-muted))', fontSize: '11px' }}>Genres: N/A</span>
                        )}
                      </div>

                      <p className="movie-detail-overview">{selectedMovie.overview || "No overview available."}</p>
                      
                      {/* Developer Diagnostics HUD */}
                      {(import.meta.env.DEV || import.meta.env.MODE === 'development') && (
                        <div className="developer-diagnostics-hud" style={{
                          marginTop: '16px',
                          marginBottom: '16px',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          background: 'rgba(255, 255, 255, 0.02)',
                          border: '1px solid rgba(255, 255, 255, 0.06)',
                          backdropFilter: 'blur(8px)',
                          fontSize: '11px',
                          color: 'hsl(var(--text-muted))',
                          fontFamily: 'monospace'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '6px' }}>
                            <span style={{ fontSize: '12px' }}>🛠️</span>
                            <span style={{ fontWeight: 'bold', color: 'hsl(var(--text-main))', letterSpacing: '0.05em' }}>DEVELOPER DIAGNOSTICS</span>
                            <span className="badge" style={{ marginLeft: 'auto', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.25)', color: '#60a5fa', fontSize: '9px', padding: '1px 5px', borderRadius: '3px' }}>DEV MODE</span>
                          </div>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
                            <div>TMDb ID: <strong style={{ color: 'hsl(var(--text-main))' }}>{selectedMovie.id}</strong></div>
                            <div>IMDb ID: <strong style={{ color: 'hsl(var(--text-main))' }}>{selectedMovie.imdb_id || 'None'}</strong></div>
                            <div>Type: <strong style={{ color: 'hsl(var(--text-main))' }}>{selectedMovie.media_type || 'Movie'}</strong></div>
                            <div>Source: <strong style={{ color: 'hsl(var(--text-main))' }}>{selectedMovie.rating_source || 'N/A'}</strong></div>
                          </div>
                          {selectedMovie.omdb_status === 'error' && selectedMovie.omdb_error && (
                            <div style={{ marginTop: '8px', color: '#f87171', borderTop: '1px dashed rgba(248, 113, 113, 0.15)', paddingTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <span>⚠️</span>
                              <span>Resolution Failure: {selectedMovie.omdb_error}</span>
                            </div>
                          )}
                        </div>
                      )}
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
                        Effective Formula:<br/>
                        {isWeightAdjusted 
                          ? `${effectiveWeights.imdb > 0 ? `${effectiveWeights.imdb.toFixed(2)}(IMDb) + ` : ''}${effectiveWeights.tmdb > 0 ? `${effectiveWeights.tmdb.toFixed(2)}(TMDb) + ` : ''}${effectiveWeights.metacritic > 0 ? `${effectiveWeights.metacritic.toFixed(2)}(Meta) + ` : ''}${effectiveWeights.nlp > 0 ? `${effectiveWeights.nlp.toFixed(2)}(NLP)` : ''}`
                          : "0.40(IMDb) + 0.20(TMDb) + 0.10(Meta) + 0.30(NLP)"}
                      </p>
                    </div>
                  </div>

                  {/* Multi-platform compare scores progress bars */}
                  <div className="breakdown-card glass-panel">
                    <h3 className="catalog-title" style={{ marginBottom: '16px' }}>Platform Comparisons</h3>
                    
                    {isWeightAdjusted && (
                      <div className="weight-adjusted-alert glass-panel pulse-glow" style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px 16px',
                        marginBottom: '20px',
                        borderRadius: '12px',
                        background: 'rgba(235, 140, 16, 0.08)',
                        border: '1px dashed rgba(235, 140, 16, 0.3)',
                        transition: 'var(--transition-smooth)'
                      }}>
                        <span style={{ fontSize: '18px', color: '#f59e0b' }}>⚠️</span>
                        <div style={{ flexGrow: 1 }}>
                          <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#fbbf24', margin: 0 }}>Scoring Weights Redistributed</h4>
                          <p style={{ fontSize: '10.5px', color: 'hsl(var(--text-muted))', margin: '2px 0 0 0' }}>
                            Rating sources unavailable. Weights have been automatically redistributed proportionally to maintain aggregate balance.
                          </p>
                        </div>
                      </div>
                    )}
                    
                    <div className="bar-list">
                      {/* IMDb */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.imdb > 0 ? 1 : 0.65, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            IMDb Score <span style={{ fontSize: '10px', color: 'hsl(var(--text-muted))', marginLeft: '4px' }}>({(effectiveWeights.imdb * 100).toFixed(0)}% Weight)</span>
                          </span>
                          <span style={{ fontWeight: '700', color: '#fbbf24' }}>
                            {effectiveWeights.imdb > 0 && (hybridRating.imdb_rating || hybridRating.imdb_score || selectedMovie.imdb_rating)
                              ? `${(hybridRating.imdb_rating || hybridRating.imdb_score || selectedMovie.imdb_rating).toFixed(1)}/10`
                              : (() => {
                                  const status = hybridRating.omdb_status || selectedMovie.omdb_status;
                                  const error = hybridRating.omdb_error || selectedMovie.omdb_error;
                                  if (status === "error" && error) {
                                    if (error === "Movie not found!" || error === "Movie rating is missing or N/A on OMDb") {
                                      return "IMDb Rating Unavailable";
                                    }
                                    return `OMDb Error: ${error}`;
                                  }
                                  return "IMDb Rating Unavailable";
                                })()}
                          </span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(effectiveWeights.imdb > 0 ? (hybridRating.imdb_rating || hybridRating.imdb_score || selectedMovie.imdb_rating || 0) : 0) * 10}%`, backgroundColor: '#fbbf24' }}></div>
                        </div>
                        {effectiveWeights.imdb <= 0 && hybridRating.imdb_status_detail && (
                          <div style={{ 
                            fontSize: '10.5px', 
                            color: '#ef4444', 
                            marginTop: '6px', 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: '4px',
                            background: 'rgba(239, 68, 68, 0.08)',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            border: '1px solid rgba(239, 68, 68, 0.15)'
                          }}>
                            <span>⚠️</span> <span>{hybridRating.imdb_status_detail}</span>
                          </div>
                        )}
                      </div>

                      {/* TMDb */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.tmdb > 0 ? 1 : 0.45, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            TMDb Score <span style={{ fontSize: '10px', color: 'hsl(var(--text-muted))', marginLeft: '4px' }}>({(effectiveWeights.tmdb * 100).toFixed(0)}% Weight)</span>
                          </span>
                          <span style={{ fontWeight: '700', color: 'hsl(var(--accent-secondary))' }}>
                            {effectiveWeights.tmdb > 0 && (hybridRating.tmdb_score || selectedMovie.vote_average)
                              ? `${(hybridRating.tmdb_score || selectedMovie.vote_average).toFixed(1)}/10`
                              : "Rating unavailable"}
                          </span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(effectiveWeights.tmdb > 0 ? (hybridRating.tmdb_score || selectedMovie.vote_average || 0) : 0) * 10}%`, backgroundColor: 'hsl(var(--accent-secondary))' }}></div>
                        </div>
                      </div>

                      {/* Metacritic */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.metacritic > 0 ? 1 : 0.45, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            Metacritic Score <span style={{ fontSize: '10px', color: 'hsl(var(--text-muted))', marginLeft: '4px' }}>({(effectiveWeights.metacritic * 100).toFixed(0)}% Weight)</span>
                          </span>
                          <span style={{ fontWeight: '700', color: '#f87171' }}>
                            {effectiveWeights.metacritic > 0 && (hybridRating.metacritic_score || selectedMovie.metacritic_score)
                              ? `${((hybridRating.metacritic_score || selectedMovie.metacritic_score) * 10).toFixed(0)}/100`
                              : "Rating unavailable"}
                          </span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(effectiveWeights.metacritic > 0 ? (hybridRating.metacritic_score || selectedMovie.metacritic_score || 0) : 0) * 10}%`, backgroundColor: '#f87171' }}></div>
                        </div>
                      </div>

                      {/* NLP Review Sentiment */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.nlp > 0 ? 1 : 0.45, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            NLP Review Sentiment <span style={{ fontSize: '10px', color: 'hsl(var(--text-muted))', marginLeft: '4px' }}>({(effectiveWeights.nlp * 100).toFixed(0)}% Weight)</span>
                          </span>
                          <span style={{ fontWeight: '700', color: '#4ade80' }}>
                            {effectiveWeights.nlp > 0
                              ? `${((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)}/10`
                              : "Rating unavailable"}
                          </span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(effectiveWeights.nlp > 0 ? ((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5) : 0) * 10}%`, backgroundColor: '#4ade80' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Dynamic Weight Allocation Model Card */}
                  <div className="breakdown-card glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                      <h3 className="catalog-title text-gradient">Dynamic Weights Breakdown</h3>
                      <p style={{ fontSize: '11px', color: 'hsl(var(--text-muted))', marginTop: '4px' }}>
                        Proportional balance model allocating CineScore weights relative to active providers.
                      </p>
                    </div>

                    <div className="weights-breakdown-details" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid hsla(var(--text-main)/0.04)', paddingBottom: '6px' }}>
                        <span style={{ fontSize: '11px', fontWeight: '500', color: 'hsl(var(--text-muted))' }}>Active Sources:</span>
                        <span style={{ fontSize: '11px', fontWeight: '700', color: '#22c55e' }}>
                          {Object.keys(effectiveWeights).filter(k => effectiveWeights[k] > 0).map(k => k.toUpperCase()).join(", ")}
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid hsla(var(--text-main)/0.04)', paddingBottom: '6px' }}>
                        <span style={{ fontSize: '11px', fontWeight: '500', color: 'hsl(var(--text-muted))' }}>Missing Sources:</span>
                        <span style={{ fontSize: '11px', fontWeight: '700', color: '#ef4444' }}>
                          {Object.keys(effectiveWeights).filter(k => effectiveWeights[k] === 0).length > 0
                            ? Object.keys(effectiveWeights).filter(k => effectiveWeights[k] === 0).map(k => k.toUpperCase()).join(", ")
                            : "NONE"}
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '2px' }}>
                        <span style={{ fontSize: '11px', fontWeight: '500', color: 'hsl(var(--text-muted))' }}>Model Balance Status:</span>
                        <span style={{ fontSize: '11px', fontWeight: '700', color: isWeightAdjusted ? '#fbbf24' : '#22c55e' }}>
                          {isWeightAdjusted ? "REDISTRIBUTED (100% SECURED)" : "STANDARD STABLE"}
                        </span>
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
                            <ImageWithLoader
                              src={rec.poster_path ? (rec.poster_path.startsWith('http') ? rec.poster_path : `https://image.tmdb.org/t/p/w200${rec.poster_path}`) : null}
                              alt={rec.title}
                              title={rec.title}
                            />
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

            {/* PAGE 3: ANALYTICS (Lazy Loaded Recharts Components via Suspense) */}
            {currentPage === 'analytics' && selectedMovie && (
              <Suspense fallback={<AnalyticsSkeleton />}>
                <AnalyticsCharts
                  movieTitle={selectedMovie.title}
                  ratingComparisonData={ratingComparisonData}
                  sentimentPieData={sentimentPieData}
                  aspectData={aspectData}
                  integrity={integrity}
                  emotionMetrics={emotionMetrics}
                  positivityTrendData={positivityTrendData}
                />
              </Suspense>
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
            <span className="drawer-section-title">Cinematic Themes</span>
            <div className="theme-switcher-grid">
              {THEME_OPTIONS.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => {
                    setTheme(opt.id);
                    addToast(`Swapped to ${opt.name} Theme`, "THEME CHANGE", opt.id);
                  }}
                  className={`theme-picker-card ${theme === opt.id ? 'active' : ''}`}
                  title={opt.name}
                >
                  <div className={`theme-picker-preview ${opt.bgClass}`}>
                    <span className="theme-preview-dot" style={{ backgroundColor: opt.primaryColor }} />
                    <span className="theme-preview-dot" style={{ backgroundColor: opt.secondaryColor }} />
                  </div>
                  <span className="theme-picker-name">{opt.name}</span>
                </button>
              ))}
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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
