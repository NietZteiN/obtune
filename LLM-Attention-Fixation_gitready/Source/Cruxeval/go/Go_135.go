package f_test

import (
    "testing"
    "fmt"
)

func f() []string {
    d := map[string][]string{
        "Russia": {"Moscow", "Vladivostok"},
        "Kazakhstan": {"Astana"},
    }
    keys := make([]string, 0, len(d))
    for k := range d {
        keys = append(keys, k)
    }
    return keys
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(), expected: []string{"Russia", "Kazakhstan"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
