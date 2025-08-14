import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta, date
import hashlib
import secrets
import pyodbc
import re
from flask import session
import logging
import mysql.connector
from mysql.connector import Error

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/units/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)

# Custom CSS integrated into app.index_string
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        .intro-filter-title {
        font-size: 1.8rem;
        padding: 1rem 1.5rem;
    }/* Date Picker Container */
.date-picker-container {
    display: flex;
    gap: 1rem;
    align-items: center;
    position: relative;
    z-index: 1000;
}

.date-picker-input {
    flex: 1;
    position: relative;
    z-index: 1000;
}/* Advanced Storage Units UI - Professional CSS */

/* Filter Section */
.filter-section {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 3rem 0;
    margin-bottom: 4rem;
    position: relative;
    overflow: visible;
    z-index: 10;
}

.filter-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" patternUnits="userSpaceOnUse" width="100" height="100"><circle cx="50" cy="50" r="0.5" fill="%23FFD700" opacity="0.03"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    pointer-events: none;
}

.filter-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    position: relative;
    z-index: 1;
}

/* Banner/Intro Title Styling */
.intro-filter-title {
    color: #FFD700;
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
    letter-spacing: -0.5px;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2;
    background: rgba(26, 26, 26, 0.7);
    padding: 2rem 4rem;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 215, 0, 0.3);
}

.intro-filter-title::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #FFD700, transparent, #FFD700);
    border-radius: 18px;
    z-index: -1;
    opacity: 0.5;
    animation: borderGlow 3s ease-in-out infinite alternate;
}

@keyframes borderGlow {
    0% { opacity: 0.3; }
    100% { opacity: 0.7; }
}

.filter-controls-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
    align-items: end;
}

.date-filter-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2rem;
    align-items: end;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.search-group {
    position: relative;
}

.date-group {
    position: relative;
}

.filter-label {
    color: #FFD700;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.filter-input {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-size: 1rem;
    color: #1a1a1a;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.search-input {
    padding-left: 3rem;
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%23666" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>');
    background-repeat: no-repeat;
    background-position: 1rem center;
    background-size: 1.2rem;
}

.filter-input:focus {
    outline: none;
    border-color: #FFD700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1), 0 8px 32px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.filter-input::placeholder {
    color: #999;
    font-style: italic;
}

/* Dropdown Styling */
.filter-dropdown .Select-control {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px);
    min-height: 52px !important;
}

.filter-dropdown .Select-control:hover,
.filter-dropdown .Select-control.is-focused {
    border-color: #FFD700 !important;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1), 0 8px 32px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-2px);
}

.filter-dropdown .Select-placeholder {
    color: #999 !important;
    font-style: italic;
}

.filter-dropdown .Select-value-label {
    color: #1a1a1a !important;
    font-weight: 500;
}

.filter-dropdown .Select-arrow-zone {
    padding: 0 1rem !important;
}

.filter-dropdown .Select-menu-outer {
    border: 2px solid #FFD700 !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
    backdrop-filter: blur(20px);
    margin-top: 4px !important;
}

.filter-dropdown .Select-option {
    padding: 1rem 1.25rem !important;
    background: rgba(255, 255, 255, 0.95) !important;
    color: #1a1a1a !important;
    font-weight: 500;
    transition: all 0.2s ease !important;
}

.filter-dropdown .Select-option:hover,
.filter-dropdown .Select-option.is-focused {
    background: #FFD700 !important;
    color: #1a1a1a !important;
}

/* Date Picker and Dropdown Z-index fixes */
.filter-dropdown .Select-menu-outer {
    border: 2px solid #FFD700 !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
    backdrop-filter: blur(20px);
    margin-top: 4px !important;
    z-index: 9999 !important;
    position: relative !important;
}

.DateInput_input {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    font-size: 1rem !important;
    color: #1a1a1a !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px);
    z-index: 9999 !important;
}

.DateRangePickerInput,
.SingleDatePickerInput {
    position: relative !important;
    z-index: 9999 !important;
}

.DateRangePickerInput__withBorder,
.SingleDatePickerInput__withBorder {
    border: none !important;
}

.DayPickerKeyboardShortcuts_panel {
    z-index: 10000 !important;
}

.DateRangePicker,
.SingleDatePicker {
    z-index: 10000 !important;
}

.DayPicker {
    z-index: 10000 !important;
}

.DateInput_input:focus {
    outline: none !important;
    border-color: #FFD700 !important;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1), 0 8px 32px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-2px);
}

