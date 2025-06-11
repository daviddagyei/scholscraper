# Scholarship Database Web App

A modern, comprehensive scholarship discovery platform with both a React frontend and automated web scraping system.

## 🎯 Overview

This project combines a modern React web application with a powerful Scrapy-based web scraping system to create a comprehensive scholarship database. The scraper automatically collects scholarship data from multiple sources, while the web app provides a beautiful, searchable interface for students.

## 🏗️ Architecture

- **Frontend**: React + TypeScript web application
- **Scraper**: Python Scrapy spiders for data collection
- **Data Integration**: Firebase/Firestore and Google Sheets
- **Automation**: Scheduled scraping with data validation

## 🚀 Features

### Web Application
- **Fuzzy Search**: Smart search functionality that finds relevant scholarships
- **Advanced Filtering**: Filter by category, amount, deadline, and eligibility
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Updates**: Fetches data from Google Sheets CSV
- **Modern UI**: Clean, Material Design interface
- **TypeScript**: Full type safety throughout the application

### Web Scraping System
- **Multi-source scraping**: CollegeScholarships.org, UNCF, HSF, APIA Scholars, Native American funds
- **Data validation and cleaning**: Comprehensive pipelines for data quality
- **Multiple export formats**: JSON, CSV, Firebase, Google Sheets
- **Respectful scraping**: Rate limiting, user agent rotation, robots.txt compliance
- **Automated scheduling**: Daily scraping with cleanup
- **Deduplication**: Prevents duplicate scholarship entries
- **Error handling**: Robust error recovery and logging

## 🛠️ Tech Stack

### Frontend
- **React 18** + TypeScript
- **Material-UI (MUI) v5** for UI components
- **Vite** for building and development
- **Fuse.js** for fuzzy search
- **date-fns** for date handling
- **Axios** for data fetching
- **PapaParse** for CSV parsing

### Scraping System
- **Scrapy** for web scraping
- **Firebase Admin SDK** for data storage
- **Google Sheets API** for spreadsheet integration
- **Beautiful Soup** for HTML parsing
- **Schedule** for automation
- **Pandas** for data processing

## 📋 Prerequisites

- **Node.js 16+** and npm (for frontend)
- **Python 3.8+** (for scraper)
- Google Sheets CSV URL (optional - app includes dummy data)
- Firebase project (optional - for data storage)
- Google Sheets API credentials (optional - for data export)

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser** to `http://localhost:5173`

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```
