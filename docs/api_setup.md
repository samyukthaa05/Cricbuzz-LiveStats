# Cricbuzz API setup

The integration is implemented in `api/cricbuzz_api.py` with `requests`, timeout handling, HTTP status handling, JSON-shape checks, and Streamlit caching for 30 seconds.

## Configure

1. Create `.env` from `.env.example`.
2. Add the API key and host issued by the Cricbuzz/RapidAPI provider.
3. Keep the standard configured base URL unless your provider documents another base URL.
4. Restart Streamlit after changing `.env`.

No credential is hard-coded. If either key or host is missing, the client does not call the network and the UI shows an honest unavailable state. The database pages remain fully functional.

## Data boundaries

The Live Match page labels responses `LIVE API DATA`. The relational totals are explicitly labeled `SAMPLE / SEED DATA`. The application never invents a live match when the provider returns an empty response or an error.