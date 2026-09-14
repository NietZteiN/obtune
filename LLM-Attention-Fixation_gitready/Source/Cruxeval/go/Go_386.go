package f_test

import (
    "testing"
    "fmt"
)

func f(concat string, di map[string]string) string {
    count := len(di)
    for i := 0; i < count; i++ {
        if _, ok := di[fmt.Sprintf("%d", i)]; ok {
            delete(di, fmt.Sprintf("%d", i))
        }
    }
    return "Done!"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mid", map[string]string{"0": "q", "1": "f", "2": "w", "3": "i"}), expected: "Done!" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
