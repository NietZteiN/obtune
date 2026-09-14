package f_test

import (
    "testing"
    "fmt"
)

func f(text string, size int) string {
    counter := len(text)
    for i := 0; i < size-int(size%2); i++ {
        text = " " + text + " "
        counter += 2
        if counter >= size {
            return text
        }
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("7", 10), expected: "     7     " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
