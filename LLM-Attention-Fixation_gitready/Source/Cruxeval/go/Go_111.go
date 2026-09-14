package f_test

import (
    "testing"
    "fmt"
)

func f(marks map[string]int) []interface{} {
    highest := 0
    lowest := 100
    for _, value := range marks {
        if value > highest {
            highest = value
        }
        if value < lowest {
            lowest = value
        }
    }
    return []interface{}{highest, lowest}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"x": 67, "v": 89, "": 4, "alij": 11, "kgfsd": 72, "yafby": 83}), expected: []interface{}{89, 4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
