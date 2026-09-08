import { useEffect, useState, useCallback } from "react";

/**
 * useFetch — runs an async fetcher function and tracks data/loading/error.
 * `fetcher` should be a stable function (e.g. from api/resource.api.js)
 * that returns a promise. Pass `deps` to control when it re-runs.
 */
export default function useFetch(fetcher, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const run = useCallback(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { data, error, loading, refetch: run };
}
