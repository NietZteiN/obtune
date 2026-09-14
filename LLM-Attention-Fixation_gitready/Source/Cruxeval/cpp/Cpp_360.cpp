#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long n) {
    if (text.length() <= 2) {
        return text;
    }
    std::string leading_chars(n - text.length() + 1, text[0]);
    return leading_chars + text.substr(1, text.length() - 2) + text.back();
}
int main() {
    auto candidate = f;
    assert(candidate(("g"), (15)) == ("g"));
}
