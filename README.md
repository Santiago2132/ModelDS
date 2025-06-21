# ModelDS

## Installation

To install and run the ModelDS application, follow these steps:

1. Ensure you have Python 3.x installed on your system.
2. Clone the repository or download the source code files.
3. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the Flask application:
   ```
   python app.py
   ```
6. The application will start running on `http://localhost:4000`.

## Usage

The ModelDS application provides a simple web interface and an API endpoint for interacting with the language model.

### Web Interface

1. Open your web browser and navigate to `http://localhost:4000`.
2. In the web interface, you can enter a query in the text area and click the "Enviar" button to get a response from the language model.
3. The response will be displayed in the "Respuesta" section.

### API Endpoint

The application also provides a `/api/ask` endpoint for making API requests.

Example request:
```
POST /api/ask
Content-Type: application/json

{
    "query": "¿Cuál es la capital de España?"
}
```

Example response:
```json
{
    "response": "La capital de España es Madrid."
}
```

## API

The ModelDS application provides the following API endpoint:

### `POST /api/ask`

- **Description:** Sends a query to the language model and returns the response.
- **Request Body:**
  - `query` (string, required): The query to be sent to the language model.
- **Response:**
  - On success:
    - `response` (string): The response from the language model.
  - On error:
    - `error` (string): A description of the error that occurred.

## Contributing

If you would like to contribute to the ModelDS project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

This project is licensed under the [MIT License](LICENSE).

## Testing

To run the tests for the ModelDS application, follow these steps:

1. Ensure you have the development dependencies installed:
   ```
   pip install -r requirements-dev.txt
   ```
2. Run the test suite:
   ```
   pytest
   ```

The test suite includes unit tests and integration tests to ensure the application is functioning correctly.
