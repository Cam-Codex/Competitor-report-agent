import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import Home from './pages/Home.jsx';
import Vendors from './pages/Vendors.jsx';
import Industry from './pages/Industry.jsx';
import Older from './pages/Older.jsx';

export default function App() {
  const [articles, setArticles] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    fetch('/articles.json')
      .then((res) => res.json())
      .then(setArticles)
      .catch(() => setArticles([]));
  }, []);

  const filtered = articles.filter((a) => {
    const text = `${a.title} ${a.summary}`.toLowerCase();
    return text.includes(query.toLowerCase());
  });

  const parseDate = (a) => new Date(a.published || a.fetched);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 2);

  const recent = filtered
    .filter((a) => {
      const d = parseDate(a);
      return !isNaN(d) && d >= cutoff;
    })
    .sort((a, b) => parseDate(b) - parseDate(a));

  const homeArticles = (recent.length ? recent : filtered).slice(0, 10);
  const older = filtered.filter((a) => {
    const d = parseDate(a);
    return isNaN(d) || d < cutoff;
  });

  return (
    <Routes>
      <Route element={<Layout query={query} setQuery={setQuery} />}>
        <Route index element={<Home articles={homeArticles} />} />
        <Route path="vendors" element={<Vendors articles={filtered} />} />
        <Route path="industry" element={<Industry articles={filtered} />} />
        <Route path="older" element={<Older articles={older} />} />
      </Route>
    </Routes>
  );
}
