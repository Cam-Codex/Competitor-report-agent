import React from 'react';
import { Link, Outlet } from 'react-router-dom';

export default function Layout({ query, setQuery }) {
  return (
    <>
      <header className="navbar">
        <h1>Analytics News</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/vendors">Vendors</Link>
          <Link to="/industry">Industry</Link>
        </nav>
        <input
          className="search"
          type="text"
          placeholder="Search articles"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </header>
      <main className="content">
        <Outlet />
      </main>
    </>
  );
}
