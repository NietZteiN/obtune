package f_test

import (
    "fmt"
    "testing"
)

func countOccurrences(arr []int, val int) int {
    count := 0
    for _, v := range arr {
        if v == val {
            count++
        }
    }
    return count
}

func f(bag map[int]int) map[int]int {
    values := make([]int, 0, len(bag))
    for _, v := range bag {
        values = append(values, v)
    }

    tbl := make(map[int]int)
    for v := 0; v < 100; v++ {
        if count := countOccurrences(values, v); count > 0 {
            tbl[v] = count
        }
    }

    return tbl
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{0: 0, 1: 0, 2: 0, 3: 0, 4: 0}), expected: map[int]int{0: 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
