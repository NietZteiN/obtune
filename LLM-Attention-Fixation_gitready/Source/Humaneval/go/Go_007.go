import (
    "strings"
)

// Filter an input list of strings only for ones that contain given substring
// >>> FilterBySubstring([], 'a')
// []
// >>> FilterBySubstring(['abc', 'bacd', 'cde', 'array'], 'a')
// ['abc', 'bacd', 'array']
func FilterBySubstring(stringList []string, substring string) []string {

    result := make([]string, 0)
    for _, x := range stringList {
        if strings.Index(x, substring) != -1 {
            result = append(result, x)
        }
    }
    return result
}

func TestFilterBySubstring(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]string{}, FilterBySubstring([]string{}, "john"))
    assert.Equal([]string{"xxx", "xxxAAA", "xxx"}, FilterBySubstring([]string{"xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"}, "xxx"))
    assert.Equal([]string{"xxx", "aaaxxy", "xxxAAA", "xxx"}, FilterBySubstring([]string{"xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"}, "xx"))
    assert.Equal([]string{"grunt", "prune"}, FilterBySubstring([]string{"grunt", "trumpet", "prune", "gruesome"}, "run"))
}
