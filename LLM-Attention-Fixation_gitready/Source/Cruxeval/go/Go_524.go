package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(dict0 map[int]int) map[int]int {
	new := make(map[int]int)
	for k, v := range dict0 {
		new[k] = v
	}
	keys := make([]int, 0, len(new))
	for k := range new {
		keys = append(keys, k)
	}
	sort.Ints(keys)
	for i := 0; i < len(keys)-1; i++ {
		dict0[keys[i]] = i
	}
	return dict0
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{2: 5, 4: 1, 3: 5, 1: 3, 5: 1}), expected: map[int]int{2: 1, 4: 3, 3: 2, 1: 0, 5: 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
