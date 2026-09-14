#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string character, long min_count) {
    long count = std::count(text.begin(), text.end(), character[0]);
    if (count < min_count) {
        std::transform(text.begin(), text.end(), text.begin(),
        [](unsigned char c){ return std::isupper(c)? std::tolower(c) : std::toupper(c); });
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("wwwwhhhtttpp"), ("w"), (3)) == ("wwwwhhhtttpp"));
}
