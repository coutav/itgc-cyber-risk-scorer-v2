"""
ITGC Cyber Risk Scoring Model — v2
Streamlit Application
Master Thesis — Ankit Vats (s242576)
PwC Denmark · DTU · Digital Assurance, Technology Risk & Information Security
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import json
import os
import time
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ITGC Risk Scorer · v2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,300&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #0a0f1e; }
  section[data-testid="stSidebar"] { background: #070b17 !important; border-right: 1px solid #1c2540; }

  /* ── Typography ── */
  h1, h2, h3 { font-family: 'DM Sans', sans-serif !important; }

  /* ── Hero banner ── */
  .hero {
    background: linear-gradient(135deg, #0d1b3e 0%, #0a1628 50%, #071020 100%);
    border: 1px solid #1e3a6e;
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, #1a56db22 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #e8edf8;
    margin: 0 0 6px;
    letter-spacing: -0.5px;
  }
  .hero-sub {
    font-size: 0.92rem;
    color: #6b82b0;
    margin: 0;
    font-weight: 300;
  }
  .hero-badge {
    display: inline-block;
    background: #1a3560;
    color: #5b9cf6;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
    border: 1px solid #2d5090;
  }

  /* ── Cards ── */
  .card {
    background: #0e1628;
    border: 1px solid #1c2d50;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #3d6acc;
    margin-bottom: 16px;
  }

  /* ── Score gauge ── */
  .score-wrap {
    background: linear-gradient(135deg, #0e1a35 0%, #091428 100%);
    border: 1px solid #1e3566;
    border-radius: 16px;
    padding: 32px 24px;
    text-align: center;
    margin-bottom: 16px;
  }
  .score-number {
    font-family: 'DM Sans', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    margin: 8px 0;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .score-label {
    font-size: 0.78rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #4a6490;
    font-weight: 600;
  }

  /* ── Industry Benchmark Panel ── */
  .bm-card {
    background: linear-gradient(135deg, #060e22 0%, #0a1220 100%);
    border: 1px solid #1e3566;
    border-radius: 14px;
    padding: 22px 26px 20px;
    margin-top: 20px;
  }
  .bm-title {
    font-size: 0.68rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #4a6490;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .bm-subtitle {
    font-size: 0.78rem;
    color: #2d4a70;
    margin-bottom: 18px;
  }
  .bm-stats-row {
    display: flex;
    gap: 0;
    margin-bottom: 20px;
    border: 1px solid #1e3566;
    border-radius: 10px;
    overflow: hidden;
  }
  .bm-stat {
    flex: 1;
    padding: 12px 16px;
    border-right: 1px solid #1e3566;
    text-align: center;
  }
  .bm-stat:last-child { border-right: none; }
  .bm-stat-label {
    font-size: 0.62rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3a5a80;
    margin-bottom: 4px;
  }
  .bm-stat-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #c4d4f0;
  }
  .bm-stat-val.bm-your-score { color: #60a5fa; }
  .bm-stat-val.bm-delta-pos  { color: #f87171; }
  .bm-stat-val.bm-delta-neg  { color: #4ade80; }
  .bm-stat-sub {
    font-size: 0.62rem;
    color: #2d4a70;
    margin-top: 2px;
  }

  /* Distribution bar */
  .bm-bar-wrap { margin-bottom: 16px; }
  .bm-bar-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.6rem;
    color: #2d4270;
    margin-bottom: 4px;
  }
  .bm-bar-track {
    position: relative;
    height: 10px;
    background: #0d1628;
    border-radius: 5px;
    border: 1px solid #1e3566;
    overflow: visible;
  }
  .bm-bar-fill {
    position: absolute;
    top: 0; bottom: 0;
    border-radius: 5px;
    background: linear-gradient(90deg, #1e3566 0%, #2d5a9e 50%, #3d6ab0 100%);
    opacity: 0.5;
  }
  .bm-bar-marker {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 18px;
    border-radius: 1px;
    transform: translateX(-50%);
  }
  .bm-bar-score-dot {
    position: absolute;
    top: 50%;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #60a5fa;
    border: 2px solid #fff;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 8px rgba(96,165,250,0.6);
    z-index: 2;
  }
  .bm-bar-p-labels {
    display: flex;
    position: relative;
    height: 16px;
    font-size: 0.58rem;
    color: #2d4270;
    margin-top: 2px;
  }
  .bm-bar-p-label {
    position: absolute;
    transform: translateX(-50%);
    white-space: nowrap;
  }

  /* Percentile badge */
  .bm-percentile-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    background: #070d1e;
    border: 1px solid #1e3566;
  }
  .bm-pct-badge {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    min-width: 52px;
    text-align: center;
  }
  .bm-pct-badge.sev-critical { color: #f87171; }
  .bm-pct-badge.sev-high     { color: #fb923c; }
  .bm-pct-badge.sev-medium   { color: #fbbf24; }
  .bm-pct-badge.sev-low      { color: #4ade80; }
  .bm-pct-text { font-size: 0.78rem; color: #4a6490; line-height: 1.4; }
  .bm-pct-text b { color: #8ea3c8; }
  .bm-domain-row {
    margin-top: 10px;
    font-size: 0.68rem;
    color: #2d4270;
    display: flex;
    gap: 16px;
  }
  .bm-domain-chip {
    background: #0b1628;
    border: 1px solid #1e3566;
    border-radius: 6px;
    padding: 3px 10px;
    color: #4a6490;
  }

  /* ── Sign-off Readiness Indicator ── */
  .signoff-card {
    background: linear-gradient(135deg, #07100a 0%, #060e14 100%);
    border: 1px solid #1a4a2a;
    border-radius: 12px;
    padding: 14px 18px 10px;
    margin-top: 12px;
  }
  .signoff-card.amber { border-color: #78350f; background: linear-gradient(135deg, #110c04 0%, #0c0a04 100%); }
  .signoff-card.green { border-color: #14532d; background: linear-gradient(135deg, #060e08 0%, #040d08 100%); }
  .signoff-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
  .signoff-tl {
    width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;
    box-shadow: 0 0 6px currentColor;
  }
  .signoff-tl.red    { background:#f87171; color:#f87171; }
  .signoff-tl.amber  { background:#fbbf24; color:#fbbf24; }
  .signoff-tl.green  { background:#4ade80; color:#4ade80; }
  .signoff-hdr-text {}
  .signoff-title-main {
    font-size: 0.68rem; letter-spacing: 2px; text-transform: uppercase;
    color: #4a7a5a; font-weight: 700; margin-bottom: 1px;
  }
  .signoff-subtitle { font-size: 0.68rem; color: #2d5040; }
  .signoff-progress-bar {
    height: 2px; background: #0f2018; border-radius: 2px;
    margin-bottom: 6px; overflow: hidden;
  }
  .signoff-progress-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.3s ease;
  }
  .signoff-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 6px 0; border-top: 1px solid #0b1a10;
  }
  .signoff-item-meta { flex: 1; min-width: 0; }
  .signoff-item-label { font-size: 0.76rem; font-weight: 600; color: #8ab89a; line-height: 1.25; }
  .signoff-item-label.done { color: #4ade80; text-decoration: line-through; opacity: 0.7; }
  .signoff-item-desc { font-size: 0.66rem; color: #2d5040; margin-top: 1px; line-height: 1.35; }
  .signoff-req-chip {
    flex-shrink: 0; font-size: 0.56rem; font-weight: 700;
    padding: 2px 6px; border-radius: 8px; margin-top: 2px;
    letter-spacing: 0.5px;
  }
  .signoff-req-mandatory { background:#1a0a0a; color:#f87171; border:1px solid #7f1d1d; }
  .signoff-req-conditional { background:#0e1a0a; color:#4ade80; border:1px solid #14532d; }
  .signoff-footer {
    margin-top: 8px; padding-top: 8px; border-top: 1px solid #0b1a10;
    display: flex; align-items: center; gap: 10px;
  }
  .signoff-status-text { font-size: 0.7rem; color: #4a7a5a; }
  .signoff-status-text b { color: #8ab89a; }
  .signoff-count {
    margin-left: auto; font-size: 0.68rem; color: #2d5040;
    font-weight: 600;
  }

  /* Override Streamlit checkbox colours inside the signoff card */
  div[data-testid="stCheckbox"] label {
    font-size: 0.82rem !important;
    color: #8ab89a !important;
  }

  /* ── Control Environment Overview ── */
  .ceo-card {
    background: linear-gradient(135deg, #06110e 0%, #060f1a 100%);
    border: 1px solid #1c3a2e;
    border-radius: 12px;
    padding: 22px 24px 18px;
    margin-bottom: 16px;
  }
  .ceo-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }
  .ceo-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #34d399;
  }
  .ceo-subtitle {
    font-size: 0.75rem;
    color: #4a6490;
  }
  .ceo-posture-chip {
    margin-left: auto;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 4px 12px;
    border-radius: 20px;
  }
  .ceo-band-row {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    align-items: center;
  }
  .ceo-band-chip {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid;
  }
  .ceo-avg-label {
    margin-left: auto;
    font-size: 0.72rem;
    color: #4a6490;
  }
  .ceo-avg-score {
    font-size: 0.78rem;
    font-weight: 700;
    color: #8ea3c8;
  }
  .ceo-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.73rem;
  }
  .ceo-table th {
    text-align: left;
    color: #3d6acc;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-size: 0.65rem;
    padding: 4px 8px 8px;
    border-bottom: 1px solid #1c2d50;
  }
  .ceo-table td {
    padding: 6px 8px;
    color: #c4d4f0;
    border-bottom: 1px solid #0e1628;
    vertical-align: middle;
  }
  .ceo-table tr:last-child td { border-bottom: none; }
  .ceo-table tr.ceo-current td { background: #0a1e14; }
  .ceo-current-marker {
    display: inline-block;
    background: #0c3322;
    color: #34d399;
    border: 1px solid #1a5c3e;
    font-size: 0.6rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 10px;
    margin-left: 6px;
    vertical-align: middle;
  }
  .ceo-domain-tag {
    display: inline-block;
    background: #0c1a38;
    color: #5b9cf6;
    border: 1px solid #1e3a6e;
    font-size: 0.65rem;
    padding: 2px 7px;
    border-radius: 8px;
  }

  /* ── Remediation Roadmap Card ── */
  .remed-card {
    background: linear-gradient(135deg, #060e22 0%, #080f1e 100%);
    border: 1px solid #1e3566;
    border-radius: 14px;
    padding: 24px 28px 20px;
    margin-top: 20px;
  }
  .remed-header { margin-bottom: 20px; }
  .remed-title-main {
    font-size: 0.72rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #4a6490;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .remed-subtitle { font-size: 0.72rem; color: #2d4a70; }
  .remed-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 14px 0;
    border-top: 1px solid #0f1e3a;
  }
  .remed-item:first-of-type { border-top: none; }
  .remed-num {
    flex-shrink: 0;
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700;
    background: #0b1628; border: 1px solid #1e3566; color: #4a6490;
    margin-top: 2px;
  }
  .remed-num.tl-now { background:#1a0a0a; border-color:#7f1d1d; color:#f87171; }
  .remed-num.tl-30  { background:#0e1a0a; border-color:#14532d; color:#4ade80; }
  .remed-num.tl-90  { background:#0e1530; border-color:#1e3a8a; color:#60a5fa; }
  .remed-content { flex: 1; min-width: 0; }
  .remed-item-title {
    font-size: 0.85rem; font-weight: 600; color: #c4d4f0;
    margin-bottom: 4px; line-height: 1.3;
  }
  .remed-detail { font-size: 0.75rem; color: #4a6490; line-height: 1.5; }
  .remed-badges {
    flex-shrink: 0;
    display: flex; flex-direction: column;
    align-items: flex-end; gap: 6px;
    min-width: 120px;
  }
  .remed-badge {
    font-size: 0.65rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.5px; white-space: nowrap;
  }
  .remed-fw { background:#0e3d1e; color:#4ade80; border:1px solid #14532d; }
  .remed-me { background:#3d2a08; color:#fbbf24; border:1px solid #78350f; }
  .remed-cx { background:#3d0e0e; color:#f87171; border:1px solid #7f1d1d; }
  .remed-tl {
    font-size: 0.63rem; color: #3a5a80;
    white-space: nowrap;
  }
  .remed-tl-now { color: #f87171; }
  .remed-tl-30  { color: #4ade80; }
  .remed-tl-90  { color: #60a5fa; }
  .remed-legend {
    display: flex; gap: 14px; margin-top: 16px;
    padding-top: 12px; border-top: 1px solid #0f1e3a;
    flex-wrap: wrap;
  }
  .remed-legend-item { font-size: 0.63rem; color: #2d4270; display: flex; align-items: center; gap: 4px; }

  /* ── PwC Priority Scale ── */
  .pwc-priority-guidance {
    margin-top: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.7rem;
    line-height: 1.5;
    text-align: left;
  }
  .pwc-guidance-p1 { background:#1a0808; border:1px solid #7f1d1d; color:#fca5a5; }
  .pwc-guidance-p2 { background:#1a1008; border:1px solid #7c2d12; color:#fdba74; }
  .pwc-guidance-p3 { background:#1a1608; border:1px solid #78350f; color:#fcd34d; }
  .pwc-guidance-p4 { background:#081a10; border:1px solid #14532d; color:#86efac; }
  .pwc-guidance-p5 { background:#081018; border:1px solid #1e3a8a; color:#93c5fd; }
  .pwc-guidance-bold { font-weight: 700; display: block; margin-bottom: 3px; font-size: 0.72rem; }
  .pwc-priority-wrap {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid #1e3566;
  }
  .pwc-priority-label {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6490;
    font-weight: 600;
    margin-bottom: 10px;
  }
  .pwc-priority-scale {
    display: flex;
    justify-content: center;
    gap: 8px;
  }
  .pwc-pip {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'DM Sans', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    border: 1px solid #1e3566;
    background: #0b1628;
    color: #2d4270;
    transition: all 0.2s;
  }
  .pwc-pip.active-p1 { background:#3d0e0e; color:#f87171; border-color:#7f1d1d; box-shadow:0 0 12px rgba(248,113,113,0.35); }
  .pwc-pip.active-p2 { background:#3d1f0e; color:#fb923c; border-color:#7c2d12; box-shadow:0 0 12px rgba(251,146,60,0.35); }
  .pwc-pip.active-p3 { background:#3d330e; color:#fbbf24; border-color:#78350f; box-shadow:0 0 12px rgba(251,191,36,0.35); }
  .pwc-pip.active-p4 { background:#0e3d1e; color:#4ade80; border-color:#14532d; box-shadow:0 0 12px rgba(74,222,128,0.35); }
  .pwc-pip.active-p5 { background:#0e3030; color:#34d399; border-color:#134e4a; box-shadow:0 0 12px rgba(52,211,153,0.35); }
  .pwc-pip.pwc-pip-demoted { opacity:0.28; text-decoration:line-through; text-decoration-color:#fb923c; text-decoration-thickness:2px; }
  .pwc-pip-sub {
    font-size: 0.45rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-top: 1px;
    opacity: 0.75;
  }

  /* ── Financial Impact card ── */
  .fin-impact-card {
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    gap: 20px;
    flex-wrap: wrap;
  }
  .fin-impact-card.sev-critical  { background:#1a0608; border:1px solid #7f1d1d; }
  .fin-impact-card.sev-significant{ background:#1a1006; border:1px solid #78350f; }
  .fin-impact-card.sev-moderate  { background:#141a06; border:1px solid #3f6212; }
  .fin-impact-card.sev-elevated  { background:#0e1420; border:1px solid #1e3a6e; }
  .fin-impact-card.sev-standard  { background:#0e1420; border:1px solid #1e3566; }
  .fin-impact-card.sev-limited   { background:#0a1628; border:1px solid #1c2d50; }
  .fin-impact-card.sev-info      { background:#0a1220; border:1px solid #1c2540; }
  .fin-impact-left { display:flex; flex-direction:column; gap:8px; flex-shrink:0; }
  .fin-chip-row    { display:flex; gap:7px; align-items:center; flex-wrap:wrap; }
  .fin-chip {
    border-radius: 6px;
    padding: 4px 11px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
  /* Impact type chips */
  .fin-chip-direct   { background:#3d0e0e; color:#f87171; border:1px solid #7f1d1d; }
  .fin-chip-indirect { background:#3d2508; color:#fb923c; border:1px solid #7c2d12; }
  .fin-chip-none     { background:#0e1628; color:#4a6490; border:1px solid #1c2d50; }
  /* Materiality chips */
  .fin-mat-high   { background:#3d0e0e; color:#fca5a5; border:1px solid #7f1d1d; }
  .fin-mat-medium { background:#3d2508; color:#fdba74; border:1px solid #7c2d12; }
  .fin-mat-low    { background:#0e3d1e; color:#6ee7b7; border:1px solid #065f46; }
  .fin-impact-right { flex:1; min-width:180px; }
  .fin-sev-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
  }
  .fin-sev-label.sev-critical   { color:#f87171; }
  .fin-sev-label.sev-significant{ color:#fb923c; }
  .fin-sev-label.sev-moderate   { color:#fbbf24; }
  .fin-sev-label.sev-elevated   { color:#93c5fd; }
  .fin-sev-label.sev-standard   { color:#60a5fa; }
  .fin-sev-label.sev-limited    { color:#6ee7b7; }
  .fin-sev-label.sev-info       { color:#4a6490; }
  .fin-action-text {
    font-size: 0.76rem;
    color: #8ea3c8;
    line-height: 1.55;
  }

  /* ── IT Dependency adjustment ── */
  .it-adj-wrap {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #1e3566;
  }
  .it-adj-label {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6490;
    font-weight: 600;
    margin-bottom: 8px;
  }
  .it-adj-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 0.72rem;
  }
  .it-base-score {
    color: #4a6490;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
  }
  .it-adj-chip {
    background: #0e2a1a;
    border: 1px solid #166534;
    border-radius: 6px;
    padding: 2px 8px;
    color: #4ade80;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'DM Sans', sans-serif;
  }
  .it-adj-chip-zero {
    background: #0e1a2a;
    border: 1px solid #1e3566;
    color: #4a6490;
  }
  .it-adj-equals {
    color: #4a6490;
    font-size: 0.8rem;
  }
  .it-final-score {
    color: #60a5fa;
    font-family: 'DM Sans', sans-serif;
    font-weight: 800;
    font-size: 0.9rem;
  }
  .it-context-chips {
    display: flex;
    gap: 5px;
    justify-content: center;
    margin-top: 6px;
    flex-wrap: wrap;
  }
  .it-context-chip {
    background: #0a1628;
    border: 1px solid #1e3566;
    border-radius: 5px;
    padding: 2px 8px;
    font-size: 0.62rem;
    color: #6b82b0;
    font-weight: 500;
  }
  .score-base-label {
    font-size: 0.65rem;
    color: #2d4270;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 2px;
  }

  /* ── Repeat Finding badge ── */
  .repeat-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: linear-gradient(135deg, #3d1a06, #2d1208);
    border: 1px solid #c2410c;
    border-radius: 8px;
    padding: 7px 12px;
    color: #fb923c;
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-top: 12px;
    animation: repeatPulse 2.5s ease-in-out infinite;
  }
  @keyframes repeatPulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(194,65,12,0); }
    50%      { box-shadow: 0 0 10px 3px rgba(194,65,12,0.35); }
  }
  .repeat-escalation-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 6px;
    font-size: 0.65rem;
    color: #7c3a12;
    font-weight: 600;
  }
  .repeat-arrow {
    color: #fb923c;
    font-size: 0.8rem;
    font-weight: 800;
  }
  .repeat-py-label {
    background: #1e0f04;
    border: 1px solid #7c3a12;
    border-radius: 5px;
    padding: 2px 7px;
    color: #c2622a;
    font-size: 0.62rem;
  }

  /* ── Ask AI chat window ── */
  .chat-window-wrap {
    background: #0b1220;
    border: 1px solid #1e3566;
    border-radius: 16px;
    overflow: hidden;
    margin-top: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }
  .chat-header {
    background: linear-gradient(90deg, #0d2050 0%, #0a1a40 100%);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #1e3566;
  }
  .chat-header-avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1a56db, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
  }
  .chat-header-info { flex: 1; }
  .chat-header-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem; font-weight: 700; color: #e2e8f0;
  }
  .chat-header-status {
    font-size: 0.68rem; color: #4ade80; margin-top: 1px;
  }
  .chat-messages-area {
    height: 420px;
    overflow-y: auto;
    padding: 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    background-image: radial-gradient(circle at 20% 50%, #0d1b3e18 0%, transparent 60%),
                      radial-gradient(circle at 80% 20%, #1a056db11 0%, transparent 50%);
    scroll-behavior: smooth;
  }
  .chat-messages-area::-webkit-scrollbar { width: 4px; }
  .chat-messages-area::-webkit-scrollbar-track { background: transparent; }
  .chat-messages-area::-webkit-scrollbar-thumb { background: #1e3566; border-radius: 4px; }
  .chat-row-ai   { display:flex; justify-content:flex-start; align-items:flex-end; gap:8px; }
  .chat-row-user { display:flex; justify-content:flex-end;  align-items:flex-end; gap:8px; }
  .chat-avatar-ai {
    width:28px; height:28px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#1a56db,#7c3aed);
    display:flex; align-items:center; justify-content:center; font-size:0.75rem;
  }
  .chat-bubble-ai {
    max-width: 72%;
    background: #162040;
    border: 1px solid #1e3566;
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px;
    color: #c8d8f0;
    font-size: 0.82rem;
    line-height: 1.6;
    word-break: break-word;
  }
  .chat-bubble-user {
    max-width: 72%;
    background: linear-gradient(135deg, #0d3b2e, #0a2e24);
    border: 1px solid #1a5c45;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    color: #d4f1e4;
    font-size: 0.82rem;
    line-height: 1.6;
    word-break: break-word;
  }
  .chat-ts {
    font-size: 0.62rem; color: #2d4270; margin-top: 4px;
    text-align: right;
  }
  .chat-ts-ai { text-align: left; }
  .ask-ai-btn-wrap {
    display: flex;
    justify-content: center;
    margin: 24px 0 8px;
  }
  .ask-ai-btn {
    background: linear-gradient(135deg, #1a56db 0%, #7c3aed 100%);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(26,86,219,0.4);
    transition: all 0.2s;
  }
  .ask-ai-btn:hover {
    box-shadow: 0 6px 28px rgba(26,86,219,0.6);
    transform: translateY(-1px);
  }
  .typing-indicator { display:flex; gap:4px; align-items:center; padding:4px 0; }
  .typing-dot {
    width:7px; height:7px; border-radius:50%; background:#3a5a8a;
    animation: typingBounce 1.2s infinite;
  }
  .typing-dot:nth-child(2) { animation-delay:0.2s; }
  .typing-dot:nth-child(3) { animation-delay:0.4s; }
  @keyframes typingBounce {
    0%,60%,100% { transform:translateY(0); opacity:0.4; }
    30% { transform:translateY(-6px); opacity:1; }
  }

  /* ── Risk band pills ── */
  .band-critical { background:#3d0e0e; color:#f87171; border:1px solid #7f1d1d; border-radius:8px; padding:6px 18px; display:inline-block; font-family:'DM Sans',sans-serif; font-weight:700; font-size:1.1rem; letter-spacing:1px; }
  .band-high     { background:#3d2008; color:#fb923c; border:1px solid #7c2d12; border-radius:8px; padding:6px 18px; display:inline-block; font-family:'DM Sans',sans-serif; font-weight:700; font-size:1.1rem; letter-spacing:1px; }
  .band-medium   { background:#2d2a08; color:#fbbf24; border:1px solid #78350f; border-radius:8px; padding:6px 18px; display:inline-block; font-family:'DM Sans',sans-serif; font-weight:700; font-size:1.1rem; letter-spacing:1px; }
  .band-low      { background:#0a2a18; color:#34d399; border:1px solid #064e3b; border-radius:8px; padding:6px 18px; display:inline-block; font-family:'DM Sans',sans-serif; font-weight:700; font-size:1.1rem; letter-spacing:1px; }

  /* ── Probability bars ── */
  .prob-row { margin-bottom: 10px; }
  .prob-label { font-size: 0.8rem; color: #8ea3c8; margin-bottom: 4px; display: flex; justify-content: space-between; }
  .prob-bar-bg { background: #131e35; border-radius: 6px; height: 8px; overflow: hidden; }
  .prob-bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }

  /* ── Feature signal grid ── */
  .signal-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .signal-item {
    background: #0b1528;
    border: 1px solid #1a2d50;
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .signal-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .signal-dot-on  { background: #34d399; box-shadow: 0 0 6px #34d39966; }
  .signal-dot-off { background: #1e3050; }
  .signal-name { font-size: 0.78rem; color: #6b82b0; flex: 1; }
  .signal-val  { font-size: 0.82rem; font-family: 'DM Sans', sans-serif; font-weight: 700; color: #c4d4f0; }

  /* ── Environment Profile ── */
  .env-profile-wrap {
    background: #060c1a;
    border: 1px solid #1e3566;
    border-radius: 10px;
    padding: 14px 12px 10px;
    margin-top: 6px;
  }
  .env-row { margin-bottom: 10px; }
  .env-row-label {
    font-size: 0.6rem; letter-spacing: 1.5px; text-transform: uppercase;
    color: #3a5a80; font-weight: 700; margin-bottom: 5px;
  }
  /* Style horizontal radio as pill strip */
  .env-profile-wrap div[data-testid="stRadio"] > div {
    gap: 4px !important;
    flex-wrap: nowrap !important;
  }
  .env-profile-wrap div[data-testid="stRadio"] label {
    background: #0b1628 !important;
    border: 1px solid #1e3566 !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    font-size: 0.68rem !important;
    color: #4a6490 !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
  }
  .env-profile-wrap div[data-testid="stRadio"] label:has(input:checked) {
    background: #0f2040 !important;
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
  }
  .env-risk-chip {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px; border-radius: 8px; margin-top: 8px;
    font-size: 0.7rem;
  }
  .env-risk-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .env-risk-label { font-weight: 700; }
  .env-risk-adj { opacity: 0.65; margin-left: auto; }
  .env-dim-row {
    display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px;
  }
  .env-dim-chip {
    font-size: 0.58rem; padding: 2px 6px; border-radius: 10px;
    background: #0a1425; border: 1px solid #1e3566; color: #3a5a80;
  }
  .env-dim-chip.pos { border-color: #7f1d1d; color: #f87171; }
  .env-dim-chip.neg { border-color: #14532d; color: #4ade80; }
  .env-dim-chip.neu { border-color: #1e3566; color: #4a6490; }

  /* ── Sidebar inputs ── */
  .sidebar-section {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #3d6acc;
    margin: 20px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1c2d50;
  }

  /* ── Stacked info rows ── */
  .info-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #111e35; }
  .info-row:last-child { border-bottom: none; }
  .info-key { font-size: 0.78rem; color: #4a6490; }
  .info-val { font-size: 0.82rem; color: #c4d4f0; font-weight: 500; }

  /* ── Flag chips ── */
  .flag-chip-on  { display:inline-block; background:#0b2a1e; color:#34d399; border:1px solid #065f46; border-radius:6px; padding:3px 10px; font-size:0.72rem; font-weight:600; margin:3px; }
  .flag-chip-off { display:inline-block; background:#0c1627; color:#2d4270; border:1px solid #162038; border-radius:6px; padding:3px 10px; font-size:0.72rem; font-weight:600; margin:3px; }

  /* ── SHAP table ── */
  .shap-row { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
  .shap-feat { font-size:0.75rem; color:#8ea3c8; width:200px; flex-shrink:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .shap-bar-wrap { flex:1; background:#0b1528; border-radius:4px; height:16px; position:relative; overflow:hidden; }
  .shap-bar { height:100%; border-radius:4px; position:absolute; top:0; }
  .shap-bar-pos { background:linear-gradient(90deg,#1d4ed8,#3b82f6); }
  .shap-bar-neg { background:linear-gradient(90deg,#b91c1c,#ef4444); right:0; }
  .shap-val { font-size:0.72rem; font-family:'DM Sans',sans-serif; font-weight:700; width:52px; text-align:right; flex-shrink:0; }

  /* ── Streamlit overrides ── */
  .stButton > button {
    width: 100%; background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white; border: none; border-radius: 10px; padding: 14px;
    font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 0.95rem;
    letter-spacing: 1px; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 4px 20px #1d4ed840;
  }
  .stButton > button:hover { background: linear-gradient(135deg, #2563eb, #3b82f6); box-shadow: 0 6px 28px #2563eb50; transform: translateY(-1px); }
  .stTextArea textarea, .stSelectbox > div > div {
    background: #0c1627 !important; border: 1px solid #1c2d50 !important;
    color: #c4d4f0 !important; border-radius: 8px !important;
  }
  .stTextArea textarea:focus { border-color: #2563eb !important; box-shadow: 0 0 0 3px #1d4ed820 !important; }
  div[data-testid="stMetric"] { background: #0e1628; border: 1px solid #1c2d50; border-radius: 10px; padding: 16px; }
  div[data-testid="stMetricLabel"] { color: #4a6490 !important; font-size: 0.75rem !important; }
  div[data-testid="stMetricValue"] { color: #c4d4f0 !important; font-family: 'DM Sans', sans-serif !important; }
  .stSpinner { color: #3b82f6 !important; }
  .stAlert { border-radius: 10px !important; }
  [data-testid="stSidebarContent"] label { color: #8ea3c8 !important; font-size: 0.82rem !important; }

  /* ── History items ── */
  .hist-item {
    background: #0e1628; border: 1px solid #1c2d50;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
    cursor: pointer; transition: border-color 0.2s;
  }
  .hist-item:hover { border-color: #2563eb; }
  .hist-item-title { font-family:'DM Sans',sans-serif; font-weight:700; font-size:0.85rem; color:#c4d4f0; margin-bottom:4px; }
  .hist-item-meta  { font-size:0.72rem; color:#4a6490; }

  /* ── Divider ── */
  .divider { border:none; border-top:1px solid #1c2d50; margin:20px 0; }

  /* ── Scrollable history ── */
  .hist-scroll { max-height:260px; overflow-y:auto; padding-right:4px; }

  /* ── Empty state ── */
  .empty-state { text-align:center; color:#2d4270; font-size:0.82rem; padding:28px 0; }

  /* ════════════════════════════════════════════
     WELCOME SCREEN
  ════════════════════════════════════════════ */
  .welcome-page {
    min-height: 88vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
  }
  .welcome-logo {
    font-size: 3.5rem;
    margin-bottom: 12px;
    animation: pulse-glow 2s ease-in-out infinite;
  }
  @keyframes pulse-glow {
    0%, 100% { text-shadow: 0 0 20px #1d4ed860; }
    50%       { text-shadow: 0 0 40px #3b82f6aa, 0 0 80px #1d4ed840; }
  }
  .welcome-badge {
    display: inline-block;
    background: #1a3560;
    color: #5b9cf6;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    border: 1px solid #2d5090;
    margin-bottom: 16px;
  }
  .welcome-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #e8edf8;
    text-align: center;
    margin: 0 0 10px;
    letter-spacing: -0.5px;
    line-height: 1.15;
  }
  .welcome-sub {
    font-size: 1.05rem;
    color: #6b82b0;
    text-align: center;
    max-width: 600px;
    line-height: 1.6;
    margin: 0 auto 36px;
  }
  .welcome-features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 860px;
    width: 100%;
    margin-bottom: 36px;
  }
  .welcome-feat-card {
    background: #0e1628;
    border: 1px solid #1c2d50;
    border-radius: 14px;
    padding: 20px 18px;
    transition: border-color 0.2s, transform 0.2s;
  }
  .welcome-feat-card:hover {
    border-color: #2563eb;
    transform: translateY(-2px);
  }
  .welcome-feat-icon {
    font-size: 1.6rem;
    margin-bottom: 10px;
    display: block;
  }
  .welcome-feat-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: #c4d4f0;
    margin-bottom: 6px;
  }
  .welcome-feat-desc {
    font-size: 0.78rem;
    color: #4a6490;
    line-height: 1.55;
  }
  .welcome-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #2563eb, transparent);
    margin: 0 auto 28px;
  }
  .welcome-cta-hint {
    font-size: 0.8rem;
    color: #3d5a8a;
    text-align: center;
    margin-top: 10px;
  }

  /* ════════════════════════════════════════════
     TOUR PANEL
  ════════════════════════════════════════════ */
  .tour-panel {
    background: linear-gradient(135deg, #0d1b3e 0%, #081022 100%);
    border: 1px solid #2563eb55;
    border-left: 4px solid #2563eb;
    border-radius: 14px;
    padding: 22px 26px 18px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .tour-panel::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, #1d4ed815 0%, transparent 70%);
    pointer-events: none;
  }
  .tour-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
  }
  .tour-step-badge {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .tour-step-num {
    background: #1d4ed8;
    color: #fff;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
  }
  .tour-section-tag {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #3d6acc;
  }
  .tour-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #e8edf8;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .tour-body {
    font-size: 0.88rem;
    color: #8ea3c8;
    line-height: 1.7;
    margin-bottom: 14px;
  }
  .tour-tip {
    background: #0b1a35;
    border: 1px solid #1c3460;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.78rem;
    color: #5b9cf6;
    margin-top: 10px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }
  .tour-tip-icon { flex-shrink: 0; font-size: 0.9rem; }
  .tour-progress-bar {
    height: 3px;
    background: #0b1528;
    border-radius: 3px;
    margin-bottom: 14px;
    overflow: hidden;
  }
  .tour-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #1d4ed8, #3b82f6);
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  .tour-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 4px;
  }
  .tour-dots {
    display: flex;
    gap: 6px;
    align-items: center;
  }
  .tour-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #1c2d50;
    transition: background 0.2s, transform 0.2s;
  }
  .tour-dot.active { background: #2563eb; transform: scale(1.3); }
  .tour-dot.done   { background: #1d4ed860; }

  /* Sidebar tour button */
  .tour-restart-btn {
    background: #0e1a35 !important;
    border: 1px solid #1c3460 !important;
    color: #5b9cf6 !important;
    font-size: 0.78rem !important;
    padding: 8px 14px !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    margin-top: 4px;
    letter-spacing: 0.5px !important;
  }
  .tour-restart-btn:hover {
    border-color: #2563eb !important;
    background: #112040 !important;
    transform: none !important;
    box-shadow: none !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Constants (matching notebook exactly) ─────────────────────────────────────
HIGH_SEV_KEYWORDS = [
    'confirmed', 'active login', 'post-termination', 'immediate',
    'critical risk', 'material weakness', 'unauthorized access detected',
    'breach', 'compromised', 'confirmed unauthorized',
    'still active', 'fully active', 'former employee',
    'sod conflict', 'segregation of duties conflict',
    'unauthorised changes', 'go into production'
]
QUANTITY_PATTERN = re.compile(r'\d+\s*(out of|of)\s*\d+', re.IGNORECASE)

APP_TIER = {
    'SAP': 5, 'SAP HANA DB': 5, 'SAP S/4HANA': 5,
    'Oracle ERP': 5, 'Oracle DB': 4,
    'Windows AD': 4, 'Windows Server': 4,
    'Windows DC / E1 / Rillion': 4,
    'Microsoft MSSQL': 3, 'Microsoft Azure': 3,
    'Qlikview': 3, 'E1': 3,
    'RetailHub': 2, 'LoanOriginX': 2, 'InternalMES': 2,
    'QualityTrack': 2, 'GridOps': 2,
    'Netsuite': 5, 'NetSuite': 5, 'Workday': 4,
    'Salesforce': 3, 'ServiceNow': 3
}

STRONG_FEATURES = [
    'flag_unauth_access', 'flag_data_loss', 'flag_priv_escalation',
    'flag_no_logging', 'flag_weak_credentials',
    'app_tier',
    'domain_BR', 'domain_CM', 'domain_NJL', 'domain_PAM',
    'violation_rate', 'finding_confirmed', 'negation_flag',
    'compensating_control', 'sod_conflict', 'access_revocation_failure',
    'data_at_risk', 'systemic_vs_isolated',
    'evidence_strength', 'llm_severity_estimate'
]

CONTROL_DOMAINS   = ['PAM', 'NJL', 'CM', 'BR']
INDUSTRIES        = ['Energy & Utilities', 'Financial Services', 'Manufacturing', 'Pharmaceuticals', 'Retail']
APP_TYPES         = ['Non-Generic', 'Generic / Home-grown']
APPLICATIONS      = sorted(list(APP_TIER.keys())) + ['Other']

EXTRACTION_PROMPT = """You are a senior IT audit expert at PwC Denmark.
Analyse this ITGC deficiency finding and extract the following signals.
Return ONLY valid JSON — no explanation, no markdown, no code blocks.

