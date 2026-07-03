# 0001: Why FastAPI over Flask for model serving

## Status

Accepted.

## Context

`services/model-serving` needs an HTTP endpoint that accepts a DNA
sequence, validates it strictly (exact length, a fixed nucleotide
alphabet -- see `app/schemas.py`), and returns a predicted class plus
per-class probabilities. This repo already uses both frameworks
elsewhere: `plugins/jbrowse2-sv-tracks/backend` is Flask, `services/fhir-api`
is FastAPI. That split is itself informative -- the choice was made
per-service based on what each service actually needed, not a blanket
preference.

## Decision

FastAPI, for three concrete reasons specific to this service (not "always
prefer FastAPI"):

1. **Pydantic-driven request validation is the actual bulk of this API's
   logic.** `PredictRequest`'s validator (length check, alphabet check)
   *is* most of what `/predict` needs to get right, and FastAPI turns a
   pydantic model directly into request parsing, validation, and OpenAPI
   schema generation with no extra code. Flask would need an add-on
   (marshmallow, or hand-rolled validation) to get the same guarantee,
   for no benefit here.
2. **Auto-generated interactive docs (`/docs`) are a genuine feature for
   a demonstration API,** not incidental -- someone evaluating this
   project can open `/docs` and try `/predict` with a real sequence
   without reading source code first.
3. **Consistency with `services/fhir-api`** lowers the cost of reading
   both services back-to-back, and this service, like `fhir-api`, is
   the kind of API where request/response shape correctness matters more
   than raw throughput.

Point 3 is a tie-breaker, not the primary reason -- `plugins/jbrowse2-sv-tracks/backend`
stayed Flask precisely because its two-endpoint, no-request-body API
didn't need any of the above, and rewriting a working, tested service
just for framework consistency would have been change for its own sake.

## Consequences

- Pulls in `pydantic`/`starlette` as dependencies (see
  `services/model-serving/pyproject.toml`) that a Flask app wouldn't need
  -- an acceptable tradeoff for a stateless service.
- `app/main.py`'s route handlers are declared `async def`, but the
  actual inference call (`bundle.model.predict(...)`) is a blocking,
  synchronous scikit-learn call -- FastAPI's async support isn't
  exploited for concurrency here. That's fine at this service's scale
  (a small model, low request volume, 2 replicas), but a real
  high-throughput deployment would want to run inference in a thread
  pool (`run_in_threadpool`) or a separate worker process rather than
  blocking the event loop, which this implementation does not do.
