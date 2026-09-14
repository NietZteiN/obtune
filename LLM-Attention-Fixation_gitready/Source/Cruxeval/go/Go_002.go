package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    new_text := []rune(text)
    for _, i := range []rune("+") {
        for index, char := range new_text {
            if char == i {
                new_text = append(new_text[:index], new_text[index+1:]...)
                break
            }
        }
    }
    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hbtofdeiequ"), expected: "hbtofdeiequ" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
