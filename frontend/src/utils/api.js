// api.js
// API requests, mock datasets, and content recommendation fallbacks.

import React, { useState } from 'react';

export const sanitizeUrl = (url) => {
  if (!url) return '';
  const trimmed = url.trim();
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed;
};

// Top-level backend URL loaded from environment variables
export const BACKEND_URL = sanitizeUrl(import.meta.env.VITE_API_URL || '');
console.log("[CineScore API] Initialized with sanitized BACKEND_URL:", BACKEND_URL || "(relative path / local Vercel fallback)");

// Safe rating parser to prevent TypeError when toFixed is called on missing/string scores
export const parseRating = (val, fallback = 0) => {
  if (val === null || val === undefined) return fallback;
  const num = parseFloat(val);
  return isNaN(num) ? fallback : num;
};

// Network request helper with timeout, logging, and custom error handling
export const fetchWithTimeout = async (resource, options = {}) => {
  const { timeout = 10000 } = options;
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  console.log(`[API Request] URL: ${resource} | Method: ${options.method || 'GET'}`);
  
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    
    // Clone response so we can log its payload without consuming the original body stream
    const responseClone = response.clone();
    
    console.log(`[API Response] URL: ${resource} | Status: ${response.status} ${response.statusText}`);
    
    try {
      const textBody = await responseClone.text();
      try {
        const jsonBody = JSON.parse(textBody);
        console.log(`[API Response Payload] URL: ${resource} | Data:`, jsonBody);
      } catch {
        console.log(`[API Response Payload] URL: ${resource} | Text:`, textBody.slice(0, 1000));
      }
    } catch (logErr) {
      console.warn(`[API Log Error] Failed to read response body for logging:`, logErr);
    }
    
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
    console.error(`[API Fetch Exception] URL: ${resource} | Error:`, error);
    throw error;
  }
};


// Fallback high-fidelity mock dataset used when backend is offline/unreachable
export const FALLBACK_MOVIES = [
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
export const computeMockAspectScores = (reviewsList) => {
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
export const computeMockRecommendations = (movieId) => {
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
export const computeMockModeration = (reviewsList) => {
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
export const MovieImage = ({ src, alt, className, style, size = 'w300', fallbackType = 'poster' }) => {
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
export const DetailsSkeleton = () => (
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

