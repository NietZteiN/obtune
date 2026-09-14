package f_test

import (
    "testing"
    "fmt"
)

func f(dictionary map[string]int, key string) string {
    delete(dictionary, key)
    minKey := ""
    minValue := int(^uint(0) >> 1)
    for k, v := range dictionary {
        if v < minValue {
            minKey = k
            minValue = v
        }
    }
    if minKey == key {
        keys := make([]string, 0, len(dictionary))
        for k := range dictionary {
            keys = append(keys, k)
        }
        key = keys[0]
    }
    return key
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"Iron Man": 4, "Captain America": 3, "Black Panther": 0, "Thor": 1, "Ant-Man": 6}, "Iron Man"), expected: "Iron Man" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
