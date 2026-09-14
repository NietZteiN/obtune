#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> new_text;
    for (char character : text) {
        if (isupper(character)) {
            new_text.insert(new_text.begin() + new_text.size() / 2, character);
        }
    }
    if (new_text.empty()) {
        new_text = {'-'};
    }
    return std::string(new_text.begin(), new_text.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("String matching is a big part of RexEx library.")) == ("RES"));
}
