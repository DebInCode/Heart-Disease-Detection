# Heart Disease Predictor - React Frontend

A modern, responsive React.js frontend for the Heart Disease Prediction Web App with advanced features, beautiful UI, and comprehensive functionality.

## 🚀 Features

### Core Features
- **Dual Mode Interface**: Patient Mode and Doctor Mode
- **Multi-step Form**: 4-step guided form for patient data collection
- **Real-time Validation**: Form validation with helpful error messages
- **AI Integration**: Seamless API integration with FastAPI backend
- **PDF Reports**: Downloadable professional medical reports
- **Batch Processing**: CSV upload for multiple patient analysis
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

### Advanced Features
- **Internationalization**: English and Hindi language support
- **Interactive Chatbot**: AI-powered health assistant with floating interface
- **Animated UI**: Smooth animations and transitions using Framer Motion
- **Particle Background**: Interactive particle system for visual appeal
- **Statistics Dashboard**: Real-time analytics and insights
- **Feature Importance**: Visual charts showing model feature importance
- **Session Management**: Local storage for prediction history
- **Professional Styling**: Modern glass-morphism design with gradients

### Technical Features
- **React 18**: Latest React features and hooks
- **Bootstrap 5**: Modern responsive framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Chart.js**: Interactive data visualization
- **Framer Motion**: Advanced animations
- **React Icons**: Comprehensive icon library
- **i18next**: Internationalization framework

## 📦 Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- FastAPI backend running on port 8501

### Setup Instructions

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Open your browser**:
   Navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML file
│   └── favicon.ico         # App icon
├── src/
│   ├── components/         # Reusable components
│   │   ├── Navbar.js       # Navigation bar
│   │   ├── Footer.js       # Footer component
│   │   ├── Chatbot.js      # AI health assistant
│   │   ├── ResultCard.js   # Prediction results display
│   │   └── LanguageSwitcher.js # Language toggle
│   ├── pages/              # Main page components
│   │   ├── Home.js         # Landing page
│   │   ├── PatientForm.js  # Patient mode form
│   │   └── DoctorView.js   # Doctor mode dashboard
│   ├── context/            # React context providers
│   │   ├── LanguageContext.js    # Language management
│   │   └── PredictionContext.js  # Prediction state management
│   ├── App.js              # Main app component
│   ├── index.js            # App entry point
│   ├── index.css           # Global styles
│   └── i18n.js             # Internationalization setup
├── package.json            # Dependencies and scripts
└── README.md               # This file
```

## 🎯 Usage Guide

### Patient Mode
1. **Navigate to Patient Mode** from the homepage
2. **Complete the 4-step form**:
   - Step 1: Basic information (age, sex)
   - Step 2: Vital signs (chest pain, blood pressure, cholesterol)
   - Step 3: Medical tests (blood sugar, ECG, heart rate, angina)
   - Step 4: Additional tests (ST depression, slope, vessels, thalassemia)
3. **Submit for prediction** and view results
4. **Download PDF report** or start a new assessment

### Doctor Mode
1. **Navigate to Doctor Mode** from the homepage
2. **Upload CSV file** with patient data (13 features required)
3. **View batch predictions** in the results table
4. **Analyze feature importance** with interactive charts
5. **Add clinical notes** and export results
6. **Download comprehensive reports**

### Chatbot Assistant
- **Click the floating heart icon** to open the chatbot
- **Ask health-related questions** about heart disease, symptoms, prevention
- **Use quick action buttons** for common queries
- **Get personalized tips** and recommendations

### Language Support
- **Toggle between English and Hindi** using the language switcher
- **All content is translated** including forms, messages, and UI elements
- **Language preference is saved** in local storage

## 🔧 Configuration

### API Endpoints
The app is configured to connect to a FastAPI backend running on `http://localhost:8501`. Update the proxy in `package.json` if needed:

```json
{
  "proxy": "http://localhost:8501"
}
```

### Environment Variables
Create a `.env` file in the frontend directory for environment-specific settings:

```env
REACT_APP_API_URL=http://localhost:8501
REACT_APP_ENVIRONMENT=development
```

## 🎨 Customization

### Styling
- **CSS Variables**: Modify colors and gradients in `public/index.html`
- **Bootstrap Theme**: Customize Bootstrap variables in `src/index.css`
- **Component Styles**: Each component has its own styling section

### Adding New Languages
1. **Add translations** to `src/i18n.js`
2. **Update language switcher** in `src/components/LanguageSwitcher.js`
3. **Test translations** across all components

### Extending Features
- **New Form Fields**: Add to `PatientForm.js` and update validation
- **Additional Charts**: Use Chart.js components in `DoctorView.js`
- **New Chatbot Responses**: Extend `Chatbot.js` knowledge base

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Netlify
1. **Connect your repository** to Netlify
2. **Set build command**: `npm run build`
3. **Set publish directory**: `build`
4. **Configure environment variables** if needed

### Deploy to Vercel
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Deploy**: `vercel --prod`

## 🔍 Troubleshooting

### Common Issues

**API Connection Errors**:
- Ensure FastAPI backend is running on port 8501
- Check CORS configuration in backend
- Verify proxy settings in package.json

**Build Errors**:
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Update dependencies: `npm update`
- Check Node.js version compatibility

**Styling Issues**:
- Clear browser cache
- Check CSS import order
- Verify Bootstrap CSS is loaded

### Performance Optimization
- **Code Splitting**: Implement React.lazy() for route-based splitting
- **Image Optimization**: Use WebP format and lazy loading
- **Bundle Analysis**: Run `npm run build --analyze` to identify large dependencies

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add feature'`
5. **Push to the branch**: `git push origin feature-name`
6. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Bootstrap** for the responsive framework
- **Framer Motion** for smooth animations
- **React Icons** for the comprehensive icon library
- **Chart.js** for data visualization
- **i18next** for internationalization

## 📞 Support

For support and questions:
- **Email**: contact@heartpredictor.com
- **GitHub Issues**: Create an issue in the repository
- **Documentation**: Check the inline code comments

---

**Made with ❤️ for better healthcare** 