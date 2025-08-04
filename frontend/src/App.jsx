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

  const today = new Date().toISOString().slice(0, 10);
  const latest = filtered.filter((a) => a.fetched === today);
  const homeArticles = latest.length ? latest : filtered;
  const older = filtered.filter((a) => a.fetched !== today);

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