{{
  "violation_rate": <float 0.0-1.0. Ratio of confirmed violations to total tested. If "0 out of 15" return 0.0. If "11 out of 15" return 0.73. If no numbers mentioned return 0.5>,
  "finding_confirmed": <1 if evidence is confirmed/proven/detected, 0 if suspected/noted/observed only>,
  "negation_flag": <1 if the finding explicitly states NO issue was found or control IS working, 0 if issue exists>,
  "compensating_control": <1 if a mitigating or compensating control is mentioned that reduces risk, 0 otherwise>,
  "sod_conflict": <1 if segregation of duties conflict is present, 0 otherwise>,
  "access_revocation_failure": <1 if terminated or former employee has active system access, 0 otherwise>,
  "data_at_risk": <1 if financial records, personal data or sensitive business data is exposed, 0 otherwise>,
  "systemic_vs_isolated": <1 if finding affects multiple users/systems/instances, 0 if single isolated case>,
  "evidence_strength": <float 0.0-1.0. 0.0=no evidence, 0.5=partial documentation, 1.0=full documented proof with logs>,
  "llm_severity_estimate": <float 0.0-1.0. Your expert judgment. 0.0=trivial procedural gap, 1.0=critical active breach>
}}

Observation: {observation}

Risk: {risk}"""

NEUTRAL_DEFAULTS = {
    "violation_rate": 0.5, "finding_confirmed": 0, "negation_flag": 0,
    "compensating_control": 0, "sod_conflict": 0, "access_revocation_failure": 0,
    "data_at_risk": 0, "systemic_vs_isolated": 0,
    "evidence_strength": 0.5, "llm_severity_estimate": 0.5
}

BAND_THRESHOLDS = [(75, "Critical"), (55, "High"), (35, "Medium"), (0, "Low")]

# ── Financial Materiality & Impact ─────────────────────────────────────────────
FIN_IMPACT_OPTIONS = [
    "Direct — Financial Statements",
    "Indirect — IT Infrastructure",
    "None",
]
FIN_MATERIALITY_OPTIONS = ["High", "Medium", "Low"]

# Audit interpretation matrix: (impact_type, materiality) → (severity_label, action_text)
FIN_INTERPRETATION = {
    ("Direct — Financial Statements", "High"):   ("Critical Exposure",   "Partner notification required. Cannot sign off without management action plan and re-testing."),
    ("Direct — Financial Statements", "Medium"): ("Significant Exposure", "Engagement manager review required before report issuance. Include in management letter."),
    ("Direct — Financial Statements", "Low"):    ("Moderate Exposure",    "Direct FS impact on low-materiality items. Document in findings, include in management letter."),
    ("Indirect — IT Infrastructure",  "High"):   ("Elevated Exposure",    "High-materiality system indirectly at risk. Assess IT dependency chain before sign-off."),
    ("Indirect — IT Infrastructure",  "Medium"): ("Standard Exposure",    "Indirect IT infrastructure risk. Address within 30 days and include in management letter."),
    ("Indirect — IT Infrastructure",  "Low"):    ("Limited Exposure",     "Indirect impact, low materiality. Monitor and track; include as advisory note."),
    ("None",                           "High"):   ("Informational",        "No direct financial impact, but high-materiality environment warrants close monitoring."),
    ("None",                           "Medium"): ("Informational",        "No financial impact identified. Standard tracking applies."),
    ("None",                           "Low"):    ("Informational",        "No financial impact identified. Advisory note only."),
}

# Priority delta per (impact_type, materiality): negative = escalate, 0 = no change
# Direct FS findings with High or Medium materiality escalate priority by 1 level.
# All other combinations are neutral — indirect/no impact doesn't override cyber risk.
FIN_PRIORITY_ADJUSTMENT = {
    ("Direct — Financial Statements", "High"):    -1,
    ("Direct — Financial Statements", "Medium"):  -1,
    ("Direct — Financial Statements", "Low"):      0,
    ("Indirect — IT Infrastructure",  "High"):     0,
    ("Indirect — IT Infrastructure",  "Medium"):   0,
    ("Indirect — IT Infrastructure",  "Low"):      0,
    ("None",                           "High"):     0,
    ("None",                           "Medium"):   0,
    ("None",                           "Low"):      0,
}

# ── Industry Benchmark Data (derived from 977 training records) ────────────────
# Key: (control_domain, industry). Values: mean, median, p25/p75/p90, n, and
# the full sorted score list for exact percentile lookup via bisect.
import bisect as _bisect

BENCHMARK_DATA = {
    ("BR", "Energy & Utilities"): {"n": 44, "mean": 52.7, "median": 49.9, "p25": 39.6, "p75": 54.7, "p90": 87.7, "scores": [23.1, 23.2, 25.4, 31.2, 33.3, 36.9, 37.2, 37.6, 38.3, 38.9, 39.5, 39.6, 41.6, 42.0, 44.6, 46.0, 46.2, 46.4, 48.3, 48.9, 49.4, 49.5, 50.2, 51.1, 51.5, 51.7, 52.7, 53.0, 53.1, 53.1, 53.6, 53.8, 54.6, 54.7, 56.0, 58.0, 84.7, 86.7, 87.4, 87.7, 88.1, 88.8, 89.5, 89.9]},
    ("BR", "Financial Services"): {"n": 43, "mean": 55.8, "median": 51.6, "p25": 39.7, "p75": 71.7, "p90": 89.4, "scores": [22.0, 29.0, 31.3, 35.1, 36.3, 36.4, 39.5, 39.6, 39.6, 39.6, 39.7, 40.4, 41.9, 46.0, 48.1, 48.4, 48.8, 48.8, 49.4, 49.7, 50.9, 51.6, 51.8, 52.2, 53.0, 53.0, 53.6, 54.1, 54.3, 54.4, 54.7, 59.6, 71.7, 75.4, 86.7, 86.7, 88.3, 89.1, 89.4, 89.7, 89.9, 89.9, 89.9]},
    ("BR", "Manufacturing"): {"n": 51, "mean": 49.4, "median": 43.5, "p25": 34.5, "p75": 53.5, "p90": 89.9, "scores": [20.2, 20.4, 21.4, 21.5, 22.7, 28.8, 30.4, 30.6, 31.4, 31.8, 33.7, 34.5, 34.5, 34.9, 36.0, 36.5, 37.6, 37.9, 38.8, 39.6, 39.6, 40.0, 40.0, 40.1, 41.9, 43.5, 44.4, 44.9, 46.0, 46.2, 46.2, 46.2, 46.5, 47.0, 48.3, 49.2, 52.8, 53.4, 53.5, 59.4, 72.8, 87.8, 88.5, 89.6, 89.9, 89.9, 89.9, 89.9, 89.9, 89.9, 89.9]},
    ("BR", "Pharmaceuticals"): {"n": 51, "mean": 48.1, "median": 46.1, "p25": 39.9, "p75": 52.9, "p90": 65.3, "scores": [20.7, 24.3, 25.9, 28.2, 30.6, 32.0, 33.8, 34.1, 34.1, 36.4, 37.6, 37.9, 39.9, 40.1, 41.2, 42.2, 42.2, 42.4, 42.4, 42.7, 43.5, 45.1, 45.4, 45.9, 46.0, 46.1, 46.6, 47.2, 49.0, 49.1, 49.5, 49.6, 50.2, 50.4, 51.1, 51.5, 52.6, 52.9, 52.9, 53.2, 53.3, 54.0, 54.2, 54.9, 58.2, 65.3, 77.7, 80.9, 87.5, 89.0, 89.8]},
    ("BR", "Retail"): {"n": 49, "mean": 45.5, "median": 41.6, "p25": 33.3, "p75": 51.9, "p90": 86.5, "scores": [20.3, 20.9, 22.0, 23.1, 23.4, 25.1, 27.5, 28.1, 28.1, 28.2, 30.8, 32.3, 33.3, 35.5, 35.5, 35.5, 36.0, 36.4, 36.9, 38.4, 38.5, 38.5, 38.5, 40.6, 41.6, 41.8, 44.1, 44.2, 47.5, 49.4, 49.9, 49.9, 49.9, 50.6, 51.2, 51.8, 51.9, 52.2, 52.3, 52.8, 53.5, 53.7, 67.6, 75.4, 86.5, 89.7, 89.8, 89.9, 89.9]},
    ("CM", "Energy & Utilities"): {"n": 49, "mean": 55.0, "median": 54.0, "p25": 46.7, "p75": 61.9, "p90": 85.4, "scores": [21.0, 24.7, 26.1, 28.2, 39.7, 40.5, 40.9, 41.2, 44.1, 45.3, 46.5, 46.7, 46.7, 50.0, 50.0, 50.1, 50.2, 50.8, 50.9, 50.9, 51.1, 51.5, 52.6, 53.2, 54.0, 54.1, 54.1, 54.7, 54.8, 54.8, 54.9, 55.0, 55.4, 56.8, 58.5, 59.1, 61.9, 63.0, 64.0, 65.0, 65.4, 67.4, 69.2, 84.5, 85.4, 86.7, 87.3, 87.7, 89.9]},
    ("CM", "Financial Services"): {"n": 47, "mean": 56.0, "median": 54.0, "p25": 50.6, "p75": 57.2, "p90": 86.3, "scores": [21.5, 27.2, 29.3, 33.8, 35.5, 40.4, 40.7, 44.6, 48.3, 48.7, 49.7, 50.6, 51.0, 51.4, 51.5, 51.6, 52.1, 52.1, 52.5, 52.5, 52.8, 53.1, 53.1, 54.0, 54.2, 54.2, 54.6, 54.8, 55.2, 55.4, 55.6, 55.8, 56.8, 57.0, 57.0, 57.2, 57.4, 62.3, 66.9, 73.7, 79.0, 86.1, 86.3, 86.8, 88.6, 89.1, 89.7]},
    ("CM", "Manufacturing"): {"n": 52, "mean": 57.2, "median": 53.2, "p25": 50.3, "p75": 63.1, "p90": 87.9, "scores": [20.9, 21.3, 23.4, 35.5, 37.7, 40.3, 40.9, 44.1, 45.6, 46.0, 47.2, 47.4, 47.9, 50.3, 50.5, 50.5, 50.5, 50.9, 51.2, 51.2, 51.5, 51.6, 51.8, 52.2, 52.9, 53.1, 53.4, 53.9, 54.2, 54.3, 54.3, 54.6, 55.8, 56.0, 56.4, 56.4, 56.7, 56.9, 57.6, 63.1, 70.3, 78.5, 81.9, 86.6, 86.6, 87.0, 87.9, 88.6, 89.2, 89.7, 89.9, 89.9]},
    ("CM", "Pharmaceuticals"): {"n": 49, "mean": 60.4, "median": 55.3, "p25": 52.1, "p75": 68.6, "p90": 88.9, "scores": [21.0, 22.4, 27.3, 42.9, 46.4, 48.7, 48.8, 49.3, 51.3, 51.5, 51.6, 51.6, 52.1, 52.5, 52.5, 52.6, 53.4, 54.0, 54.3, 54.3, 54.4, 54.7, 55.0, 55.1, 55.3, 55.4, 56.0, 56.1, 56.4, 56.6, 57.4, 58.1, 61.6, 62.4, 64.8, 67.0, 68.6, 74.0, 75.4, 78.4, 86.3, 87.4, 88.6, 88.6, 88.9, 89.3, 89.7, 89.8, 89.8]},
    ("CM", "Retail"): {"n": 47, "mean": 56.6, "median": 54.6, "p25": 46.5, "p75": 59.9, "p90": 88.7, "scores": [20.8, 23.8, 26.1, 27.8, 36.4, 39.5, 41.6, 42.8, 43.4, 44.2, 44.5, 46.5, 47.8, 48.4, 48.4, 48.4, 48.9, 52.2, 52.2, 52.7, 54.3, 54.5, 54.5, 54.6, 54.7, 54.8, 56.0, 56.8, 56.9, 57.2, 57.2, 57.5, 57.7, 58.4, 58.7, 59.9, 60.0, 69.4, 83.9, 86.0, 87.6, 88.2, 88.7, 89.1, 89.4, 89.8, 89.9]},
    ("NJL", "Energy & Utilities"): {"n": 50, "mean": 57.4, "median": 51.5, "p25": 36.1, "p75": 87.4, "p90": 89.6, "scores": [21.5, 22.1, 24.4, 25.9, 27.3, 29.2, 29.5, 31.3, 31.7, 31.8, 31.8, 35.8, 36.1, 39.9, 41.8, 42.3, 43.6, 44.1, 46.4, 46.4, 47.1, 47.5, 48.0, 48.8, 51.4, 51.6, 51.9, 52.1, 52.5, 53.0, 54.6, 55.8, 74.8, 78.5, 85.3, 86.6, 87.4, 87.4, 87.4, 89.1, 89.2, 89.3, 89.3, 89.3, 89.4, 89.6, 89.8, 89.8, 89.9, 89.9]},
    ("NJL", "Financial Services"): {"n": 48, "mean": 65.6, "median": 54.2, "p25": 50.3, "p75": 89.5, "p90": 89.8, "scores": [20.9, 21.0, 26.4, 36.2, 42.8, 43.6, 46.8, 47.0, 47.8, 49.1, 49.6, 49.7, 50.3, 50.4, 50.4, 50.6, 50.6, 50.8, 51.0, 52.7, 52.8, 52.9, 53.7, 53.9, 54.5, 55.0, 78.5, 84.6, 84.8, 85.7, 86.1, 88.2, 88.3, 88.7, 88.9, 89.4, 89.5, 89.5, 89.5, 89.5, 89.6, 89.8, 89.8, 89.8, 89.8, 89.9, 89.9, 89.9]},
    ("NJL", "Manufacturing"): {"n": 52, "mean": 63.5, "median": 56.4, "p25": 42.3, "p75": 89.5, "p90": 89.9, "scores": [21.7, 22.3, 24.6, 26.5, 28.1, 28.7, 30.4, 31.1, 31.6, 33.6, 36.3, 37.4, 41.5, 42.3, 44.7, 44.8, 45.4, 47.5, 48.7, 49.5, 50.0, 50.0, 50.4, 51.7, 52.0, 54.5, 58.2, 81.4, 85.4, 85.9, 86.7, 87.0, 88.1, 88.4, 89.0, 89.1, 89.4, 89.5, 89.5, 89.5, 89.6, 89.7, 89.7, 89.8, 89.8, 89.8, 89.9, 89.9, 89.9, 89.9, 89.9, 90.0]},
    ("NJL", "Pharmaceuticals"): {"n": 44, "mean": 60.7, "median": 53.4, "p25": 44.7, "p75": 88.3, "p90": 89.8, "scores": [25.6, 26.8, 30.5, 30.9, 32.0, 34.0, 34.3, 41.4, 42.2, 42.5, 42.8, 44.7, 45.2, 48.2, 48.4, 49.8, 50.1, 50.9, 52.1, 53.0, 53.0, 53.4, 53.4, 53.6, 53.8, 54.8, 56.7, 71.2, 73.8, 75.7, 86.7, 86.9, 87.8, 88.3, 88.9, 89.2, 89.4, 89.4, 89.6, 89.8, 89.9, 89.9, 89.9, 89.9]},
    ("NJL", "Retail"): {"n": 50, "mean": 59.2, "median": 52.3, "p25": 43.3, "p75": 87.8, "p90": 89.9, "scores": [20.4, 21.7, 27.9, 29.4, 32.3, 33.2, 34.5, 35.1, 40.0, 40.5, 41.9, 41.9, 43.3, 46.0, 46.1, 47.4, 47.7, 48.8, 48.9, 50.1, 51.3, 51.4, 51.7, 51.9, 52.3, 52.4, 52.9, 52.9, 53.0, 53.0, 54.5, 54.7, 55.2, 81.0, 81.0, 84.0, 87.6, 87.8, 87.9, 88.3, 89.4, 89.4, 89.6, 89.7, 89.7, 89.9, 89.9, 89.9, 89.9, 89.9]},
    ("PAM", "Energy & Utilities"): {"n": 57, "mean": 57.2, "median": 49.4, "p25": 34.9, "p75": 88.2, "p90": 89.3, "scores": [20.5, 20.9, 21.0, 21.1, 21.5, 23.8, 25.1, 25.2, 25.9, 27.6, 28.0, 28.9, 29.4, 31.4, 34.9, 36.5, 37.1, 38.0, 39.9, 40.7, 42.0, 43.2, 43.5, 43.9, 45.6, 46.8, 47.5, 48.8, 49.4, 49.5, 50.7, 54.7, 55.0, 59.3, 67.4, 83.0, 84.3, 84.6, 85.2, 87.0, 87.6, 88.0, 88.2, 88.3, 88.6, 88.6, 88.7, 88.8, 89.0, 89.1, 89.3, 89.3, 89.5, 89.6, 89.6, 89.8, 89.9]},
    ("PAM", "Financial Services"): {"n": 49, "mean": 63.4, "median": 55.8, "p25": 46.4, "p75": 89.2, "p90": 89.6, "scores": [21.5, 26.1, 28.8, 32.7, 32.8, 33.7, 35.8, 37.4, 40.2, 43.4, 43.4, 44.4, 46.4, 47.4, 48.1, 48.2, 49.6, 49.7, 50.6, 50.8, 52.0, 53.1, 54.0, 54.6, 55.8, 55.9, 55.9, 63.5, 79.7, 83.9, 85.1, 86.2, 86.4, 88.6, 89.1, 89.1, 89.2, 89.3, 89.3, 89.3, 89.4, 89.5, 89.5, 89.6, 89.6, 89.7, 89.8, 89.8, 89.8]},
    ("PAM", "Manufacturing"): {"n": 44, "mean": 60.5, "median": 53.8, "p25": 37.7, "p75": 88.9, "p90": 89.6, "scores": [20.1, 20.7, 21.4, 24.3, 26.8, 28.0, 29.0, 30.7, 30.9, 32.9, 35.1, 37.7, 38.4, 43.3, 48.3, 49.0, 49.3, 49.6, 50.4, 51.6, 52.1, 53.8, 53.8, 54.3, 65.2, 71.6, 84.1, 86.4, 87.9, 88.1, 88.5, 88.8, 88.9, 88.9, 89.0, 89.1, 89.1, 89.3, 89.5, 89.6, 89.6, 89.6, 89.6, 89.9]},
    ("PAM", "Pharmaceuticals"): {"n": 49, "mean": 61.9, "median": 54.4, "p25": 40.3, "p75": 88.5, "p90": 89.8, "scores": [21.1, 23.9, 23.9, 24.5, 24.7, 26.3, 27.5, 27.7, 27.7, 34.0, 34.1, 34.1, 40.3, 40.9, 44.4, 46.4, 46.4, 47.3, 49.6, 50.7, 51.2, 52.1, 52.3, 52.7, 54.4, 55.5, 75.7, 84.1, 84.7, 85.5, 86.4, 86.6, 87.4, 87.6, 87.7, 87.9, 88.5, 88.8, 88.8, 89.4, 89.6, 89.6, 89.7, 89.7, 89.8, 89.8, 89.9, 89.9, 89.9]},
    ("PAM", "Retail"): {"n": 52, "mean": 55.6, "median": 49.3, "p25": 30.2, "p75": 88.7, "p90": 89.3, "scores": [20.8, 20.9, 23.1, 24.6, 25.0, 25.1, 25.6, 25.6, 26.0, 27.0, 27.4, 29.0, 30.1, 30.2, 32.4, 36.9, 37.0, 37.6, 38.0, 38.0, 38.6, 43.2, 43.9, 45.8, 48.6, 49.3, 49.3, 49.7, 51.9, 52.2, 52.5, 53.3, 54.3, 83.5, 84.6, 85.0, 88.0, 88.6, 88.6, 88.7, 88.8, 88.8, 88.9, 89.1, 89.2, 89.2, 89.3, 89.4, 89.5, 89.6, 89.7, 89.9]},
}

BENCHMARK_DOMAIN_DATA = {
    "BR":  {"n": 238, "mean": 50.1, "median": 46.5, "p25": 37.6, "p75": 53.6, "p90": 88.5},
    "CM":  {"n": 244, "mean": 57.1, "median": 54.3, "p25": 49.7, "p75": 62.3, "p90": 87.6},
    "NJL": {"n": 244, "mean": 61.3, "median": 52.9, "p25": 44.1, "p75": 89.0, "p90": 89.8},
    "PAM": {"n": 251, "mean": 59.6, "median": 52.3, "p25": 37.0, "p75": 88.7, "p90": 89.6},
}

def compute_benchmark(score: float, domain: str, industry: str) -> dict:
    """Return benchmark stats and exact percentile rank for score vs domain×industry peers."""
    key = (domain, industry)
    bm  = BENCHMARK_DATA.get(key)
    if not bm:
        return {}
    sorted_scores = bm["scores"]
    pos           = _bisect.bisect_left(sorted_scores, score)
    pct_rank      = round(100 * pos / bm["n"])   # % of scores BELOW this score
    top_pct       = 100 - pct_rank               # top X% most severe
    delta         = round(score - bm["mean"], 1)
    return {
        "n":        bm["n"],
        "mean":     bm["mean"],
        "median":   bm["median"],
        "p25":      bm["p25"],
        "p75":      bm["p75"],
        "p90":      bm["p90"],
        "pct_rank": pct_rank,   # percentile from bottom (higher = more severe)
        "top_pct":  top_pct,    # top-X% label (lower = more severe)
        "delta":    delta,
    }

# ── IT Dependency multiplier matrix ────────────────────────────────────────────
IT_DEP_COUNT_OPTIONS = ["≤ 5 processes", "6 – 15 processes", "16+ processes"]
IT_INTERFACE_OPTIONS = ["Standard reports", "Custom interfaces", "APIs", "Direct DB access"]

IT_INTERFACE_WEIGHTS = {
    "Standard reports":  0,
    "Custom interfaces": 4,
    "APIs":              6,
    "Direct DB access":  9,
}
IT_VOLUME_MULTIPLIERS = {
    "≤ 5 processes":    0.5,
    "6 – 15 processes": 1.0,
    "16+ processes":    1.5,
}

# ── Client Environment Profile ──────────────────────────────────────────────────
ENV_DEPLOY_OPTIONS = ["☁️  Cloud / SaaS", "🌐  Hybrid", "🏢  On-Premise"]
ENV_AGE_OPTIONS    = ["✨  Modern (< 5 yrs)", "📅  Moderate (5–10 yrs)", "⚠️  Legacy (> 10 yrs)"]
ENV_SCOPE_OPTIONS  = ["🏢  Single Entity", "🏭  Multi-Entity", "🌍  Group-Wide"]

# Score adjustments (applied on top of IT-dep adjusted score)
# Rationale: on-prem legacy group-wide PAM deficiency is fundamentally riskier
# than a single-entity modern SaaS finding. Range: −4 to +14 pts.
ENV_DEPLOY_ADJ = {"☁️  Cloud / SaaS": -2, "🌐  Hybrid": 0, "🏢  On-Premise": 3}
ENV_AGE_ADJ    = {"✨  Modern (< 5 yrs)": -2, "📅  Moderate (5–10 yrs)": 0, "⚠️  Legacy (> 10 yrs)": 5}
ENV_SCOPE_ADJ  = {"🏢  Single Entity": 0, "🏭  Multi-Entity": 3, "🌍  Group-Wide": 6}

ENV_RISK_LEVELS = [
    (8,  "Very High", "#f87171", "#3d0e0e"),
    (4,  "High",      "#fb923c", "#3d1f0e"),
    (1,  "Moderate",  "#fbbf24", "#3d330e"),
    (-99,"Low",       "#4ade80", "#0e3d1e"),
]

def compute_env_adjustment(deploy: str, age: str, scope: str) -> int:
    return ENV_DEPLOY_ADJ.get(deploy, 0) + ENV_AGE_ADJ.get(age, 0) + ENV_SCOPE_ADJ.get(scope, 0)

def env_risk_level(adj: int) -> tuple:
    for threshold, label, color, bg in ENV_RISK_LEVELS:
        if adj >= threshold:
            return label, color, bg
    return "Low", "#4ade80", "#0e3d1e"

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_result_id" not in st.session_state:
    st.session_state.chat_result_id = None
if "prior_year_finding" not in st.session_state:
    st.session_state.prior_year_finding = False
if "prior_year_priority" not in st.session_state:
    st.session_state.prior_year_priority = 3
if "it_dep_count" not in st.session_state:
    st.session_state.it_dep_count = IT_DEP_COUNT_OPTIONS[0]
if "it_interface_type" not in st.session_state:
    st.session_state.it_interface_type = IT_INTERFACE_OPTIONS[0]
if "env_deploy" not in st.session_state:
    st.session_state.env_deploy = ENV_DEPLOY_OPTIONS[1]   # Hybrid default
if "env_age" not in st.session_state:
    st.session_state.env_age = ENV_AGE_OPTIONS[1]          # Moderate default
if "env_scope" not in st.session_state:
    st.session_state.env_scope = ENV_SCOPE_OPTIONS[0]      # Single Entity default
if "fin_impact_type" not in st.session_state:
    st.session_state.fin_impact_type = FIN_IMPACT_OPTIONS[0]
if "fin_materiality" not in st.session_state:
    st.session_state.fin_materiality = FIN_MATERIALITY_OPTIONS[0]
if "api_key" not in st.session_state:
    # 1. Streamlit Cloud secrets (injected as env var)
    _saved_key = os.environ.get("ANTHROPIC_API_KEY", "")
    # 2. Local .env file fallback
    if not _saved_key:
        _env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(_env_path):
            with open(_env_path) as _f:
                for _line in _f:
                    if _line.startswith("ANTHROPIC_API_KEY="):
                        _saved_key = _line.strip().split("=", 1)[1]
                        break
    st.session_state.api_key = _saved_key

# ── Guide / tour session state ─────────────────────────────────────────────────
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True    # show on first load
if "tour_active" not in st.session_state:
    st.session_state.tour_active = False
if "tour_step" not in st.session_state:
    st.session_state.tour_step = 0

# ── Tour steps definition ──────────────────────────────────────────────────────
TOUR_STEPS = [
    {
        "icon": "🛡️",
        "section": "Overview",
        "title": "Welcome to ITGC Risk Scorer v2",
        "body": (
            "This tool helps IT auditors at PwC quickly and accurately assess the severity of "
            "<b>IT General Control (ITGC) findings</b> — the weaknesses found during an audit of "
            "a company's IT systems.<br><br>"
            "Instead of relying on gut feel, the scorer combines a trained <b>XGBoost machine-learning "
            "model</b> with <b>Claude Haiku AI</b> to produce a transparent, explainable risk score "
            "from 0–100. Every score comes with detailed reasoning so the auditor knows exactly why "
            "a finding ranked the way it did."
        ),
        "tip": "You can restart this tour anytime by clicking 'Take the Tour' in the left sidebar.",
    },
    {
        "icon": "📋",
        "section": "Sidebar → Finding Context",
        "title": "Setting the Finding Context",
        "body": (
            "Before entering any text, configure the <b>Finding Context</b> in the left sidebar. "
            "These four fields tell the model exactly what kind of control is being audited:<br><br>"
            "<b>• Control Domain</b> — the type of IT control:<br>"
            "&nbsp;&nbsp;– <em>PAM</em> = Privileged Access Management (who has admin rights)<br>"
            "&nbsp;&nbsp;– <em>NJL</em> = New Joiners &amp; Leavers (access when staff join/leave)<br>"
            "&nbsp;&nbsp;– <em>CM</em> = Change Management (how code/config changes are approved)<br>"
            "&nbsp;&nbsp;– <em>BR</em> = Backup &amp; Restoration (data backup processes)<br><br>"
            "<b>• Application</b> — the specific system involved (SAP, Oracle, etc.)<br>"
            "<b>• Industry</b> — the client's industry (affects benchmark comparison)<br>"
            "<b>• Application Type</b> — ERP or non-ERP"
        ),
        "tip": "The model was trained on data from all four control domains, so selecting the correct domain is critical for an accurate score.",
    },
    {
        "icon": "🔗",
        "section": "Sidebar → IT Dependency",
        "title": "IT Dependency Context",
        "body": (
            "The <b>IT Dependency</b> section captures how deeply the affected system is embedded "
            "in the client's financial reporting process.<br><br>"
            "<b>Financial Processes Dependent</b> — how many key financial processes run through "
            "this system? More processes = higher exposure if something goes wrong.<br><br>"
            "<b>Interface / Integration Type</b> — how does this system connect to others?<br>"
            "&nbsp;&nbsp;– <em>Direct DB access</em> carries the most risk<br>"
            "&nbsp;&nbsp;– <em>API integration</em> is moderate risk<br>"
            "&nbsp;&nbsp;– <em>Standard reports / manual export</em> carry the least<br><br>"
            "The tool automatically calculates a <b>score adjustment</b> (shown live below the "
            "dropdowns) and adds it to the base model score."
        ),
        "tip": "A Direct DB access connection on a system with 5+ financial processes can add up to +13.5 points to the final risk score.",
    },
    {
        "icon": "🌐",
        "section": "Sidebar → Client Environment",
        "title": "Client Environment Profile",
        "body": (
            "The <b>Client Environment</b> section captures three dimensions of the client's "
            "technical environment that affect inherent risk:<br><br>"
            "<b>• Deployment Model</b> — On-premise, Cloud, or Hybrid. Cloud and Hybrid "
            "environments may introduce additional exposure through shared responsibility models.<br><br>"
            "<b>• System Age</b> — Legacy systems (10+ years old) are harder to patch and "
            "often lack modern security controls. Newer systems carry lower inherent risk.<br><br>"
            "<b>• Audit Scope</b> — Single entity vs. multi-entity (group audit). A wider scope "
            "amplifies the potential blast radius of any control weakness.<br><br>"
            "The <b>live risk chip</b> (e.g., 'High Environment Risk +8 pts') shows the combined "
            "impact of all three selections in real time."
        ),
        "tip": "Environment adjustments range from −4 to +14 points and are applied on top of the IT dependency adjustment.",
    },
    {
        "icon": "💰",
        "section": "Sidebar → Financial Context",
        "title": "Financial Context & Materiality",
        "body": (
            "The <b>Financial Context</b> section links the IT finding to the financial audit:<br><br>"
            "<b>Financial Impact Type</b> — does this control weakness directly affect financial "
            "statements, or only the underlying IT infrastructure? A direct financial impact "
            "is significantly more serious.<br><br>"
            "<b>Materiality Level</b> — the audit's quantitative materiality threshold for this "
            "client. A finding that is material to a small company may be immaterial at a large one.<br><br>"
            "The combination of these two inputs maps to a <b>severity classification</b> "
            "(e.g., 'Significant Deficiency') and may escalate the PwC Priority level by one step."
        ),
        "tip": "Financial context only adjusts the priority level — it does not change the 0–100 risk score itself.",
    },
    {
        "icon": "🔁",
        "section": "Sidebar → Prior Year Context",
        "title": "Prior Year & Repeat Findings",
        "body": (
            "If this same control weakness was identified in a <b>previous year's audit</b>, "
            "toggle on <em>'Prior year finding'</em> and select the priority it was assigned then.<br><br>"
            "Repeat findings are treated more seriously in audit standards because management "
            "was already notified and had the opportunity to remediate — yet the weakness persists.<br><br>"
            "The scorer automatically <b>escalates the priority by one level</b> "
            "(e.g., P3 → P2) for repeat findings, reflecting this increased audit significance."
        ),
        "tip": "Repeat findings at P1 cannot escalate further — P1 is already the highest priority (Critical).",
    },
    {
        "icon": "✍️",
        "section": "Main Area → Input",
        "title": "Entering a Finding",
        "body": (
            "The two main text fields are the core of the scorer:<br><br>"
            "<b>Observation</b> — describe what you <em>found</em> during testing. Be factual "
            "and specific: mention the system, the number of exceptions, what the evidence showed, "
            "and whether any exceptions had real-world impact (e.g., post-termination logins).<br><br>"
            "<b>Risk Statement</b> — describe the <em>risk</em> that the observation creates. "
            "What could go wrong? Who is affected? How likely is exploitation?<br><br>"
            "Both fields are read by Claude Haiku AI, which extracts 10 semantic risk signals "
            "from your free-text. The richer the input, the more accurate the score."
        ),
        "tip": "Use the Quick Examples below the text boxes to see how high, medium, and low severity findings are typically written.",
    },
    {
        "icon": "⚡",
        "section": "Main Area → Scoring",
        "title": "Scoring the Finding",
        "body": (
            "Once you've filled in the context (sidebar) and entered the finding text, click "
            "<b>Score This Finding</b>.<br><br>"
            "The scoring pipeline runs in two phases:<br>"
            "<b>Phase 1 — Claude Haiku (AI)</b>: reads your observation and risk statement and "
            "extracts 10 semantic signals such as whether a violation was confirmed, whether "
            "data was directly at risk, and the AI's own severity estimate.<br><br>"
            "<b>Phase 2 — XGBoost Model</b>: combines the AI signals with your structured "
            "inputs (domain, application, industry, etc.), predicts a Low / Medium / High class "
            "with probabilities, then converts these to a continuous 0–100 score.<br><br>"
            "Post-model adjustments for IT dependency, environment, and financial materiality "
            "are then layered on top."
        ),
        "tip": "The full pipeline typically takes 3–6 seconds — most of the time is the Claude Haiku API call for semantic extraction.",
    },
    {
        "icon": "📊",
        "section": "Results → Risk Score",
        "title": "Understanding the Risk Score & Priority",
        "body": (
            "The main output is a <b>0–100 Risk Score</b>, grouped into four bands:<br>"
            "<b>🔴 Critical ≥75</b> — Immediate partner escalation required<br>"
            "<b>🟠 High 55–74</b> — Urgent remediation; include in management letter<br>"
            "<b>🟡 Medium 35–54</b> — Address within 30 days<br>"
            "<b>🟢 Low &lt;35</b> — Monitor and track<br><br>"
            "Each band maps to a <b>PwC Priority (P1–P5)</b>. The interactive pip-scale below "
            "the score highlights your finding's priority and shows the exact audit guidance "
            "(sign-off requirements, escalation steps, management response obligations).<br><br>"
            "The three-step <b>priority chain</b> shows how each adjustment layer affected the "
            "final priority: Base → Financial Adj → Prior Year Escalation."
        ),
        "tip": "Click on any step in the priority chain to see what triggered that adjustment.",
    },
    {
        "icon": "🤖",
        "section": "Results → AI Signals",
        "title": "LLM Semantic Signals & Cyber Risk Flags",
        "body": (
            "Two sections explain what the AI 'read' from your text:<br><br>"
            "<b>Cyber Risk Flags</b> (keyword-based) — six binary flags detected from specific "
            "audit terms: Unauthorised Access, Data Loss, Privilege Escalation, No Logging, "
            "Weak Credentials, and Quantity Finding (e.g., '8 out of 20 cases').<br><br>"
            "<b>LLM Semantic Signals</b> — ten scores extracted by Claude Haiku from the "
            "full free-text. These capture nuance that keywords alone can't:<br>"
            "&nbsp;&nbsp;– <em>Violation Rate</em>: how many exceptions were found?<br>"
            "&nbsp;&nbsp;– <em>Finding Confirmed</em>: was the issue actually verified?<br>"
            "&nbsp;&nbsp;– <em>Compensating Control</em>: is there a mitigating control?<br>"
            "&nbsp;&nbsp;– <em>SoD Conflict</em>: is there a segregation of duties issue?<br>"
            "&nbsp;&nbsp;– <em>Evidence Strength</em>: how robust is the audit evidence?"
        ),
        "tip": "Green dots in the Semantic Signals grid indicate active/elevated signals. Grey dots mean the signal is inactive or neutral.",
    },
    {
        "icon": "🔍",
        "section": "Results → Explainability",
        "title": "SHAP Feature Attribution",
        "body": (
            "<b>SHAP</b> (SHapley Additive exPlanations) is an industry-standard technique for "
            "explaining machine-learning predictions. It answers: <em>'Which features pushed "
            "the score up or down, and by how much?'</em><br><br>"
            "The bar chart shows the <b>top 10 features</b> by impact:<br>"
            "&nbsp;&nbsp;– <b>Blue bars →</b> pushed the score <em>higher</em> (increased risk)<br>"
            "&nbsp;&nbsp;– <b>Red bars →</b> pushed the score <em>lower</em> (reduced risk)<br>"
            "&nbsp;&nbsp;– Longer bars = more influence<br><br>"
            "This makes every score <b>fully auditable</b> — you can always justify the rating "
            "by pointing to the specific features the model weighted most heavily."
        ),
        "tip": "SHAP values are calculated independently for every finding — the same observation in different contexts may produce different explanations.",
    },
    {
        "icon": "📈",
        "section": "Results → Benchmark",
        "title": "Industry Benchmark Panel",
        "body": (
            "The benchmark panel compares your finding against <b>historical audit data</b> "
            "from the same control domain and industry.<br><br>"
            "Key metrics shown:<br>"
            "&nbsp;&nbsp;– <b>Percentile rank</b>: e.g., 'Top 15% most severe' means this "
            "finding scores higher than 85% of similar historical findings<br>"
            "&nbsp;&nbsp;– <b>Delta vs industry average</b>: how many points above/below the mean<br>"
            "&nbsp;&nbsp;– <b>P25 / P75 / P90</b>: the distribution of scores in this segment<br><br>"
            "This helps auditors contextualise findings — a score of 60 might be typical "
            "for PAM findings in Financial Services, but unusually high in Retail."
        ),
        "tip": "Benchmarks are based on 977 scored findings across 20 domain × industry combinations from the training dataset.",
    },
    {
        "icon": "🛠️",
        "section": "Results → Remediation",
        "title": "Remediation Roadmap",
        "body": (
            "The <b>Remediation Roadmap</b> provides 3–5 targeted, actionable recommendations "
            "based on the specific combination of domain, active flags, and priority level.<br><br>"
            "Each action card shows:<br>"
            "&nbsp;&nbsp;– <b>Action title</b> and detailed description<br>"
            "&nbsp;&nbsp;– <b>Feasibility</b>: Quick Win, Medium Effort, or Strategic<br>"
            "&nbsp;&nbsp;– <b>Timeline</b>: how long the remediation typically takes<br><br>"
            "Recommendations are deterministic and domain-specific — PAM findings get access "
            "management actions, CM findings get change control actions, and so on. "
            "Cross-domain actions (e.g., escalation procedures for Critical findings) are added "
            "automatically when relevant."
        ),
        "tip": "For P1 and P2 findings, the roadmap will always include an escalation or immediate remediation action.",
    },
    {
        "icon": "✅",
        "section": "Results → Sign-off",
        "title": "Sign-off Readiness Checklist",
        "body": (
            "For <b>P1 and P2 findings</b>, the <em>Sign-off Readiness</em> section appears "
            "with a context-driven checklist that the auditor must complete before the "
            "engagement can be signed off.<br><br>"
            "Checklist items vary based on: priority level, whether it's a repeat finding, "
            "financial materiality, and whether compensating controls exist. Examples:<br>"
            "&nbsp;&nbsp;– Management action plan with named owner and target date<br>"
            "&nbsp;&nbsp;– Evidence of re-testing (if compensating controls are claimed)<br>"
            "&nbsp;&nbsp;– Partner notification documented in the engagement file<br>"
            "&nbsp;&nbsp;– Formal escalation if a prior-year finding is still unresolved<br><br>"
            "A <b>live progress bar</b> tracks how many checklist items have been completed."
        ),
        "tip": "Sign-off checklist items are saved per scoring session. Completing items here does not update any external system.",
    },
    {
        "icon": "💬",
        "section": "Results → AI Chat",
        "title": "Ask AI — Deep-dive Chat",
        "body": (
            "Click <b>Ask AI</b> below any result to open an AI-powered chat window. "
            "The assistant is fully briefed on your specific finding — the score, all SHAP "
            "drivers, LLM signals, financial context, and session history — so you can ask "
            "natural-language questions without any copy-pasting.<br><br>"
            "Example questions you can ask:<br>"
            "&nbsp;&nbsp;– <em>'Why did this score as High rather than Medium?'</em><br>"
            "&nbsp;&nbsp;– <em>'What is the difference between SoD and access revocation risk?'</em><br>"
            "&nbsp;&nbsp;– <em>'Draft a management action plan for this finding.'</em><br>"
            "&nbsp;&nbsp;– <em>'How does this compare to our other findings this session?'</em><br><br>"
            "The AI responds using <b>PwC audit language</b> and never fabricates information "
            "not present in the scoring result."
        ),
        "tip": "The chat window is tied to the current finding. Scoring a new finding resets the chat so the AI always has the right context.",
    },
    {
        "icon": "⬇️",
        "section": "Results → Export",
        "title": "Exporting Results & Session History",
        "body": (
            "Every scored finding can be exported as a structured <b>JSON file</b> using the "
            "Export button. The JSON includes every field: raw score, adjusted score, all "
            "LLM signals, SHAP values, financial context, and priority chain — "
            "ready for import into audit management systems or further analysis.<br><br>"
            "The <b>Session History</b> panel in the left sidebar shows the last five findings "
            "scored in the current session, with their band and domain, so you can keep track "
            "of a full engagement's findings side by side.<br><br>"
            "When two or more findings have been scored, the <b>Control Environment Overview</b> "
            "section also appears at the bottom, giving a cross-finding risk summary for the "
            "entire session."
        ),
        "tip": "You have now completed the full tour! Click 'End Tour' to start scoring, or use the Quick Examples to try the tool immediately.",
    },
]


# ── Helper functions ───────────────────────────────────────────────────────────
def assign_band(score: float) -> str:
    for threshold, band in BAND_THRESHOLDS:
        if score >= threshold:
            return band
    return "Low"

def assign_pwc_priority(score: float) -> int:
    """Map 0-100 risk score to PwC priority scale (1 = highest, 5 = lowest)."""
    if score >= 75: return 1
    if score >= 55: return 2
    if score >= 35: return 3
    if score >= 15: return 4
    return 5


def _build_session_summary(current_r: dict) -> str:
    """Return a compact text summary of all session findings except the current one."""
    import streamlit as _st
    history = _st.session_state.get("history", [])
    others = [rec for rec in history if rec is not current_r]
    if not others:
        return "  No other findings scored in this session yet."
    lines = []
    for i, rec in enumerate(others, 1):
        fs = rec.get("env_adjusted_score", rec.get("it_adjusted_score", rec.get("risk_score", 0)))
        fb = rec.get("env_adjusted_band", rec.get("it_adjusted_band", rec.get("risk_band", "Low")))
        fp = rec.get("escalated_pwc_priority") or rec.get("fin_adjusted_priority") or assign_pwc_priority(fs)
        lines.append(
            f"  {i}. {rec.get('control_domain','?')} · {rec.get('application','?')} · "
            f"{rec.get('industry','?')} — Score {fs} ({fb}) · P{fp}"
        )
    return "\n".join(lines)


def build_chat_system_prompt(r: dict, observation: str, risk: str) -> str:
    """Build a rich system prompt giving the LLM full scoring context."""
    shap_top = ""
    if r.get("shap_values"):
        sorted_shap = sorted(r["shap_values"].items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        shap_top = "\n".join(f"  • {k}: {v:+.3f}" for k, v in sorted_shap)
    llm_feats = "\n".join(f"  • {k}: {v}" for k, v in r.get("llm_features", {}).items())
    flags = r.get("structured_flags", {})
    active_flags = [k for k, v in flags.items() if v == 1]
    pwc_p = assign_pwc_priority(r["risk_score"])
    pwc_desc = {1:"Critical – Immediate escalation required", 2:"High – Urgent remediation",
                3:"Medium – Address in near term", 4:"Low – Monitor and track", 5:"Minimal – Advisory note"}[pwc_p]
    repeat_section = ""
    if r.get("prior_year_finding"):
        _raw_p  = assign_pwc_priority(r["risk_score"])
        _esc_p  = r.get("escalated_pwc_priority", _raw_p)
        _py_p   = r.get("prior_year_priority", "Unknown")
        repeat_section = f"""
