import json


from app.prompts.knowledge_selection_prompt import knowledge_selection_prompt

from app.schemas.knowledge_selection import CandidateSelection

from app.services.ai_service import AIService


class KnowledgeSelectionService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    # Copia trechos recuperados e acrescenta identificadores "cadidate_id" para cada candidato, no formato "C01", "C02"
    def _build_candidates(self, sources: list[dict]) -> list[dict]:
        candidates = []

        for source in sources:
            paragraphs = source["content"].split("\n\n")

            for paragraph in paragraphs:
                paragraph = paragraph.strip()

                if not paragraph:
                    continue

                candidate = source.copy()

                candidate["content"] = paragraph

                candidate["candidate_id"] = f"C{len(candidates) + 1:02d}"

                candidates.append(candidate)

        return candidates

    # seleciona conteúdo de apoio e retorna os candidatos selecionados em JSON
    def select_context(
        self,
        user_context: str,
        retrieved_context: str,
        document_purpose: str,
    ) -> str:
        if not retrieved_context:
            return ""

        sources = json.loads(retrieved_context)

        if not sources:
            return ""

        candidates = self._build_candidates(sources)

        candidates_json = json.dumps(candidates, ensure_ascii=False, indent=2)

        prompt = knowledge_selection_prompt(
            user_context=user_context,
            candidates_json=candidates_json,
            document_purpose=document_purpose,
        )

        generated_response = self.ai_service.generate(prompt)

        print("===== SELEÇÃO DE CONHECIMENTO =====")
        print(generated_response, flush=True)
        print("===================================")

        selection_data = json.loads(generated_response)
        selection = CandidateSelection(**selection_data)

        selected_sources = []

        available_ids = [candidate["candidate_id"] for candidate in candidates]

        for selected_id in selection.selected_ids:
            if selected_id not in available_ids:
                raise ValueError(
                    f"O modelo selecionou um identificador inexistente: {selected_id}"
                )

        for candidate in candidates:
            if candidate["candidate_id"] in selection.selected_ids:
                selected_sources.append(candidate)

        if not selected_sources:
            return ""

        return json.dumps(
            selected_sources,
            ensure_ascii=False,
            indent=2,
        )
