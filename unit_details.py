import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta, date
import hashlib
import secrets
import pyodbc
import re
from flask import request, session
import logging
import mysql.connector
from mysql.connector import Error
import json

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/unit_details/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    ]
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
  /* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #1a1a1a;
    background-color: #ffffff;
    overflow-x: hidden;
}

/* Header Styles */
.main-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    transition: all 0.3s ease;
}

.header-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 80px;
}

.logo-container .logo {
    height: 50px;
    width: auto;
    object-fit: contain;
}

.nav-menu {
    display: flex;
    align-items: center;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 2rem;
    list-style: none;
}

.nav-link {
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.5rem 0;
    position: relative;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-link:hover {
    color: #FFD700;
}

.nav-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: #FFD700;
    transition: width 0.3s ease;
}

.nav-link:hover::after {
    width: 100%;
}

.auth-link {
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.3s ease;
}

.auth-link:hover {
    background: #FFD700;
    color: #1a1a1a;
    border-color: #FFD700;
    transform: translateY(-1px);
}

.mobile-menu-toggle, .mobile-menu-close {
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #1a1a1a;
    cursor: pointer;
    padding: 0.5rem;
}

/* Unit Details Page Styles */

/* Hero Section */
.unit-hero-section {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    padding: 120px 0 80px;
    position: relative;
    overflow: hidden;
}

.unit-hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23FFD700" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23FFD700" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="%23FFD700" opacity="0.05"/><circle cx="10" cy="60" r="1" fill="%23FFD700" opacity="0.08"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    pointer-events: none;
}

.hero-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    position: relative;
    z-index: 2;
}

.breadcrumb-nav {
    margin-bottom: 2rem;
    font-size: 0.9rem;
}

.breadcrumb-link {
    color: #ccc;
    text-decoration: none;
    transition: color 0.3s ease;
}

.breadcrumb-link:hover {
    color: #FFD700;
}

.breadcrumb-separator {
    color: #666;
    margin: 0 0.5rem;
}

.breadcrumb-current {
    color: #FFD700;
    font-weight: 500;
}

.unit-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}

.unit-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
    font-size: 1.1rem;
}

.unit-location, .unit-availability {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.unit-availability.available {
    color: #4ade80;
}

.unit-availability.unavailable {
    color: #f87171;
}

/* Main Content Layout */
.main-content-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 4rem 2rem;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 4rem;
    align-items: start;
}

.main-content-left {
    display: flex;
    flex-direction: column;
    gap: 3rem;
}

/* Warehouse Image */
.warehouse-image-container {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.warehouse-image-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
}

.warehouse-main-image {
    width: 100%;
    height: 400px;
    object-fit: cover;
    display: block;
}

.image-overlay-controls {
    position: absolute;
    top: 1rem;
    right: 1rem;
    display: flex;
    gap: 0.5rem;
}

.fullscreen-btn, .favorite-btn {
    background: rgba(0, 0, 0, 0.7);
    border: none;
    color: white;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.fullscreen-btn:hover, .favorite-btn:hover {
    background: rgba(255, 215, 0, 0.9);
    color: #1a1a1a;
    transform: scale(1.1);
}

/* Unit Information Section */
.unit-info-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.unit-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    border-left: 4px solid #FFD700;
    transition: all 0.3s ease;
}

.info-item:hover {
    background: #f1f3f4;
    transform: translateY(-2px);
}

.info-item i {
    color: #FFD700;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
}

.info-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.info-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
}

.info-value.price {
    color: #FFD700;
    font-size: 1.3rem;
}

.save-unit-btn {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.save-unit-btn:hover {
    background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
    color: #1a1a1a;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(255, 215, 0, 0.3);
}

/* Section Titles */
.section-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a1a1a;
    position: relative;
    padding-bottom: 0.5rem;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #FFD700 0%, #e6c200 100%);
    border-radius: 2px;
}

/* Unit Description */
.unit-description-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.unit-description-text {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #4a5568;
    margin-bottom: 2rem;
}

.description-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.description-feature {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 10px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.description-feature:hover {
    background: #e9ecef;
    transform: translateX(5px);
}

.description-feature i {
    color: #FFD700;
    font-size: 1.1rem;
}

/* Facilities Section */
.facilities-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.facilities-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.facility-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.25rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.facility-item:hover {
    background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
    color: #1a1a1a;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(255, 215, 0, 0.3);
    border-color: #FFD700;
}

.facility-item i {
    font-size: 1.2rem;
    color: #1a1a1a;
}

.facility-item:hover i {
    color: #1a1a1a;
}

/* Warehouse Visualization */
.warehouse-visualization {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.visualization-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a1a1a;
    text-align: center;
}

.visualization-legend {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
}

.legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid rgba(0, 0, 0, 0.1);
}

.legend-color.available {
    background: #22c55e;
}

.legend-color.booked {
    background: #ef4444;
}

.legend-color.unavailable {
    background: #6b7280;
}

.legend-color.current-unit {
    background: #3b82f6;
    border-color: #FFD700;
    border-width: 3px;
}

.warehouse-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
    max-height: 400px;
    overflow-y: auto;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
}

.unit-cell {
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.25rem;
}

.unit-cell.not_taken {
    background: #22c55e;
    color: white;
}

.unit-cell.booked {
    background: #ef4444;
    color: white;
}

.unit-cell.unavailable {
    background: #6b7280;
    color: white;
}

.unit-cell.current-unit {
    background: #3b82f6;
    color: white;
    border-color: #FFD700;
    border-width: 3px;
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
}