=== PRIOR YEAR / REPEAT FINDING ===
⚠️  This control deficiency was ALSO RAISED IN A PRIOR YEAR AUDIT.
Prior Year Priority : P{_py_p}
Model-Derived Priority : P{_raw_p}
Escalated Priority  : P{_esc_p}  ← effective priority shown to auditor
Escalation Reason   : Repeat findings carry higher audit significance because management
                      was already made aware and remediation has not been completed.
When discussing this finding, emphasise the recurrence, management accountability,
and the increased likelihood of a material weakness classification if unresolved.
"""

    return f"""You are an expert IT audit AI assistant at PwC Denmark, specialising in IT General Controls (ITGC) and cyber risk.
A PwC auditor has just run the ITGC Cyber Risk Scoring Model and you must help them understand the result in depth.

=== SCORED FINDING ===
Observation:
{observation}

Risk Statement:
{risk}

=== SCORING RESULT ===
Risk Score : {r['risk_score']} / 100
Risk Band  : {r['risk_band']}
PwC Priority: P{pwc_p} — {pwc_desc}
Predicted Class: {r['predicted_class']}
Class Probabilities:
  • High   : {r['p_high']*100:.1f}%
  • Medium : {r['p_medium']*100:.1f}%
  • Low    : {r['p_low']*100:.1f}%

