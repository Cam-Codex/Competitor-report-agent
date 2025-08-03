import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import Home from './pages/Home.jsx';
import Vendors from './pages/Vendors.jsx';
import Industry from './pages/Industry.jsx';

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

  return (
    <Routes>
      <Route element={<Layout query={query} setQuery={setQuery} />}>
        <Route index element={<Home articles={filtered} />} />
        <Route path="vendors" element={<Vendors articles={filtered} />} />
        <Route path="industry" element={<Industry articles={filtered} />} />
      </Route>
    </Routes>
  );
}
