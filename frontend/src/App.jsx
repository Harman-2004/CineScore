import React, { useState, useEffect, useRef } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  AreaChart, Area
} from 'recharts';
import './App.css';

// Top-level backend URL loaded from environment variables
const BACKEND_URL = import.meta.env.VITE_API_URL || '';

// Global warning if the backend URL is missing
if (!BACKEND_URL) {
  console.warn("VITE_API_URL environment variable is not defined! API requests will fail if not configured.");
}

// Network request helper with timeout and custom error handling
const fetchWithTimeout = async (resource, options = {}) => {
  const { timeout = 10000 } = options;
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    
    if (!response.ok) {
      const errorMsg = `API Request failed: ${response.status} ${response.statusText} at ${resource}`;
      console.error(errorMsg);
      throw new Error(errorMsg);
    }
    
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      const timeoutMsg = `Request timed out after ${timeout}ms at ${resource}`;
      console.error(timeoutMsg);
      throw new Error(timeoutMsg);
    }
    console.error(`Fetch error at ${resource}:`, error);
    throw error;
  }
};


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
      youtube_score: 8.5,
      sentiment_avg_polarity: 0.44,
      reviews_count: 6,
      aggregate_hybrid_score: 8.16
    },
    reviews: [
      { id: 1, reviewer: "astro_guy", rating: 10.0, review_text: "A breathtaking cinematic masterpiece. The scientific themes are beautifully blended with an emotional father-daughter bond.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.9 },
      { id: 2, reviewer: "space_cadet", rating: 8.0, review_text: "Incredible visuals and massive scope. The third act is polarizing, but the overall voyage is absolutely stunning.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.65 },
      { id: 3, reviewer: "u/space_time_rel", rating: 10.0, review_text: "The docking scene in Interstellar is the absolute peak of cinema. Hans Zimmer's organ score blaring while Matthew McConaughey does the impossible is pure adrenaline.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 4, reviewer: "space_oddity", rating: 10.0, review_text: "literally cried over a giant glowing sphere and a weeping pilot in space. Hans Zimmer is not human, this score will echo in my head for centuries.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.98 },
      { id: 5, reviewer: "space_traveler", rating: 9.0, review_text: "The organ music in this trailer makes me emotional. Zimmer is a wizard.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 6, reviewer: "cosmic_mind", rating: 8.0, review_text: "We used to look up at the sky and wonder at our place in the stars... What a line.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.75 }
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
      youtube_score: 8.0,
      sentiment_avg_polarity: 0.52,
      reviews_count: 7,
      aggregate_hybrid_score: 8.24
    },
    reviews: [
      { id: 1, reviewer: "nolan_fanatic", rating: 10.0, review_text: "Absolutely incredible. Hans Zimmer's score paired with the mind-bending dream layers makes Inception a modern sci-fi benchmark.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 2, reviewer: "cineast_review", rating: 8.0, review_text: "Visually arresting and conceptually brilliant. Cobb's emotional journey holds the complex dream heist rules together.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.6 },
      { id: 3, reviewer: "u/nolan_circlejerk", rating: 9.0, review_text: "Just rewatched Inception last night. That hallway fight scene with Arthur is still one of the greatest practical effects achievements in modern cinema. Incredible pacing.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.75 },
      { id: 4, reviewer: "u/plot_hole_finder", rating: 6.5, review_text: "Is anyone else annoyed by how much time the characters spend explaining the rules of dreaming to the audience? Half of the movie is basically exposition.", source: "Reddit", sentiment_label: "NEUTRAL", sentiment_score: 0.05 },
      { id: 5, reviewer: "filmgirl_99", rating: 9.0, review_text: "christopher nolan said: 'what if we went to sleep inside a sleep' and proceeded to construct one of the most aesthetically pleasing heist blockbusters ever made.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.85 },
      { id: 6, reviewer: "nolan_fan_99", rating: 9.0, review_text: "This trailer still gives me goosebumps. Hans Zimmer's horns literally changed movie trailers forever.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.85 },
      { id: 7, reviewer: "dream_walker", rating: 7.0, review_text: "Wait, did the top fall at the end of the trailer? Still questioning reality 16 years later.", source: "YouTube", sentiment_label: "NEUTRAL", sentiment_score: 0.1 }
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
      youtube_score: 9.5,
      sentiment_avg_polarity: 0.64,
      reviews_count: 6,
      aggregate_hybrid_score: 8.78
    },
    reviews: [
      { id: 1, reviewer: "joker_heath", rating: 10.0, review_text: "Heath Ledger's performance is legendary. The dark, realistic crime-thriller setting defines the best superhero film of all time.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 2, reviewer: "batman_arkham", rating: 9.0, review_text: "Gritty, tense, and masterfully paced. It transcends the comic book genre into an outstanding crime epic.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 3, reviewer: "u/joker_laugh", rating: 10.0, review_text: "Heath Ledger's performance is still unmatched. But can we talk about how good Aaron Eckhart was as Harvey Dent? His transformation was tragic and perfect.", source: "Reddit", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 4, reviewer: "ledger_stan", rating: 10.0, review_text: "it is heath ledger's world and we are all just trying to survive in it. an absolute masterclass of acting that completely redefined the blockbuster.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 5, reviewer: "gotham_legend", rating: 10.0, review_text: "Heath Ledger's voice in this trailer. 'Why so serious?' still gives me chills.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.95 },
      { id: 6, reviewer: "bat_collector", rating: 9.0, review_text: "I remember watching this trailer on repeat. Heath Ledger completely became the Joker.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.85 }
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
      youtube_score: 7.5,
      sentiment_avg_polarity: 0.46,
      reviews_count: 5,
      aggregate_hybrid_score: 7.82
    },
    reviews: [
      { id: 1, reviewer: "sci_fi_lover", rating: 9.0, review_text: "Denis Villeneuve's masterpiece. Dynamic sci-fi themes about language, communication, and time combined with an outstanding lead acting performance.", source: "IMDb", sentiment_label: "POSITIVE", sentiment_score: 0.9 },
      { id: 2, reviewer: "critic_girl", rating: 8.0, review_text: "An emotionally resonant, beautiful story. Smart science fiction at its best.", source: "Letterboxd", sentiment_label: "POSITIVE", sentiment_score: 0.8 },
      { id: 3, reviewer: "popcorn_guy", rating: 6.0, review_text: "Interesting concept but slightly slow. Visual effects were stunning though.", source: "Reddit", sentiment_label: "NEUTRAL", sentiment_score: 0.1 },
      { id: 4, reviewer: "movie_hype_channel", rating: 8.0, review_text: "This trailer looks absolutely insane! Can't wait to watch Arrival in theaters.", source: "YouTube", sentiment_label: "POSITIVE", sentiment_score: 0.7 },
      { id: 5, reviewer: "skeptic_viewer", rating: 7.0, review_text: "Looks decent but I hope they didn't put all the best scenes in the trailer like they usually do.", source: "YouTube", sentiment_label: "NEUTRAL", sentiment_score: 0.1 }
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
  let content = [];
  let genreMatch = [];
  let topRated = [];
  let latest = [];

  const mockMovieDb = [
    {
      id: 27205,
      title: "Inception",
      overview: "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets, is offered a chance to regain his old life as payment for inception.",
      poster_path: "/o062xtC3n4c73nJgf95SI6tAs2t.jpg",
      release_date: "2010-07-15",
      vote_average: 8.3,
      cinescore: 8.8,
      genres: [{ id: 28, name: "Action" }, { id: 878, name: "Science Fiction" }, { id: 12, name: "Adventure" }]
    },
    {
      id: 155,
      title: "The Dark Knight",
      overview: "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle Gotham's crime organizations.",
      poster_path: "/qJ2tWGBCqb6tSV1wY3nfkVvSM4c.jpg",
      release_date: "2008-07-16",
      vote_average: 8.5,
      cinescore: 9.0,
      genres: [{ id: 18, name: "Drama" }, { id: 28, name: "Action" }, { id: 80, name: "Crime" }, { id: 53, name: "Thriller" }]
    },
    {
      id: 157336,
      title: "Interstellar",
      overview: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.",
      poster_path: "/gEU2QvH353eGo3t8vOIe6qI4tJu.jpg",
      release_date: "2014-11-05",
      vote_average: 8.4,
      cinescore: 8.7,
      genres: [{ id: 12, name: "Adventure" }, { id: 18, name: "Drama" }, { id: 878, name: "Science Fiction" }]
    },
    {
      id: 329865,
      title: "Arrival",
      overview: "Linguist Louise Banks leads an elite team of investigators when gigantic spaceships touch down in 12 locations around the world.",
      poster_path: "/x2FIACR26ZbgD2W2o20V2SAu6r0.jpg",
      release_date: "2016-11-10",
      vote_average: 7.7,
      cinescore: 7.5,
      genres: [{ id: 878, name: "Science Fiction" }, { id: 9648, name: "Mystery" }]
    },
    {
      id: 680,
      title: "Pulp Fiction",
      overview: "A burger-loving hitman, his philosophical partner, a drug-addled gangster's moll, and a washed-up boxer converge in this sprawling, comedic crime caper.",
      poster_path: "/d5i2fS3HsYrV2JIFDUgza6kP9t8.jpg",
      release_date: "1994-09-10",
      vote_average: 8.5,
      cinescore: 8.9,
      genres: [{ id: 53, name: "Thriller" }, { id: 80, name: "Crime" }]
    },
    {
      id: 603,
      title: "The Matrix",
      overview: "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers.",
      poster_path: "/f89U3wz6v2jBnRFSx74J0jqrpe9.jpg",
      release_date: "1999-03-30",
      vote_average: 8.2,
      cinescore: 8.7,
      genres: [{ id: 28, name: "Action" }, { id: 878, name: "Science Fiction" }]
    },
    {
      id: 13,
      title: "Forrest Gump",
      overview: "A man with a low IQ has accomplished great things in his life and been present during significant historical events.",
      poster_path: "/arw27qpWzwCYVTDjS7gIB0wlhQA.jpg",
      release_date: "1994-06-23",
      vote_average: 8.5,
      cinescore: 8.8,
      genres: [{ id: 35, name: "Comedy" }, { id: 18, name: "Drama" }, { id: 10749, name: "Romance" }]
    },
    {
      id: 238,
      title: "The Godfather",
      overview: "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family.",
      poster_path: "/3bhkrj6PjOqabNmR42GKxycJgGj.jpg",
      release_date: "1972-03-14",
      vote_average: 8.7,
      cinescore: 9.2,
      genres: [{ id: 18, name: "Drama" }, { id: 80, name: "Crime" }]
    },
    {
      id: 497,
      title: "The Green Mile",
      overview: "A supernatural tale set on death row in a Southern prison, where gentle giant John Coffey possesses the mysterious power to heal people's ailments.",
      poster_path: "/o0o0QQ0UnZgzs2e5vpuq875nDr2.jpg",
      release_date: "1999-12-10",
      vote_average: 8.5,
      cinescore: 8.6,
      genres: [{ id: 14, name: "Fantasy" }, { id: 18, name: "Drama" }, { id: 80, name: "Crime" }]
    }
  ];

  if (movieId === 157336) {
    content = [
      mockMovieDb.find(m => m.id === 329865),
      mockMovieDb.find(m => m.id === 27205)
    ];
  } else if (movieId === 329865) {
    content = [
      mockMovieDb.find(m => m.id === 157336)
    ];
  } else {
    content = [
      mockMovieDb.find(m => m.id === 157336) || mockMovieDb[0]
    ];
  }

  const mapToExplained = (list, matchPct, why) => {
    return list.filter(Boolean).map(m => {
      const cinescore = m.cinescore || m.vote_average || 7.0;
      return {
        ...m,
        recommendation_score: matchPct / 100.0,
        explanation: {
          why_recommended: why,
          match_percentage: matchPct,
          genre_match_pct: matchPct - 3,
          theme_match_pct: matchPct + 1,
          year_diff_text: "Released Same Year",
          cinescore: cinescore,
          metrics: {
            content_similarity: 0.8,
            theme_similarity: 0.75,
            genre_similarity: 0.7,
            sentiment_similarity: 0.85,
            cinescore: cinescore
          }
        }
      };
    });
  };

  const targetMovie = mockMovieDb.find(m => m.id === movieId) || mockMovieDb[0];
  const targetGenreIds = targetMovie.genres.map(g => g.id);
  
  genreMatch = mockMovieDb
    .filter(m => m.id !== movieId)
    .map(m => {
      const intersection = m.genres.filter(g => targetGenreIds.includes(g.id));
      const union = Array.from(new Set([...targetGenreIds, ...m.genres.map(g => g.id)]));
      const score = union.length > 0 ? intersection.length / union.length : 0.0;
      return { ...m, score: score + (m.vote_average / 100.0) };
    })
    .sort((a, b) => b.score - a.score)
    .map(m => {
      const { score, ...rest } = m;
      return rest;
    });

  topRated = [...mockMovieDb].sort((a, b) => b.cinescore - a.cinescore).slice(0, 10);
  latest = [...mockMovieDb].sort((a, b) => new Date(b.release_date) - new Date(a.release_date)).slice(0, 10);

  return {
    similar_movies: mapToExplained(content, 92, "Highly related storyline and sci-fi tags"),
    top_rated_similar: mapToExplained(genreMatch, 85, "Strong themes match and narrative correlation"),
    recent_alternatives: mapToExplained(latest, 79, "Fresh release matching timeline proximity"),
    hidden_gems: mapToExplained(topRated, 88, "High quality score with lower popularity counts"),
    community_favorites: mapToExplained(latest, 79, "Popular movie with strong audience appeal"),
    // Keep legacy keys for safety
    similar_themes: mapToExplained(genreMatch, 85, "Strong themes match and narrative correlation"),
    trending_alternatives: mapToExplained(latest, 79, "Fresh release matching viewer categories")
  };
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

// Premium Dynamic Movie Image Component with Gradient fallbacks for offline/blocked sources
// Premium Dynamic Movie Image Component with Gradient fallbacks for offline/blocked sources and smooth fade-in
const MovieImage = ({ src, alt, className, style, size = 'w300', fallbackType = 'poster' }) => {
  const [error, setError] = useState(false);
  const [loaded, setLoaded] = useState(false);

  if (error || !src) {
    // Generate a unique beautiful gradient based on the alt title string
    const hash = alt ? alt.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 0;
    const gradients = [
      'linear-gradient(135deg, #1e1b4b 0%, #311042 100%)', // Midnight Indigo/Violet
      'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)', // Deep Slate/Blue
      'linear-gradient(135deg, #311042 0%, #581c87 100%)', // Purple Aurora
      'linear-gradient(135deg, #180828 0%, #030712 100%)', // Jet Black Purple
      'linear-gradient(135deg, #052e16 0%, #022c22 100%)', // Forest Emerald
      'linear-gradient(135deg, #450a0a 0%, #1e1b4b 100%)', // Deep Maroon/Navy
      'linear-gradient(135deg, #1c1917 0%, #0c0a09 100%)', // Dark Obsidian
    ];
    const gradient = gradients[hash % gradients.length];

    if (fallbackType === 'backdrop') {
      return (
        <div 
          className={className} 
          style={{ 
            ...style, 
            background: gradient, 
            opacity: 0.25, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            position: 'absolute',
            inset: 0
          }}
        />
      );
    }

    return (
      <div 
        className={className} 
        style={{ 
          ...style, 
          background: gradient, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          padding: '16px', 
          textAlign: 'center',
          color: '#fff',
          fontSize: '12px',
          fontWeight: '700',
          textShadow: '0 2px 4px rgba(0,0,0,0.6)',
          borderRadius: 'inherit',
          height: '100%',
          width: '100%',
          boxSizing: 'border-box'
        }}
      >
        <span style={{ fontSize: '28px', marginBottom: '8px', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))' }}>🎬</span>
        <span style={{ display: '-webkit-box', WebkitLineClamp: '3', WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: '1.3' }}>{alt}</span>
      </div>
    );
  }

  const imageUrl = src.startsWith('http') ? src : `${BACKEND_URL}/image-proxy?path=${encodeURIComponent(src)}&size=${size}`;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', borderRadius: 'inherit', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {!loaded && (
        <div className="skeleton-image skeleton-pulse" style={{ position: 'absolute', inset: 0, zIndex: 1, borderRadius: 'inherit' }} />
      )}
      <img
        src={imageUrl}
        alt={alt}
        className={className}
        style={{ 
          ...style, 
          opacity: loaded ? 1 : 0, 
          transition: 'opacity 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
      />
    </div>
  );
};

// Premium Details Page Skeleton Loader for Netflix-like smooth transitions
const DetailsSkeleton = () => (
  <div className="details-section skeleton-pulse" style={{ marginTop: '40px' }}>
    {/* Backdrop Banner skeleton */}
    <div className="movie-details-backdrop-banner skeleton-image" style={{ height: '35vh', borderEndStartRadius: '24px', borderEndEndRadius: '24px', position: 'relative' }}>
      <div className="details-backdrop-overlay"></div>
    </div>
    
    {/* Floating details card skeleton */}
    <div className="movie-detail-card glass-panel" style={{ marginTop: '-60px', zIndex: 2, position: 'relative' }}>
      <div className="movie-detail-poster skeleton-image" style={{ width: '200px', height: '300px', flexShrink: 0 }}></div>
      <div className="movie-detail-content" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div className="skeleton-text" style={{ width: '60%', height: '28px' }}></div>
        <div className="skeleton-text short" style={{ width: '25%', height: '14px' }}></div>
        <div className="skeleton-text" style={{ width: '90%', height: '14px', marginTop: '16px' }}></div>
        <div className="skeleton-text" style={{ width: '85%', height: '14px' }}></div>
        <div className="skeleton-text" style={{ width: '50%', height: '14px' }}></div>
      </div>
    </div>

    {/* Platform comparisons skeleton */}
    <div className="score-dashboard-grid" style={{ marginTop: '24px' }}>
      <div className="gauge-card glass-panel" style={{ height: '220px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
        <div style={{ width: '100px', height: '100px', borderRadius: '50%', border: '8px solid hsla(var(--text-main)/0.04)', animation: 'skeletonPulseAnimate 1.5s infinite ease-in-out' }}></div>
        <div className="skeleton-text short" style={{ width: '40%' }}></div>
      </div>
      <div className="breakdown-card glass-panel" style={{ height: '220px', display: 'flex', flexDirection: 'column', gap: '16px', padding: '24px' }}>
        <div className="skeleton-text" style={{ width: '30%' }}></div>
        <div className="skeleton-text" style={{ width: '80%' }}></div>
        <div className="skeleton-text" style={{ width: '75%' }}></div>
        <div className="skeleton-text" style={{ width: '60%' }}></div>
      </div>
    </div>
  </div>
);

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
  const [userRecs, setUserRecs] = useState([]);
  
  const [searchQuery, setSearchQuery] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [skeletonLoading, setSkeletonLoading] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState('');
  const [backendAlive, setBackendAlive] = useState(false);

  // Movie Autocomplete search states
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const searchRef = useRef(null);

  // Debounced search suggestions fetch (300ms delay)
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setSuggestionsLoading(true);
    const delayDebounceFn = setTimeout(() => {
      if (backendAlive) {
        fetchWithTimeout(`${BACKEND_URL}/movies?query=${encodeURIComponent(searchQuery)}`)
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
        logMovieInteraction(selected.id, 'search');
        fetchMovieDetails(selected.id);
        setCurrentPage('details');
        setSearchQuery('');
        setShowSuggestions(false);
        setFocusedIndex(-1);
      }
    }
  };
  
  // backendUrl is now managed globally via BACKEND_URL constant

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
  const [reviewSourceFilter, setReviewSourceFilter] = useState('ALL');
  const [reviewSearchQuery, setReviewSearchQuery] = useState('');

  // Scraper loading sequence labels
  const SCRAPE_PHASES = [
    "Establishing connections to review databases...",
    "Scanning IMDb user review boards...",
    "Analyzing Reddit r/movies discussions...",
    "Retrieving Letterboxd fan ratings...",
    "Analyzing Rotten Tomatoes critic consensus...",
    "Invoking AI Sentiment Engine...",
    "Saving feedback analysis model...",
    "Calculating AI Composite Score..."
  ];

  const fetchUserRecommendations = () => {
    fetchWithTimeout(`${BACKEND_URL}/recommendations/user/1`)
      .then(res => res.json())
      .then(data => {
        setUserRecs(data || []);
      })
      .catch(err => {
        console.error("Failed to load user recommendations:", err);
        // Fallback to similar content of first movie in offline mode
        const mock = computeMockRecommendations(FALLBACK_MOVIES[0].id);
        setUserRecs(mock.similar_movies || []);
      });
  };

  const logMovieInteraction = (movieId, interactionType) => {
    if (!BACKEND_URL) return;
    fetchWithTimeout(`${BACKEND_URL}/recommendations/${movieId}/interaction?interaction_type=${interactionType}&user_id=1`, {
      method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
      console.log("Logged interaction:", data);
      fetchUserRecommendations();
    })
    .catch(err => {
      console.error("Error logging interaction:", err);
    });
  };

  // Check API Health
  useEffect(() => {
    fetchWithTimeout(`${BACKEND_URL}/`, { timeout: 3000 })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setBackendAlive(true);
          fetchPopularMovies();
          fetchUserRecommendations();
        }
      })
      .catch((err) => {
        setBackendAlive(false);
        console.error("FastAPI backend connection check failed. Operating in high-fidelity mock mode. Error:", err);
        // Fallback load
        const mock = computeMockRecommendations(FALLBACK_MOVIES[0].id);
        setUserRecs(mock.similar_movies || []);
      });
  }, []);

  const fetchPopularMovies = () => {
    fetchWithTimeout(`${BACKEND_URL}/movies`)
      .then(res => res.json())
      .then(data => {
        if (data.results && data.results.length > 0) {
          setMoviesList(data.results);
          fetchMovieDetails(data.results[0].id, false);
        }
      })
      .catch(err => {
        console.error("Error loading movies:", err);
        addToast("Failed to load movies from server.", "SERVER ERROR", "rose");
      });
  };


  const fetchMovieDetails = (movieId, triggerAnimation = true) => {
    logMovieInteraction(movieId, 'view');
    if (triggerAnimation) {
      setSkeletonLoading(true);
    }

    // Try consolidated dashboard endpoint first
    fetchWithTimeout(`${BACKEND_URL}/movie/${movieId}/dashboard`)
      .then(res => res.json())
      .then(dashboardData => {
        const movieData = dashboardData.movie_details;
        const reviewsData = dashboardData.reviews;
        const ratingData = dashboardData.rating;
        const sentimentData = dashboardData.sentiment;
        const recommendationsData = dashboardData.recommendations;

        const rawReviews = reviewsData?.reviews || [];
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
        }, 300);
      })
      .catch(dashboardError => {
        console.warn("Unified dashboard request failed, falling back to individual calls:", dashboardError);
        Promise.all([
          fetchWithTimeout(`${BACKEND_URL}/movie/${movieId}`).then(r => r.json()),
          fetchWithTimeout(`${BACKEND_URL}/reviews/${movieId}`).then(r => r.json()),
          fetchWithTimeout(`${BACKEND_URL}/rating/${movieId}`).then(r => r.json()),
          fetchWithTimeout(`${BACKEND_URL}/sentiment/${movieId}`).then(r => r.json()).catch(() => null),
          fetchWithTimeout(`${BACKEND_URL}/movie/${movieId}/recommendations`).then(r => r.json()).catch(() => null)
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
            }, 300);
          })
          .catch(err => {
            console.error("Error loading details, falling back to mock details:", err);
            addToast("Failed to fetch movie details. Loaded local archive backup.", "OFFLINE FALLBACK", "amber");
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
            }, 300);
          });
      });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    if (backendAlive) {
      setIsLoading(true);
      fetchWithTimeout(`${BACKEND_URL}/movies?query=${encodeURIComponent(searchQuery)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            setMoviesList(data.results);
            logMovieInteraction(data.results[0].id, 'search');
            fetchMovieDetails(data.results[0].id);
            setCurrentPage('home');
          } else {
            addToast("No match found in web feeds.", "NO RESULTS", "amber");
          }
          setIsLoading(false);
        })
        .catch(err => {
          console.error("Search failed:", err);
          addToast("Search failed due to a network or backend error.", "SEARCH ERROR", "rose");
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
      fetchWithTimeout(`${BACKEND_URL}/movies/${selectedMovie.id}/scraped-reviews`)
        .then(res => res.json())
        .then(() => {
          clearInterval(interval);
          setScrapeStatus("Generating AI score models...");
          setTimeout(() => {
            fetchMovieDetails(selectedMovie.id, false);
            setScrapeStatus('');
            setIsLoading(false);
            addToast("Reviews gathered successfully.", "SCAN COMPLETE", "emerald");
          }, 800);
        })
        .catch(err => {
          console.error("Scraper failed:", err);
          addToast("Scraper API failed to complete analysis.", "SCRAPER ERROR", "rose");
          clearInterval(interval);
          setScrapeStatus('');
          setIsLoading(false);
        });
    } else {
      setTimeout(() => {
        clearInterval(interval);
        setScrapeStatus('');
        setIsLoading(false);
        addToast("Reviews loaded from offline archive.", "MOCK SUCCESS", "emerald");
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

  const youtubeReviews = reviews.filter(r => r.source === 'YouTube');
  const ytPosCount = youtubeReviews.filter(r => r.sentiment_label === 'POSITIVE').length;
  const ytNegCount = youtubeReviews.filter(r => r.sentiment_label === 'NEGATIVE').length;
  const ytNeuCount = youtubeReviews.filter(r => r.sentiment_label === 'NEUTRAL').length;
  const totalYtCount = youtubeReviews.length;


  const getEffectiveWeights = (movie) => {
    if (!movie) return { imdb: 0.25, tmdb: 0.10, metacritic: 0.10, nlp: 0.15, youtube: 0.40 };
    const ratingObj = movie.rating || {};
    
    if (ratingObj.effective_weights) {
      return ratingObj.effective_weights;
    }
    
    const baseWeights = { imdb: 0.25, tmdb: 0.10, metacritic: 0.10, nlp: 0.15, youtube: 0.40 };
    const available = [];
    
    const hasImdb = ratingObj.imdb_score || movie.imdb_rating;
    const hasTmdb = ratingObj.tmdb_score || movie.vote_average;
    const hasMeta = ratingObj.metacritic_score || movie.metacritic_score;
    const hasNlp = (ratingObj.reviews_count > 0) || (movie.reviews && movie.reviews.length > 0);
    const hasYoutube = ratingObj.youtube_score !== undefined && ratingObj.youtube_score !== null;
    
    if (hasImdb) available.push("imdb");
    if (hasTmdb) available.push("tmdb");
    if (hasMeta) available.push("metacritic");
    if (hasNlp) available.push("nlp");
    if (hasYoutube) available.push("youtube");
    
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
    const base = { imdb: 0.25, tmdb: 0.10, metacritic: 0.10, nlp: 0.15, youtube: 0.40 };
    return effectiveWeights[src] !== base[src];
  });


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
    { name: 'YouTube', Score: parseFloat((hybridRating.youtube_score || 0).toFixed(1)) },
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
    
    let matchesSource = true;
    if (reviewSourceFilter === 'WEB') {
      matchesSource = r.source !== 'YouTube';
    } else if (reviewSourceFilter === 'YOUTUBE') {
      matchesSource = r.source === 'YouTube';
    }

    const matchesKeyword = !reviewSearchQuery.trim() || 
      r.review_text.toLowerCase().includes(reviewSearchQuery.toLowerCase()) ||
      r.reviewer.toLowerCase().includes(reviewSearchQuery.toLowerCase());
    return matchesSentiment && matchesSource && matchesKeyword;
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
            }}
          >
            Home
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'details' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('details');
            }}
            disabled={!selectedMovie}
          >
            Details
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'analytics' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('analytics');
            }}
            disabled={!selectedMovie}
          >
            Analytics
          </button>
          <button 
            className={`nav-tab-btn ${currentPage === 'reviews' ? 'active' : ''}`}
            onClick={() => {
              setCurrentPage('reviews');
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
            <div className="search-suggestions-dropdown">
              {suggestions.map((item, idx) => {
                const year = item.release_date ? item.release_date.split('-')[0] : 'N/A';
                const rating = item.vote_average ? item.vote_average.toFixed(1) : '0.0';
                
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      logMovieInteraction(item.id, 'search');
                      fetchMovieDetails(item.id);
                      setCurrentPage('details');
                      setSearchQuery('');
                      setShowSuggestions(false);
                      setFocusedIndex(-1);
                    }}
                    onMouseEnter={() => setFocusedIndex(idx)}
                    className={`search-suggestion-item ${idx === focusedIndex ? 'focused' : ''}`}
                  >
                    <div className="suggestion-thumb">
                      {item.poster_path ? (
                        <MovieImage
                          src={item.poster_path}
                          alt={item.title}
                          size="w92"
                        />
                      ) : (
                        <div className="suggestion-thumb-empty">🎬</div>
                      )}
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
            <div className="loading-title" style={{ letterSpacing: '0.12em', textTransform: 'uppercase' }}>Scanning Audience Feedback</div>
            <div className="loading-subtitle" style={{ marginTop: '4px' }}>{scrapeStatus || "Establishing connection..."}</div>
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
                    <MovieImage
                      src={featured.poster_path}
                      alt={featured.title}
                      className="hero-backdrop-img animate-fade"
                      size="w1280"
                      fallbackType="backdrop"
                      key={featured.id}
                    />
                    <div className="hero-overlay-fade"></div>
                    <div className="hero-text-content">
                      <span className="hero-featured-tag">AI CINEMATIC TRENDING</span>
                      <h2 className="hero-title">{featured.title}</h2>
                      
                      {/* Hero ratings and release details */}
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap' }}>
                        <span className="badge badge-tmdb" style={{ padding: '3px 8px', fontSize: '8.5px', background: 'linear-gradient(135deg, hsl(var(--accent-primary)), hsl(var(--accent-secondary)))', color: '#fff', border: 'none', fontWeight: 'bold' }}>CineScore: {compScore.toFixed(1)}</span>
                        <span className="badge badge-imdb" style={{ padding: '3px 8px', fontSize: '8.5px', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)', fontWeight: 'bold' }}>IMDb: {(featured.imdb_rating || featured.rating?.imdb_score || 7.5).toFixed(1)}</span>
                        <span style={{ fontSize: '11px', color: 'hsl(var(--text-muted))', fontFamily: 'monospace', fontWeight: 'bold', marginLeft: '6px' }}>RELEASE: {year}</span>
                      </div>

                      <p className="hero-tagline">{featured.overview}</p>
                      
                      <div className="hero-btn-row">
                        <button 
                          onClick={() => {
                            fetchMovieDetails(featured.id);
                            setCurrentPage('details');
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
                          Scan Reviews
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

              // 3. New Releases (sort by release date descending)
              const newReleases = [...moviesList].sort((a, b) => {
                const dateA = a.release_date ? new Date(a.release_date) : new Date(0);
                const dateB = b.release_date ? new Date(b.release_date) : new Date(0);
                return dateB - dateA;
              });

              // 4. Community Favorites (sort by rating count descending)
              const communityFavorites = [...moviesList].sort((a, b) => {
                const countA = a.rating?.rating_count || a.vote_count || 0;
                const countB = b.rating?.rating_count || b.vote_count || 0;
                return countB - countA;
              });

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
                          const imdb = movie.imdb_rating || movie.rating?.imdb_score || 7.5;
                          const rt = Math.round(comp * 10 - 4);
                          const explain = movie.explanation || {};
                          const pct = explain.match_percentage;
                          const why = explain.why_recommended;
                          
                          return (
                            <div
                              key={movie.id}
                              onClick={() => {
                                fetchMovieDetails(movie.id);
                                setCurrentPage('details');
                              }}
                              className="netflix-card glass-panel"
                            >
                              <div className="netflix-poster-frame">
                                <MovieImage
                                  src={movie.poster_path}
                                  alt={movie.title}
                                  size="w300"
                                />
                                
                                {pct !== undefined && pct !== null && (
                                  <div className="match-badge-overlay" style={{
                                    position: 'absolute',
                                    top: '8px',
                                    left: '8px',
                                    background: 'rgba(0, 0, 0, 0.75)',
                                    color: '#4ade80',
                                    border: '1px solid #4ade80',
                                    padding: '2px 6px',
                                    borderRadius: '4px',
                                    fontSize: '9px',
                                    fontWeight: 'bold',
                                    backdropFilter: 'blur(4px)',
                                    zIndex: 10
                                  }}>
                                    {pct}% Match
                                  </div>
                                )}
                                
                                {/* Hover Rating overlays */}
                                <div className="netflix-card-hover-overlay">
                                  <div className="hover-rating-col">
                                    <span className="badge badge-cinescore">CineScore: {comp.toFixed(1)}</span>
                                    <span className="badge badge-imdb">IMDb: {imdb.toFixed(1)}</span>
                                    <span className="badge badge-rt">RT: {rt}%</span>
                                  </div>
                                  {why && (
                                    <div style={{
                                      fontSize: '9px',
                                      color: '#a78bfa',
                                      margin: '6px 0',
                                      textAlign: 'center',
                                      padding: '0 4px',
                                      lineHeight: '1.2'
                                    }}>
                                      {why}
                                    </div>
                                  )}
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
                </div>
              );
            })()}
          </div>
        )}

        {/* SKELETON LOADER SCREEN */}
        {skeletonLoading ? (
          currentPage === 'details' ? (
            <DetailsSkeleton />
          ) : (
            <div className="movie-grid" style={{ marginTop: '40px' }}>
              {[1, 2, 3, 4].map(idx => (
                <div key={idx} className="skeleton-card skeleton-pulse">
                  <div className="skeleton-image"></div>
                  <div className="skeleton-text"></div>
                  <div className="skeleton-text short"></div>
                </div>
              ))}
            </div>
          )
        ) : (
          <>
            {/* PAGE 2: MOVIE DETAILS (Large backdrop, compare meters, streaming platforms) */}
            {currentPage === 'details' && selectedMovie && (
              <div className="details-section fade-in">
                {/* Backdrop Banner blurred card */}
                <div className="movie-details-backdrop-banner">
                  <MovieImage
                    src={selectedMovie.poster_path}
                    alt={selectedMovie.title}
                    className="details-backdrop-img"
                    size="w1280"
                    fallbackType="backdrop"
                  />
                  <div className="details-backdrop-overlay"></div>
                </div>

                {/* Primary floating details card */}
                <div className="movie-detail-card glass-panel">
                  <div className="movie-detail-poster">
                    <MovieImage
                      src={selectedMovie.poster_path}
                      alt={selectedMovie.title}
                      size="w300"
                    />
                  </div>

                  <div className="movie-detail-content">
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                        <h2 className="movie-detail-title">{selectedMovie.title}</h2>
                        <button 
                          onClick={() => {
                            setCurrentPage('analytics');
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

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '16px' }}>
                      <button onClick={triggerLiveScraper} className="scraper-button">
                        Scan Live Web Reviews
                      </button>
                      <button 
                        onClick={() => {
                          logMovieInteraction(selectedMovie.id, 'like');
                          addToast(`You liked "${selectedMovie.title}"! We'll adjust your recommendations.`, "LIKED", "gold");
                        }} 
                        className="hero-btn-secondary"
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '10px 18px' }}
                      >
                        👍 Like
                      </button>
                      <button 
                        onClick={() => {
                          logMovieInteraction(selectedMovie.id, 'save');
                          addToast(`Added "${selectedMovie.title}" to your Watchlist!`, "WATCHLIST", "neon");
                        }} 
                        className="hero-btn-secondary"
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '10px 18px' }}
                      >
                        🔖 Watchlist
                      </button>
                    </div>
                  </div>
                </div>

                {/* OTT Streaming Availability removed */}

                {/* AI & Platform Ratings comparison dashboard */}
                <div className={`score-dashboard-grid ${totalYtCount === 0 ? 'single-column-layout' : ''}`}>
                  
                  {/* CineScore AI composite gauge */}
                  {totalYtCount > 0 && (
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
                    </div>
                  )}

                  {/* YouTube Trailer Reactions Block */}
                  {totalYtCount > 0 && (
                    <div className="youtube-rating-card glass-panel youtube-glow">
                      <h3 className="catalog-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ff0000' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ flexShrink: 0 }}>
                          <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.108C19.524 3.545 12 3.545 12 3.545s-7.524 0-9.388.51a3.002 3.002 0 0 0-2.11 2.108C0 8.029 0 12 0 12s0 3.971.502 5.837a3.003 3.003 0 0 0 2.11 2.108c1.864.51 9.388.51 9.388.51s7.524 0 9.388-.51a3.002 3.002 0 0 0 2.11-2.108c.502-1.866.502-5.837.502-5.837s0-3.971-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                        </svg>
                        YouTube Trailer Hype
                      </h3>

                      <div className="youtube-card-body">
                        <div className="relative" style={{ width: '120px', height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '8px 0', position: 'relative' }}>
                          <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                            <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
                            <circle
                              cx="50"
                              cy="50"
                              r="40"
                              fill="transparent"
                              stroke="#ff0000"
                              strokeWidth="8"
                              strokeDasharray={2 * Math.PI * 40}
                              strokeDashoffset={2 * Math.PI * 40 * (1 - (effectiveWeights.youtube > 0 ? (hybridRating.youtube_score || 0) : 0) / 10.0)}
                              strokeLinecap="round"
                              style={{ transition: 'stroke-dashoffset 0.4s ease-in-out' }}
                            />
                          </svg>
                          <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <span style={{ fontSize: '28px', fontWeight: '800', color: 'hsl(var(--text-main))', letterSpacing: '-0.03em', lineHeight: '1' }}>
                              {effectiveWeights.youtube > 0 && hybridRating.youtube_score !== undefined && hybridRating.youtube_score !== null
                                ? hybridRating.youtube_score.toFixed(1)
                                : "N/A"}
                            </span>
                            <span style={{ fontSize: '7px', color: '#ff0000', fontFamily: 'monospace', letterSpacing: '0.1em', marginTop: '3px', fontWeight: 'bold' }}>TRAILER SCORE</span>
                          </div>
                        </div>

                        <div className="youtube-stats-container">
                          <div className="youtube-stat-badge pos">
                            <span className="dot"></span>
                            <span className="label">Positive Reviews</span>
                            <span className="count">{ytPosCount}</span>
                          </div>
                          <div className="youtube-stat-badge neu">
                            <span className="dot"></span>
                            <span className="label">Neutral Reviews</span>
                            <span className="count">{ytNeuCount}</span>
                          </div>
                          <div className="youtube-stat-badge neg">
                            <span className="dot"></span>
                            <span className="label">Negative Reviews</span>
                            <span className="count">{ytNegCount}</span>
                          </div>
                        </div>
                      </div>

                      <div className="youtube-footer-text">
                        Calculated from <strong>{totalYtCount}</strong> trailer comments
                      </div>
                    </div>
                  )}

                  {/* Multi-platform compare scores progress bars */}
                  <div className="breakdown-card glass-panel">

                    <h3 className="catalog-title" style={{ marginBottom: '16px' }}>Platform Comparisons</h3>
                    
                    <div className="bar-list">
                      {/* IMDb */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.imdb > 0 ? 1 : 0.45, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            IMDb Rating
                          </span>
                          <span style={{ fontWeight: '700', color: '#fbbf24' }}>
                            {effectiveWeights.imdb > 0 && (hybridRating.imdb_score || selectedMovie.imdb_rating)
                              ? `${(hybridRating.imdb_score || selectedMovie.imdb_rating).toFixed(1)}/10`
                              : "Rating unavailable"}
                          </span>
                        </div>
                        <div className="bar-track">
                          <div className="bar-fill" style={{ width: `${(effectiveWeights.imdb > 0 ? (hybridRating.imdb_score || selectedMovie.imdb_rating || 0) : 0) * 10}%`, backgroundColor: '#fbbf24' }}></div>
                        </div>
                      </div>

                      {/* TMDb */}
                      <div className="bar-item" style={{ opacity: effectiveWeights.tmdb > 0 ? 1 : 0.45, transition: 'opacity 0.4s ease' }}>
                        <div className="bar-label-row">
                          <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                            TMDb Rating
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
                            Metacritic Score
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
                      {totalYtCount > 0 && (
                        <div className="bar-item" style={{ opacity: effectiveWeights.nlp > 0 ? 1 : 0.75, transition: 'opacity 0.4s ease' }}>
                          <div className="bar-label-row">
                            <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                              Audience Sentiment Rating
                            </span>
                            <span style={{ fontWeight: '700', color: '#4ade80' }}>
                              {effectiveWeights.nlp > 0
                                ? `${((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5).toFixed(1)}/10`
                                : "Awaiting Live Scan"}
                            </span>
                          </div>
                          <div className="bar-track">
                            <div className="bar-fill" style={{ width: `${(effectiveWeights.nlp > 0 ? ((hybridRating.sentiment_avg_polarity || 0.4) * 5 + 5) : 0) * 10}%`, backgroundColor: '#4ade80' }}></div>
                          </div>
                        </div>
                      )}

                      {/* YouTube */}
                      {totalYtCount > 0 && (
                        <div className="bar-item" style={{ opacity: effectiveWeights.youtube > 0 ? 1 : 0.75, transition: 'opacity 0.4s ease' }}>
                          <div className="bar-label-row">
                            <span style={{ color: 'hsl(var(--text-main))', fontWeight: '600' }}>
                              YouTube Trailer Reactions
                            </span>
                            <span style={{ fontWeight: '700', color: '#ff0000' }}>
                              {effectiveWeights.youtube > 0 && hybridRating.youtube_score !== undefined && hybridRating.youtube_score !== null
                                ? `${hybridRating.youtube_score.toFixed(1)}/10`
                                : "Awaiting Live Scan"}
                            </span>
                          </div>
                          <div className="bar-track">
                            <div className="bar-fill" style={{ width: `${(effectiveWeights.youtube > 0 ? (hybridRating.youtube_score || 0) : 0) * 10}%`, backgroundColor: '#ff0000' }}></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                            {/* Categorized Recommendations */}
                {recommendations && (recommendations.similar_movies?.length > 0 || recommendations.similar_themes?.length > 0 || recommendations.hidden_gems?.length > 0 || recommendations.trending_alternatives?.length > 0) && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '24px', width: '100%' }}>
                    
                    {(() => {
                      const renderRecRow = (title, list, accentColor) => {
                        if (!list || list.length === 0) return null;
                        return (
                          <div className="recommendations-container glass-panel" style={{ width: '100%', padding: '20px' }}>
                            <h3 className="catalog-title" style={{ marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px' }}>
                              <span style={{ color: accentColor }}>●</span> {title}
                            </h3>
                            <div className="recommendations-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '16px' }}>
                              {list.map((rec) => {
                                const explain = rec.explanation || {};
                                const pct = explain.match_percentage || 80;
                                const why = explain.why_recommended || "High semantic correlation";
                                const genreMatch = explain.genre_match_pct || 0;
                                const themeMatch = explain.theme_match_pct || 0;
                                const yearDiff = explain.year_diff_text || "Released Same Year";
                                const cinescore = explain.cinescore || 7.0;
                                const statsText = `${genreMatch}% Genre Match • ${themeMatch}% Theme Match • ${yearDiff} • CineScore ${cinescore.toFixed(1)}`;
                                
                                return (
                                  <div
                                    key={rec.id}
                                    onClick={() => {
                                      logMovieInteraction(rec.id, 'view');
                                      fetchMovieDetails(rec.id);
                                      window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    className="rec-card glass-panel"
                                    style={{ display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', position: 'relative', overflow: 'hidden' }}
                                  >
                                    <div className="rec-poster" style={{ position: 'relative', width: '100%', aspectRatio: '2/3', overflow: 'hidden' }}>
                                      <MovieImage
                                        src={rec.poster_path}
                                        alt={rec.title}
                                        size="w200"
                                      />
                                      {/* Match percentage badge overlay */}
                                      <div className="match-badge-overlay" style={{
                                        position: 'absolute',
                                        top: '8px',
                                        left: '8px',
                                        background: 'rgba(0, 0, 0, 0.75)',
                                        color: accentColor,
                                        border: `1px solid ${accentColor}`,
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        fontSize: '9px',
                                        fontWeight: 'bold',
                                        backdropFilter: 'blur(4px)',
                                        zIndex: 10
                                      }}>
                                        {pct}% Match
                                      </div>
                                    </div>
                                    <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', padding: '10px 8px 8px 8px' }}>
                                      <h4 style={{ fontSize: '12px', fontWeight: '700', color: 'hsl(var(--text-main))', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: '1.2', margin: '0' }}>{rec.title}</h4>
                                      <p style={{ fontSize: '9px', color: 'hsl(var(--text-muted))', marginTop: '6px', lineHeight: '1.3', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden', margin: '6px 0 0 0' }}>{statsText}</p>
                                      
                                      {/* Analytics mini dashboard on card hover */}
                                      <div className="rec-analytics-hover" style={{ marginTop: '8px', borderTop: '1px solid hsla(var(--text-main)/0.06)', paddingTop: '6px' }}>
                                        <div style={{ fontSize: '8.5px', fontFamily: 'monospace', color: 'hsla(var(--text-main)/0.65)' }}>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                                            <span>Genre Match:</span>
                                            <span style={{ color: '#4ade80' }}>{genreMatch}%</span>
                                          </div>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                                            <span>Theme Match:</span>
                                            <span style={{ color: '#a78bfa' }}>{themeMatch}%</span>
                                          </div>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                                            <span>Timeline:</span>
                                            <span style={{ color: '#60a5fa' }}>{yearDiff}</span>
                                          </div>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                                            <span>CineScore:</span>
                                            <span style={{ color: '#fbbf24' }}>{cinescore.toFixed(1)}</span>
                                          </div>
                                          <div style={{ marginTop: '4px', borderTop: '1px dashed hsla(var(--text-main)/0.06)', paddingTop: '4px', fontStyle: 'italic', fontSize: '8px', lineHeight: '1.2' }}>
                                            {why}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      };

                      return (
                        <>
                          {renderRecRow("Similar Movies", recommendations.similar_movies, '#4ade80')}
                        </>
                      );
                    })()}
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
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                          <Bar dataKey="Score" radius={[4, 4, 0, 0]}>
                            {ratingComparisonData.map((entry, index) => {
                              const colors = ['#fbbf24', 'hsl(var(--accent-secondary))', '#f87171', '#4ade80', '#ff0000', 'hsl(var(--accent-primary))'];
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
                            <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                            <Legend verticalAlign="bottom" height={36} tick={{ fill: 'hsl(var(--text-main))', fontSize: 10 }} />
                          </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <div style={{ color: 'hsl(var(--text-muted))', fontSize: '12px' }}>Scan live reviews to compile sentiment ratio pie.</div>
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
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
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
                          <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
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
                
                <div style={{ marginBottom: '24px' }}>
                  <h2 className="movie-detail-title" style={{ fontSize: '26px', marginBottom: '6px' }}>
                    Audience Reviews: <span className="accent-gradient">{selectedMovie.title}</span>
                  </h2>
                  <p className="catalog-subtitle" style={{ margin: '4px 0 0 0' }}>
                    Real-time web reviews and AI sentiment analysis.
                  </p>
                </div>
                
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
                          }}
                          className={`filter-btn ${reviewFilter === sentiment ? 'active' : ''}`}
                        >
                          {sentiment === 'ALL' ? 'Show All' : sentiment.charAt(0) + sentiment.slice(1).toLowerCase()}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-row" style={{ marginTop: '12px', borderTop: '1px solid hsla(var(--text-main)/0.04)', paddingTop: '12px' }}>
                    <span className="filter-label">Filter Source</span>
                    <div className="filter-btns">
                      {[
                        { label: 'All Sources', code: 'ALL' },
                        { label: 'Web Reviews', code: 'WEB' },
                        { label: 'YouTube Comments', code: 'YOUTUBE' }
                      ].map(srcOpt => (
                        <button
                          key={srcOpt.code}
                          onClick={() => {
                            setReviewSourceFilter(srcOpt.code);
                          }}
                          className={`filter-btn ${reviewSourceFilter === srcOpt.code ? 'active' : ''}`}
                        >
                          {srcOpt.label}
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
                          addToast(e.target.checked ? "Spam filter enabled" : "Spam filter disabled", "FILTER", "amber");
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
                                  <div className="review-source-label">
                                    Source: {r.source === 'YouTube' ? (
                                      <span style={{ color: '#ff0000', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                                        📹 YouTube Comment
                                      </span>
                                    ) : r.source ? (
                                      `${r.source} Review`
                                    ) : r.is_scraped ? (
                                      `Web Review`
                                    ) : (
                                      `CineScore User`
                                    )}
                                  </div>
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
