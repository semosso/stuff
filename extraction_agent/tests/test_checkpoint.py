"""Testes do checkpoint interativo, da contagem de uso e do recorte da
etapa de classificação."""

import dataclasses

import pytest

from agent.checkpoint import (
    NON_INTERACTIVE_CONTINUE,
    NON_INTERACTIVE_STOP,
    REASON_BUDGET,
    REASON_DEAL_COUNT,
    Checkpoint,
)
from agent.loop import ExtractionLoop
from agent.usage import UsageTracker, format_tokens


class FakeTerminal:
    """Terminal falso: grava o que foi escrito, devolve respostas na fila."""

    def __init__(self, answers=(), available=True):
        self.available = available
        self.written = []
        self._answers = list(answers)

    def write(self, text):
        self.written.append(text)

    def readline(self):
        return self._answers.pop(0) if self._answers else "\n"

    def close(self):
        pass

    @property
    def text(self):
        return "".join(self.written)


class FakeUsage:
    def __init__(self, input_tokens=0, output_tokens=0,
                 cache_creation_input_tokens=0, cache_read_input_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_creation_input_tokens = cache_creation_input_tokens
        self.cache_read_input_tokens = cache_read_input_tokens


class TestUsageTracker:
    def test_accumulates_all_four_buckets(self):
        tracker = UsageTracker()
        tracker.record(FakeUsage(1000, 500, 2000, 3000))
        tracker.record(FakeUsage(1000, 500, 0, 3000))
        assert tracker.calls == 2
        assert tracker.input_tokens == 2000
        assert tracker.output_tokens == 1000
        assert tracker.cache_creation_tokens == 2000
        assert tracker.cache_read_tokens == 6000
        assert tracker.total_input_tokens == 10000

    def test_cache_is_priced_below_normal_input(self):
        """Tratar cache a preço cheio superestimaria o gasto."""
        cached = UsageTracker(cache_read_tokens=1_000_000)
        plain = UsageTracker(input_tokens=1_000_000)
        assert cached.cost_usd(5.0, 25.0) == pytest.approx(0.50)
        assert plain.cost_usd(5.0, 25.0) == pytest.approx(5.00)

    def test_cache_write_costs_more_than_normal_input(self):
        written = UsageTracker(cache_creation_tokens=1_000_000)
        assert written.cost_usd(5.0, 25.0) == pytest.approx(6.25)

    def test_output_uses_the_output_price(self):
        assert UsageTracker(output_tokens=1_000_000).cost_usd(5.0, 25.0) == pytest.approx(25.0)

    def test_record_tolerates_none(self):
        tracker = UsageTracker()
        tracker.record(None)
        assert tracker.calls == 0

    def test_format_tokens(self):
        assert format_tokens(950) == "950"
        assert format_tokens(12_500) == "12K"
        assert format_tokens(2_400_000) == "2.4M"


class TestCheckpointTriggers:
    def test_disabled_when_nothing_configured(self):
        assert not Checkpoint(terminal=FakeTerminal()).enabled

    def test_pauses_every_n_deals(self):
        cp = Checkpoint(pause_every=3, terminal=FakeTerminal())
        usage = UsageTracker()
        assert cp.reason_to_pause(1, usage) == ""
        assert cp.reason_to_pause(2, usage) == ""
        assert cp.reason_to_pause(3, usage) == REASON_DEAL_COUNT

    def test_counter_restarts_after_a_pause(self):
        term = FakeTerminal(answers=["s\n"])
        cp = Checkpoint(pause_every=3, terminal=term)
        usage = UsageTracker()
        assert cp.reason_to_pause(3, usage) == REASON_DEAL_COUNT
        cp.review(3, 10, usage, REASON_DEAL_COUNT)
        assert cp.reason_to_pause(4, usage) == ""
        assert cp.reason_to_pause(6, usage) == REASON_DEAL_COUNT

    def test_budget_threshold_fires(self):
        # 1M tokens de output a $25/M = $25 = 50% de um orçamento de $50
        cp = Checkpoint(budget_usd=50.0, warn_pct=40, terminal=FakeTerminal())
        usage = UsageTracker(output_tokens=1_000_000)
        assert cp.reason_to_pause(1, usage) == REASON_BUDGET

    def test_budget_below_threshold_does_not_fire(self):
        cp = Checkpoint(budget_usd=50.0, warn_pct=80, terminal=FakeTerminal())
        assert cp.reason_to_pause(1, UsageTracker(output_tokens=1_000_000)) == ""

    def test_budget_asks_at_warn_then_at_100_then_stops_nagging(self):
        term = FakeTerminal(answers=["s\n", "s\n", "s\n"])
        cp = Checkpoint(budget_usd=50.0, warn_pct=80, terminal=term)
        usage = UsageTracker(output_tokens=1_700_000)  # $42.50 = 85%

        assert cp.reason_to_pause(1, usage) == REASON_BUDGET
        cp.review(1, 10, usage, REASON_BUDGET)

        usage.output_tokens = 2_200_000  # $55 = 110%
        assert cp.reason_to_pause(2, usage) == REASON_BUDGET
        cp.review(2, 10, usage, REASON_BUDGET)

        usage.output_tokens = 4_000_000  # $100 = 200%, já avisou duas vezes
        assert cp.reason_to_pause(3, usage) == ""

    def test_budget_wins_over_deal_count_when_both_would_fire(self):
        cp = Checkpoint(pause_every=1, budget_usd=10.0, warn_pct=50,
                        terminal=FakeTerminal())
        usage = UsageTracker(output_tokens=1_000_000)  # $25 > 50% de $10
        assert cp.reason_to_pause(1, usage) == REASON_BUDGET


class TestCheckpointPrompt:
    def test_yes_continues(self):
        term = FakeTerminal(answers=["s\n"])
        cp = Checkpoint(pause_every=1, terminal=term)
        assert cp.review(1, 10, UsageTracker(), REASON_DEAL_COUNT) is True

    def test_empty_answer_defaults_to_stopping(self):
        term = FakeTerminal(answers=["\n"])
        cp = Checkpoint(pause_every=1, terminal=term)
        assert cp.review(1, 10, UsageTracker(), REASON_DEAL_COUNT) is False

    def test_no_stops(self):
        term = FakeTerminal(answers=["n\n"])
        cp = Checkpoint(pause_every=1, terminal=term)
        assert cp.review(1, 10, UsageTracker(), REASON_DEAL_COUNT) is False

    def test_prompt_reports_the_numbers(self):
        term = FakeTerminal(answers=["s\n"])
        cp = Checkpoint(pause_every=5, budget_usd=100.0, terminal=term)
        usage = UsageTracker(input_tokens=500_000, output_tokens=200_000,
                             cache_read_tokens=1_000_000, calls=42)
        cp.review(5, 50, usage, REASON_DEAL_COUNT)
        text = term.text
        assert "5 de 50 deals" in text
        assert "42" in text                    # chamadas
        assert "Custo estimado" in text
        assert "Orçamento" in text
        assert "Projeção até o fim" in text
        assert "idempot" in text.lower()       # avisa que parar é seguro

    def test_budget_reason_is_explained(self):
        term = FakeTerminal(answers=["s\n"])
        cp = Checkpoint(budget_usd=10.0, warn_pct=50, terminal=term)
        cp.review(1, 10, UsageTracker(output_tokens=1_000_000), REASON_BUDGET)
        assert "orçamento declarado" in term.text


class TestCheckpointWithoutTerminal:
    def test_stops_by_default(self):
        cp = Checkpoint(pause_every=1, terminal=FakeTerminal(available=False))
        assert cp.review(1, 10, UsageTracker(), REASON_DEAL_COUNT) is False

    def test_can_be_configured_to_continue(self):
        cp = Checkpoint(pause_every=1, terminal=FakeTerminal(available=False),
                        non_interactive=NON_INTERACTIVE_CONTINUE)
        assert cp.review(1, 10, UsageTracker(), REASON_DEAL_COUNT) is True


class TestClassifyExcerpt:
    def test_short_document_is_sent_whole(self):
        text = "a" * 100
        assert ExtractionLoop.classify_excerpt(text, 12000) == text

    def test_zero_limit_disables_truncation(self):
        """REVERTER a otimização: CLASSIFY_CHAR_LIMIT=0."""
        text = "a" * 50_000
        assert ExtractionLoop.classify_excerpt(text, 0) == text

    def test_keeps_the_beginning_and_the_end(self):
        """O fim importa: é onde está a página de assinaturas."""
        text = "INICIO" + ("x" * 50_000) + "ASSINATURAS"
        excerpt = ExtractionLoop.classify_excerpt(text, 1000)
        assert excerpt.startswith("INICIO")
        assert excerpt.endswith("ASSINATURAS")
        assert len(excerpt) < len(text)

    def test_marks_the_omitted_middle(self):
        excerpt = ExtractionLoop.classify_excerpt("y" * 50_000, 1000)
        assert "omitido" in excerpt

    def test_respects_the_size_budget(self):
        excerpt = ExtractionLoop.classify_excerpt("z" * 100_000, 5000)
        # trecho + marcador; o marcador é curto e fixo
        assert len(excerpt) < 5000 + 200


class TestBatchIntegrationWithCheckpoint:
    def test_stopping_at_checkpoint_ends_the_batch(self, config):
        from agent.loop import DealResult, STATUS_PROCESSED
        from tests.test_batch import DEALS_HEADER, LINK_A, LINK_B, clients_with

        clients, _ = clients_with(config, {
            "Deals": [
                DEALS_HEADER,
                ["Acme Ltda", LINK_A, "x"],
                ["Beta S.A.", LINK_B, "x"],
            ],
            "Pendente": [], "Publicado": [],
        })
        loop = ExtractionLoop(config, clients=clients, claude=object())
        loop.run_deal = lambda c, f: DealResult(c, STATUS_PROCESSED)

        cp = Checkpoint(pause_every=1, terminal=FakeTerminal(answers=["n\n"]))
        summary = loop.run_batch(checkpoint=cp)

        assert len(summary.deals) == 1  # parou depois do primeiro
        assert summary.stopped
        assert "continuar de onde parou" in summary.stopped

    def test_continuing_processes_everything(self, config):
        from agent.loop import DealResult, STATUS_PROCESSED
        from tests.test_batch import DEALS_HEADER, LINK_A, LINK_B, clients_with

        clients, _ = clients_with(config, {
            "Deals": [
                DEALS_HEADER,
                ["Acme Ltda", LINK_A, "x"],
                ["Beta S.A.", LINK_B, "x"],
            ],
            "Pendente": [], "Publicado": [],
        })
        loop = ExtractionLoop(config, clients=clients, claude=object())
        loop.run_deal = lambda c, f: DealResult(c, STATUS_PROCESSED)

        cp = Checkpoint(pause_every=1, terminal=FakeTerminal(answers=["s\n", "s\n"]))
        summary = loop.run_batch(checkpoint=cp)

        assert len(summary.deals) == 2
        assert not summary.stopped


class TestEffortIsConfigurable:
    def test_default_is_medium(self, config):
        assert config.effort == "medium"

    def test_can_be_reverted_to_high(self, config):
        """REVERTER a otimização: CLAUDE_EFFORT=high."""
        assert dataclasses.replace(config, effort="high").effort == "high"
