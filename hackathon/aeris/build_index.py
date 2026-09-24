# Generator for AERIS index.html
import os

HTML_CONTENT = r'''<!DOCTYPE html>
<html class="dark" lang="en">
<head>
  <meta charset="utf-8">
  <meta content="width=device-width, initial-scale=1.0" name="viewport">
  <meta content="web_dashboard" name="shell-type">
  <title>AERIS — Environmental Intelligence Platform</title>
  
  <!-- Fonts & Material Symbols -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  
  <style>
    @layer base {
      html, body { margin: 0; padding: 0; }
      body { overscroll-behavior: none; }
    }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0a0e15; }
    ::-webkit-scrollbar-thumb { background: #263346; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #06B6D4; }
    .material-symbols-outlined {
      font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
      display: inline-block;
      vertical-align: middle;
      line-height: 1;
    }
  </style>

  <!-- Tailwind Theme Configuration matching Google Stitch design -->
  <script id="tailwind-config">
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            "background": "#0f131b",
            "surface-base": "#090D14",
            "surface-panel": "#0E141F",
            "surface-card": "#151D2A",
            "surface-container": "#1c2027",
            "surface-container-high": "#262a32",
            "surface-container-highest": "#31353d",
            "surface-container-lowest": "#0a0e15",
            "border-subtle": "#1E293B",
            "border-strong": "#263346",
            "telemetry-cyan": "#00E5FF",
            "precision-teal": "#06B6D4",
            "secondary": "#4cd7f6",
            "secondary-fixed": "#acedff",
            "baseline-emerald": "#10B981",
            "alert-amber": "#F59E0B",
            "alert-crimson": "#EF4444",
            "text-primary": "#F8FAFC",
            "text-muted": "#94A3B8",
            "text-dim": "#475569",
            "on-surface": "#dfe2ed",
            "on-surface-variant": "#bac9cc",
            "primary-container": "#00e5ff",
            "on-primary-container": "#00626e",
            "on-secondary-fixed": "#001f26",
            "on-error": "#690005"
          },
          fontFamily: {
            "body-lg": ["Inter", "sans-serif"],
            "body-md": ["Inter", "sans-serif"],
            "body-sm": ["Inter", "sans-serif"],
            "headline-xl": ["Inter", "sans-serif"],
            "headline-lg": ["Inter", "sans-serif"],
            "headline-md": ["Inter", "sans-serif"],
            "headline-sm": ["Inter", "sans-serif"],
            "label-lg": ["JetBrains Mono", "monospace"],
            "label-md": ["JetBrains Mono", "monospace"],
            "label-sm": ["JetBrains Mono", "monospace"],
            "telemetry-metric": ["JetBrains Mono", "monospace"]
          }
        }
      }
    };
  </script>

  <!-- React 18 & Babel Standalone -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- Real Forecast Data from Python CSV Processor -->
  <script src="./data/forecastData.js"></script>
</head>
<body class="bg-surface-base font-body-md text-on-surface antialiased selection:bg-primary-container selection:text-on-primary-container min-h-screen flex flex-col">
  <div id="root"></div>

  <!-- Main React Application Script -->
  <script type="text/babel">
    const { useState, useEffect, useMemo, useCallback } = React;

    const fmt = (v) => (v !== undefined && v !== null ? Number(v).toFixed(1) : '--');

    // Official AERIS Logo SVG Component
    function AerisLogo({ className = "h-7" }) {
      return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 40" fill="none">
          <g transform="translate(4, 4)">
            <circle cx="16" cy="16" r="14" stroke="#00E5FF" strokeWidth="1.75" strokeOpacity="0.35" strokeDasharray="2 3"/>
            <circle cx="16" cy="16" r="10" stroke="#00E5FF" strokeWidth="2" strokeOpacity="0.8"/>
            <circle cx="16" cy="16" r="4.5" fill="#00E5FF"/>
            <path d="M16 2 L16 7 M16 25 L16 30 M2 16 L7 16 M25 16 L30 16" stroke="#00E5FF" strokeWidth="1.5" strokeLinecap="round"/>
            <path d="M24 8 L20 12 M8 24 L12 20" stroke="#38BDF8" strokeWidth="1.2" strokeLinecap="round" strokeOpacity="0.7"/>
          </g>
          <text x="44" y="23" fill="#FFFFFF" fontFamily="Inter, sans-serif" fontWeight="800" fontSize="15" letterSpacing="2.5">AERIS</text>
          <text x="44" y="32" fill="#94A3B8" fontFamily="Inter, sans-serif" fontWeight="500" fontSize="6.8" letterSpacing="1.2">AIR INTELLIGENCE &amp; RESPONSE</text>
        </svg>
      );
    }
'''

print("Writing generator...")
with open("build_index.py", "w", encoding="utf-8") as f:
    f.write("# Part 1 written\n")
