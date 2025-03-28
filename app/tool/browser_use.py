from app.utils.image_utils import resize_image


async def _try_all_engines(self, query: str) -> str:
    """Try all available search engines in sequence."""
    for engine in self.engines:
        try:
            result = await self._search_with_engine(engine, query)
            if result:
                return result
        except Exception as e:
            logger.error(f"Error with {engine}: {e}")
            continue
    return ""


async def _search_with_engine(self, engine: str, query: str) -> str:
    """Search using a specific engine."""
    try:
        if engine == "google":
            return await self._search_google(query)
        elif engine == "bing":
            return await self._search_bing(query)
        elif engine == "duckduckgo":
            return await self._search_duckduckgo(query)
        else:
            raise ValueError(f"Unsupported search engine: {engine}")
    except Exception as e:
        logger.error(f"Error searching with {engine}: {e}")
        return ""


async def _search_google(self, query: str) -> str:
    """Search using Google."""
    try:
        # Esegui la ricerca
        results = await self._execute_search(query)
        if not results:
            return ""

        # Ridimensiona le immagini se presenti
        for result in results:
            if "image" in result and "data" in result["image"]:
                result["image"]["data"] = resize_image(result["image"]["data"])

        return results
    except Exception as e:
        logger.error(f"Error searching with Google: {e}")
        return ""


# ... existing code ...
