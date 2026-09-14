package f_test

import (
    "testing"
    "fmt"
)

func f(myString string) string {
    if myString == "" {
        return "more than ASCII"
    }
    for _, char := range myString {
        if (char < 'A' || char > 'Z') && (char < 'a' || char > 'z') && (char < '0' || char > '9') {
            return "more than ASCII"
        }
    }
    return "ascii encoded is allowed for this language"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Str zahrnuje anglo-ameriæske vasi piscina and kuca!"), expected: "more than ASCII" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
