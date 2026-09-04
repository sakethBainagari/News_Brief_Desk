import React, { useState, useEffect } from "react";
import { getRawItems } from "../api/rawItems";

export default function RawWireView() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedItem, setSelectedItem] = useState(null);

  const categories = ["Technology", "Business", "Transport", "Energy", "Healthcare", "Environment", "Science", "Economy", "Local", "Sports"];

  const fetchItems = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getRawItems(page, 15, category, "", search);
      setItems(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message || "Failed to load raw news wire items.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [page, category]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchItems();
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>Incoming Raw Wire Copy</h2>
          <p className="description">
            Unprocessed incoming wire copy, press releases, and feeds before AI event grouping.
          </p>
        </div>
        <div className="header-badge">Total Items: {total}</div>
      </div>

      <div className="filter-bar">
        <form onSubmit={handleSearchSubmit} className="search-box">
          <input
            type="text"
            placeholder="Search headline or body copy..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>

        <div className="category-filter">
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}>
            <option value="">All Categories ({total})</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading raw wire feed...</div>
      ) : error ? (
        <div className="error-alert">{error}</div>
      ) : items.length === 0 ? (
        <div className="empty-state">No raw items match the selected criteria.</div>
      ) : (
        <div className="wire-grid">
          {items.map((item) => (
            <article key={item.id} className="wire-card" onClick={() => setSelectedItem(item)}>
              <div className="wire-card-meta">
                <span className="source-name">{item.source_name}</span>
                <span className="category-tag">{item.category || "General"}</span>
              </div>
              <h3 className="wire-headline">{item.headline}</h3>
              <p className="wire-preview">{item.body.slice(0, 140)}...</p>
              <div className="wire-card-footer">
                <span>Received: {new Date(item.source_published_at || item.ingested_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                <button className="view-link">Read Full Wire &rarr;</button>
              </div>
            </article>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>&larr; Previous</button>
          <span>Page {page} of {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next &rarr;</button>
        </div>
      )}

      {selectedItem && (
        <div className="modal-backdrop" onClick={() => setSelectedItem(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="category-tag">{selectedItem.category}</span>
              <button className="close-btn" onClick={() => setSelectedItem(null)}>&times;</button>
            </div>
            <h2>{selectedItem.headline}</h2>
            <div className="modal-meta">
              <strong>Source:</strong> {selectedItem.source_name} &bull; 
              <strong> Received:</strong> {new Date(selectedItem.source_published_at || selectedItem.ingested_at).toLocaleString()}
            </div>
            <div className="modal-body">
              <p>{selectedItem.body}</p>
            </div>
            <div className="modal-footer">
              <button onClick={() => setSelectedItem(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
