package f_test

import (
	"testing"
	"fmt"
)

func f(a map[int]string, b int, c string, d string, e float64) string {
	num := ""
	if _, ok := a[b]; ok { // use b as the key to delete from the map
		num = a[b]
		delete(a, b)
	}
	if b > 3 {
		return c
	} else {
		return num
	}
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]string{7: "ii5p", 1: "o3Jwus", 3: "lot9L", 2: "04g", 9: "Wjf", 8: "5b", 0: "te6", 5: "flLO", 6: "jq", 4: "vfa0tW"}, 4, "Wy", "Wy", 1.0), expected: "Wy" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
