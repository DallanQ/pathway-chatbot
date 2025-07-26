from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters


def generate_filters(doc_ids, role="missionary"):
    """
    Generate public/private document filters based on the doc_ids and the vector store.
    """
     # Always require that documents match the selected role (ACM or missionary)
    role_filter = MetadataFilter(key="role", value=role)

    # Define a filter to include only public documents (i.e. where private != true)
    public_doc_filter = MetadataFilter(
        key="private",
        value="true",
        operator="!=",
    )

    if len(doc_ids) > 0:
        # If specific document IDs are provided, allow those in addition to public ones
        selected_doc_filter = MetadataFilter(
            key="doc_id",
            value=doc_ids,
            operator="in",
        )

        # Combine filters:
        # - The user role must match (AND)
        # - And either the document is public OR it's one of the selected doc_ids
        return MetadataFilters(
            filters=[
                role_filter,
                MetadataFilters(
                    filters=[
                        public_doc_filter,
                        selected_doc_filter,
                    ],
                    condition="or",
                ),
            ],
            condition="and",
        )

    else:
        # If no doc_ids provided, allow only documents that match the role AND are public
        return MetadataFilters(
            filters=[role_filter, public_doc_filter],
            condition="and",
        )