Control Domain : {r['control_domain']}
Application    : {r['application']}
Industry       : {r['industry']}

IT Dependency Context:
  • Financial processes dependent : {r.get('it_dep_count', 'Not specified')}
  • Interface / integration type  : {r.get('it_interface_type', 'Not specified')}
  • IT dependency score adjustment: +{r.get('it_dep_adjustment', 0)} pts (post-model multiplier)
  • IT-adjusted score             : {r.get('it_adjusted_score', r['risk_score'])}

Client Environment Profile:
  • Deployment model              : {r.get('env_deploy', 'Not specified')}
  • System age                    : {r.get('env_age', 'Not specified')}
  • Audit scope                   : {r.get('env_scope', 'Not specified')}
  • Environment score adjustment  : {r.get('env_score_adj', 0):+d} pts
  • Final adjusted score          : {r.get('env_adjusted_score', r.get('it_adjusted_score', r['risk_score']))}

Financial Materiality & Impact:
  • Financial impact type         : {r.get('fin_impact_type', 'Not specified')}
  • Materiality level             : {r.get('fin_materiality', 'Not specified')}
  • Audit exposure classification : {r.get('fin_sev_label', '—')}
  • Priority adjustment           : {r.get('fin_priority_adj', 0):+d} level(s) (negative = escalation)
  • Priority after financial adj  : P{r.get('fin_adjusted_priority', '—')}
  • Recommended audit action      : {r.get('fin_action_text', '—')}

{repeat_section}
=== INDUSTRY BENCHMARK CONTEXT ===
{(lambda bm: f'''  • Peer group                    : {r.get("control_domain","")} findings in {r.get("industry","")} (n={bm["n"]})
  • Industry average score        : {bm["mean"]} (median: {bm["median"]})
  • This finding vs average       : {bm["delta"]:+.1f} points
  • Percentile rank               : Top {bm["top_pct"]}% most severe (scores higher than {bm["pct_rank"]}% of peers)
  • P25 / P75 / P90               : {bm["p25"]} / {bm["p75"]} / {bm["p90"]}''' if (bm := compute_benchmark(r.get("it_adjusted_score", r.get("risk_score", 0)), r.get("control_domain",""), r.get("industry",""))) else "  Not available")}

=== KEY RISK DRIVERS (SHAP — top 5) ===
{shap_top if shap_top else "  Not available"}

=== LLM SEMANTIC SIGNALS ===
{llm_feats}

=== ACTIVE CYBER RISK FLAGS ===
{', '.join(active_flags) if active_flags else 'None'}

=== SESSION CONTEXT (other findings scored this engagement) ===
{_build_session_summary(r)}

=== YOUR ROLE ===
1. When the auditor opens this chat, provide a clear, structured explanation of WHY this score was assigned.
2. Reference specific signals (SHAP drivers, LLM features, flags) to justify the score.
3. Frame everything in PwC audit language — use terms like "control deficiency", "remediation priority", "management action".
4. Answer any follow-up questions the auditor asks about the finding, score, methodology, or recommended actions.
5. Be concise but thorough. Use bullet points and structure where helpful.
6. Never make up information not present in the context above.
7. When the auditor asks about the broader engagement picture or other findings, reference the session context below."""


def call_chat_llm(messages: list, api_key: str) -> str:
    """Send conversation to Claude and return assistant reply."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Strip any extra fields (e.g. 'ts') — Anthropic API only accepts 'role' + 'content'
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages[1:]                    # skip system prompt entry
        ]
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=messages[0]["content"],           # system prompt is first entry
            messages=api_messages,
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"⚠️ Error contacting AI: {e}"


