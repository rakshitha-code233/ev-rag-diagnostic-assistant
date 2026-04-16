from rag import build_manual_index


if __name__ == "__main__":
    stats = build_manual_index()
    print(
        f"Indexed manuals successfully. Manuals: {stats['manuals_indexed']}, "
        f"chunks: {stats['chunks_indexed']}"
    )
