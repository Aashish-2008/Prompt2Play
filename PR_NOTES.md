PR: Improve LLM parsing, repair, fallback and generator variability

This PR contains:
- Stronger structured prompt schema (mechanics, entities, assets) to force varied LLM specs.
- Improved repair instruction and extraction logic.
- Richer rule-based fallback that maps keywords to mechanics/entities/assets to avoid a single generic output.
- Generator updates to honor spec.entities (shape/colors) so generated games vary by prompt.

Testing done locally: generated sample Shooter and Hole previews via /api/generate (manual spec). See backend/generated_games/*.html for artifacts.

Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>
