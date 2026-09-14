package f_test

import (
    "testing"
    "fmt"
)

func f(cities []string, name string) []string {
    if name == "" {
        return cities
    }
    if name != "cities" {
        return []string{}
    }
    result := []string{}
    for _, city := range cities {
        result = append(result, name+city)
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"Sydney", "Hong Kong", "Melbourne", "Sao Paolo", "Istanbul", "Boston"}, "Somewhere "), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
