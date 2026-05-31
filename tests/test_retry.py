from __future__ import annotations

from unittest.mock import patch

import pytest

from app.utils.retry import async_retry, retry


class TestRetry:
    def test_retry_success_first_try(self) -> None:
        call_count = 0

        @retry(max_retries=3)
        def succeed() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_retry_retry_then_succeed(self) -> None:
        call_count = 0

        @retry(max_retries=3, base_delay=0.01)
        def fail_twice() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fail_twice()
        assert result == "ok"
        assert call_count == 3

    def test_retry_exhausted(self) -> None:
        call_count = 0

        @retry(max_retries=2, base_delay=0.01)
        def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("always fails")

        with pytest.raises(RuntimeError, match="Failed after 2 retries"):
            always_fail()

        assert call_count == 3  # initial + 2 retries

    def test_retry_specific_exception(self) -> None:
        @retry(max_retries=1, base_delay=0.01, exceptions=(ValueError,))
        def raises_type_error() -> None:
            raise TypeError("wrong type")

        with pytest.raises(TypeError, match="wrong type"):
            raises_type_error()

    def test_retry_with_jitter(self) -> None:
        call_count = 0

        @retry(max_retries=1, base_delay=0.01, jitter=True)
        def fail_once() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("fail")
            return "ok"

        with patch("random.random", return_value=0.5), patch("time.sleep"):
            result = fail_once()

        assert result == "ok"

    def test_retry_without_jitter(self) -> None:
        call_count = 0

        @retry(max_retries=1, base_delay=0.01, jitter=False)
        def fail_once() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("fail")
            return "ok"

        result = fail_once()
        assert result == "ok"

    def test_retry_max_delay_cap(self) -> None:
        call_count = 0

        @retry(max_retries=3, base_delay=1.0, max_delay=1.5, exponential_base=10.0)
        def fail_often() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with (
            patch("random.random", return_value=0.0),
            patch("time.sleep") as mock_sleep,
            pytest.raises(RuntimeError),
        ):
            fail_often()

        assert mock_sleep.call_count == 3
        for call_args in mock_sleep.call_args_list:
            delay = call_args[0][0]
            assert delay <= 1.5


class TestAsyncRetry:
    @pytest.mark.asyncio
    async def test_async_retry_success(self) -> None:
        call_count = 0

        @async_retry(max_retries=2, base_delay=0.01)
        async def succeed() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await succeed()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry_exhausted(self) -> None:
        call_count = 0

        @async_retry(max_retries=1, base_delay=0.01)
        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(RuntimeError, match="Failed after 1 retries"):
            await always_fail()

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retry_with_jitter(self) -> None:
        call_count = 0

        @async_retry(max_retries=1, base_delay=0.01, jitter=True)
        async def fail_once() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("fail")
            return "ok"

        with patch("random.random", return_value=0.5), patch("asyncio.sleep"):
            result = await fail_once()

        assert result == "ok"
