# StatifyPlus

StatifyPlus is a tool designed to provide insights into Spotify user data. This project allows users to view their top artists and tracks over customizable time ranges.
if you want to try demo contact with me for demo access
https://statifyplus.onrender.com
if you don't have an access permission you can take "failed to fetch data error."

## Features

- **User Authentication**: Securely log in with your Spotify account using OAuth.
- **Listening Analysis**: Discover your top artists and tracks for specified time periods.

## Installation

### Prerequisites

Before installing StatifyPlus, ensure you have the following installed:

- [Python](https://www.python.org/downloads/) (version 3.7 or higher)
- [Spotify Developer Account](https://developer.spotify.com/)
- Required Python packages (listed in `requirements.txt`)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/ceyhunemre0/StatifyPlus.git
   cd StatifyPlus
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Spotify API credentials:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create a new application and note the `Client ID` and `Client Secret`.
   - Add the redirect URI: `http://localhost:8080/callback`.
   - Create a `.env` file in the root directory with the following:
     ```env
     CLIENT_ID=your_spotify_client_id
     CLIENT_SECRET=your_spotify_client_secret
     REDIRECT_URI=http://localhost:8080/callback
     ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:8080`.

## Usage

1. Log in using your Spotify account.
2. Allow the application to access your Spotify data.
3. View your top artists and tracks for the selected time range.

## Contributing

Currently, contributions are not being accepted as the project is in its initial stages. Once the codebase is stable, contribution guidelines and processes will be updated here.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Flask](https://flask.palletsprojects.com/)

---