.clear-date-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 215, 0, 0.3);
    color: #FFD700;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.clear-date-btn:hover {
    background: rgba(255, 215, 0, 0.1);
    border-color: #FFD700;
    transform: translateY(-1px);
}

.date-availability-info {
    background: rgba(255, 215, 0, 0.1);
    border: 1px solid rgba(255, 215, 0, 0.3);
    border-radius: 8px;
    padding: 1rem;
    color: #FFD700;
    font-size: 0.9rem;
    margin-top: 1rem;
    backdrop-filter: blur(10px);
}

/* Stats Cards */
.filter-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 215, 0, 0.2);
    max-width: 1400px;
    margin-left: auto;
    margin-right: auto;
    padding-left: 2rem;
    padding-right: 2rem;
}

.stat-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem 1.5rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 215, 0, 0.1);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #FFD700, transparent);
    transition: left 0.5s ease;
}

.stat-card:hover::before {
    left: 100%;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 215, 0, 0.3);
}

.stat-number {
    display: block;
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Units Grid Container */
.units-grid-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem 4rem;
}

/* Units Grid */
.units-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 2.5rem;
    margin-top: 3rem;
}

.unit-card {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(0, 0, 0, 0.05);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    backdrop-filter: blur(10px);
}

.unit-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #FFD700, #FFA500, #FFD700);
    transform: scaleX(0);
    transition: transform 0.4s ease;
}

.unit-card:hover::before {
    transform: scaleX(1);
}

.unit-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 215, 0, 0.2);
}

.unit-image-container {
    position: relative;
    overflow: hidden;
    height: 240px;
    background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
}

.unit-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.unit-card:hover .unit-image {
    transform: scale(1.08);
}

.unit-image-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.1));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.unit-card:hover .unit-image-container::after {
    opacity: 1;
}

.unit-info {
    padding: 2rem;
    background: white;
    position: relative;
}

.unit-price {
    font-size: 1.6rem;
    font-weight: 800;
    color: #FFD700;
    margin-bottom: 0.75rem;
    text-shadow: 0 2px 4px rgba(255, 215, 0, 0.2);
    position: relative;
}

.unit-price::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 40px;
    height: 2px;
    background: #FFD700;
    border-radius: 1px;
}

.unit-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.75rem;
    line-height: 1.3;
    letter-spacing: -0.3px;
}

.unit-location {
    color: #666;
    margin-bottom: 1.25rem;
    font-size: 1rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.unit-location::before {
    content: '📍';
    font-size: 0.9rem;
}

.unit-status {
    position: absolute;
    top: 1rem;
    right: 1rem;
    display: inline-flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.95);
    color: #2d5a2d;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid rgba(45, 90, 45, 0.2);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 2;
}

.unit-status::before {
    content: '●';
    color: #4CAF50;
    font-size: 0.8rem;
    margin-right: 0.5rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.unit-details-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
    color: white;
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 140px;
}

.unit-details-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
}

.unit-details-btn:hover::before {
    left: 100%;
}

.unit-details-btn:hover {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: #1a1a1a;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.unit-details-btn::after {
    content: '→';
    margin-left: 0.5rem;
    transition: transform 0.3s ease;
}

.unit-details-btn:hover::after {
    transform: translateX(4px);
}

/* No Units Message */
.no-units-message {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
    font-size: 1.1rem;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 16px;
    border: 2px dashed rgba(255, 215, 0, 0.3);
    backdrop-filter: blur(10px);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .filter-controls-row {
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }
    
    .units-container {
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 2rem;
    }
}

