# ElevatrAI 🚀

An AI-powered career development platform that helps users transition between tech roles by providing personalized skill gap analysis and learning recommendations. Built with Flask and modern ML/NLP techniques.

## 🌟 Key Features

- **Smart Skill Analysis**
  - Extract skills from resumes (PDF/DOCX)
  - Manual skill entry with fuzzy matching
  - ML-powered skill gap detection
  - Role-specific skill recommendations

- **Career Path Planning**
  - Upskilling in current role
  - Career transition guidance
  - Complete beginner pathways
  - Personalized learning roadmaps

- **ML/NLP Capabilities**
  - Semantic skill matching using Sentence Transformers
  - Context-aware skill extraction
  - Intelligent role recommendations
  - Adaptive learning paths

## 🛠 Technology Stack

- **Backend**: Python 3.12, Flask 2.3.3
- **ML/NLP**: Sentence Transformers, PyTorch
- **Document Processing**: PyPDF2, python-docx
- **Deployment**: Gunicorn

## 🚀 Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/Anslemakadu/ElevatrAI.git
cd elevatrai
```

2. **Set Up Python Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Create .env file with:
PORT=5000
FLASK_ENV=development
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

4. **Run the Application**
```bash
python run.py
```

Visit `http://localhost:5000` in your browser

## 📂 Project Structure

```
elevatrai/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── routes.py            # API endpoints and request handling
│   ├── recommender.py       # ML-powered recommendation engine
│   ├── parser.py            # Resume and skill parsing
│   ├── nlp_utils.py         # NLP utilities and ML models
│   ├── file_utils.py        # File handling utilities
│   ├── static/
│   │   └── css/
│   │       └── styles.css   # Application styles
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Landing page
│       └── results.html     # Analysis results
├── resources/
│   ├── roles.json          # Role definitions
│   ├── skills_matrix.json  # Skill relationships
│   └── learning_resources.json  # Learning materials
├── tests/
│   ├── test_parser.py      # Parser unit tests
│   └── test_recommender.py # Recommender unit tests
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
└── run.py                 # Application entry point
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m tests.test_parser
python -m tests.test_recommender
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function arguments
- Add docstrings for modules, classes, and functions
- Include inline comments for complex logic

## 🚢 Deployment

### Production Setup
1. Configure environment variables
2. Update dependencies: `pip install -r requirements.txt`
3. Run with Gunicorn:
```bash
gunicorn 'run:app' --workers 2 --threads 2 --timeout 60
```

### Docker Deployment (Coming Soon)
- Containerized deployment
- Docker Compose setup
- Cloud-native configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/amazing-feature
```
3. Make your changes
4. Run tests:
```bash
python -m unittest discover tests
```
5. Commit your changes:
```bash
git commit -m 'Add amazing feature'
```
6. Push and create a Pull Request

### Contribution Guidelines
- Add tests for new features
- Update documentation
- Follow code style guidelines
- Keep commits atomic and well-described

## 📝 Future Enhancements

- [ ] Add skill versioning support
- [ ] Implement skill relationship graph
- [ ] Add context-aware skill extraction
- [ ] Support multiple languages
- [ ] Add progress tracking
- [ ] Implement A/B testing framework
- [ ] Add recommendation quality metrics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Anslem Akadu** - *Initial work* - [GitHub](https://github.com/Anslemakadu)

## 🙏 Acknowledgments

- Sentence Transformers for NLP capabilities
- Flask for the web framework
- Open source community for various tools and libraries
