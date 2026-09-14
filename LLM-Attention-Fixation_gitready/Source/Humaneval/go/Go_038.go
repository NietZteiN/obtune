import (
    "math"
    "strings"
    "time"
)

// returns encoded string by cycling groups of three characters.
func EncodeCyclic(s string) string {
    groups := make([]string, 0)
    for i := 0; i < ((len(s) + 2) / 3); i++ {
        groups = append(groups, s[3*i:int(math.Min(float64(3*i+3), float64(len(s))))])
    }
    newGroups := make([]string, 0)
    for _, group := range groups {
        runes := []rune(group)
        if len(group) == 3 {
            newGroups = append(newGroups, string(append(runes[1:], runes[0])))
        } else {
            newGroups = append(newGroups, group)
        }
    }
    return strings.Join(newGroups, "")
}

// takes as input string encoded with EncodeCyclic function. Returns decoded string.
func DecodeCyclic(s string) string {

    return EncodeCyclic(EncodeCyclic(s))
}

func TestDecodeCyclic(t *testing.T) {
    assert := assert.New(t)
    randInt := func(min, max int) int {
        rng := rand.New(rand.NewSource(time.Now().UnixNano()))
        if min >= max || min == 0 || max == 0 {
            return max
        }
        return rng.Intn(max-min) + min
    }
    for i := 0; i <100 ; i++ {
        runes := make([]rune, 0)
        for j := 0; j < randInt(10,20); j++ {
            runes = append(runes, int32(randInt('a','z')))
        }
        encoded_str := EncodeCyclic(string(runes))
        assert.Equal(string(runes), DecodeCyclic(encoded_str))
    }
}