.unit-cell:hover:not(.current-unit) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.unit-cell-name {
    font-weight: 700;
    font-size: 0.9rem;
}

.unit-cell-status {
    font-size: 0.75rem;
    opacity: 0.9;
    text-transform: capitalize;
}

/* Location Section */
.location-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.location-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    align-items: start;
}

.location-map {
    width: 100%;
    height: 300px;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.location-info {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.location-detail {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 12px;
    border-left: 4px solid #FFD700;
}

.location-detail i {
    color: #FFD700;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
}

.location-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.location-value {
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a1a;
}

.directions-link {
    color: #FFD700;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s ease;
}

.directions-link:hover {
    color: #e6c200;
    text-decoration: underline;
}

/* Booking Panel */
.main-content-right {
    position: sticky;
    top: 100px;
}

.booking-panel {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.booking-panel:hover {
    transform: translateY(-5px);
    box-shadow: 0 30px 70px rgba(0, 0, 0, 0.2);
}

.booking-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid #f1f3f4;
}

.booking-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 1rem;
}

.booking-price-display {
    font-size: 2.5rem;
    font-weight: 800;
    color: #FFD700;
    line-height: 1;
}

.booking-price-period {
    color: #666;
    font-size: 1rem;
    font-weight: 500;
}

.booking-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.booking-field {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.booking-label {
    font-weight: 600;
    color: #1a1a1a;
    font-size: 1rem;
}

.quantity-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
}

.quantity-btn {
    width: 40px;
    height: 40px;
    border: 2px solid #FFD700;
    background: white;
    color: #FFD700;
    border-radius: 50%;
    font-size: 1.2rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.quantity-btn:hover {
    background: #FFD700;
    color: #1a1a1a;
    transform: scale(1.1);
}

.quantity-display {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    min-width: 40px;
    text-align: center;
}

.insurance-dropdown, .duration-dropdown {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 0.75rem;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    background: white;
}

.insurance-dropdown:focus, .duration-dropdown:focus {
    outline: none;
    border-color: #FFD700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

.insurance-description {
    font-size: 0.9rem;
    color: #666;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin-top: 0.5rem;
}

/* Booking Summary */
.summary-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.summary-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 1rem;
    text-align: center;
}

.booking-summary {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
}

.summary-label {
    color: #666;
    font-weight: 500;
}

.summary-value {
    color: #1a1a1a;
    font-weight: 600;
}

.summary-divider {
    border: none;
    height: 1px;
    background: #d1d5db;
    margin: 0.5rem 0;
}

.total-row {
    padding: 1rem 0 0.5rem;
    border-top: 2px solid #FFD700;
}

.summary-label.total, .summary-value.total {
    font-size: 1.2rem;
    font-weight: 700;
}

.summary-value.total {
    color: #FFD700;
}

/* Action Buttons */
.book-now-btn {
    width: 100%;
    padding: 1.25rem;
    background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
    color: #1a1a1a;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.book-now-btn:hover {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.additional-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.secondary-btn {
    padding: 0.875rem;
    background: white;
    color: #1a1a1a;
    border: 2px solid #e9ecef;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.secondary-btn:hover {
    border-color: #FFD700;
    background: #FFD700;
    color: #1a1a1a;
    transform: translateY(-1px);
}

/* Footer */
.main-footer {
    background: #1a1a1a;
    color: white;
    padding: 4rem 2rem 2rem;
}

.footer-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.footer-section h4 {
    color: #FFD700;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    font-weight: 600;
}

.footer-section p, .footer-section ul {
    color: #ccc;
    line-height: 1.6;
}

.footer-section ul {
    list-style: none;
}

.footer-section ul li {
    margin-bottom: 0.5rem;
}

.footer-section a {
    color: #ccc;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-section a:hover {
    color: #FFD700;
}

.footer-bottom {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #333;
    color: #999;
}

/* Error Message */
.error-message {
    text-align: center;
    padding: 4rem 2rem;
    font-size: 1.2rem;
    color: #ef4444;
    background: #fef2f2;
    border-radius: 12px;
    border: 1px solid #fecaca;
    margin: 2rem auto;
    max-width: 600px;
}

/* Mobile Responsive */
@media (max-width: 1200px) {
    .main-content-container {
        grid-template-columns: 1fr;
        gap: 3rem;
    }
    
    .main-content-right {
        position: static;
        max-width: 500px;
        margin: 0 auto;
    }
    
    .location-container {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .mobile-menu-toggle {
        display: block;
    }

    .nav-menu {
        position: fixed;
        top: 0;
        right: -100%;
        width: 300px;
        height: 100vh;
        background: white;
        flex-direction: column;
        justify-content: flex-start;
        padding: 2rem;
        box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
        transition: right 0.3s ease;
        z-index: 1001;
    }

    .nav-menu.active {
        right: 0;
    }

    .mobile-menu-close {
        display: block;
        position: absolute;
        top: 1rem;
        right: 1rem;
    }

    .nav-links {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
        width: 100%;
        margin-top: 3rem;
    }

    .nav-link {
        width: 100%;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .header-container {
        padding: 0 1rem;
    }
    
    .main-content-container {
        padding: 2rem 1rem;
        gap: 2rem;
    }
    
    .unit-meta {
        flex-direction: column;
        gap: 1rem;
    }
    
    .unit-info-grid {
        grid-template-columns: 1fr;
    }
    
    .facilities-grid {
        grid-template-columns: 1fr;
    }
    
    .warehouse-grid {
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
    
    .visualization-legend {
        gap: 1rem;
        justify-content: flex-start;
    }
    
    .booking-panel {
        padding: 1.5rem;
    }
    
    .booking-price-display {
        font-size: 2rem;
    }
    
    .additional-actions {
        grid-template-columns: 1fr;
    }
    
    .description-features {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .hero-container {
        padding: 0 1rem;
    }
    
    .unit-title {
        font-size: 2rem;
    }
    
    .warehouse-main-image {
        height: 250px;
    }
    
    .unit-info-section,
    .unit-description-section,
    .facilities-section,
    .warehouse-visualization,
    .location-section {
        padding: 1.5rem;
        margin: 0 -0.5rem;
        border-radius: 12px;
    }
    
    .booking-panel {
        padding: 1rem;
        border-radius: 16px;
    }
    
    .booking-title {
        font-size: 1.5rem;
    }
    
    .booking-price-display {
        font-size: 1.8rem;
    }
    
    .warehouse-grid {
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 0.5rem;
    }
    
    .unit-cell {
        padding: 0.75rem;
        min-height: 60px;
        font-size: 0.75rem;
    }
    
    .location-map {
        height: 200px;
    }
}

/* Page Specific Styles */
.page-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    text-align: center;
    margin: 6rem auto 1rem;
    color: #1a1a1a;
    padding: 0 2rem;
}

.page-subtitle {
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 3rem;
    color: #666;
    padding: 0 2rem;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Loading states and animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Animation classes */
.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out forwards;
}

.animate-slide-in-right {
    animation: slideInRight 0.6s ease-out forwards;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

/* Utility classes */
.text-gradient {
    background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.shadow-gold {
    box-shadow: 0 10px 25px rgba(255, 215, 0, 0.2);
}

.border-gold {
    border-color: #FFD700 !important;
}

/* Custom scrollbar for warehouse grid */
.warehouse-grid::-webkit-scrollbar {
    width: 8px;
}

.warehouse-grid::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.warehouse-grid::-webkit-scrollbar-thumb {
    background: #FFD700;
    border-radius: 10px;
}

.warehouse-grid::-webkit-scrollbar-thumb:hover {
    background: #e6c200;
}

/* Focus states for accessibility */
.quantity-btn:focus,
.book-now-btn:focus,
.secondary-btn:focus,
.save-unit-btn:focus {
    outline: 3px solid rgba(255, 215, 0, 0.3);
    outline-offset: 2px;
}

/* Print styles */
@media print {
    .main-header,
    .main-footer,
    .booking-panel,
    .image-overlay-controls {
        display: none;
    }
    
    .main-content-container {
        grid-template-columns: 1fr;
        padding: 1rem;
    }
    
    .unit-hero-section {
        background: white;
        color: black;
        padding: 2rem 0;
    }
    
    .warehouse-main-image {
        height: 200px;
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .unit-cell,
    .facility-item,
    .info-item,
    .description-feature {
        border: 2px solid #000;
    }
    
    .booking-panel {
        border: 3px solid #000;
    }
    
    .legend-color {
        border-width: 3px;
        border-color: #000;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .warehouse-image-container:hover,
    .booking-panel:hover,
    .facility-item:hover,
    .unit-cell:hover {
        transform: none;
    }
}
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Mobile menu functionality
            document.addEventListener('DOMContentLoaded', function() {
                const menuToggle = document.getElementById('mobile-menu-toggle');
                const menuClose = document.getElementById('mobile-menu-close');
                const navMenu = document.getElementById('nav-menu');

                if (menuToggle) {
                    menuToggle.addEventListener('click', function() {
                        navMenu.classList.add('active');
                    });
                }

                if (menuClose) {
                    menuClose.addEventListener('click', function() {
                        navMenu.classList.remove('active');
                    });
                }

                // Close menu when clicking outside
                document.addEventListener('click', function(e) {
                    if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                        navMenu.classList.remove('active');
                    }
                });

        </script>
    </body>
</html>
'''

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='warehouse_db',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Get unit details by ID
def get_unit_details(unit_id):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            u.id,
            u.name as unit_name,
            u.price,
            u.availability,
            u.status,
            u.created_at,
            w.id as warehouse_id,
            w.name as warehouse_name,
            w.location as warehouse_location,
            w.capacity as warehouse_capacity,
            w.image_path as warehouse_image,
            w.status as warehouse_status
        FROM units u
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE u.id = %s AND u.status = 'active'
        """
        cursor.execute(query, (unit_id,))
        unit = cursor.fetchone()
        return unit
    except Error as e:
        print(f"Error fetching unit details: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Get all units in a warehouse for availability visualization
def get_warehouse_units(warehouse_id):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            u.id,
            u.name as unit_name,
            u.availability,
            u.status,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM bookings b 
                    WHERE b.unit_id = u.id 
                    AND b.status IN ('confirmed', 'pending')
                    AND CURDATE() BETWEEN b.start_date AND b.end_date
                ) THEN 'booked'
                WHEN u.availability = 'not taken' THEN 'available'
                ELSE 'unavailable'
            END as booking_status
        FROM units u
        WHERE u.warehouse_id = %s AND u.status = 'active'
        ORDER BY u.name
        """
        cursor.execute(query, (warehouse_id,))
        units = cursor.fetchall()
        return units
    except Error as e:
        print(f"Error fetching warehouse units: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Get insurance plans
def get_insurance_plans():
    return [
        {'id': 1, 'name': 'Basic Protection', 'price': 50, 'description': 'Basic coverage for fire and theft'},
        {'id': 2, 'name': 'Standard Protection', 'price': 100, 'description': 'Enhanced coverage including water damage'},
        {'id': 3, 'name': 'Premium Protection', 'price': 200, 'description': 'Comprehensive coverage for all risks'},
        {'id': 4, 'name': 'Full Coverage', 'price': 300, 'description': 'Maximum protection with replacement value'}
    ]

# Create authenticated user booking
def create_user_booking(booking_data):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Calculate end date (assuming monthly booking for now)
        start_date = datetime.now().date()
        duration_months = booking_data.get('duration', 1)
        end_date = start_date + timedelta(days=30 * duration_months)
        
        # Insert into bookings table
        insert_query = """
        INSERT INTO bookings 
        (unit_id, user_id, customer_name, customer_email, customer_phone, 
         start_date, end_date, total_amount, status, payment_status, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Get user details for booking
        user_query = """
        SELECT 
            CASE 
                WHEN user_type = 'corporate' THEN contact_first_name
                ELSE first_name 
            END as first_name,
            CASE 
                WHEN user_type = 'corporate' THEN contact_last_name
                ELSE last_name 
            END as last_name,
            CASE 
                WHEN user_type = 'corporate' THEN contact_email
                ELSE email 
            END as email,
            CASE 
                WHEN user_type = 'corporate' THEN contact_phone
                ELSE phone 
            END as phone,
            user_type
        FROM users WHERE id = %s
        """
        
        cursor.execute(user_query, (booking_data['user_id'],))
        user_data = cursor.fetchone()
        
        if not user_data:
            return False
        
        customer_name = f"{user_data[0] or ''} {user_data[1] or ''}".strip()
        if not customer_name:
            customer_name = "User"
        
        # Create booking notes with details
        insurance_note = ""
        if booking_data.get('insurance_plan_id'):
            plans = get_insurance_plans()
            selected_plan = next((plan for plan in plans if plan['id'] == booking_data['insurance_plan_id']), None)
            if selected_plan:
                insurance_note = f"Insurance: {selected_plan['name']} (₦{selected_plan['price']}/month)"
        
        notes = f"Units: {booking_data['units_count']}, Duration: {duration_months} month(s). {insurance_note}"
        
        cursor.execute(insert_query, (
            booking_data['unit_id'],
            booking_data['user_id'],
            customer_name,
            user_data[2],  # email
            user_data[3],  # phone
            start_date,
            end_date,
            booking_data['total_amount'],
            'pending',
            'pending',
            notes
        ))
        
        connection.commit()
        return cursor.lastrowid
        
    except Error as e:
        print(f"Error creating user booking: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Create guest booking entry
def create_guest_booking(booking_data):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        # Create guest_bookings table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS guest_bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unit_id INT NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            session_id VARCHAR(255),
            customer_name VARCHAR(100),
            customer_email VARCHAR(100),
            customer_phone VARCHAR(20),
            units_count INT DEFAULT 1,
            insurance_plan_id INT,
            total_amount DECIMAL(10,2),
            duration INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
            INDEX idx_guest_ip (ip_address),
            INDEX idx_guest_session (session_id),
            INDEX idx_guest_expires (expires_at)
        )
        """
        cursor.execute(create_table_query)
        
        # Insert guest booking
        insert_query = """
        INSERT INTO guest_bookings 
        (unit_id, ip_address, session_id, customer_name, customer_email, customer_phone, 
         units_count, insurance_plan_id, total_amount, duration)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            booking_data['unit_id'],
            booking_data['ip_address'],
            booking_data['session_id'],
            booking_data.get('customer_name'),
            booking_data.get('customer_email'),
            booking_data.get('customer_phone'),
            booking_data['units_count'],
            booking_data.get('insurance_plan_id'),
            booking_data['total_amount'],
            booking_data.get('duration', 1)
        ))
        
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error creating guest booking: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Create responsive header component
def create_header():
    return html.Header([
        html.Div([
            html.Div([
                html.Img(src="./assets/images/logo.jpg", alt="CaelumSpace Logo", className="logo")
            ], className="logo-container"),
            
            html.Button([
                html.I(className="fas fa-bars")
            ], className="mobile-menu-toggle", id="mobile-menu-toggle"),
            
            html.Nav([
                html.Div([
                    html.A("Home", href="/home/", className="nav-link"),
                    html.A("Warehouse & Units", href="/units/", className="nav-link"),
                    html.A("About Us", href="/about/", className="nav-link"),
                    html.A("Our Services", href="/services/", className="nav-link"),
                    html.A("Contact Us", href="/contact/", className="nav-link"),
                    html.A([
                        html.I(className="fas fa-user-plus"),
                        html.Span("Signup")
                    ], href="/signup/", className="nav-link auth-link"),
                    html.A([
                        html.I(className="fas fa-sign-in-alt"),
                        html.Span("Login")
                    ], href="/login/", className="nav-link auth-link"),
                ], className="nav-links"),
                
                html.Button([
                    html.I(className="fas fa-times")
                ], className="mobile-menu-close", id="mobile-menu-close")
            ], className="nav-menu", id="nav-menu")
        ], className="header-container")
    ], className="main-header")

# Create footer
def create_footer():
    return html.Footer([
        html.Div([
            html.Div([
                html.Div([
                    html.H4("CaelumSpace"),
                    html.P("Premium storage solutions for modern living. Secure, accessible, and reliable.")
                ], className="footer-section"),
                html.Div([
                    html.H4("Quick Links"),
                    html.Ul([
                        html.Li(html.A("Find Units", href="/units/")),
                        html.Li(html.A("Pricing", href="/pricing/")),
                        html.Li(html.A("About Us", href="/about/")),
                        html.Li(html.A("Contact", href="/contact/"))
                    ])
                ], className="footer-section"),
                html.Div([
                    html.H4("Support"),
                    html.Ul([
                        html.Li(html.A("Help Center", href="/help/")),
                        html.Li(html.A("Privacy Policy", href="/privacy/")),
                        html.Li(html.A("Terms of Service", href="/terms/")),
                        html.Li(html.A("FAQ", href="/faq/"))
                    ])
                ], className="footer-section"),
                html.Div([
                    html.H4("Contact Info"),
                    html.P("📧 info@caelumspace.com"),
                    html.P("📞 +1 (555) 123-4567"),
                    html.P("📍 123 Storage Ave, City, State")
                ], className="footer-section")
            ], className="footer-container"),
            html.Div([
                html.P("© 2025 CaelumSpace. All rights reserved.")
            ], className="footer-bottom")
        ])
    ], className="main-footer")

# Create hero section
def create_hero_section(unit_data):
    if not unit_data:
        return html.Div("Unit not found", className="error-message")
    
    return html.Section([
        html.Div([
            html.Div([
                html.Nav([
                    html.A("Home", href="/home/", className="breadcrumb-link"),
                    html.Span(" > ", className="breadcrumb-separator"),
                    html.A("Units", href="/units/", className="breadcrumb-link"),
                    html.Span(" > ", className="breadcrumb-separator"),
                    html.Span(unit_data['unit_name'], className="breadcrumb-current")
                ], className="breadcrumb-nav"),
                
                html.H1(unit_data['unit_name'], className="unit-title"),
                html.Div([
                    html.Span([
                        html.I(className="fas fa-map-marker-alt"),
                        f" {unit_data['warehouse_name']} - {unit_data['warehouse_location']}"
                    ], className="unit-location"),
                    html.Span([
                        html.I(className="fas fa-check-circle" if unit_data['availability'] == 'not taken' else "fas fa-times-circle"),
                        f" {unit_data['availability'].replace('_', ' ').title()}"
                    ], className=f"unit-availability {'available' if unit_data['availability'] == 'not taken' else 'unavailable'}")
                ], className="unit-meta")
            ], className="hero-content")
        ], className="hero-container")
    ], className="unit-hero-section")

# Create warehouse visualization
def create_warehouse_visualization(warehouse_id, unit_id):
    units = get_warehouse_units(warehouse_id)
    
    # Create grid layout (adjust based on your warehouse layout preferences)
    grid_size = max(10, int(len(units) ** 0.5) + 1)  # Dynamic grid size
    
    visualization_grid = []
    for i, unit in enumerate(units):
        is_current = unit['id'] == int(unit_id)
        status_class = f"unit-cell {unit['booking_status']}"
        if is_current:
            status_class += " current-unit"
        
        cell = html.Div([
            html.Div(unit['unit_name'], className="unit-cell-name"),
            html.Div(unit['booking_status'].title(), className="unit-cell-status")
        ], 
        className=status_class,
        id=f"unit-cell-{unit['id']}",
        **{"data-unit-id": unit['id']})
        
        visualization_grid.append(cell)
    
    return html.Div([
        html.H3("Warehouse Unit Availability", className="visualization-title"),
        html.Div([
            html.Div([
                html.Span(className="legend-color available"),
                html.Span("Available", className="legend-text")
            ], className="legend-item"),
            html.Div([
                html.Span(className="legend-color booked"),
                html.Span("Booked", className="legend-text")
            ], className="legend-item"),
            html.Div([
                html.Span(className="legend-color unavailable"),
                html.Span("Unavailable", className="legend-text")
            ], className="legend-item"),
            html.Div([
                html.Span(className="legend-color current-unit"),
                html.Span("Current Unit", className="legend-text")
            ], className="legend-item")
        ], className="visualization-legend"),
        html.Div(visualization_grid, className="warehouse-grid")
    ], className="warehouse-visualization")

# Create main content area
def create_main_content(unit_data, unit_id):
    if not unit_data:
        return html.Div("Unit not found", className="error-message")
    
    # Warehouse image with fallback
    image_src = unit_data.get('warehouse_image') or 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    
    return html.Div([
        # Left Column (8 columns)
        html.Div([
            # Warehouse Image
            html.Div([
                html.Img(src=image_src, alt=f"{unit_data['warehouse_name']} Image", className="warehouse-main-image"),
                html.Div([
                    html.Button([html.I(className="fas fa-expand")], className="fullscreen-btn"),
                    html.Button([html.I(className="fas fa-heart")], className="favorite-btn", id="favorite-btn")
                ], className="image-overlay-controls")
            ], className="warehouse-image-container"),
            
            # Unit Info Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-toggle-on" if unit_data['warehouse_status'] == 'active' else "fas fa-toggle-off"),
                        html.Span("Warehouse Status", className="info-label"),
                        html.Span(unit_data['warehouse_status'].title(), className="info-value")
                    ], className="info-item"),
                    
                    html.Div([
                        html.I(className="fas fa-expand-arrows-alt"),
                        html.Span("Unit Size", className="info-label"),
                        html.Span("Large", className="info-value")  # You can make this dynamic
                    ], className="info-item"),
                    
                    html.Div([
                        html.I(className="fas fa-warehouse"),
                        html.Span("Warehouse", className="info-label"),
                        html.Span(unit_data['warehouse_name'], className="info-value")
                    ], className="info-item"),
                    
                    html.Div([
                        html.I(className="fas fa-tag"),
                        html.Span("Price", className="info-label"),
                        html.Span(f"₦{unit_data['price']}/month", className="info-value price")
                    ], className="info-item")
                ], className="unit-info-grid"),
                
                html.Button([
                    html.I(className="fas fa-bookmark"),
                    " Save Unit"
                ], className="save-unit-btn", id="save-unit-btn")
            ], className="unit-info-section"),
            
            # Unit Description
            html.Div([
                html.H3("Unit Description", className="section-title"),
                html.P([
                    f"This premium storage unit at {unit_data['warehouse_name']} offers secure and convenient storage solutions. ",
                    "Located in a prime area with excellent accessibility, this unit provides the perfect balance of security, ",
                    "convenience, and affordability. Whether you're storing household items, business inventory, or personal belongings, ",
                    "this unit offers the space and security you need."
                ], className="unit-description-text"),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-ruler-combined"),
                        html.Span("Large capacity storage space")
                    ], className="description-feature"),
                    html.Div([
                        html.I(className="fas fa-thermometer-half"),
                        html.Span("Climate controlled environment")
                    ], className="description-feature"),
                    html.Div([
                        html.I(className="fas fa-truck"),
                        html.Span("Easy loading and unloading access")
                    ], className="description-feature")
                ], className="description-features")
            ], className="unit-description-section"),
            
            # Unit Facilities
            html.Div([
                html.H3("Unit Facilities", className="section-title"),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-shield-alt"),
                        html.Span("24/7 Security Monitoring")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-key"),
                        html.Span("Access Code Enabled")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-video"),
                        html.Span("CCTV Surveillance")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-fire-extinguisher"),
                        html.Span("Fire Protection System")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-lightbulb"),
                        html.Span("LED Lighting")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-parking"),
                        html.Span("Parking Available")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-clock"),
                        html.Span("24/7 Access")
                    ], className="facility-item"),
                    html.Div([
                        html.I(className="fas fa-lock"),
                        html.Span("Individual Unit Locks")
                    ], className="facility-item")
                ], className="facilities-grid")
            ], className="facilities-section"),
            
            # Warehouse Visualization
            create_warehouse_visualization(unit_data['warehouse_id'], unit_id),
            
            # Location Map
            html.Div([
                html.H3("Location", className="section-title"),
                html.Div([
                    html.Div(id="location-map", className="location-map"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt"),
                            html.Span("Address", className="location-label"),
                            html.Span(unit_data['warehouse_location'], className="location-value")
                        ], className="location-detail"),
                        html.Div([
                            html.I(className="fas fa-route"),
                            html.Span("Directions", className="location-label"),
                            html.A("Get Directions", href=f"https://www.google.com/maps/search/{unit_data['warehouse_location']}", 
                                  target="_blank", className="directions-link")
                        ], className="location-detail")
                    ], className="location-info")
                ], className="location-container")
            ], className="location-section")
        ], className="main-content-left"),
        
        # Right Column (4 columns) - Booking Panel
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Book This Unit", className="booking-title"),
                    html.Div(f"₦{unit_data['price']}", className="booking-price-display"),
                    html.Span("per month", className="booking-price-period")
                ], className="booking-header"),
                
                # Booking Form
                html.Div([
                    # Number of Units
                    html.Div([
                        html.Label("Number of Units", className="booking-label"),
                        html.Div([
                            html.Button("-", className="quantity-btn", id="quantity-decrease"),
                            html.Span("1", className="quantity-display", id="quantity-display"),
                            html.Button("+", className="quantity-btn", id="quantity-increase")
                        ], className="quantity-controls")
                    ], className="booking-field"),
                    
                    # Insurance Plan
                    html.Div([
                        html.Label("Insurance Plan (Optional)", className="booking-label"),
                        dcc.Dropdown(
                            id="insurance-dropdown",
                            options=[{'label': 'No Insurance', 'value': 0}] + 
                                   [{'label': f"{plan['name']} - ₦{plan['price']}/month", 'value': plan['id']} 
                                    for plan in get_insurance_plans()],
                            value=0,
                            className="insurance-dropdown"
                        ),
                        html.Div(id="insurance-description", className="insurance-description")
                    ], className="booking-field"),
                    
                    # Duration (Optional - for future enhancement)
                    html.Div([
                        html.Label("Rental Duration", className="booking-label"),
                        dcc.Dropdown(
                            id="duration-dropdown",
                            options=[
                                {'label': '1 Month', 'value': 1},
                                {'label': '3 Months', 'value': 3},
                                {'label': '6 Months', 'value': 6},
                                {'label': '12 Months', 'value': 12}
                            ],
                            value=1,
                            className="duration-dropdown"
                        )
                    ], className="booking-field"),
                    
                    # Booking Summary
                    html.Div([
                        html.H4("Booking Summary", className="summary-title"),
                        html.Div([
                            html.Div([
                                html.Span("Unit Price:", className="summary-label"),
                                html.Span(f"₦{unit_data['price']}", className="summary-value", id="unit-price-summary")
                            ], className="summary-row"),
                            html.Div([
                                html.Span("Quantity:", className="summary-label"),
                                html.Span("1", className="summary-value", id="quantity-summary")
                            ], className="summary-row"),
                            html.Div([
                                html.Span("Insurance:", className="summary-label"),
                                html.Span("₦0", className="summary-value", id="insurance-summary")
                            ], className="summary-row"),
                            html.Hr(className="summary-divider"),
                            html.Div([
                                html.Span("Total Monthly:", className="summary-label total"),
                                html.Span(f"₦{unit_data['price']}", className="summary-value total", id="total-summary")
                            ], className="summary-row total-row")
                        ], className="booking-summary")
                    ], className="summary-section"),
                    
                    # Book Now Button
                    html.Button([
                        html.I(className="fas fa-calendar-check"),
                        " Book Now"
                    ], className="book-now-btn", id="book-now-btn"),
                    
                    # Additional Actions
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-phone"),
                            " Call for Info"
                        ], className="secondary-btn"),
                        html.Button([
                            html.I(className="fas fa-share-alt"),
                            " Share Unit"
                        ], className="secondary-btn", id="share-btn")
                    ], className="additional-actions")
                ], className="booking-form")
            ], className="booking-panel")
        ], className="main-content-right")
    ], className="main-content-container")

# Create unit details layout
def create_unit_details_layout(unit_id):
    unit_data = get_unit_details(unit_id)
    
    return html.Div([
        create_header(),
        create_hero_section(unit_data),
        create_main_content(unit_data, unit_id),
        create_footer(),
        
        # Store unit data for callbacks
        dcc.Store(id="unit-data-store", data=unit_data),
        dcc.Store(id="booking-calculation-store", data={
            'base_price': unit_data['price'] if unit_data else 0,
            'quantity': 1,
            'insurance_price': 0,
            'total': unit_data['price'] if unit_data else 0
        }),
        # Store for booking ID to trigger redirect
        dcc.Store(id="booking-id-store", data=None),
        # Location component for handling redirects
        dcc.Location(id="redirect-location", refresh=True),
        
        # Map initialization script
        html.Script(f"""
        document.addEventListener('DOMContentLoaded', function() {{
            // Initialize map
            if (typeof L !== 'undefined') {{
                var map = L.map('location-map').setView([6.2088, 6.9915], 13);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);
                
                // Add marker for warehouse location
                L.marker([6.2088, 6.9915]).addTo(map)
                    .bindPopup('{unit_data["warehouse_name"] if unit_data else "Warehouse Location"}')
                    .openPopup();
            }}
        }});
        """)
    ])

# Set the layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# URL routing callback
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname and pathname.startswith('/unit_details/'):
        # Extract unit ID from URL
        unit_id = pathname.split('/')[-1]
        if unit_id.isdigit():
            return create_unit_details_layout(int(unit_id))
    
    return html.Div([
        html.H1("Unit Not Found"),
        html.P("The requested unit could not be found."),
        html.A("Back to Units", href="/units/", className="btn btn-primary")
    ], className="error-page")

# Quantity controls callback
@app.callback(
    [Output('quantity-display', 'children'),
     Output('quantity-summary', 'children')],
    [Input('quantity-increase', 'n_clicks'),
     Input('quantity-decrease', 'n_clicks')],
    [State('quantity-display', 'children')],
    prevent_initial_call=True
)
def update_quantity(increase_clicks, decrease_clicks, current_quantity):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_quantity, current_quantity
    
    current_qty = int(current_quantity)
    
    if ctx.triggered[0]['prop_id'] == 'quantity-increase.n_clicks':
        new_qty = min(current_qty + 1, 10)  # Max 10 units
    elif ctx.triggered[0]['prop_id'] == 'quantity-decrease.n_clicks':
        new_qty = max(current_qty - 1, 1)  # Min 1 unit
    else:
        new_qty = current_qty
    
    return str(new_qty), str(new_qty)

# Insurance description callback
@app.callback(
    Output('insurance-description', 'children'),
    [Input('insurance-dropdown', 'value')]
)
def update_insurance_description(insurance_id):
    if not insurance_id or insurance_id == 0:
        return ""
    
    plans = get_insurance_plans()
    selected_plan = next((plan for plan in plans if plan['id'] == insurance_id), None)
    
    if selected_plan:
        return html.Div([
            html.I(className="fas fa-info-circle"),
            html.Span(selected_plan['description'])
        ], className="insurance-desc-text")
    return ""

# Booking calculation callback
@app.callback(
    [Output('unit-price-summary', 'children'),
     Output('insurance-summary', 'children'),
     Output('total-summary', 'children'),
     Output('booking-calculation-store', 'data')],
    [Input('quantity-display', 'children'),
     Input('insurance-dropdown', 'value'),
     Input('duration-dropdown', 'value')],
    [State('unit-data-store', 'data')],
    prevent_initial_call=True
)
def calculate_booking_total(quantity, insurance_id, duration, unit_data):
    if not unit_data:
        return "₦0", "₦0", "₦0", {}
    
    base_price = unit_data['price']
    qty = int(quantity)
    
    # Get insurance price
    insurance_price = 0
    if insurance_id and insurance_id != 0:
        plans = get_insurance_plans()
        selected_plan = next((plan for plan in plans if plan['id'] == insurance_id), None)
        if selected_plan:
            insurance_price = selected_plan['price']
    
    # Calculate totals
    unit_total = base_price * qty
    insurance_total = insurance_price * qty
    monthly_total = unit_total + insurance_total
    
    calculation_data = {
        'base_price': base_price,
        'quantity': qty,
        'insurance_price': insurance_price,
        'unit_total': unit_total,
        'insurance_total': insurance_total,
        'monthly_total': monthly_total,
        'duration': duration,
        'total_amount': monthly_total * duration
    }
    
    return (
        f"₦{unit_total:,.0f}",
        f"₦{insurance_total:,.0f}",
        f"₦{monthly_total:,.0f}",
        calculation_data
    )

# Book now callback with proper redirect handling
@app.callback(
    [Output('book-now-btn', 'children'),
     Output('book-now-btn', 'disabled'),
     Output('booking-id-store', 'data')],
    [Input('book-now-btn', 'n_clicks')],
    [State('unit-data-store', 'data'),
     State('booking-calculation-store', 'data'),
     State('insurance-dropdown', 'value'),
     State('duration-dropdown', 'value')],
    prevent_initial_call=True
)
def handle_book_now(n_clicks, unit_data, calculation_data, insurance_id, duration):
    if not n_clicks or not unit_data:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Check if user is logged in
    user_id = session.get('user_id')
    user_logged_in = user_id is not None
    
    if user_logged_in:
        # Create booking record for logged-in user
        booking_data = {
            'unit_id': unit_data['id'],
            'user_id': user_id,
            'units_count': calculation_data.get('quantity', 1),
            'insurance_plan_id': insurance_id if insurance_id != 0 else None,
            'total_amount': calculation_data.get('total_amount', calculation_data.get('monthly_total', 0)),
            'duration': duration
        }
        
        booking_id = create_user_booking(booking_data)
        
        if booking_id:
            # Store booking ID in session for the booking confirmation page
            session['current_booking_id'] = booking_id
            
            # Return booking ID to trigger redirect
            return [
                html.I(className="fas fa-check-circle"),
                " Booking Created - Redirecting..."
            ], True, booking_id
        else:
            return [
                html.I(className="fas fa-exclamation-triangle"),
                " Error Creating Booking"
            ], False, None
    else:
        # Create guest booking and redirect to login/guest booking page
        guest_booking_data = {
            'unit_id': unit_data['id'],
            'ip_address': request.environ.get('REMOTE_ADDR', '127.0.0.1'),
            'session_id': session.get('session_id', secrets.token_urlsafe(32)),
            'units_count': calculation_data.get('quantity', 1),
            'insurance_plan_id': insurance_id if insurance_id != 0 else None,
            'total_amount': calculation_data.get('total_amount', calculation_data.get('monthly_total', 0)),
            'duration': duration
        }
        
        guest_booking_id = create_guest_booking(guest_booking_data)
        
        if guest_booking_id:
            # Store guest booking ID in session
            session['guest_booking_id'] = guest_booking_id
            # Return guest booking ID with login flag
            return [
                html.I(className="fas fa-user-plus"),
                " Login to Complete Booking"
            ], False, f"guest_{guest_booking_id}"
        else:
            return [
                html.I(className="fas fa-exclamation-triangle"),
                " Error - Try Again"
            ], False, None

# Redirect callback - handles the actual page redirect
@app.callback(
    Output('redirect-location', 'href'),
    [Input('booking-id-store', 'data')],
    prevent_initial_call=True
)
def handle_redirect(booking_id):
    if not booking_id:
        return dash.no_update
    
    # Check if it's a guest booking
    if str(booking_id).startswith('guest_'):
        # Redirect to login page with booking context
        return "/login/?redirect=booking&booking_type=guest"
    else:
        # Redirect to booking confirmation page for logged-in users
        return f"/book_now/{booking_id}"

# Save unit callback
@app.callback(
    Output('save-unit-btn', 'children'),
    [Input('save-unit-btn', 'n_clicks')],
    [State('unit-data-store', 'data')],
    prevent_initial_call=True
)
def save_unit(n_clicks, unit_data):
    if not n_clicks:
        return dash.no_update
    
    # Here you would implement saving to user's favorites
    # For now, just show feedback
    return [
        html.I(className="fas fa-check"),
        " Unit Saved!"
    ]

# Favorite button callback
@app.callback(
    Output('favorite-btn', 'className'),
    [Input('favorite-btn', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_favorite(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        return "favorite-btn favorited"
    return "favorite-btn"

# Share button callback
@app.callback(
    Output('share-btn', 'children'),
    [Input('share-btn', 'n_clicks')],
    prevent_initial_call=True
)
def share_unit(n_clicks):
    if not n_clicks:
        return dash.no_update
    
    # Show temporary feedback
    return [
        html.I(className="fas fa-check"),
        " Link Copied!"
    ]

# Mobile menu toggle callback
@app.callback(
    Output('nav-menu', 'className'),
    [Input('mobile-menu-toggle', 'n_clicks'),
     Input('mobile-menu-close', 'n_clicks')],
    [State('nav-menu', 'className')],
    prevent_initial_call=True
)
def toggle_mobile_menu(toggle_clicks, close_clicks, current_class):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# Optional: Add a client-side callback to show loading state during redirect
app.clientside_callback(
    """
    function(booking_id) {
        if (booking_id) {
            // Show a loading overlay or message
            setTimeout(function() {
                if (booking_id.toString().startsWith('guest_')) {
                    console.log('Redirecting to login page for guest booking...');
                } else {
                    console.log('Redirecting to booking confirmation page...');
                }
            }, 1000);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('book-now-btn', 'title'),  # Dummy output
    Input('booking-id-store', 'data')
)
