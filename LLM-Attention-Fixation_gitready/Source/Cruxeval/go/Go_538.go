package f_test

import (
    "testing"
    "fmt"
)

func f(text string, width int) string {
    runeText := []rune(text)
    if len(runeText) > width {
        runeText = runeText[:width]
    }

    for len(runeText) < width {
        runeText = append([]rune{'z'}, runeText...)
        if len(runeText) < width {
            runeText = append(runeText, 'z')
        }
    }

    return string(runeText)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("0574", 9), expected: "zzz0574zz" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
