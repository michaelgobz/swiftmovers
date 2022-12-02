class AllocationStrategy:
    """Determine the allocation strategy for the channel.

    PRIORITIZE_SORTING_ORDER - allocate using distance order
    within the zone asc

    PRIORITIZE_HIGH_RISK - allocate using priority number and risk factor
    """

    PRIORITIZE_SORTING_ORDER = "prioritize-sorting-order"
    PRIORITIZE_HIGH_RISK = "prioritize-high-risk"

    CHOICES = [
        (PRIORITIZE_SORTING_ORDER, "Prioritize sorting order"),
        (PRIORITIZE_HIGH_RISK, "Prioritize high risk"),
    ]