def _md_to_html(text: str) -> str:
    """Lightweight markdown → HTML converter for chat bubbles."""
    import html as hl, re
    t = hl.escape(text)
    # headings
    t = re.sub(r'^### (.+)$', r'<h4 style="margin:8px 0 4px;font-size:0.85rem;color:#a8c0e8;">\1</h4>', t, flags=re.MULTILINE)
    t = re.sub(r'^## (.+)$',  r'<h3 style="margin:10px 0 4px;font-size:0.9rem;color:#c0d4f5;">\1</h3>', t, flags=re.MULTILINE)
    t = re.sub(r'^# (.+)$',   r'<h2 style="margin:10px 0 4px;font-size:1rem;color:#d0e0ff;">\1</h2>',  t, flags=re.MULTILINE)
    # bold / italic
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', t)
    # horizontal rule
    t = re.sub(r'^---+$', r'<hr style="border:none;border-top:1px solid #1e3566;margin:8px 0;">', t, flags=re.MULTILINE)
    # bullet list items (-, •, *)
    t = re.sub(r'^[\-\*•] (.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)
    t = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul style="margin:4px 0 4px 16px;padding:0;">{m.group(0)}</ul>', t, flags=re.DOTALL)
    # line breaks
    t = t.replace('\n', '<br>')
    # clean up doubled <br> around block elements
    t = re.sub(r'(<br>)+(<h[2-4])', r'\2', t)
    t = re.sub(r'(</h[2-4]>)(<br>)+', r'\1', t)
    t = re.sub(r'(<br>)+(<ul)', r'\2', t)
    t = re.sub(r'(</ul>)(<br>)+', r'\1', t)
    t = re.sub(r'(<br>)+(<hr)', r'\2', t)
    return t


def render_chat_component(msgs: list) -> str:
    """Return a complete self-contained HTML document for the chat iframe."""
    bubbles_html = []
    for m in msgs:
        if m["role"] == "system":
            continue
        ts = m.get("ts", "")
        if m["role"] == "assistant":
            body = _md_to_html(m["content"])
            bubbles_html.append(f"""
            <div class="row-ai">
              <div class="avatar">🤖</div>
              <div class="col">
                <div class="bubble-ai">{body}</div>
                <div class="ts ts-ai">{ts}</div>
              </div>
            </div>""")
        else:
            import html as hl
            body = hl.escape(m["content"]).replace("\n", "<br>")
            bubbles_html.append(f"""
            <div class="row-user">
              <div class="col">
                <div class="bubble-user">{body}</div>
                <div class="ts ts-user">{ts}</div>
              </div>
            </div>""")

    bubbles_joined = "\n".join(bubbles_html)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0b1220;
    font-family: 'DM Sans', sans-serif;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-height: 100%;
  }}
  .row-ai   {{ display:flex; justify-content:flex-start; align-items:flex-end; gap:8px; }}
  .row-user {{ display:flex; justify-content:flex-end;  align-items:flex-end; gap:8px; }}
  .avatar {{
    width:30px; height:30px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#1a56db,#7c3aed);
    display:flex; align-items:center; justify-content:center;
    font-size:0.8rem;
  }}
  .col {{ display:flex; flex-direction:column; max-width:72%; }}
  .bubble-ai {{
    background: #162040;
    border: 1px solid #1e3566;
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px;
    color: #c8d8f0;
    font-size: 0.82rem;
    line-height: 1.65;
    word-break: break-word;
  }}
  .bubble-user {{
    background: linear-gradient(135deg,#0d3b2e,#0a2e24);
    border: 1px solid #1a5c45;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    color: #d4f1e4;
    font-size: 0.82rem;
    line-height: 1.65;
    word-break: break-word;
  }}
  .ts {{ font-size:0.62rem; color:#3a5278; margin-top:4px; }}
  .ts-ai   {{ text-align:left; }}
  .ts-user {{ text-align:right; }}
  strong {{ color:#e2eafc; }}
  em {{ color:#a8c0e8; font-style:italic; }}
  li {{ margin-left:4px; margin-bottom:2px; color:#b0c8e8; }}
  h2,h3,h4 {{ font-family:'DM Sans',sans-serif; }}
</style>
</head>
<body>
{bubbles_joined}
<div id="anchor"></div>
<script>
  // Scroll to bottom reliably after layout is painted
  function scrollToBottom() {{
    var anchor = document.getElementById('anchor');
    if (anchor) {{
      anchor.scrollIntoView({{behavior: 'instant', block: 'end'}});
    }}
  }}
  // Run immediately, then again after a short delay to catch any late reflows
  scrollToBottom();
  requestAnimationFrame(function() {{
    scrollToBottom();
    setTimeout(scrollToBottom, 120);
  }});
</script>
</body>
</html>"""


def render_financial_impact_card(r: dict) -> str:
    """Build the Financial Impact card HTML from result dict."""
    impact   = r.get("fin_impact_type",  "None")
    mat      = r.get("fin_materiality",  "Low")
    sev      = r.get("fin_sev_label",    "Informational")
    action   = r.get("fin_action_text",  "")

    # CSS class keys derived from severity label
    sev_slug = sev.lower().replace(" ", "-")   # e.g. "critical-exposure" → "critical"
    sev_cls  = sev_slug.split("-")[0]           # first word only: "critical"

    # Impact type chip class
    if "Direct" in impact:
        impact_chip_cls, impact_icon = "fin-chip-direct",   "🔴"
    elif "Indirect" in impact:
        impact_chip_cls, impact_icon = "fin-chip-indirect", "🟡"
    else:
        impact_chip_cls, impact_icon = "fin-chip-none",     "⬜"

    # Materiality chip class
    mat_chip_cls = {"High": "fin-mat-high", "Medium": "fin-mat-medium", "Low": "fin-mat-low"}.get(mat, "fin-mat-low")
    mat_icon     = {"High": "▲", "Medium": "◆", "Low": "▼"}.get(mat, "▼")

    return f"""
    <div class="fin-impact-card sev-{sev_cls}">
      <div class="fin-impact-left">
        <div class="fin-chip-row">
          <span class="fin-chip {impact_chip_cls}">{impact_icon} {impact}</span>
        </div>
        <div class="fin-chip-row">
          <span class="fin-chip {mat_chip_cls}">{mat_icon} {mat} Materiality</span>
        </div>
      </div>
      <div class="fin-impact-right">
        <div class="fin-sev-label sev-{sev_cls}">💰 {sev}</div>
        <div class="fin-action-text">{action}</div>
      </div>
    </div>"""


def compute_it_dep_adjustment(count_label: str, interface_label: str) -> float:
    """Post-processing score adjustment based on IT dependency complexity.
    Adjustment = interface_weight × volume_multiplier (max +13.5 pts).
    Standard reports always return 0 regardless of volume.
    """
    weight     = IT_INTERFACE_WEIGHTS.get(interface_label, 0)
    multiplier = IT_VOLUME_MULTIPLIERS.get(count_label, 1.0)
    return round(weight * multiplier, 1)


def band_class(band: str) -> str:
    return {"Critical": "band-critical", "High": "band-high",
            "Medium": "band-medium", "Low": "band-low"}.get(band, "band-low")


@st.cache_resource
def load_model_artefacts():
    """Load saved model artefacts — cached so only loaded once."""
    try:
        import joblib
        artefact_dir = "model_artefacts_v2"
        if not os.path.exists(artefact_dir):
            return None, None, None, None
        model   = joblib.load(f"{artefact_dir}/xgb_model.pkl")
        scaler  = joblib.load(f"{artefact_dir}/scaler.pkl")
        le      = joblib.load(f"{artefact_dir}/label_encoder.pkl")
        indices = joblib.load(f"{artefact_dir}/class_indices.pkl")
        feat_cols = joblib.load(f"{artefact_dir}/feature_columns.pkl")
        return model, scaler, le, indices, feat_cols
    except Exception as e:
        return None, None, None, None, None


def extract_llm_features(observation: str, risk: str, api_key: str) -> dict:
    """Call Claude Haiku to extract 10 semantic features."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = EXTRACTION_PROMPT.format(
            observation=str(observation)[:2000],
            risk=str(risk)[:1000]
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        features = json.loads(raw.strip())
        for k in NEUTRAL_DEFAULTS:
            if k not in features:
                features[k] = NEUTRAL_DEFAULTS[k]
        return features, None
    except ImportError:
        return NEUTRAL_DEFAULTS.copy(), "anthropic package not installed. Run: pip install anthropic"
    except Exception as e:
        return NEUTRAL_DEFAULTS.copy(), str(e)


def extract_structured_features(observation, risk, control_domain, application, industry, app_type):
    """Replicate Phase 2a structured feature extraction."""
    row = pd.DataFrame([{
        'Observation': observation, 'Risk': risk,
        'Control Domain': control_domain, 'Application': application,
        'Industry': industry, 'Application Type': app_type
    }])
    combined = (row['Observation'] + ' ' + row['Risk']).str.lower()

    feats = {}
    feats['obs_bullet_count']     = int(observation.count('\n'))
    feats['high_sev_kw_count']    = sum(1 for kw in HIGH_SEV_KEYWORDS if kw in (observation + ' ' + risk).lower())
    feats['has_quantity_finding'] = 1 if QUANTITY_PATTERN.search(observation + ' ' + risk) else 0
    feats['flag_unauth_access']   = 1 if re.search(r'unauthori[sz]ed access|former employ|post.termination|active login', (observation + ' ' + risk).lower()) else 0
    feats['flag_data_loss']       = 1 if re.search(r'data loss|alterat|erroneous|integrity|financial posting', (observation + ' ' + risk).lower()) else 0
    feats['flag_priv_escalation'] = 1 if re.search(r'privilege|escalat|admin|segregation of duties|sod violation', (observation + ' ' + risk).lower()) else 0
    feats['flag_no_logging']      = 1 if re.search(r'audit trail|logging|traceability|incident detect|no auditing', (observation + ' ' + risk).lower()) else 0
    feats['flag_weak_credentials']= 1 if re.search(r'brute.?force|password|credential|default pass|weak pass', (observation + ' ' + risk).lower()) else 0
    feats['app_tier']             = APP_TIER.get(application, 2)

    for d in ['BR', 'CM', 'NJL', 'PAM']:
        feats[f'domain_{d}'] = int(control_domain == d)
    for ind in ['Energy & Utilities', 'Financial Services', 'Manufacturing', 'Pharmaceuticals', 'Retail']:
        feats[f'industry_{ind}'] = int(industry == ind)
    for at in ['Generic / Home-grown', 'Non-Generic']:
        feats[f'apptype_{at}'] = int(app_type == at)

    return feats


def run_prediction(observation, risk, control_domain, application, industry, app_type, api_key):
    """Full predict_risk_v2 pipeline."""
    model, scaler, le, indices, feat_cols = load_model_artefacts()

    if model is None:
        return None, "❌ Model artefacts not found. Place `model_artefacts_v2/` folder next to app.py."

    # LLM features
    llm_feats, llm_err = extract_llm_features(observation, risk, api_key)
    if llm_err:
        llm_feats = NEUTRAL_DEFAULTS.copy()

    # Structured features
    struct = extract_structured_features(observation, risk, control_domain, application, industry, app_type)

    # Combine
    feats = {**struct, **llm_feats}
    feats_df = pd.DataFrame([feats])
    X_new = feats_df.reindex(columns=feat_cols, fill_value=0)
    X_new_scaled = pd.DataFrame(scaler.transform(X_new), columns=X_new.columns)

    # Predict
    probs = model.predict_proba(X_new_scaled)[0]
    idx_low    = indices['idx_low']
    idx_medium = indices['idx_medium']
    idx_high   = indices['idx_high']

    p_low    = float(probs[idx_low])
    p_medium = float(probs[idx_medium])
    p_high   = float(probs[idx_high])

    llm_sev = llm_feats.get('llm_severity_estimate', 0.5)
    llm_neg = llm_feats.get('negation_flag', 0)

    if (p_medium > 0.10 and llm_sev >= 0.45 and llm_neg == 0 and p_high < 0.50):
        pred_class = 'Medium'
        score = p_low * 20 + p_medium * 55 + p_high * 90
        if score < 40:
            score = score * 0.3 + 55 * 0.7
    else:
        pred_class = le.inverse_transform(model.predict(X_new_scaled))[0]
        score = p_low * 20 + p_medium * 55 + p_high * 90

    # SHAP
    shap_values = None
    try:
        import shap
        explainer  = shap.TreeExplainer(model)
        sv         = explainer.shap_values(X_new_scaled)
        # sv shape: [n_classes, n_samples, n_features] or [n_samples, n_features, n_classes]
        if isinstance(sv, list):
            sv_high = sv[idx_high][0]
        else:
            sv_high = sv[0, :, idx_high]
        shap_values = dict(zip(feat_cols, sv_high))
    except Exception:
        pass

    result = {
        "risk_score":             round(score, 1),
        "risk_band":              assign_band(score),
        "predicted_class":        pred_class,
        "p_low":                  round(p_low, 3),
        "p_medium":               round(p_medium, 3),
        "p_high":                 round(p_high, 3),
        "llm_features":           llm_feats,
        "structured_flags": {
            "flag_unauth_access":    struct.get("flag_unauth_access", 0),
            "flag_data_loss":        struct.get("flag_data_loss", 0),
            "flag_priv_escalation":  struct.get("flag_priv_escalation", 0),
            "flag_no_logging":       struct.get("flag_no_logging", 0),
            "flag_weak_credentials": struct.get("flag_weak_credentials", 0),
            "has_quantity_finding":  struct.get("has_quantity_finding", 0),
            "high_sev_kw_count":     struct.get("high_sev_kw_count", 0),
            "app_tier":              struct.get("app_tier", 2),
        },
        "shap_values":            shap_values,
        "llm_error":              llm_err,
        "control_domain":         control_domain,
        "application":            application,
        "industry":               industry,
        "observation_snippet":    observation[:80] + ("..." if len(observation) > 80 else ""),
    }
    return result, None


def render_probability_bars(p_low, p_medium, p_high):
    bars_html = ""
    for label, prob, color in [
        ("High", p_high, "linear-gradient(90deg,#b91c1c,#ef4444)"),
        ("Medium", p_medium, "linear-gradient(90deg,#b45309,#f59e0b)"),
        ("Low", p_low, "linear-gradient(90deg,#065f46,#10b981)"),
    ]:
        pct = prob * 100
        bars_html += f"""
        <div class="prob-row">
          <div class="prob-label">
            <span>{label}</span>
            <span style="color:#c4d4f0;font-weight:600;">{pct:.1f}%</span>
          </div>
          <div class="prob-bar-bg">
            <div class="prob-bar-fill" style="width:{pct}%;background:{color};"></div>
          </div>
        </div>"""
    return bars_html


# ── Remediation Action Library ─────────────────────────────────────────────────
# Each entry: (title, detail, feasibility, timeline)
# feasibility : "Quick Win" | "Medium Effort" | "Complex"
# timeline    : "Immediate" | "30 days" | "60–90 days"
_R = {
    # ── PAM ────────────────────────────────────────────────────────────────────
    ("PAM","unauth_access"):        ("Disable all identified unauthorized accounts", "Lock or revoke the specific accounts named in the observation. Confirm session termination and document evidence of disablement with timestamps for the working paper.", "Quick Win", "Immediate"),
    ("PAM","priv_escalation"):      ("Apply least-privilege model to all privileged accounts", "Conduct an access-rights review and remove excessive privileges. Implement role-based access control (RBAC) with an approval workflow for any privilege-elevation requests.", "Medium Effort", "30 days"),
    ("PAM","no_logging"):           ("Enable audit logging for all privileged account activity", "Configure logging for all administrative actions — login, privilege use, configuration changes. Forward logs to a SIEM and define a retention policy.", "Quick Win", "30 days"),
    ("PAM","weak_credentials"):     ("Enforce MFA on all privileged accounts", "Mandate multi-factor authentication for every account with elevated access. Reset passwords and revoke any compromised credentials immediately.", "Quick Win", "Immediate"),
    ("PAM","data_loss"):            ("Assess data exposure from unauthorized privileged access", "Review audit logs to identify data accessed or exported by affected accounts. Notify the Data Protection Officer if sensitive data was exfiltrated.", "Medium Effort", "30 days"),
    ("PAM","sod_conflict"):         ("Segregate privileged account administration from approval roles", "No individual should be able to create and approve their own access. Separate the user-administration function from the access-approval function.", "Medium Effort", "30 days"),
    ("PAM","access_revocation_fail"):("Automate leaver process integration with IAM system", "Integrate the HR offboarding workflow directly with the Identity and Access Management system to trigger automatic account disablement on the employee exit date.", "Complex", "60–90 days"),
    ("PAM","systemic"):             ("Redesign the access governance programme", "The systemic nature of violations indicates a process breakdown. Commission a full access-governance review and implement periodic access-recertification campaigns.", "Complex", "60–90 days"),
    ("PAM","baseline_1"):           ("Implement quarterly privileged access certification", "Establish a formal certification process where application owners review and certify all privileged accounts every quarter.", "Medium Effort", "30 days"),
    ("PAM","baseline_2"):           ("Deploy PAM tool with session recording", "Implement a Privileged Access Management solution to vault credentials, record privileged sessions, and enforce just-in-time access for all admin accounts.", "Complex", "60–90 days"),

    # ── NJL ────────────────────────────────────────────────────────────────────
    ("NJL","unauth_access"):        ("Terminate and block unauthorized network jump sessions", "Immediately disconnect identified unauthorized connections. Review firewall rules and jump-server ACLs to close the access path and prevent recurrence.", "Quick Win", "Immediate"),
    ("NJL","no_logging"):           ("Implement centralized logging for all jump-server sessions", "Enable session logging on all network jump servers capturing source, duration, commands executed, and files transferred. Integrate with SIEM.", "Medium Effort", "30 days"),
    ("NJL","weak_credentials"):     ("Rotate jump-server credentials and enforce certificate-based auth", "Immediately rotate all shared credentials. Replace password-based authentication with certificate-based or SSH-key authentication on all jump servers.", "Quick Win", "Immediate"),
    ("NJL","priv_escalation"):      ("Restrict jump-server access to approved network administrators only", "Revoke access for all non-network-administration roles. Implement just-in-time access with time-limited tokens for emergency requests.", "Medium Effort", "30 days"),
    ("NJL","sod_conflict"):         ("Separate network administration from security monitoring responsibilities", "Ensure individuals who administer jump-server access are not the same individuals monitoring network security events.", "Medium Effort", "30 days"),
    ("NJL","systemic"):             ("Redesign network access control architecture", "The systemic pattern indicates the current jump-server architecture is not fit for purpose. Commission a network-segmentation review and implement zero-trust network access.", "Complex", "60–90 days"),
    ("NJL","baseline_1"):           ("Validate all active jump-server connections against approved tickets", "Pull an inventory of active and recent network jump sessions. Verify every connection is linked to an approved change request or operational ticket.", "Quick Win", "Immediate"),
    ("NJL","baseline_2"):           ("Implement a jump-access request and approval workflow", "Require all network jump access to be pre-approved via a formal change request with time-limited, purpose-specific access tokens.", "Medium Effort", "30 days"),

    # ── CM ─────────────────────────────────────────────────────────────────────
    ("CM","unauth_access"):         ("Initiate change freeze and investigate unauthorized changes", "Halt all non-emergency changes. Review what was modified, assess business impact, and roll back unauthorized changes where possible.", "Quick Win", "Immediate"),
    ("CM","sod_conflict"):          ("Enforce four-eyes principle across all change types", "No individual should request, develop, test, and promote a change to production without independent review. Implement mandatory approver assignment in the ITSM tool.", "Medium Effort", "30 days"),
    ("CM","no_logging"):            ("Enable end-to-end change audit trail", "Capture requestor, reviewer, approver, tester, and deployer for every change — with timestamps and configuration diffs — in a tamper-evident log.", "Quick Win", "30 days"),
    ("CM","systemic"):              ("Implement automated workflow gates in the change management tool", "The systemic pattern shows the current process is not consistently enforced. Configure ITSM workflow gates that block promotion without mandatory approvals.", "Complex", "60–90 days"),
    ("CM","priv_escalation"):       ("Restrict production deployment rights to a dedicated release role", "Remove production-deployment access from developers and testers. Create a release-management role solely responsible for all production promotions.", "Medium Effort", "30 days"),
    ("CM","weak_credentials"):      ("Rotate and harden service account credentials in deployment pipelines", "Review all service accounts used in CI/CD pipelines. Rotate credentials, enforce least-privilege permissions, and implement secrets management.", "Medium Effort", "30 days"),
    ("CM","access_revocation_fail"):("Remove change-approval rights from departed or transferred staff", "Audit the change-approval authority list against current HR records. Revoke rights from individuals who have left the team or the organisation.", "Quick Win", "Immediate"),
    ("CM","baseline_1"):            ("Mandate independent review for all financial system changes", "Require at least one approver not involved in development or testing for all changes to financially significant systems.", "Medium Effort", "30 days"),
    ("CM","baseline_2"):            ("Implement post-implementation review for high-risk changes", "Define a post-implementation review process including a 48-hour monitoring window and sign-off from the application owner.", "Medium Effort", "60–90 days"),

    # ── BR ─────────────────────────────────────────────────────────────────────
    ("BR","data_loss"):             ("Verify backup integrity and perform a test restoration immediately", "Confirm the most recent backup set is complete and uncorrupted. Perform an immediate test restoration to a non-production environment to validate recoverability.", "Quick Win", "Immediate"),
    ("BR","no_logging"):            ("Implement automated backup-completion monitoring and alerting", "Configure automated alerting for failed or incomplete backup jobs routed to an on-call team with a defined response SLA.", "Quick Win", "30 days"),
    ("BR","systemic"):              ("Implement a formal backup governance framework with DR testing", "Define backup SLAs, RPO, and RTO targets. Schedule periodic disaster-recovery tests and obtain business-owner sign-off on test results.", "Complex", "60–90 days"),
    ("BR","unauth_access"):         ("Restrict backup storage access to authorised administrators only", "Review who has access to backup storage, tapes, and cloud vaults. Revoke access for anyone outside the defined backup-administration role.", "Quick Win", "30 days"),
    ("BR","priv_escalation"):       ("Segregate backup administration from production system administration", "Ensure backup operators do not have unrestricted access to production data. Use dedicated backup service accounts with limited scope.", "Medium Effort", "30 days"),
    ("BR","baseline_1"):            ("Enforce backup documentation and ticketing standards", "Require all backup completion reports to be logged in the ticketing system — not distributed by email — and retained as audit evidence.", "Quick Win", "30 days"),
    ("BR","baseline_2"):            ("Establish a backup-status monitoring dashboard for the operations team", "Implement a real-time dashboard showing backup success rate, last successful restore date, and RTO/RPO compliance.", "Medium Effort", "60–90 days"),
}

# Cross-domain actions keyed by trigger name
_R_CROSS = {
    "critical_band":     ("Notify senior management and initiate formal incident response", "The severity warrants immediate escalation. Notify the engagement partner and client senior management. Document as a significant deficiency in the management letter.", "Quick Win", "Immediate"),
    "repeat_finding":    ("Formalise management remediation commitment with milestone tracking", "This is a repeat finding. Obtain a written management remediation plan with defined milestone dates and a named owner responsible for closure.", "Medium Effort", "30 days"),
    "direct_fs_high":    ("Engage independent specialist for control re-assessment", "Given the direct financial-statement impact and high materiality, obtain independent assurance that the control has been effectively remediated before audit sign-off.", "Complex", "60–90 days"),
    "compensating_ctrl": ("Formalise and test the compensating control as a permanent mitigant", "Document the compensating control in the control framework, assign an owner, and schedule periodic testing to confirm its continued effectiveness.", "Medium Effort", "30 days"),
}

_TL_ORDER = {"Immediate": 0, "30 days": 1, "60–90 days": 2}
_FW_ORDER = {"Quick Win": 0, "Medium Effort": 1, "Complex": 2}


def generate_remediation_roadmap(r: dict) -> list:
    """Select 3–5 deterministic remediation actions from the library based on result flags."""
    domain = r.get('control_domain', 'PAM')
    band   = r.get('it_adjusted_band', r.get('risk_band', 'Low'))
    sf     = r.get('structured_flags', {})
    lf     = r.get('llm_features', {})

    actions, seen = [], set()

    def _add(key, entry):
        if entry and key not in seen:
            seen.add(key)
            title, detail, fw, tl = entry
            actions.append({"title": title, "detail": detail, "feasibility": fw, "timeline": tl})

    # 1. Cross-domain: critical / high band — always first
    if band in ('Critical', 'High'):
        _add("critical_band", _R_CROSS["critical_band"])

    # 2. Structured flag–triggered domain actions
    for flag in ("unauth_access", "data_loss", "priv_escalation", "no_logging", "weak_credentials"):
        if sf.get(f"flag_{flag}", 0):
            _add(f"{domain}_{flag}", _R.get((domain, flag)))

    # 3. LLM signal–triggered domain actions
    for sig, key in (("sod_conflict","sod_conflict"), ("access_revocation_failure","access_revocation_fail"), ("systemic_vs_isolated","systemic")):
        if lf.get(sig, 0):
            _add(f"{domain}_{key}", _R.get((domain, key)))

    # 4. Cross-domain context triggers
    if r.get('prior_year_finding'):
        _add("repeat_finding", _R_CROSS["repeat_finding"])
    if r.get('fin_impact_type','') == 'Direct — Financial Statements' and r.get('fin_materiality','') in ('High','Medium'):
        _add("direct_fs_high", _R_CROSS["direct_fs_high"])
    if lf.get('compensating_control', 0):
        _add("compensating_ctrl", _R_CROSS["compensating_ctrl"])

    # 5. Fill to minimum 3 with domain baselines
    for i in range(1, 4):
        if len(actions) >= 5:
            break
        _add(f"{domain}_baseline_{i}", _R.get((domain, f"baseline_{i}")))

    # Sort: Immediate first, then by feasibility within each timeline group
    actions.sort(key=lambda a: (_TL_ORDER.get(a['timeline'], 3), _FW_ORDER.get(a['feasibility'], 3)))
    return actions[:5]


def build_signoff_checklist(r: dict, pwc_p: int) -> list:
    """
    Return a context-driven list of sign-off checklist items.
    Each item: {id, label, description, mandatory}
    """
    lf   = r.get('llm_features', {})
    sf   = r.get('structured_flags', {})
    band = r.get('it_adjusted_band', r.get('risk_band', 'Low'))
    items = []

    def _item(id_, label, desc, mandatory=True):
        items.append({"id": id_, "label": label, "description": desc, "mandatory": mandatory})

    # ── Always required for P1/P2 ──────────────────────────────────────────────
    _item("mgmt_plan",
          "Management action plan obtained",
          "Written plan with named owner, specific remediation steps, and a signed target completion date.")
    _item("partner_notified",
          "Partner / Director formally notified",
          "Engagement partner and responsible director informed of the finding and its priority classification.")
    _item("retest_scheduled",
          "Re-test of control scheduled",
          "Date confirmed for re-testing the deficient control. Testing scope and responsible team documented.")

    # ── Conditional: Critical band ─────────────────────────────────────────────
    if band == "Critical" or pwc_p == 1:
        _item("escalation_file",
              "Formal escalation documented in engagement file",
              "Significant deficiency or material weakness classification assessed. Documented in the management letter and engagement quality review file.")

    # ── Conditional: direct financial statement impact ─────────────────────────
    if r.get('fin_impact_type', '') == 'Direct — Financial Statements':
        _item("regulatory_assessed",
              "Regulatory notification requirement assessed",
              "Checked whether the deficiency triggers mandatory regulatory disclosure (GDPR, sector regulator, stock exchange rules).",
              mandatory=False)

    # ── Conditional: compensating control identified ───────────────────────────
    if lf.get('compensating_control', 0):
        _item("comp_ctrl_documented",
              "Compensating control formally documented",
              "Compensating control described, owner assigned, and effectiveness testing evidence retained in the working paper file.",
              mandatory=False)

    # ── Conditional: repeat finding ────────────────────────────────────────────
    if r.get('prior_year_finding', False):
        _item("py_closure_evidence",
              "Prior year closure evidence obtained",
              "Management explanation of why the control failed again this year. Written commitment to root-cause remediation rather than point-in-time fix.")

    # ── Conditional: high materiality ─────────────────────────────────────────
    if r.get('fin_materiality', '') == 'High':
        _item("risk_register",
              "Client risk register updated",
              "Deficiency formally logged in the client's enterprise risk register with agreed risk owner and residual risk assessment.",
              mandatory=False)

    return items


def render_signoff_section(r: dict, pwc_p: int) -> None:
    """Render the interactive Sign-off Readiness checklist using native Streamlit widgets."""
    items   = build_signoff_checklist(r, pwc_p)
    n_total = len(items)

    # Namespace per result — widget keys are the source of truth
    _ns = f"so_{r.get('risk_score',0)}_{r.get('control_domain','')}_{r.get('industry','')}"

    # Initialise widget keys on first render so they exist before we read them
    for item in items:
        wk = f"{_ns}_{item['id']}"
        if wk not in st.session_state:
            st.session_state[wk] = False

    # Read counts directly from widget keys — these are already updated by
    # Streamlit before this render function runs, so the value is always current
    n_checked = sum(1 for item in items if st.session_state.get(f"{_ns}_{item['id']}", False))
    pct       = round(100 * n_checked / n_total) if n_total else 0

    # Traffic light
    if pct == 100:
        tl_cls, tl_label, card_cls = "green", "Ready for sign-off", "green"
        fill_color = "#4ade80"
        status_msg = "All sign-off conditions met. Finding may proceed to report."
    elif pct == 0:
        tl_cls, tl_label, card_cls = "red", "Not ready for sign-off", ""
        fill_color = "#f87171"
        status_msg = "No sign-off conditions met. Complete all mandatory items before closing."
    else:
        tl_cls, tl_label, card_cls = "amber", "In progress", "amber"
        fill_color = "#fbbf24"
        status_msg = f"{n_checked} of {n_total} items complete. Resolve remaining items before sign-off."

    pwc_p_label = {1: "P1 — Critical", 2: "P2 — High"}.get(pwc_p, f"P{pwc_p}")

    # ── Card header ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="signoff-card {card_cls}">
  <div class="signoff-header">
    <div class="signoff-tl {tl_cls}"></div>
    <div class="signoff-hdr-text">
      <div class="signoff-title-main">✅ Audit Sign-off Readiness — {pwc_p_label}</div>
      <div class="signoff-subtitle">{tl_label} &nbsp;·&nbsp; {n_checked}/{n_total} items complete</div>
    </div>
  </div>
  <div class="signoff-progress-bar">
    <div class="signoff-progress-fill" style="width:{pct}%;background:{fill_color};"></div>
  </div>
""", unsafe_allow_html=True)

    # ── Checklist items ────────────────────────────────────────────────────────
    # Inject scoped CSS to collapse Streamlit's default inter-row gap for this section
    st.markdown("""
<style>
  /* Tighten the vertical gap between checkbox rows inside the sign-off checklist */
  section[data-testid="stSidebar"] ~ div [data-testid="stVerticalBlock"]
    > [data-testid="stVerticalBlockBorderWrapper"]
    > [data-testid="stVerticalBlock"] {
    gap: 0.1rem;
  }
  [data-testid="stCheckbox"] { padding-bottom: 0 !important; margin-bottom: 0 !important; }
  [data-testid="stCheckbox"] label { padding: 2px 0 !important; }
</style>""", unsafe_allow_html=True)
    for item in items:
        col_check, col_meta, col_chip = st.columns([0.05, 0.78, 0.17])
        wk      = f"{_ns}_{item['id']}"
        checked = st.session_state.get(wk, False)

        with col_check:
            st.checkbox(label="", key=wk, label_visibility="collapsed")

        with col_meta:
            label_cls = "signoff-item-label done" if checked else "signoff-item-label"
            st.markdown(
                f'<div class="{label_cls}">{item["label"]}</div>'
                f'<div class="signoff-item-desc">{item["description"]}</div>',
                unsafe_allow_html=True,
            )

        with col_chip:
            chip_cls = "signoff-req-mandatory" if item['mandatory'] else "signoff-req-conditional"
            chip_lbl = "Required" if item['mandatory'] else "Recommended"
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:center;height:100%;padding-top:4px;">'
                f'<span class="signoff-req-chip {chip_cls}">{chip_lbl}</span></div>',
                unsafe_allow_html=True,
            )

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
  <div class="signoff-footer">
    <div class="signoff-status-text">{status_msg}</div>
    <div class="signoff-count">{pct}% complete</div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_remediation_card(r: dict) -> str:
    """Return HTML for the Remediation Roadmap card."""
    actions = generate_remediation_roadmap(r)
    if not actions:
        return ""

    domain = r.get('control_domain', '')
    band   = r.get('it_adjusted_band', r.get('risk_band', ''))

    _fw_style = {
        "Quick Win":    ("remed-fw", "⚡"),
        "Medium Effort":("remed-me", "⚙"),
        "Complex":      ("remed-cx", "🔧"),
    }
    _tl_cls = {"Immediate": "tl-now", "30 days": "tl-30", "60–90 days": "tl-90"}
    _tl_label_cls = {"Immediate": "remed-tl-now", "30 days": "remed-tl-30", "60–90 days": "remed-tl-90"}

    items_html = ""
    for i, a in enumerate(actions, 1):
        fw_cls, fw_icon = _fw_style.get(a['feasibility'], ("remed-me", "⚙"))
        num_cls   = _tl_cls.get(a['timeline'], "tl-30")
        tl_l_cls  = _tl_label_cls.get(a['timeline'], "remed-tl-30")
        items_html += f"""
  <div class="remed-item">
    <div class="remed-num {num_cls}">{i}</div>
    <div class="remed-content">
      <div class="remed-item-title">{a['title']}</div>
      <div class="remed-detail">{a['detail']}</div>
    </div>
    <div class="remed-badges">
      <span class="remed-badge {fw_cls}">{fw_icon} {a['feasibility']}</span>
      <span class="remed-tl {tl_l_cls}">🕐 {a['timeline']}</span>
    </div>
  </div>"""

    legend = """
  <div class="remed-legend">
    <span class="remed-legend-item"><span class="remed-badge remed-fw" style="font-size:0.58rem;padding:2px 7px;">⚡ Quick Win</span> Low effort, high impact</span>
    <span class="remed-legend-item"><span class="remed-badge remed-me" style="font-size:0.58rem;padding:2px 7px;">⚙ Medium Effort</span> Requires planning</span>
    <span class="remed-legend-item"><span class="remed-badge remed-cx" style="font-size:0.58rem;padding:2px 7px;">🔧 Complex</span> Multi-team initiative</span>
    <span class="remed-legend-item" style="margin-left:auto;">Deterministic · no API key required</span>
  </div>"""

    return f"""
<div class="remed-card">
  <div class="remed-header">
    <div class="remed-title-main">🛠 Remediation Roadmap</div>
    <div class="remed-subtitle">{domain} · {band} · {len(actions)} recommended actions prioritised by urgency</div>
  </div>
  {items_html}
  {legend}
</div>"""


def render_env_overview(history: list, current_result: dict) -> str:
    """Return HTML for the Cross-Control Environment Overview panel.

    Shown when ≥2 findings exist in the session.  Uses the final adjusted
    score (env > it > base) for every record, mirroring the display logic in
    the results card.
    """
    def _final_score(rec: dict) -> float:
        return rec.get("env_adjusted_score",
               rec.get("it_adjusted_score",
               rec.get("risk_score", 0)))

    def _final_band(rec: dict) -> str:
        return rec.get("env_adjusted_band",
               rec.get("it_adjusted_band",
               rec.get("risk_band", "Low")))

    def _final_priority(rec: dict) -> int:
        return rec.get("escalated_pwc_priority") or \
               rec.get("fin_adjusted_priority") or \
               assign_pwc_priority(_final_score(rec))

    # Band counts
    _band_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    _band_styles = {
        "Critical": ("#f87171", "#2d0a0a", "#5c1a1a"),
        "High":     ("#fb923c", "#2d1500", "#5c2e0a"),
        "Medium":   ("#fbbf24", "#2d2000", "#5c4210"),
        "Low":      ("#34d399", "#0a2d1a", "#1a5c3a"),
    }
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    scores = []
    current_id = id(current_result)

    for rec in history:
        b = _final_band(rec)
        counts[b] = counts.get(b, 0) + 1
        scores.append(_final_score(rec))

    avg_score = round(sum(scores) / len(scores), 1)
    highest_band = max((b for b, c in counts.items() if c > 0),
                       key=lambda b: _band_order.get(b, 0))

    # Combined posture: driven by highest band, escalated if multiple high-severity findings
    n_crit = counts["Critical"]
    n_high = counts["High"]
    n_med  = counts["Medium"]
    if n_crit >= 2 or (n_crit >= 1 and n_high >= 1):
        posture, posture_desc = "Critical", "Immediate engagement-level escalation required"
    elif n_crit >= 1:
        posture, posture_desc = "Critical", "Critical finding present — escalation required"
    elif n_high >= 2 or (n_high >= 1 and n_med >= 1):
        posture, posture_desc = "High", "Multiple elevated findings — urgent remediation needed"
    elif n_high >= 1:
        posture, posture_desc = "High", "High-severity finding present — urgent remediation"
    elif n_med >= 2:
        posture, posture_desc = "Medium", "Multiple medium findings — address within 30 days"
    elif n_med >= 1:
        posture, posture_desc = "Medium", "Medium-severity finding — include in management letter"
    else:
        posture, posture_desc = "Low", "Low-severity findings only — advisory observations"

    _pc, _pb, _pbo = _band_styles.get(posture, ("#c4d4f0", "#0e1628", "#1c2d50"))
    _posture_chip = (
        f'<span class="ceo-posture-chip" '
        f'style="color:{_pc};background:{_pb};border:1px solid {_pbo};">'
        f'Combined Posture: {posture}</span>'
    )

    # Band count chips
    _band_chips = ""
    for band in ["Critical", "High", "Medium", "Low"]:
        c = counts[band]
        if c == 0:
            continue
        col, bg, bo = _band_styles[band]
        _band_chips += (
            f'<span class="ceo-band-chip" style="color:{col};background:{bg};border-color:{bo};">'
            f'{c} {band}</span>'
        )

    # Summary sentence (matches the spec)
    _band_parts = []
    for band in ["Critical", "High", "Medium", "Low"]:
        c = counts[band]
        if c:
            _band_parts.append(f"{c} {band}")
    _summary_txt = ", ".join(_band_parts)
    n_total = len(history)

    # Mini findings table
    _rows = ""
    for i, rec in enumerate(history):
        fs   = _final_score(rec)
        fb   = _final_band(rec)
        fp   = _final_priority(rec)
        dom  = rec.get("control_domain", "—")
        app  = rec.get("application", "—")
        ind  = rec.get("industry", "—")
        col, bg, bo = _band_styles.get(fb, ("#c4d4f0", "#0e1628", "#1c2d50"))
        _is_current = (rec is current_result)
        _row_cls = " ceo-current" if _is_current else ""
        _marker  = '<span class="ceo-current-marker">current</span>' if _is_current else ""
        _band_pill = (
            f'<span style="font-size:0.68rem;font-weight:700;color:{col};'
            f'background:{bg};border:1px solid {bo};padding:2px 8px;border-radius:10px;">'
            f'{fb}</span>'
        )
        _rows += f"""
        <tr class="{_row_cls}">
          <td style="color:#6b82b0;font-size:0.65rem;">{i+1}</td>
          <td><span class="ceo-domain-tag">{dom}</span>{_marker}</td>
          <td style="color:#8ea3c8;font-size:0.7rem;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{app}</td>
          <td style="color:#4a6490;font-size:0.7rem;">{ind}</td>
          <td style="font-weight:700;color:#e8edf8;">{fs}</td>
          <td>{_band_pill}</td>
          <td style="font-weight:700;color:#e8edf8;">P{fp}</td>
        </tr>"""

    return f"""
<div class="ceo-card">
  <div class="ceo-header">
    <div>
      <div class="ceo-title">🔗 Control Environment Overview</div>
      <div class="ceo-subtitle">
        You have scored <b style="color:#c4d4f0;">{n_total} findings</b> this engagement
        — {_summary_txt}.
      </div>
    </div>
    {_posture_chip}
  </div>
  <div class="ceo-band-row">
    {_band_chips}
    <span class="ceo-avg-label">Avg score &nbsp;<span class="ceo-avg-score">{avg_score}</span></span>
  </div>
  <table class="ceo-table">
    <thead>
      <tr>
        <th>#</th><th>Domain</th><th>Application</th><th>Industry</th>
        <th>Score</th><th>Band</th><th>Priority</th>
      </tr>
    </thead>
    <tbody>{_rows}</tbody>
  </table>
  <div style="margin-top:10px;font-size:0.7rem;color:#3a5080;font-style:italic;">
    {posture_desc}
  </div>
</div>"""


def render_benchmark_panel(score: float, domain: str, industry: str) -> str:
    """Return HTML for the industry benchmark comparison panel."""
    bm = compute_benchmark(score, domain, industry)
    if not bm:
        return ""

    n         = bm["n"]
    mean      = bm["mean"]
    median    = bm["median"]
    p25       = bm["p25"]
    p75       = bm["p75"]
    p90       = bm["p90"]
    top_pct   = bm["top_pct"]
    pct_rank  = bm["pct_rank"]
    delta     = bm["delta"]
    dom_bm    = BENCHMARK_DOMAIN_DATA.get(domain, {})

    # Colour-code the delta
    delta_cls  = "bm-delta-pos" if delta > 0 else ("bm-delta-neg" if delta < 0 else "")
    delta_str  = f"+{delta}" if delta > 0 else str(delta)

    # Severity bucket for the percentile badge
    if top_pct <= 15:
        sev_cls, sev_label = "sev-critical", "Top 15% most severe"
    elif top_pct <= 35:
        sev_cls, sev_label = "sev-high",     "Above-average severity"
    elif top_pct <= 65:
        sev_cls, sev_label = "sev-medium",   "Near industry median"
    else:
        sev_cls, sev_label = "sev-low",      "Below industry average"

    # Distribution bar — display range 20-90 (covers full score spread in training data)
    _lo, _hi = 20.0, 90.0
    def _pct(v):
        return round(max(0.0, min(100.0, (v - _lo) / (_hi - _lo) * 100)), 2)

    p25_pct    = _pct(p25)
    p75_pct    = _pct(p75)
    p90_pct    = _pct(p90)
    med_pct    = _pct(median)
    score_pct  = _pct(score)

    # IQR fill
    iqr_left  = p25_pct
    iqr_width = p75_pct - p25_pct

    # Domain-wide context
    dom_str = (
        f'<span class="bm-domain-chip">All {domain} findings: avg {dom_bm.get("mean","—")} '
        f'· n={dom_bm.get("n","—")}</span>'
        if dom_bm else ""
    )

    return f"""
<div class="bm-card">
  <div class="bm-title">📊 Industry Benchmark Comparison</div>
  <div class="bm-subtitle">{domain} findings · {industry} · based on {n} scored findings</div>

  <div class="bm-stats-row">
    <div class="bm-stat">
      <div class="bm-stat-label">Your Score</div>
      <div class="bm-stat-val bm-your-score">{score}</div>
      <div class="bm-stat-sub">current finding</div>
    </div>
    <div class="bm-stat">
      <div class="bm-stat-label">Industry Avg</div>
      <div class="bm-stat-val">{mean}</div>
      <div class="bm-stat-sub">{domain} · {industry}</div>
    </div>
    <div class="bm-stat">
      <div class="bm-stat-label">vs Average</div>
      <div class="bm-stat-val {delta_cls}">{delta_str}</div>
      <div class="bm-stat-sub">score delta</div>
    </div>
    <div class="bm-stat">
      <div class="bm-stat-label">Median</div>
      <div class="bm-stat-val">{median}</div>
      <div class="bm-stat-sub">50th percentile</div>
    </div>
    <div class="bm-stat">
      <div class="bm-stat-label">P75 / P90</div>
      <div class="bm-stat-val">{p75} <span style="font-size:0.7rem;color:#2d4270;">/ {p90}</span></div>
      <div class="bm-stat-sub">upper quartile</div>
    </div>
  </div>

  <div class="bm-bar-wrap">
    <div class="bm-bar-labels">
      <span>Low risk (20)</span>
      <span>Score distribution across {n} {domain} findings in {industry}</span>
      <span>High risk (90+)</span>
    </div>
    <div class="bm-bar-track">
      <!-- IQR fill (p25–p75) -->
      <div class="bm-bar-fill" style="left:{iqr_left}%;width:{iqr_width}%;"></div>
      <!-- P25 marker -->
      <div class="bm-bar-marker" style="left:{p25_pct}%;background:#2d5a9e;"></div>
      <!-- Median marker -->
      <div class="bm-bar-marker" style="left:{med_pct}%;background:#6b9de8;"></div>
      <!-- P75 marker -->
      <div class="bm-bar-marker" style="left:{p75_pct}%;background:#2d5a9e;"></div>
      <!-- P90 marker -->
      <div class="bm-bar-marker" style="left:{p90_pct}%;background:#8b4513;width:1px;opacity:0.6;"></div>
      <!-- Current score dot -->
      <div class="bm-bar-score-dot" style="left:{score_pct}%;"></div>
    </div>
    <div class="bm-bar-p-labels">
      <div class="bm-bar-p-label" style="left:{p25_pct}%;">P25 {p25}</div>
      <div class="bm-bar-p-label" style="left:{med_pct}%;">Med {median}</div>
      <div class="bm-bar-p-label" style="left:{p75_pct}%;">P75 {p75}</div>
      <div class="bm-bar-p-label" style="left:{p90_pct}%;">P90 {p90}</div>
    </div>
  </div>

  <div class="bm-percentile-row">
    <div class="bm-pct-badge {sev_cls}">Top<br>{top_pct}%</div>
    <div class="bm-pct-text">
      <b>This finding ranks in the top {top_pct}% most severe {domain} findings in {industry}</b>
      — scoring higher than {pct_rank}% of the {n} comparable findings in the training dataset.
      {sev_label}.
    </div>
  </div>

  <div class="bm-domain-row">
    {dom_str}
    <span class="bm-domain-chip">Source: PwC training dataset · 977 findings</span>
  </div>
</div>"""


def render_shap_chart(shap_values: dict, top_n: int = 10):
    if not shap_values:
        return "<div class='empty-state'>SHAP not available (install shap)</div>"

    sorted_sv = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    max_abs = max(abs(v) for _, v in sorted_sv) if sorted_sv else 1

    rows = ""
    for feat, val in sorted_sv:
        pct = abs(val) / max_abs * 100 if max_abs else 0
        color = "#3b82f6" if val > 0 else "#ef4444"
        val_color = "#60a5fa" if val > 0 else "#f87171"
        display_name = feat.replace("_", " ").replace("flag ", "⚑ ").replace("domain ", "⬡ ").replace("industry ", "⬡ ").replace("apptype ", "⬡ ").title()
        rows += f"""
        <div class="shap-row">
          <div class="shap-feat" title="{feat}">{display_name}</div>
          <div class="shap-bar-wrap">
            <div class="shap-bar {'shap-bar-pos' if val > 0 else 'shap-bar-neg'}" style="width:{pct}%;background:{color};opacity:0.85;"></div>
          </div>
          <div class="shap-val" style="color:{val_color};">{val:+.3f}</div>
        </div>"""
    return rows


def render_llm_signals(llm_feats):
    SIGNAL_LABELS = {
        "violation_rate":            "Violation Rate",
        "finding_confirmed":         "Finding Confirmed",
        "negation_flag":             "Negation Flag",
        "compensating_control":      "Compensating Control",
        "sod_conflict":              "SoD Conflict",
        "access_revocation_failure": "Access Revocation Fail",
        "data_at_risk":              "Data at Risk",
        "systemic_vs_isolated":      "Systemic (vs Isolated)",
        "evidence_strength":         "Evidence Strength",
        "llm_severity_estimate":     "LLM Severity Estimate",
    }
    items = ""
    for key, label in SIGNAL_LABELS.items():
        val = llm_feats.get(key, 0)
        is_active = val > 0.5 if isinstance(val, float) else bool(val)
        dot_cls = "signal-dot-on" if is_active else "signal-dot-off"
        if isinstance(val, float):
            disp = f"{val:.2f}"
        else:
            disp = "✓" if val else "✗"
        items += f"""
        <div class="signal-item">
          <div class="signal-dot {dot_cls}"></div>
          <div class="signal-name">{label}</div>
          <div class="signal-val">{disp}</div>
        </div>"""
    return f'<div class="signal-grid">{items}</div>'


# ── Welcome screen ─────────────────────────────────────────────────────────────
if st.session_state.show_welcome:
    # Hide sidebar on the welcome screen for a clean first impression
    st.markdown("""
    <style>
      section[data-testid="stSidebar"] { display: none !important; }
      .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-page">
      <div class="welcome-logo">🛡️</div>
      <div class="welcome-badge">DTU × PwC Denmark · Master Thesis s242576</div>
      <div class="welcome-title">ITGC Cyber Risk Scoring Model</div>
      <div class="welcome-sub">
        An AI-powered audit tool that transforms free-text IT findings into transparent,
        explainable risk scores — so every judgement is data-driven and fully defensible.
      </div>
      <div class="welcome-divider"></div>
      <div class="welcome-features">
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">🤖</span>
          <div class="welcome-feat-title">Claude Haiku AI Extraction</div>
          <div class="welcome-feat-desc">Reads your observation and risk statement and extracts 10 semantic risk signals — understanding nuance that simple keywords miss.</div>
        </div>
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">⚡</span>
          <div class="welcome-feat-title">XGBoost Risk Model</div>
          <div class="welcome-feat-desc">A trained machine-learning model combines AI signals with structured audit context to produce a precise 0–100 risk score.</div>
        </div>
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">🔍</span>
          <div class="welcome-feat-title">SHAP Explainability</div>
          <div class="welcome-feat-desc">Every score is fully explained — see exactly which features drove the rating up or down, making each finding fully auditable.</div>
        </div>
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">📈</span>
          <div class="welcome-feat-title">Industry Benchmarking</div>
          <div class="welcome-feat-desc">Compare each finding against 977 historical records across 20 domain × industry combinations to contextualise severity.</div>
        </div>
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">🛠️</span>
          <div class="welcome-feat-title">Remediation Roadmap</div>
          <div class="welcome-feat-desc">Get 3–5 targeted, domain-specific remediation actions with feasibility ratings and implementation timelines.</div>
        </div>
        <div class="welcome-feat-card">
          <span class="welcome-feat-icon">💬</span>
          <div class="welcome-feat-title">AI Audit Assistant</div>
          <div class="welcome-feat-desc">Ask the AI anything about your scored finding — it knows the full context and responds in professional PwC audit language.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons — centered using columns
    _, c1, gap, c2, _ = st.columns([1.5, 1.2, 0.3, 1.2, 1.5])
    with c1:
        if st.button("📖  Start Interactive Tour", use_container_width=True, type="primary"):
            st.session_state.show_welcome = False
            st.session_state.tour_active = True
            st.session_state.tour_step = 0
            st.rerun()
    with c2:
        if st.button("→  Skip tour, open the app", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()

    st.markdown(
        '<p class="welcome-cta-hint">You can restart the tour at any time from the sidebar.</p>',
        unsafe_allow_html=True,
    )
    st.stop()  # Do not render the rest of the app on the welcome screen


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
      <div style="font-family:'DM Sans',sans-serif;font-size:1.1rem;font-weight:800;color:#e8edf8;">🛡️ ITGC Scorer</div>
      <div style="font-size:0.68rem;color:#3d6acc;letter-spacing:2px;font-weight:700;margin-top:2px;">V2 · LLM-ENHANCED</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Finding Context</div>', unsafe_allow_html=True)

    control_domain = st.selectbox("Control Domain", CONTROL_DOMAINS, help="ITGC control domain")

    domain_desc = {
        "PAM": "Privileged Access Management",
        "NJL": "New Joiners & Leavers",
        "CM":  "Change Management",
        "BR":  "Backup & Restoration"
    }
    st.caption(f"↳ {domain_desc[control_domain]}")

    application = st.selectbox("Application", APPLICATIONS)
    industry    = st.selectbox("Industry", INDUSTRIES)
    app_type    = st.selectbox("Application Type", APP_TYPES)

    # ── IT Dependency Context ───────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">IT Dependency</div>', unsafe_allow_html=True)

    it_dep_count = st.selectbox(
        "Financial Processes Dependent",
        IT_DEP_COUNT_OPTIONS,
        index=IT_DEP_COUNT_OPTIONS.index(st.session_state.it_dep_count),
        help="Number of IT-dependent financial processes running through this system.",
    )
    st.session_state.it_dep_count = it_dep_count

    it_interface_type = st.selectbox(
        "Interface / Integration Type",
        IT_INTERFACE_OPTIONS,
        index=IT_INTERFACE_OPTIONS.index(st.session_state.it_interface_type),
        help="Nature of the integration. Direct DB access and APIs carry more risk than standard reports.",
    )
    st.session_state.it_interface_type = it_interface_type

    _preview_adj = compute_it_dep_adjustment(it_dep_count, it_interface_type)
    if _preview_adj > 0:
        st.caption(f"↳ Score adjustment: **+{_preview_adj} pts** will be applied")
    else:
        st.caption("↳ No score adjustment (standard reports carry neutral risk)")

    # ── Client Environment Profile ──────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Client Environment</div>', unsafe_allow_html=True)
    st.markdown('<div class="env-profile-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="env-row-label">Deployment Model</div>', unsafe_allow_html=True)
    env_deploy = st.radio("deploy", ENV_DEPLOY_OPTIONS,
        index=ENV_DEPLOY_OPTIONS.index(st.session_state.env_deploy),
        horizontal=True, label_visibility="collapsed", key="_env_deploy_radio")
    st.session_state.env_deploy = env_deploy

    st.markdown('<div class="env-row-label" style="margin-top:8px;">System Age</div>', unsafe_allow_html=True)
    env_age = st.radio("age", ENV_AGE_OPTIONS,
        index=ENV_AGE_OPTIONS.index(st.session_state.env_age),
        horizontal=True, label_visibility="collapsed", key="_env_age_radio")
    st.session_state.env_age = env_age

    st.markdown('<div class="env-row-label" style="margin-top:8px;">Audit Scope</div>', unsafe_allow_html=True)
    env_scope = st.radio("scope", ENV_SCOPE_OPTIONS,
        index=ENV_SCOPE_OPTIONS.index(st.session_state.env_scope),
        horizontal=True, label_visibility="collapsed", key="_env_scope_radio")
    st.session_state.env_scope = env_scope

    # Live environment risk composite
    _ev_adj   = compute_env_adjustment(env_deploy, env_age, env_scope)
    _ev_label, _ev_color, _ev_bg = env_risk_level(_ev_adj)
    _d_adj = ENV_DEPLOY_ADJ.get(env_deploy, 0)
    _a_adj = ENV_AGE_ADJ.get(env_age, 0)
    _s_adj = ENV_SCOPE_ADJ.get(env_scope, 0)
    def _chip(v, lbl):
        cls = "pos" if v > 0 else ("neg" if v < 0 else "neu")
        sign = f"+{v}" if v > 0 else str(v)
        return f'<span class="env-dim-chip {cls}">{lbl} {sign}</span>'
    _adj_str = f"+{_ev_adj}" if _ev_adj > 0 else str(_ev_adj)
    st.markdown(f"""
<div class="env-risk-chip" style="background:{_ev_bg};border:1px solid {_ev_color}30;">
  <div class="env-risk-dot" style="background:{_ev_color};box-shadow:0 0 6px {_ev_color};"></div>
  <span class="env-risk-label" style="color:{_ev_color};">{_ev_label} Environment Risk</span>
  <span class="env-risk-adj" style="color:{_ev_color};">{_adj_str} pts</span>
</div>
<div class="env-dim-row">
  {_chip(_d_adj,"Deploy")} {_chip(_a_adj,"Age")} {_chip(_s_adj,"Scope")}
</div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close env-profile-wrap

    # ── Financial Context ───────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Financial Context</div>', unsafe_allow_html=True)

    fin_impact_type = st.selectbox(
        "Financial Impact Type",
        FIN_IMPACT_OPTIONS,
        index=FIN_IMPACT_OPTIONS.index(st.session_state.fin_impact_type),
        help="Whether the deficiency directly affects financial statements or only IT infrastructure.",
    )
    st.session_state.fin_impact_type = fin_impact_type

    fin_materiality = st.selectbox(
        "Materiality Level",
        FIN_MATERIALITY_OPTIONS,
        index=FIN_MATERIALITY_OPTIONS.index(st.session_state.fin_materiality),
        help="Audit materiality threshold for this client/application. Maps to the engagement's quantitative materiality.",
    )
    st.session_state.fin_materiality = fin_materiality

    _fin_sev, _fin_action = FIN_INTERPRETATION.get(
        (fin_impact_type, fin_materiality), ("—", "—")
    )
    _fin_p_adj = FIN_PRIORITY_ADJUSTMENT.get((fin_impact_type, fin_materiality), 0)
    if _fin_p_adj < 0:
        st.caption(f"↳ **{_fin_sev}** · Priority escalates by {abs(_fin_p_adj)} level")
    else:
        st.caption(f"↳ **{_fin_sev}** · No priority adjustment")

    # ── Prior Year Context ──────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Prior Year Context</div>', unsafe_allow_html=True)

    prior_year_finding = st.toggle(
        "Prior year finding",
        value=st.session_state.prior_year_finding,
        help="Was this same control deficiency raised in a prior year audit? Activates automatic priority escalation.",
    )
    st.session_state.prior_year_finding = prior_year_finding

    if prior_year_finding:
        _py_options = ["P1 — Critical", "P2 — High", "P3 — Medium", "P4 — Low", "P5 — Minimal"]
        _py_sel = st.selectbox(
            "Prior Year Priority",
            _py_options,
            index=st.session_state.prior_year_priority - 1,
            help="Priority level assigned to this finding in the prior year audit report.",
        )
        prior_year_priority = int(_py_sel[1])
        st.session_state.prior_year_priority = prior_year_priority
        _raw_p = assign_pwc_priority(st.session_state.result['risk_score']) if st.session_state.result else "–"
        _esc_p = max(1, _raw_p - 1) if isinstance(_raw_p, int) else "–"
        st.caption(f"↳ Score-derived priority will escalate by one level (P{_raw_p} → P{_esc_p})" if isinstance(_raw_p, int) else "↳ Score finding first to preview escalation")
    else:
        prior_year_priority = st.session_state.prior_year_priority

    st.markdown('<div class="sidebar-section">Scoring Info</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem;color:#4a6490;line-height:1.7;">
      <b style="color:#6b82b0;">Pipeline v2</b><br>
      Phase 1: Data load & audit<br>
      Phase 2a: Structured features<br>
      Phase 2b: LLM extraction (Haiku)<br>
      Phase 2c: Feature matrix merge<br>
      Phase 3: Label design<br>
      Phase 4: XGBoost training<br>
      Phase 5: Score calibration + SHAP<br>
      Phase 6: Real-data validation<br><br>
      <b style="color:#6b82b0;">Score bands</b><br>
      🔴 Critical: ≥75 · 🟠 High: ≥55<br>
      🟡 Medium: ≥35 · 🟢 Low: &lt;35
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown('<div class="sidebar-section">Session History</div>', unsafe_allow_html=True)
        for i, h in enumerate(reversed(st.session_state.history[-5:])):
            band_color = {"Critical":"#f87171","High":"#fb923c","Medium":"#fbbf24","Low":"#34d399"}.get(h['risk_band'],'#c4d4f0')
            st.markdown(f"""
            <div class="hist-item">
              <div class="hist-item-title" style="color:{band_color};">
                {h['risk_score']} · {h['risk_band']}
              </div>
              <div class="hist-item-meta">{h['control_domain']} · {h['observation_snippet'][:40]}...</div>
            </div>""", unsafe_allow_html=True)

    # ── Tour / Help ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Help & Guide</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tour-restart-btn" style="display:none;"></div>',
        unsafe_allow_html=True,
    )
    if st.button("📖  Take the Tour", use_container_width=True, key="sidebar_tour_btn"):
        st.session_state.tour_active = True
        st.session_state.tour_step = 0
        st.rerun()
    st.markdown(
        '<div style="font-size:0.72rem;color:#2d4270;margin-top:6px;line-height:1.5;">'
        '16 steps · covers every feature<br>from scoring to AI chat</div>',
        unsafe_allow_html=True,
    )


# ── Main content ───────────────────────────────────────────────────────────────

# ── Tour panel ─────────────────────────────────────────────────────────────────
if st.session_state.tour_active:
    _total   = len(TOUR_STEPS)
    _idx     = min(st.session_state.tour_step, _total - 1)
    _step    = TOUR_STEPS[_idx]
    _pct     = round((_idx + 1) / _total * 100)

    # Dot indicators (show up to 15; for readability collapse into groups if more)
    _dots_html = ""
    for _d in range(_total):
        if _d < _idx:
            _cls = "tour-dot done"
        elif _d == _idx:
            _cls = "tour-dot active"
        else:
            _cls = "tour-dot"
        _dots_html += f'<div class="{_cls}"></div>'

    st.markdown(f"""
    <div class="tour-panel">
      <div class="tour-header">
        <div class="tour-step-badge">
          <div class="tour-step-num">Step {_idx + 1} of {_total}</div>
          <div class="tour-section-tag">{_step['section']}</div>
        </div>
      </div>
      <div class="tour-progress-bar">
        <div class="tour-progress-fill" style="width:{_pct}%;"></div>
      </div>
      <div class="tour-title">{_step['icon']}&nbsp; {_step['title']}</div>
      <div class="tour-body">{_step['body']}</div>
      <div class="tour-tip">
        <span class="tour-tip-icon">💡</span>
        <span>{_step['tip']}</span>
      </div>
      <div class="tour-nav" style="margin-top:16px;">
        <div class="tour-dots">{_dots_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons — Streamlit renders these below the HTML card
    _nav_prev, _nav_next, _nav_end, _ = st.columns([1, 1, 1.2, 3])
    with _nav_prev:
        _prev_disabled = (_idx == 0)
        if st.button("← Previous", disabled=_prev_disabled, key="tour_prev", use_container_width=True):
            st.session_state.tour_step = max(0, _idx - 1)
            st.rerun()
    with _nav_next:
        _is_last = (_idx == _total - 1)
        _next_label = "Finish Tour ✓" if _is_last else "Next →"
        if st.button(_next_label, key="tour_next", use_container_width=True, type="primary"):
            if _is_last:
                st.session_state.tour_active = False
                st.session_state.tour_step = 0
            else:
                st.session_state.tour_step = _idx + 1
            st.rerun()
    with _nav_end:
        if st.button("✕  End Tour", key="tour_end", use_container_width=True):
            st.session_state.tour_active = False
            st.session_state.tour_step = 0
            st.rerun()

    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-badge">DTU × PwC Denmark · Master Thesis s242576</div>
  <div class="hero-title">ITGC Cyber Risk Scoring Model</div>
  <div class="hero-sub">
    XGBoost + Claude Haiku semantic extraction · SHAP explainability · 0–100 continuous score
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input columns ──────────────────────────────────────────────────────────────
col_obs, col_risk = st.columns(2)

with col_obs:
    st.markdown('<div class="card-title">📋 Observation</div>', unsafe_allow_html=True)
    observation = st.text_area(
        "observation",
        label_visibility="collapsed",
        placeholder='During our review of SAP user access, we identified 3 terminated employees with active accounts...',
        height=180,
        key="obs_input"
    )

with col_risk:
    st.markdown('<div class="card-title">⚠️ Risk Statement</div>', unsafe_allow_html=True)
    risk = st.text_area(
        "risk",
        label_visibility="collapsed",
        placeholder='There is a high risk that unauthorised access to financial systems by former employees could result in fraudulent postings...',
        height=180,
        key="risk_input"
    )

# ── Example buttons ────────────────────────────────────────────────────────────
def _set_high_example():
    st.session_state["obs_input"] = "During our review of SAP user access, we identified 3 terminated employees with active accounts. Login confirmed on 2 accounts post-termination."
    st.session_state["risk_input"] = "Unauthorised access to financial systems by former employees confirmed. Risk of fraudulent postings."

def _set_medium_example():
    st.session_state["obs_input"] = "During our review of the New Joiners and Leavers process for SAP HANA DB, we observed that the formal offboarding checklist is not consistently completed. Our testing of 20 leaver cases identified that 8 out of 20 cases did not have a completed offboarding checklist. In all 8 cases, access was eventually revoked but the revocation was performed between 3 and 12 business days after the recorded termination date, exceeding the organisation's defined SLA of 1 business day. No login activity was identified on any of the delayed accounts."
    st.session_state["risk_input"] = "There is a moderate risk that delayed access revocation creates a window of opportunity for unauthorised system access by former employees. Although no exploitation was identified during the audit period, the systematic breach of the 1 business day SLA across 8 out of 20 leavers indicates a process control weakness."

def _set_low_example():
    st.session_state["obs_input"] = "During our review of backup controls for RetailHub, automated daily backups are performed and monitored. Our testing of 12 backup cycles confirmed all 12 completed successfully with no failures. A minor observation was noted whereby backup completion reports are distributed via email rather than logged in the ticketing system. No backup failures or data loss incidents were identified."
    st.session_state["risk_input"] = "There is a low risk of procedural non-compliance in documentation of backup evidence. The backup process itself is functioning correctly and no data integrity issues were identified."

st.markdown("**Quick examples:**")
ex_col1, ex_col2, ex_col3 = st.columns(3)

with ex_col1:
    st.button("🔴 High severity example", on_click=_set_high_example)

with ex_col2:
    st.button("🟡 Medium severity example", on_click=_set_medium_example)

with ex_col3:
    st.button("🟢 Low severity example", on_click=_set_low_example)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Score button ───────────────────────────────────────────────────────────────
run_col, _ = st.columns([1, 2])
with run_col:
    score_btn = st.button("⚡  Score This Finding", key="score_btn")

if score_btn:
    if not observation.strip() or not risk.strip():
        st.warning("Please enter both an Observation and a Risk statement.")
    elif not st.session_state.api_key:
        st.warning("Anthropic API key not configured. Set ANTHROPIC_API_KEY in the .env file to enable LLM feature extraction.")
    else:
        with st.spinner("Extracting semantic features via Claude Haiku, running XGBoost..."):
            result, err = run_prediction(
                observation=observation,
                risk=risk,
                control_domain=control_domain,
                application=application,
                industry=industry,
                app_type=app_type,
                api_key=st.session_state.api_key,
            )

        if err:
            st.error(err)
        else:
            # ── Attach IT dependency adjustment ─────────────────────────────
            _it_adj = compute_it_dep_adjustment(
                st.session_state.it_dep_count,
                st.session_state.it_interface_type,
            )
            result["it_dep_count"]      = st.session_state.it_dep_count
            result["it_interface_type"] = st.session_state.it_interface_type
            result["it_dep_adjustment"] = _it_adj
            result["it_adjusted_score"] = round(min(100.0, result["risk_score"] + _it_adj), 1)
            # Recompute band from adjusted score so it reflects the full picture
            result["it_adjusted_band"]  = assign_band(result["it_adjusted_score"])

            # ── Client Environment Profile ────────────────────────────────────
            _env_adj = compute_env_adjustment(
                st.session_state.env_deploy,
                st.session_state.env_age,
                st.session_state.env_scope,
            )
            result["env_deploy"]       = st.session_state.env_deploy
            result["env_age"]          = st.session_state.env_age
            result["env_scope"]        = st.session_state.env_scope
            result["env_score_adj"]    = _env_adj
            _env_base                  = result["it_adjusted_score"]
            result["env_adjusted_score"] = round(min(100.0, max(0.0, _env_base + _env_adj)), 1)
            result["env_adjusted_band"]  = assign_band(result["env_adjusted_score"])

            # ── Financial materiality & impact ───────────────────────────────
            _fin_key = (st.session_state.fin_impact_type, st.session_state.fin_materiality)
            _fin_sev_label, _fin_action_text = FIN_INTERPRETATION.get(_fin_key, ("—", "—"))
            _fin_priority_adj = FIN_PRIORITY_ADJUSTMENT.get(_fin_key, 0)
            result["fin_impact_type"]       = st.session_state.fin_impact_type
            result["fin_materiality"]       = st.session_state.fin_materiality
            result["fin_sev_label"]         = _fin_sev_label
            result["fin_action_text"]       = _fin_action_text
            result["fin_priority_adj"]      = _fin_priority_adj

            # ── Priority chain ────────────────────────────────────────────────
            # Step 1: base priority from fully environment-adjusted score
            _p_it  = assign_pwc_priority(result.get("env_adjusted_score", result.get("it_adjusted_score", result["risk_score"])))
            # Step 2: financial materiality adjustment (capped P1–P5)
            _p_fin = max(1, min(5, _p_it + _fin_priority_adj))
            result["fin_adjusted_priority"] = _p_fin

            # Step 3: prior year escalation (chains from fin-adjusted priority)
            result["prior_year_finding"]  = st.session_state.prior_year_finding
            result["prior_year_priority"] = (
                st.session_state.prior_year_priority
                if st.session_state.prior_year_finding else None
            )
            if st.session_state.prior_year_finding:
                result["escalated_pwc_priority"] = max(1, _p_fin - 1)
            else:
                result["escalated_pwc_priority"] = None

            st.session_state.result = result
            st.session_state.history.append(result)
            if result.get("llm_error"):
                st.warning(f"LLM extraction used fallback defaults: {result['llm_error']}")

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Top-level score row ────────────────────────────────────────────────────
    g1, g2, g3, g4 = st.columns([1.2, 1, 1, 1])

    with g1:
        # ── Priority chain resolution ───────────────────────────────────────
        _it_adj     = r.get('it_dep_adjustment', 0)
        _env_adj    = r.get('env_score_adj', 0)
        _base_score = r['risk_score']
        _disp_score = r.get('env_adjusted_score', r.get('it_adjusted_score', _base_score))
        _disp_band  = r.get('env_adjusted_band',  r.get('it_adjusted_band', r['risk_band']))
        band_cls    = band_class(_disp_band)

        _p_it       = assign_pwc_priority(_disp_score)            # after IT adj score
        _p_fin      = r.get('fin_adjusted_priority', _p_it)       # after financial adj
        pwc_p       = r.get('escalated_pwc_priority') or _p_fin   # after prior year escalation
        is_repeat   = r.get('prior_year_finding', False)
        py_p        = r.get('prior_year_priority')
        _fin_adj    = r.get('fin_priority_adj', 0)                 # −1 or 0

        _pip_labels = {1: ("1", "Critical"), 2: ("2", "High"), 3: ("3", "Medium"), 4: ("4", "Low"), 5: ("5", "Min")}

        _pip_guidance = {
            1: ("P1 — Immediate Escalation", "Partner notification required before any report issuance. Cannot sign off without a signed management action plan, evidence of re-testing, and formal escalation documented in the engagement file."),
            2: ("P2 — Urgent Remediation", "Raise with engagement manager before report issuance. A written management response with a target remediation date is required. Include as a significant finding in the management letter."),
            3: ("P3 — Address Within 30 Days", "Include in the management letter with a management response. Obtain a named owner and target date. Schedule a follow-up to confirm remediation before the next audit cycle."),
            4: ("P4 — Address Within 60 Days", "Log as an advisory finding. Management response recommended but not mandatory. Monitor resolution status and carry forward if unresolved at next audit."),
            5: ("P5 — Low Priority", "Document as an observation for management awareness. No formal management response required. Re-assess at the next scheduled audit."),
        }

        # Pip: highlight final priority; strike-through the pre-adjustment pip
        # when any adjustment actually changed the value
        _pre_adj_p = _p_it   # the pip that would have been shown without any adjustment

        def _pip_cls(i):
            if i == pwc_p:
                return f" active-p{i}"
            # Show a demoted pip for wherever the score-only priority sat,
            # but only when at least one adjustment moved it
            if i == _pre_adj_p and _pre_adj_p != pwc_p:
                return " pwc-pip-demoted"
            return ""

        _pips_html = "".join(
            f'<div class="pwc-pip{_pip_cls(i)}">'
            f'{_pip_labels[i][0]}'
            f'<span class="pwc-pip-sub">{_pip_labels[i][1]}</span>'
            f'</div>'
            for i in range(1, 6)
        )

        # Financial priority adjustment note
        if _fin_adj < 0:
            _fin_note_html = f"""
          <div class="repeat-escalation-row" style="margin-top:6px;">
            <span class="repeat-py-label" style="background:#0e1a3d;border-color:#1e3a8a;color:#60a5fa;">💰 Fin.</span>
            <span class="repeat-arrow" style="color:#60a5fa;">→</span>
            <span style="color:#93c5fd;font-size:0.68rem;">P{_p_it} → <b>P{_p_fin}</b> · Direct FS × {r.get('fin_materiality','')} Mat</span>
          </div>"""
        else:
            _fin_note_html = ""

        # Repeat finding badge
        if is_repeat:
            _already_max = (pwc_p == 1 and _p_fin == 1)
            if _already_max:
                _escalation_row = f"""
          <div class="repeat-escalation-row">
            <span class="repeat-py-label">PY: P{py_p}</span>
            <span class="repeat-arrow">·</span>
            <span style="color:#fb923c;font-size:0.68rem;">Already at highest priority (P1)</span>
          </div>"""
            else:
                _escalation_row = f"""
          <div class="repeat-escalation-row">
            <span class="repeat-py-label">PY: P{py_p}</span>
            <span class="repeat-arrow">→</span>
            <span style="color:#fb923c;font-size:0.68rem;">P{_p_fin} upgraded to <b>P{pwc_p}</b></span>
          </div>"""
            _badge_label = "⚠️&nbsp; Repeat Finding — Already at P1" if _already_max else "⚠️&nbsp; Repeat Finding — Priority Escalated"
            _repeat_html = f"""
          <div class="repeat-badge">{_badge_label}</div>
          {_escalation_row}"""
        else:
            _repeat_html = ""

        # Score breakdown block — show all active adjustment layers
        _it_score   = r.get('it_adjusted_score', _base_score)
        _env_sign   = f"+{_env_adj}" if _env_adj >= 0 else str(_env_adj)
        _env_color  = "#4ade80" if _env_adj > 0 else ("#f87171" if _env_adj < 0 else "#6b82b0")
        if _it_adj > 0 and _env_adj != 0:
            # Both layers active: base → +IT → ±env → final
            _it_adj_html = f"""
          <div class="it-adj-wrap">
            <div class="it-adj-label">Score Breakdown</div>
            <div class="it-adj-row">
              <span class="it-base-score">{_base_score}</span>
              <span class="it-adj-chip">+{_it_adj}</span>
              <span class="it-adj-equals">=</span>
              <span class="it-base-score">{_it_score}</span>
              <span class="it-adj-chip" style="background:#0e3a2a;color:{_env_color};border-color:{_env_color}33;">{_env_sign}</span>
              <span class="it-adj-equals">=</span>
              <span class="it-final-score">{_disp_score}</span>
            </div>
            <div class="it-context-chips">
              <span class="it-context-chip">⚙ {r.get('it_dep_count','')}</span>
              <span class="it-context-chip">⇄ {r.get('it_interface_type','')}</span>
              <span class="it-context-chip">🌐 Env</span>
            </div>
          </div>"""
        elif _it_adj > 0:
            # IT only
            _it_adj_html = f"""
          <div class="it-adj-wrap">
            <div class="it-adj-label">Score Breakdown</div>
            <div class="it-adj-row">
              <span class="it-base-score">{_base_score}</span>
              <span class="it-adj-chip">+{_it_adj}</span>
              <span class="it-adj-equals">=</span>
              <span class="it-final-score">{_disp_score}</span>
            </div>
            <div class="it-context-chips">
              <span class="it-context-chip">⚙ {r.get('it_dep_count','')}</span>
              <span class="it-context-chip">⇄ {r.get('it_interface_type','')}</span>
            </div>
          </div>"""
        elif _env_adj != 0:
            # Env only
            _it_adj_html = f"""
          <div class="it-adj-wrap">
            <div class="it-adj-label">Score Breakdown</div>
            <div class="it-adj-row">
              <span class="it-base-score">{_base_score}</span>
              <span class="it-adj-chip" style="background:#0e3a2a;color:{_env_color};border-color:{_env_color}33;">{_env_sign}</span>
              <span class="it-adj-equals">=</span>
              <span class="it-final-score">{_disp_score}</span>
            </div>
            <div class="it-context-chips">
              <span class="it-context-chip">🌐 Env adj</span>
            </div>
          </div>"""
        else:
            _it_adj_html = ""

        st.markdown(f"""
        <div class="score-wrap">
          <div class="score-label">Risk Score</div>
          {"<div class='score-base-label'>Base score</div>" if (_it_adj > 0 or _env_adj != 0) else ""}
          <div class="score-number">{_disp_score}</div>
          <div><span class="{band_cls}">{_disp_band}</span></div>
          <div style="margin-top:10px;font-size:0.72rem;color:#4a6490;">Predicted class: <b style="color:#8ea3c8;">{r['predicted_class']}</b></div>
          {_it_adj_html}
          <div class="pwc-priority-wrap">
            <div class="pwc-priority-label">PwC Priority</div>
            <div class="pwc-priority-scale">{_pips_html}</div>
            {_fin_note_html}
            <div class="pwc-priority-guidance pwc-guidance-p{pwc_p}">
              <span class="pwc-guidance-bold">{_pip_guidance[pwc_p][0]}</span>
              {_pip_guidance[pwc_p][1]}
            </div>
          </div>
          {_repeat_html}
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="card"><div class="card-title">Class Probabilities</div>', unsafe_allow_html=True)
        st.markdown(render_probability_bars(r['p_low'], r['p_medium'], r['p_high']), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g3:
        st.markdown('<div class="card"><div class="card-title">Context</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-row"><span class="info-key">Domain</span><span class="info-val">{r['control_domain']}</span></div>
        <div class="info-row"><span class="info-key">Application</span><span class="info-val">{r['application']}</span></div>
        <div class="info-row"><span class="info-key">Industry</span><span class="info-val">{r['industry']}</span></div>
        <div class="info-row"><span class="info-key">App Tier</span><span class="info-val">{r['structured_flags']['app_tier']} / 5</span></div>
        <div class="info-row"><span class="info-key">IT Processes</span><span class="info-val">{r.get('it_dep_count','—')}</span></div>
        <div class="info-row"><span class="info-key">Interface</span><span class="info-val">{r.get('it_interface_type','—')}</span></div>
        <div class="info-row"><span class="info-key">IT Adj</span><span class="info-val" style="color:{'#4ade80' if r.get('it_dep_adjustment',0)>0 else '#4a6490'};">{"+" if r.get('it_dep_adjustment',0)>0 else ""}{r.get('it_dep_adjustment',0)} pts</span></div>
        <div class="info-row"><span class="info-key">Env Adj</span><span class="info-val" style="color:{'#4ade80' if r.get('env_score_adj',0)>0 else ('#f87171' if r.get('env_score_adj',0)<0 else '#4a6490')};">{"+" if r.get('env_score_adj',0)>0 else ""}{r.get('env_score_adj',0)} pts</span></div>
        <div class="info-row"><span class="info-key">Deploy</span><span class="info-val">{r.get('env_deploy','—').split('  ')[-1]}</span></div>
        <div class="info-row"><span class="info-key">Age</span><span class="info-val">{r.get('env_age','—').split('  ')[-1]}</span></div>
        <div class="info-row"><span class="info-key">Scope</span><span class="info-val">{r.get('env_scope','—').split('  ')[-1]}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with g4:
        st.markdown('<div class="card"><div class="card-title">Cyber Risk Flags</div>', unsafe_allow_html=True)
        flags = [
            ("Unauth Access",    r['structured_flags']['flag_unauth_access']),
            ("Data Loss",        r['structured_flags']['flag_data_loss']),
            ("Priv Escalation",  r['structured_flags']['flag_priv_escalation']),
            ("No Logging",       r['structured_flags']['flag_no_logging']),
            ("Weak Credentials", r['structured_flags']['flag_weak_credentials']),
            ("Quantity Finding", r['structured_flags']['has_quantity_finding']),
        ]
        chips = "".join(
            f'<span class="{"flag-chip-on" if v else "flag-chip-off"}">{n}</span>'
            for n, v in flags
        )
        kw_cnt = r['structured_flags']['high_sev_kw_count']
        st.markdown(f"""
        {chips}
        <div style="margin-top:12px;font-size:0.75rem;color:#4a6490;">High-severity keywords matched: <b style="color:#8ea3c8;">{kw_cnt}</b></div>
        </div>""", unsafe_allow_html=True)

    # ── Financial Impact row (full width) ──────────────────────────────────────
    if r.get("fin_impact_type"):
        st.markdown(
            f'<div class="card-title" style="margin-bottom:8px;">💰 Financial Impact & Materiality Assessment</div>'
            + render_financial_impact_card(r),
            unsafe_allow_html=True,
        )

    # ── LLM Signals + SHAP row ─────────────────────────────────────────────────
    sig_col, shap_col = st.columns(2)

    with sig_col:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">🤖 LLM Semantic Signals (Claude Haiku)</div>
          {render_llm_signals(r['llm_features'])}
        </div>
        """, unsafe_allow_html=True)

    with shap_col:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">📊 SHAP Feature Attribution (Top 10)</div>
          <div style="font-size:0.7rem;color:#2d4270;margin-bottom:12px;">
            🔵 Blue = increases risk score &nbsp;&nbsp; 🔴 Red = decreases risk score
          </div>
          {render_shap_chart(r.get('shap_values'))}
        </div>
        """, unsafe_allow_html=True)

    # ── Industry Benchmark Panel ────────────────────────────────────────────────
    _bm_html = render_benchmark_panel(
        _disp_score,
        r.get('control_domain', ''),
        r.get('industry', ''),
    )
    if _bm_html:
        st.markdown(_bm_html, unsafe_allow_html=True)

    # ── Remediation Roadmap ─────────────────────────────────────────────────────
    st.markdown(render_remediation_card(r), unsafe_allow_html=True)

    # ── Sign-off Readiness (P1/P2 only) ────────────────────────────────────────
    if pwc_p <= 2:
        render_signoff_section(r, pwc_p)

    # ── Cross-Control Environment Overview (≥2 findings in session) ────────────
    if len(st.session_state.history) >= 2:
        st.markdown(render_env_overview(st.session_state.history, r), unsafe_allow_html=True)

    # ── Export row ─────────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    exp_col, _ = st.columns([1, 2])
    with exp_col:
        export_data = {
            "risk_score":           r['risk_score'],
            "it_adjusted_score":    r.get('it_adjusted_score', r['risk_score']),
            "it_dep_adjustment":    r.get('it_dep_adjustment', 0),
            "risk_band":            r.get('it_adjusted_band', r['risk_band']),
            "predicted_class":      r['predicted_class'],
            "p_high":               r['p_high'],
            "p_medium":             r['p_medium'],
            "p_low":                r['p_low'],
            "control_domain":       r['control_domain'],
            "application":          r['application'],
            "industry":             r['industry'],
            "it_dep_count":         r.get('it_dep_count', ''),
            "it_interface_type":    r.get('it_interface_type', ''),
            "fin_impact_type":      r.get('fin_impact_type', ''),
            "fin_materiality":      r.get('fin_materiality', ''),
            "fin_sev_label":        r.get('fin_sev_label', ''),
            "fin_action_text":      r.get('fin_action_text', ''),
            "prior_year_finding":   r.get('prior_year_finding', False),
            "prior_year_priority":  r.get('prior_year_priority'),
            "escalated_pwc_priority": r.get('escalated_pwc_priority'),
            **{f"llm_{k}": v for k, v in r['llm_features'].items()},
            **{f"flag_{k}": v for k, v in r['structured_flags'].items()},
        }
        st.download_button(
            label="⬇  Export result as JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"itgc_score_{r['control_domain']}_{r['risk_score']}.json",
            mime="application/json",
        )

    # ── Ask AI chat ────────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Detect if result changed so we reset chat history
    _result_id = f"{r['risk_score']}_{r['control_domain']}_{r['risk_band']}"
    if st.session_state.chat_result_id != _result_id:
        st.session_state.chat_messages = []
        st.session_state.show_chat = False
        st.session_state.chat_result_id = _result_id

    _btn_label = "💬 Ask AI" if not st.session_state.show_chat else "✕ Close AI Chat"
    _btn_col, _ = st.columns([1, 4])
    with _btn_col:
        if st.button(_btn_label, key="toggle_chat_btn", use_container_width=True):
            st.session_state.show_chat = not st.session_state.show_chat
            # Seed chat with system prompt + auto-opening AI message on first open
            if st.session_state.show_chat and not st.session_state.chat_messages:
                _sys_prompt = build_chat_system_prompt(r, observation, risk)
                st.session_state.chat_messages = [{"role": "system", "content": _sys_prompt}]
                with st.spinner("AI is preparing your briefing…"):
                    _intro = call_chat_llm(
                        st.session_state.chat_messages + [
                            {"role": "user", "content":
                             "Please explain this risk score in depth — what drove it, what it means for the audit, and what the recommended next steps are."}
                        ],
                        st.session_state.api_key,
                    )
                import datetime as _dt
                _ts = _dt.datetime.now().strftime("%H:%M")
                st.session_state.chat_messages.append({"role": "assistant", "content": _intro, "ts": _ts})
            st.rerun()

    if st.session_state.show_chat:
        import streamlit.components.v1 as _components
        # Chat header (simple, no dynamic content — markdown is safe here)
        st.markdown("""
        <div class="chat-window-wrap" style="border-radius:16px 16px 0 0; border-bottom:none;">
          <div class="chat-header">
            <div class="chat-header-avatar">🤖</div>
            <div class="chat-header-info">
              <div class="chat-header-name">ITGC Risk AI &nbsp;·&nbsp; PwC Audit Assistant</div>
              <div class="chat-header-status">● Online — Claude Haiku</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        # Messages area — rendered in a true iframe, scrolling=True enables native scrollbar
        _chat_html = render_chat_component(st.session_state.chat_messages)
        _components.html(_chat_html, height=500, scrolling=True)
        # Bottom border closes the card visually
        st.markdown("""<div style="border:1px solid #1e3566;border-top:none;
                        border-radius:0 0 16px 16px;height:8px;
                        background:#0b1220;margin-bottom:12px;"></div>""",
                    unsafe_allow_html=True)

        # ── Follow-up input — must be the LAST element so nothing breaks the chat flow
        _user_input = st.chat_input("Ask a follow-up question about this finding…", key="chat_input_box")
        if _user_input:
            import datetime as _dt
            _ts = _dt.datetime.now().strftime("%H:%M")
            st.session_state.chat_messages.append({"role": "user", "content": _user_input, "ts": _ts})
            with st.spinner("AI is thinking…"):
                _reply = call_chat_llm(st.session_state.chat_messages, st.session_state.api_key)
            _ts2 = _dt.datetime.now().strftime("%H:%M")
            st.session_state.chat_messages.append({"role": "assistant", "content": _reply, "ts": _ts2})
            st.rerun()

    else:
        # ── Raw finding preview — only shown when chat is closed so it never interrupts the chat UX
        with st.expander("📄 View input finding text"):
            st.markdown(f"**Observation:** {observation}")
            st.markdown(f"**Risk:** {risk}")
