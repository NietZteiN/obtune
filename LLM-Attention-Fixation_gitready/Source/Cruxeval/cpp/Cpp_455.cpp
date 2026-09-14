#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int uppers = 0;
    for (char c : text) {
        if (std::isupper(c)) {
            uppers++;
        }
    }
    return (uppers >= 10) ? std::string(text.begin(), text.end()) : text;
}
int main() {
    auto candidate = f;
    assert(candidate(("?XyZ")) == ("?XyZ"));
}
