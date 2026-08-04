"""Deterministic ``ModelClient`` implementations for Wave09 AnswerAudit tests.

The vendor's :class:`~taaqqul_slot_geometry.audit.model_client.ModelClient`
protocol has a single method: ``complete(prompt: str) -> str``. This module
provides test-and-integration infrastructure — not a semantic engine — so
the deterministic AnswerAudit engine can be exercised without a live provider.

Constitutional constraints (docs/01, docs/18, campaign directive Phase D):

* The client returns bounded transport-layer payloads only.
* It does NOT construct :class:`AuditedAnswer` — that is vendor's job.
* It does NOT decide gamma / gate / verdict — pure kernel's job.
* It does NOT inspect Quranic surface or span identity to choose outputs.
* It does NOT bypass the native ``AnswerAudit.audit`` entrypoint — it is
  invoked by AnswerAudit through ``self._client.complete(prompt)``.

The three clients cover the failure-mode taxonomy required by Phase D:

* :class:`DeterministicModelClient` — configurable prompt→response mapping;
  deterministic; call log for verification.
* :class:`FailingModelClient` — raises a configured exception when
  ``complete`` is called (timeout, transport failure, arbitrary error).
* :class:`MalformedModelClient` — returns a non-string sentinel to
  exercise the vendor's own ``TypeError`` guard at answer_audit.py:411.

Every client has a deterministic ``call_log`` so tests can assert exact
per-scenario invocation counts, prompts, and (where applicable) returned
payloads without any secret / live provider exposure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class _CallRecord:
    prompt: str
    response: Any
    exception: BaseException | None = None


class DeterministicModelClient:
    """Prompt-to-response mapping with a stable ordering and call log.

    Two mapping modes:

    * ``responses`` — a dict of exact-prompt → response (str). Any prompt
      not in the dict falls back to ``default_response`` (a string). Both
      must be strings; None or non-str default raises at construction.
    * ``responder`` — a pure callable ``(prompt: str) -> str``. If provided
      it takes precedence over ``responses``. The callable MUST be
      deterministic; the module cannot enforce that but stores every
      call in ``call_log`` so tests can detect divergence.

    The client is a plain Python class (not a Protocol implementation
    with runtime magic): the vendor's ``@runtime_checkable`` protocol
    accepts any object exposing ``complete``, so this is sufficient.
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        default_response: str = "",
        responder: Callable[[str], str] | None = None,
    ) -> None:
        if responses is not None:
            if not isinstance(responses, dict):
                raise TypeError("responses must be dict[str, str] or None")
            for k, v in responses.items():
                if not isinstance(k, str):
                    raise TypeError("responses keys must be str")
                if not isinstance(v, str):
                    raise TypeError("responses values must be str")
        if not isinstance(default_response, str):
            raise TypeError("default_response must be str")
        if responder is not None and not callable(responder):
            raise TypeError("responder must be a callable or None")
        self._responses = dict(responses) if responses else {}
        self._default = default_response
        self._responder = responder
        self.call_log: list[_CallRecord] = []

    def complete(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            # The vendor protocol says prompt is str; we refuse
            # loudly to catch programmer error at the boundary.
            raise TypeError("complete() requires a str prompt")
        if self._responder is not None:
            response = self._responder(prompt)
            if not isinstance(response, str):
                raise TypeError(
                    "responder must return str; got "
                    f"{type(response).__name__}"
                )
        elif prompt in self._responses:
            response = self._responses[prompt]
        else:
            response = self._default
        self.call_log.append(_CallRecord(prompt=prompt, response=response))
        return response


class FailingModelClient:
    """Raises a configured exception on every ``complete`` call.

    Used to exercise the vendor's exception propagation contract: the
    ``AnswerAudit.audit`` method does NOT wrap ``self._client.complete``
    in try/except, so any exception raised by the client propagates to
    the caller. The Hokom adapter must convert the exception into a
    typed fail-closed integration outcome (never into a success).

    Common configurations:

    * ``FailingModelClient(exception=TimeoutError('provider timed out'))``
    * ``FailingModelClient(exception=ConnectionError('transport dead'))``
    * ``FailingModelClient(exception=RuntimeError('provider bug'))``
    """

    def __init__(self, exception: BaseException) -> None:
        if not isinstance(exception, BaseException):
            raise TypeError("exception must be a BaseException instance")
        self._exception = exception
        self.call_log: list[_CallRecord] = []

    def complete(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            raise TypeError("complete() requires a str prompt")
        record = _CallRecord(prompt=prompt, response=None,
                             exception=self._exception)
        self.call_log.append(record)
        raise self._exception


class MalformedModelClient:
    """Returns a non-string sentinel to exercise vendor's type guard.

    Vendor answer_audit.py:410-413 asserts::

        if not isinstance(answer, str):
            raise TypeError(
                "ModelClient.complete() must return a string answer (docs/01)"
            )

    This client's ``complete`` return value is deliberately typed as
    ``Any`` — the type checker will accept it; the vendor runtime will
    reject it. Used to prove that Hokom's adapter surfaces the vendor's
    TypeError as a typed integration DEFER rather than a raw exception
    or a fabricated success.
    """

    def __init__(self, payload: Any) -> None:
        # We deliberately do NOT type-check the payload here; the point
        # is to send a non-str value across the docs/01 boundary and
        # observe the vendor's own guard fire.
        self._payload = payload
        self.call_log: list[_CallRecord] = []

    def complete(self, prompt: str) -> Any:  # type: ignore[override]
        if not isinstance(prompt, str):
            raise TypeError("complete() requires a str prompt")
        self.call_log.append(_CallRecord(prompt=prompt, response=self._payload))
        return self._payload


__all__ = [
    "DeterministicModelClient",
    "FailingModelClient",
    "MalformedModelClient",
]
