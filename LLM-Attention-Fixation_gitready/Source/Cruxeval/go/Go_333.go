package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(places []int, lazy []int) int {
	sort.Ints(places)
	for _, l := range lazy {
		for i, p := range places {
			if p == l {
				places = append(places[:i], places[i+1:]...)
				break
			}
		}
	}

	if len(places) == 1 {
		return 1
	}

	for i, place := range places {
		if countAdjacent(places, place+1) == 0 {
			return i + 1
		}
	}

	return len(places)
}

func countAdjacent(places []int, target int) int {
	count := 0
	for _, place := range places {
		if place == target {
			count++
		}
	}
	return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{375, 564, 857, 90, 728, 92}, []int{728}), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
