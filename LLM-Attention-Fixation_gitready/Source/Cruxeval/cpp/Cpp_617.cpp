#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (std::all_of(text.begin(), text.end(), isascii)) {
        return "ascii";
    } else {
        return "non ascii";
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("<<<<")) == ("ascii"));
}
