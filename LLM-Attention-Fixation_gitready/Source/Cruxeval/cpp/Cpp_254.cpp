#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string repl) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    std::transform(repl.begin(), repl.end(), repl.begin(), ::tolower);

    std::map<char, char> trans;
    for (size_t i = 0; i < text.size(); ++i) {
        trans[text[i]] = repl[i % repl.size()];
    }

    for (size_t i = 0; i < text.size(); ++i) {
        text[i] = trans[text[i]];
    }

    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("upper case"), ("lower case")) == ("lwwer case"));
}
