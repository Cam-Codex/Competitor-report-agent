import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function Layout({ query, setQuery }) {
  return (
    <>
      <header className="navbar">
        <h1>Analytics News</h1>
        <nav>
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/vendors">Vendors</NavLink>
          <NavLink to="/industry">Industry</NavLink>
          <NavLink to="/older">Older</NavLink>
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
