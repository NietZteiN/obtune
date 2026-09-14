package f_test

import (
    "testing"
    "fmt"
    "sort"
)

func f(m map[string]int) string {
    type kv struct {
        Key string
        Value int
    }

    var ss []kv
    for k, v := range m {
        ss = append(ss, kv{k, v})
    }

    sort.Slice(ss, func(i, j int) bool {
        return ss[i].Value < ss[j].Value
    })

    keys := make([]string, 0, len(ss))
    for _, kv := range ss {
        keys = append(keys, kv.Key)
    }

    if len(keys)%2 == 0 {
        return fmt.Sprintf("%s=%s", keys[0], keys[1])
    } else {
        return fmt.Sprintf("%s=%s", keys[1], keys[0])
    }
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"l": 4, "h": 6, "o": 9}), expected: "h=l" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
