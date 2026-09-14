#include <assert.h>
#include <bits/stdc++.h>
std::string f(std::string text, std::string character) {
    size_t length = text.length();
    int index = -1;
    for (size_t i = 0; i < length; ++i) {
        if (text[i] == character[0]) {
            index = i;
        }
    }
    if (index == -1) {
        index = length / 2;
    }
    text.erase(index, 1);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("o horseto"), ("r")) == ("o hoseto"));
}
