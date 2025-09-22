import httpx
import os
from app.langfuse import langfuse
from langfuse.decorators import langfuse_context

async def get_location_from_ip(ip_address: str) -> dict:
    """
    Fetches geographical location (country, state, city) from an IP address using Geoapify.
    """
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        print("GEOAPIFY_API_KEY not set in environment variables.")
        return {}

    # Initialize location_data with ip_address, so it's always present
    location_data = {"ip_address": ip_address}

    # Send IP address to Langfuse
    with langfuse.span(name="get_location_from_ip", trace_id=langfuse_context.get_current_trace_id(), input={"ip_address": ip_address}) as span:

        print(f"[DEBUG] get_location_from_ip called with IP: {ip_address}")

        url = f"https://api.geoapify.com/v1/ipinfo?ip={ip_address}&apiKey={api_key}"
        print(f"[DEBUG] Geoapify API URL: {url}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                print(f"[DEBUG] Geoapify API response data: {data}")

                if "country" in data:
                    location_data["country"] = data["country"]["name"]
                if "state" in data:
                    location_data["state"] = data["state"]["name"]
                if "city" in data:
                    location_data["city"] = data["city"]["name"]
                
                span.update(output=location_data)
                return location_data

        except httpx.RequestError as e:
            print(f"[ERROR] An error occurred while requesting Geoapify API: {e}")
        except httpx.HTTPStatusError as e:
            print(f"[ERROR] Geoapify API returned an error status {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")
        
        # If an error occurs, ensure ip_address is still in the output
        span.update(output=location_data)
        return location_data