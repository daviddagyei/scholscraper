# Scholarship Database Web App

A modern, responsive web application for searching and filtering scholarship opportunities. Built with React, TypeScript, and Material-UI.

## 🚀 Features

- **Fuzzy Search**: Smart search functionality that finds relevant scholarships
- **Advanced Filtering**: Filter by category, location, amount, deadline, and eligibility
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Updates**: Fetches data from Google Sheets CSV
- **Modern UI**: Clean, Material Design interface
- **TypeScript**: Full type safety throughout the application

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **UI Library**: Material-UI (MUI) v5
- **Build Tool**: Vite
- **Search**: Fuse.js for fuzzy search
- **Date Handling**: date-fns
- **Data Fetching**: Axios
- **CSV Parsing**: PapaParse

## 📋 Prerequisites

- Node.js 16+ and npm
- A published Google Sheets CSV URL (optional - app includes dummy data)

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
