#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long count) {
    for (int i = 0; i < count; i++) {
        std::reverse(text.begin(), text.end());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("439m2670hlsw"), (3)) == ("wslh0762m934"));
}
