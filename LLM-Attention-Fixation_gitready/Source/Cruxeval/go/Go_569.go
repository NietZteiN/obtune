package f_test

import (
    "testing"
    "fmt"
)

func f(txt string) int {
    coincidences := make(map[rune]int)
    for _, c := range txt {
        if val, ok := coincidences[c]; ok {
            coincidences[c] = val + 1
        } else {
            coincidences[c] = 1
        }
    }
    
    sum := 0
    for _, value := range coincidences {
        sum += value
    }
    
    return sum
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("11 1 1"), expected: 6 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