@media (max-width: 768px) {
    .filter-container {
        padding: 0 1rem;
    }
    
    .filter-controls-row {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .date-filter-row {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .filter-stats {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .units-container {
        grid-template-columns: 1fr;
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .unit-card {
        margin: 0 auto;
        max-width: 400px;
    }
    
    .unit-info {
        padding: 1.5rem;
    }
    
    .intro-filter-title {
        font-size: 2.2rem;
        padding: 1.5rem 2rem;
    }
}

@media (max-width: 480px) {
    .filter-section {
        padding: 2rem 0;
    }
    
    .units-grid-container {
        padding: 0 1rem 2rem;
    }
    
    .unit-image-container {
        height: 200px;
    }
    
    .stat-card {
        padding: 1.5rem 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
    }
}

/* Loading States */
.filter-input:disabled,
.filter-dropdown.is-disabled .Select-control {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Focus Indicators for Accessibility */
.unit-details-btn:focus {
    outline: 3px solid rgba(255, 215, 0, 0.5);
    outline-offset: 2px;
}

/* Print Styles */
@media print {
    .filter-section {
        background: white !important;
        color: black !important;
    }
    
    .unit-card {
        break-inside: avoid;
        box-shadow: none !important;
        border: 1px solid #ccc !important;
    }
}

          /* Add CSS to prevent scroll jumping */
            html {
                scroll-behavior: smooth;
            }
            .nav-menu.mobile-active {
                display: block !important;
            }
            @media (max-width: 768px) {
                .nav-menu {
                    display: none;
                }
            }
            .date-availability-indicator {
                position: absolute;
                top: 2px;
                right: 2px;
                background: #28a745;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                font-size: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .date-unavailable .date-availability-indicator {
                background: #dc3545;
            }
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

            /* Hero Section */
            .hero-section {
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }

            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.4);
                z-index: 1;
            }

            .hero-container {
                position: relative;
                z-index: 2;
                text-align: center;
                color: white;
                max-width: 800px;
                padding: 0 2rem;
            }

            .hero-title {
                font-size: clamp(2.5rem, 5vw, 4rem);
                font-weight: 700;
                margin-bottom: 1.5rem;
                letter-spacing: -0.02em;
            }

            .hero-subtitle {
                font-size: 1.2rem;
                margin-bottom: 2.5rem;
                opacity: 0.9;
                font-weight: 400;
            }

            
            .secondary-button {
                display: inline-block;
                background: transparent;
                color: #1a1a1a;
                padding: 1rem 2rem;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                border: 2px solid #1a1a1a;
                transition: all 0.3s ease;
                margin-left: 1rem;
            }

            .secondary-button:hover {
                background: #1a1a1a;
                color: white;
                transform: translateY(-2px);
            }

            /* Section Styles */
            .section-title {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 700;
                text-align: center;
                margin-bottom: 1rem;
                color: #1a1a1a;
                letter-spacing: -0.02em;
            }

            .section-subtitle {
                font-size: 1.1rem;
                text-align: center;
                margin-bottom: 4rem;
                color: #666;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }

            .services-section, .units-section, .how-it-works, .blog-section, .faq-section {
                padding: 6rem 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }

            

            /* Units Grid */
            .units-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 2rem;
                margin-top: 3rem;
            }

            .unit-card {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }

            .unit-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
            }

            .unit-image-container {
                position: relative;
                overflow: hidden;
                height: 220px;
            }

            .unit-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }

            .unit-card:hover .unit-image {
                transform: scale(1.05);
            }

            .unit-info {
                padding: 1.5rem;
            }

            .unit-price {
                font-size: 1.4rem;
                font-weight: 700;
                color: #FFD700;
                margin-bottom: 0.5rem;
            }

            .unit-name {
                font-size: 1.2rem;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
            }

            .unit-location {
                color: #666;
                margin-bottom: 1rem;
                font-size: 0.95rem;
            }

            .unit-status {
                display: inline-block;
                background: #e8f5e8;
                color: #2d5a2d;
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
                margin-bottom: 1rem;
            }

            .unit-details-btn {
                display: inline-block;
                background: #1a1a1a;
                color: white;
                padding: 0.7rem 1.5rem;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .unit-details-btn:hover {
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

            /* Mobile Responsive */
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

                .hero-container {
                    padding: 0 1rem;
                }

                .services-section, .units-section, .how-it-works, .blog-section, .faq-section {
                    padding: 4rem 1rem;
                }

                .units-container {
                    grid-template-columns: 1fr;
                }

                .services-container {
                    grid-template-columns: 1fr;
                }

                .steps-container {
                    grid-template-columns: 1fr;
                }

                .blog-container {
                    grid-template-columns: 1fr;
                }

                .secondary-button {
                    margin-left: 0;
                    margin-top: 1rem;
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

            .units-page {
                min-height: calc(100vh - 80px);
                padding: 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }

            .no-units-message {
                text-align: center;
                color: #666;
                font-size: 1.1rem;
                padding: 3rem;
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

            .service-card, .unit-card, .blog-card, .step-card {
                animation: fadeInUp 0.6s ease-out;
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

                // FAQ toggle functionality
                const faqToggles = document.querySelectorAll('.faq-toggle');
                faqToggles.forEach(toggle => {
                    toggle.addEventListener('click', function() {
                        const target = this.getAttribute('data-target');
                        const answer = document.getElementById(target);
                        const icon = this.querySelector('i');
                        
                        if (answer.style.display === 'block') {
                            answer.style.display = 'none';
                            icon.className = 'fas fa-plus';
                        } else {
                            answer.style.display = 'block';
                            icon.className = 'fas fa-minus';
                        }
                    });
                });
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

# Enhanced function to get available units with date filtering
def get_available_units(search_term=None, warehouse_filter=None, price_range=None, sort_by=None, selected_date=None):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Base query to get unit details with warehouse information
        base_query = """
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
            w.image_path as warehouse_image
        FROM units u
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE u.status = 'active' AND w.status = 'active'
        """
        
        conditions = []
        params = []
        
        # If date is selected, check for bookings on that date
        if selected_date:
            base_query = """
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
                w.image_path as warehouse_image
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            LEFT JOIN bookings b ON u.id = b.unit_id 
                AND b.status IN ('confirmed', 'pending')
                AND %s BETWEEN b.start_date AND b.end_date
            WHERE u.status = 'active' AND w.status = 'active' 
                AND u.availability = 'not taken'
                AND b.id IS NULL
            """
            params.append(selected_date)
        else:
            conditions.append("u.availability = 'not taken'")
        
        # Add search filter
        if search_term:
            conditions.append("(u.name LIKE %s OR w.name LIKE %s OR w.location LIKE %s)")
            search_param = f"%{search_term}%"
            params.extend([search_param, search_param, search_param])
        
        # Add warehouse filter
        if warehouse_filter and warehouse_filter != 'all':
            conditions.append("w.id = %s")
            params.append(warehouse_filter)
        
        # Add price range filter
        if price_range and price_range != 'all':
            if price_range == '0-100':
                conditions.append("u.price BETWEEN 0 AND 100")
            elif price_range == '100-500':
                conditions.append("u.price BETWEEN 100 AND 500")
            elif price_range == '500-1000':
                conditions.append("u.price BETWEEN 500 AND 1000")
            elif price_range == '1000+':
                conditions.append("u.price > 1000")
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Add sorting
        if sort_by == 'price_low':
            base_query += " ORDER BY u.price ASC"
        elif sort_by == 'price_high':
            base_query += " ORDER BY u.price DESC"
        elif sort_by == 'name':
            base_query += " ORDER BY u.name ASC"
        elif sort_by == 'warehouse':
            base_query += " ORDER BY w.name ASC"
        elif sort_by == 'location':
            base_query += " ORDER BY w.location ASC"
        else:
            base_query += " ORDER BY u.created_at DESC"
        
        cursor.execute(base_query, params)
        units = cursor.fetchall()
        
        return units
        
    except Error as e:
        print(f"Error fetching units: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Get warehouse list for filter dropdown
def get_warehouses():
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM warehouses WHERE status = 'active' ORDER BY name")
        warehouses = cursor.fetchall()
        return warehouses
    except Error as e:
        print(f"Error fetching warehouses: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Get available units count for a specific date
def get_units_available_on_date(target_date):
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor()
        
        # Count units that are not booked on the target date
        query = """
        SELECT COUNT(*) as available_count
        FROM units u
        JOIN warehouses w ON u.warehouse_id = w.id
        LEFT JOIN bookings b ON u.id = b.unit_id 
            AND b.status IN ('confirmed', 'pending')
            AND %s BETWEEN b.start_date AND b.end_date
        WHERE u.status = 'active' 
            AND w.status = 'active' 
            AND u.availability = 'not taken'
            AND b.id IS NULL
        """
        
        cursor.execute(query, (target_date,))
        result = cursor.fetchone()
        return result[0] if result else 0
        
    except Error as e:
        print(f"Error getting available units for date: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Create responsive header component (same as original)
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
                    html.A("About Us", href="/about_us/", className="nav-link"),
                    html.A("Newsroom", href="/newsroom/", className="nav-link"),
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

# Create footer (same as original)
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

# Create compact intro banner
def create_units_intro():
    return html.Section([
        html.Div([
            html.H1("Browse Storage Units", className="units-page-title"),
             # html.H3("Filter & Sort Units", className="filter-title"),
            html.P("Find the perfect storage solution for your needs", className="units-page-subtitle")
        ], className="units-intro-content")
    ], className="units-intro-section", 
    style={
        "backgroundImage": "url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')",
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "backgroundRepeat": "no-repeat",
        "height": "300px"
    })

# Create advanced filter section
def create_filter_section():
    warehouses = get_warehouses()
    warehouse_options = [{'label': 'All Warehouses', 'value': 'all'}]
    warehouse_options.extend([{'label': w['name'], 'value': w['id']} for w in warehouses])
    
    return html.Section([
        html.Div([
            
            # Filter Controls Row
            html.Div([
                # Search Input
                html.Div([
                    html.Label("Search Units", className="filter-label"),
                    dcc.Input(
                        id="search-input",
                        type="text",
                        placeholder="Search by unit name, warehouse, or location...",
                        className="filter-input search-input",
                        debounce=True
                    )
                ], className="filter-group search-group"),
                
                # Warehouse Filter
                html.Div([
                    html.Label("Warehouse", className="filter-label"),
                    dcc.Dropdown(
                        id="warehouse-filter",
                        options=warehouse_options,
                        value='all',
                        className="filter-dropdown"
                    )
                ], className="filter-group"),
                
                # Price Range Filter
                html.Div([
                    html.Label("Price Range", className="filter-label"),
                    dcc.Dropdown(
                        id="price-filter",
                        options=[
                            {'label': 'All Prices', 'value': 'all'},
                            {'label': '₦0 - ₦100', 'value': '0-100'},
                            {'label': '₦100 - ₦500', 'value': '100-500'},
                            {'label': '₦500 - ₦1,000', 'value': '500-1000'},
                            {'label': '₦1,000+', 'value': '1000+'}
                        ],
                        value='all',
                        className="filter-dropdown"
                    )
                ], className="filter-group"),
                
                # Sort By
                html.Div([
                    html.Label("Sort By", className="filter-label"),
                    dcc.Dropdown(
                        id="sort-filter",
                        options=[
                            {'label': 'Newest First', 'value': 'newest'},
                            {'label': 'Price: Low to High', 'value': 'price_low'},
                            {'label': 'Price: High to Low', 'value': 'price_high'},
                            {'label': 'Unit Name A-Z', 'value': 'name'},
                            {'label': 'Warehouse Name', 'value': 'warehouse'},
                            {'label': 'Location', 'value': 'location'}
                        ],
                        value='newest',
                        className="filter-dropdown"
                    )
                ], className="filter-group")
            ], className="filter-controls-row"),
            
            # Date Picker Row
            html.Div([
                html.Div([
                    html.Label("Check Availability for Specific Date", className="filter-label"),
                    html.Div([
                        dcc.DatePickerSingle(
                            id="date-picker",
                            placeholder="Select a date to check availability",
                            display_format="YYYY-MM-DD",
                            style={"width": "100%"},
                            className="date-picker-input"
                        ),
                        html.Button([
                            html.I(className="fas fa-times"),
                            " Clear Date"
                        ], id="clear-date-btn", className="clear-date-btn", style={"display": "none"})
                    ], className="date-picker-container")
                ], className="filter-group date-group"),
                
                # Date availability info
                html.Div(id="date-availability-info", className="date-availability-info")
            ], className="date-filter-row")
        ], className="filter-container")
    ], className="filter-section")

# Create stats cards
def create_stats_cards():
    return html.Div([
        html.Div([
            html.Span("0", className="stat-number", id="total-units-stat"),
            html.Span("Available Units", className="stat-label")
        ], className="stat-card"),
        
        html.Div([
            html.Span("0", className="stat-number", id="warehouses-stat"),
            html.Span("Warehouses", className="stat-label")
        ], className="stat-card"),
        
        html.Div([
            html.Span("₦0", className="stat-number", id="avg-price-stat"),
            html.Span("Avg. Price", className="stat-label")
        ], className="stat-card"),
        
        html.Div([
            html.Span("0", className="stat-number", id="total-available-stat"),
            html.Span("Total Available", className="stat-label")
        ], className="stat-card")
    ], className="filter-stats", id="filter-stats")

# Create units grid
def create_units_grid():
    return html.Div([
        html.Div(id="units-grid", className="units-container"),
        html.Div(id="no-units-message", style={"display": "none"}, className="no-units-message")
    ], className="units-grid-container")

# Main units page layout
def create_units_layout():
    return html.Div([
        create_header(),
        create_units_intro(),
        create_filter_section(),
        create_stats_cards(),
        create_units_grid(),
        create_footer()
    ])

# Set the layout
app.layout = create_units_layout()

# Mobile menu toggle callback
@app.callback(
    Output('nav-menu', 'className'),
    [Input('mobile-menu-toggle', 'n_clicks'),
     Input('mobile-menu-close', 'n_clicks')],
    [State('nav-menu', 'className')],
    prevent_initial_call=True
)
def toggle_mobile_menu(toggle_clicks, close_clicks, current_class):
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# Clear date button visibility callback
@app.callback(
    Output('clear-date-btn', 'style'),
    [Input('date-picker', 'date')],
    prevent_initial_call=True
)
def toggle_clear_date_btn(selected_date):
    if selected_date:
        return {"display": "inline-flex"}
    return {"display": "none"}

# Clear date callback
@app.callback(
    Output('date-picker', 'date'),
    [Input('clear-date-btn', 'n_clicks')],
    prevent_initial_call=True
)
def clear_date(n_clicks):
    if n_clicks:
        return None
    return dash.no_update

# Date availability info callback
@app.callback(
    Output('date-availability-info', 'children'),
    [Input('date-picker', 'date')],
    prevent_initial_call=True
)
def update_date_availability_info(selected_date):
    if not selected_date:
        return ""
    
    available_count = get_units_available_on_date(selected_date)
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    formatted_date = selected_date_obj.strftime('%B %d, %Y')
    
    if available_count > 0:
        return html.Div([
            html.I(className="fas fa-check-circle", style={"color": "#28a745", "marginRight": "8px"}),
            html.Span(f"{available_count} units available on {formatted_date}")
        ], className="availability-info success")
    else:
        return html.Div([
            html.I(className="fas fa-exclamation-circle", style={"color": "#dc3545", "marginRight": "8px"}),
            html.Span(f"No units available on {formatted_date}")
        ], className="availability-info warning")

# Main callback for updating units and stats
@app.callback(
    [Output('units-grid', 'children'),
     Output('no-units-message', 'children'),
     Output('no-units-message', 'style'),
     Output('total-units-stat', 'children'),
     Output('warehouses-stat', 'children'),
     Output('avg-price-stat', 'children'),
     Output('total-available-stat', 'children')],
    [Input('search-input', 'value'),
     Input('warehouse-filter', 'value'),
     Input('price-filter', 'value'),
     Input('sort-filter', 'value'),
     Input('date-picker', 'date')]
)
def update_units_and_stats(search_term, warehouse_filter, price_filter, sort_by, selected_date):
    # Get filtered units
    units = get_available_units(search_term, warehouse_filter, price_filter, sort_by, selected_date)
    
    # Get total available units (without filters for comparison)
    all_units = get_available_units()
    
    # Create unit cards
    unit_cards = []
    for unit in units:
        # Use warehouse image or fallback
        image_src = unit.get('warehouse_image', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80')
        if not image_src or image_src.strip() == '':
            image_src = 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80'
            
        unit_cards.append(
            html.Div([
                html.Div([
                    html.Img(src=image_src, alt=f"{unit['unit_name']} Storage", className="unit-image")
                ], className="unit-image-container"),
                html.Div([
                    html.Div(f"₦{unit['price']}/month", className="unit-price"),
                    html.Div(unit['unit_name'], className="unit-name"),
                    html.Div(f"{unit['warehouse_name']} - {unit['warehouse_location']}", className="unit-location"),
                    html.Div("Available", className="unit-status"),
                    html.A("View Details", href=f"/unit_details/{unit['id']}", className="unit-details-btn")
                ], className="unit-info")
            ], className="unit-card")
        )
    
    # Handle no units case
    if not units:
        no_units_style = {"display": "block"}
        if selected_date:
            no_units_msg = f"No units available for {selected_date}. Try selecting a different date or adjusting your filters."
        else:
            no_units_msg = "No units match your current filters. Try adjusting your search criteria."
    else:
        no_units_style = {"display": "none"}
        no_units_msg = ""
    
    # Calculate stats
    filtered_count = len(units)
    warehouses_count = len(set([unit['warehouse_id'] for unit in units])) if units else 0
    avg_price = sum([unit['price'] for unit in units]) / len(units) if units else 0
    total_available = len(all_units)
    
    return (
        unit_cards,
        no_units_msg,
        no_units_style,
        str(filtered_count),
        str(warehouses_count),
        f"₦{avg_price:.0f}",
        str(total_available)
    )
