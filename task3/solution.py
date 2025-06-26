def appearance(intervals: dict[str, list[int]]) -> int:
    """
    Calculates the total time in seconds that a pupil and a tutor
    are simultaneously present during a lesson.
    """

    lesson_start, lesson_end = intervals["lesson"]

    PERSON_PUPIL = 0
    PERSON_TUTOR = 1
    person_intervals = enumerate([intervals["pupil"], intervals["tutor"]])

    INACTIVE = -1
    ACTIVE   = +1
    events = []
    for person, times in person_intervals:
        for i in range(0, len(times), 2):
            start, end = times[i], times[i+1]
            assert start <= end, "Back to the future!"
            start = min(max(start, lesson_start), lesson_end)
            end   = min(max(end,   lesson_start), lesson_end)
            events.append((start, ACTIVE, person))
            events.append((end, INACTIVE, person))


    # If boundaries collide, the old end (0) will be processed before new start (1)
    events.sort()


    total_overlap = 0
    last_time = lesson_start
    # State starts with 0, and then gets pulled towards active or inactive
    # And it accumulates them. Why - for example user will log in with two devices
    # A A I I - this should be active on all 3 periods.
    pupil_state = 0
    tutor_state = 0
    for time, event, person in events:
        is_pupil_active = pupil_state > 0
        is_tutor_active = tutor_state > 0
        if is_pupil_active and is_tutor_active:
            duration = time - last_time
            total_overlap += duration

        if person == PERSON_PUPIL:
            pupil_state += event
        else:
            assert person == PERSON_TUTOR, f"Unexpected person #{person}"
            tutor_state += event

        last_time = time

    return total_overlap
