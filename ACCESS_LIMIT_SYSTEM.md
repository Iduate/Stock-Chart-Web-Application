# Stock Chart Web Application

This web application allows users to view stock and cryptocurrency charts, make price predictions, and compare them with actual market data.

## Features

### User Access Levels
- **Anonymous Users**: Can view the site without registering with limited access
- **Free Users**: Can access premium information with a 3-visit limit
- **Paid Users**: Have unlimited access to all features

### Prediction System
- Select any stock or cryptocurrency
- Choose a future date and duration
- Set expected price
- System automatically compares predictions with actual market data
- Calculates accuracy based on results

### Public Chart Board
- All predictions are automatically published to the public chart board
- Free users have limited access (10 predictions)
- Paid users have unlimited access
- View top-performing predictions and users

### Subscription System
- Free tier with 3-visit limit to premium content
- Premium subscription options
- Payment system integration

## Setup Instructions

### 1. Configure Environment
Ensure you have Python and Django installed. Then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Database Setup
Run migrations to set up the database:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 3. Run Development Server
Start the Django development server:

```bash
cd backend
python manage.py runserver
```

### 4. Automatic Prediction Updates
To automatically update predictions when their target date passes:

- Use the provided management command:
  ```bash
  python manage.py update_predictions
  ```
  
- For Windows, use the batch file:
  ```
  update_predictions.bat
  ```

- Set up a scheduled task to run this command daily

## Access Limit System

The system automatically tracks visits to premium content:

1. Anonymous users can access premium content 3 times
2. Free registered users can access premium content 3 times
3. After reaching the limit, users are prompted to upgrade
4. Paid users have unlimited access

## Technical Details

### Key Components

1. **VisitTrackerMiddleware**: 
   - Tracks visits to premium content
   - Enforces access limits
   - Redirects to subscription page when needed

2. **ChartPrediction Model**:
   - Stores user predictions
   - Automatically calculates accuracy when target date is reached
   - Publishes predictions to the public chart board

3. **Automatic Update System**:
   - Periodically checks predictions that have reached their target date
   - Updates prediction status and calculates accuracy
   - Updates user's overall prediction accuracy

4. **Access Control**:
   - Differentiates between anonymous, free, and paid users
   - Limits access based on user type and visit count
   - Provides appropriate payment prompts

## Admin Tasks

### Creating a Superuser
```bash
python manage.py createsuperuser
```

### Running Prediction Updates Manually
```bash
python manage.py update_predictions
```

### Resetting Free Visit Counter (For Testing)
Visit the admin panel and edit user records directly, or use the API endpoint:
```
/api/users/reset-free-visits/
```
