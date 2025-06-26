import pytest
from solution import appearance

provided_tests = [
    {
        'id': 'provided_1',
        'intervals': {
            'lesson': [1594663200, 1594666800],
            'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
            'tutor': [1594663290, 1594663430, 1594663443, 1594666473]
        },
        'answer': 3117
    },
    {
        'id': 'provided_2',
        'intervals': {
            'lesson': [1594702800, 1594706400],
            'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564, 1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096, 1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500, 1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
            'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463]
        },
        'answer': 3577
    },
    {
        'id': 'provided_3',
        'intervals': {
            'lesson': [1594692000, 1594695600],
            'pupil': [1594692033, 1594696347],
            'tutor': [1594692017, 1594692066, 1594692068, 1594696341]
        },
        'answer': 3565
    },
]

custom_tests = [
    {
        'id': 'no_overlap',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 200], 'tutor': [300, 400]},
        'answer': 0
    },
    {
        'id': 'empty_intervals',
        'intervals': {'lesson': [0, 1000], 'pupil': [], 'tutor': []},
        'answer': 0
    },
    {
        'id': 'one_side_empty',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 200], 'tutor': []},
        'answer': 0
    },
    {
        'id': 'full_containment_tutor_in_pupil',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 500], 'tutor': [200, 300]},
        'answer': 100
    },
    {
        'id': 'intervals_need_merging',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 200, 180, 300], 'tutor': [150, 250]},
        'answer': 100
    },
    {
        'id': 'intervals_outside_lesson_time',
        'intervals': {'lesson': [100, 200], 'pupil': [0, 50, 250, 300], 'tutor': [0, 300]},
        'answer': 0
    },
    {
        'id': 'partial_lesson_overlap',
        'intervals': {'lesson': [100, 200], 'pupil': [50, 150], 'tutor': [120, 250]},
        'answer': 30
    },
    {
        'id': 'zero_duration_interval_ignored',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 200, 250, 250], 'tutor': [150, 300]},
        'answer': 50
    },
    {
        'id': 'touching_intervals_no_overlap',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 200], 'tutor': [200, 300]},
        'answer': 0
    },
    {
        'id': 'multiple_logins_same_person',
        'intervals': {'lesson': [0, 1000], 'pupil': [100, 300, 150, 250], 'tutor': [120, 280]},
        'answer': 160 # Overlap is [120, 280]
    },
    {
        'id': 'fully_nested_interval',
        'intervals': {
            'lesson': [0, 1000],
            'pupil': [100, 300, 150, 200],
            'tutor': [50, 350]
        },
        'answer': 200
    }
]


all_tests = provided_tests + custom_tests

@pytest.mark.parametrize("test_case", all_tests, ids=[tc['id'] for tc in all_tests])
def test_appearance(test_case):
    """Runs a single test case for the appearance function."""
    result = appearance(test_case['intervals'])
    assert result == test_case['answer'], f"Failed on test: {test_case['id']}"

if __name__ == "__main__":
    print("Running tests...")
    exit_code = pytest.main(["-v", "-s", __file__])
    print(f"\nTests finished with exit code: {exit_code}")
