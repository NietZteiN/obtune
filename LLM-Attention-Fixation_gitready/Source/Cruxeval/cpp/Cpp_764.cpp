#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string old, std::string replacement) {
    std::string text2 = text;
    size_t pos = text2.find(old);
    while (pos != std::string::npos) {
        text2.replace(pos, old.length(), replacement);
        pos = text2.find(old, pos + replacement.length());
    }

    std::string old2 = old;
    std::reverse(old2.begin(), old2.end());
    pos = text2.find(old2);
    while (pos != std::string::npos) {
        text2.replace(pos, old2.length(), replacement);
        pos = text2.find(old2, pos + replacement.length());
    }

    return text2;
}
int main() {
    auto candidate = f;
    assert(candidate(("some test string"), ("some"), ("any")) == ("any test string"));
}
