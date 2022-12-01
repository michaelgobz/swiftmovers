class AllocationStrategy:
    """Determine the allocation strategy for each zone.

    PRIORITIZE_SORTING_ORDER - allocate stocks according to the traffic and distance in ascending' order
    within the zone based on how urgent transportation is needed
    """

    PRIORITIZE_SORTING_ORDER = "prioritize-sorting-order"
    PRIORITIZE_PRIVACY_CONCERNS = "prioritize-privacy-concerns"

    CHOICES = [
        (PRIORITIZE_SORTING_ORDER, "Prioritize sorting order"),
        (PRIORITIZE_PRIVACY_CONCERNS, "Prioritize privacy concerns")
    ]
